"""
bottle_sync.py: connects the AquaPod bottle to the AquaSip app.

What it does
  1. Reads the bottle's records from the Firebase Realtime Database
     (/events/<BOTTLE_ID> and /status/<BOTTLE_ID>, written by the ESP32).
  2. Adds every new "drink" the bottle detected to the app's drink history,
     exactly as if the user had logged it, so totals, history and the AI coach
     all use real bottle data. Pours and refills are never counted as intake.
  3. Shows a small "Your bottle" card: online/offline, water left, tilt.
     It refreshes by itself every 10 seconds.

Settings (in .streamlit/secrets.toml, or as environment variables)
  FIREBASE_RTDB_HOST = "your-project-default-rtdb.asia-southeast1.firebasedatabase.app"
  BOTTLE_ID          = "AquaSip-3F2A"
  FIREBASE_RTDB_AUTH = ""      # optional, only once the database rules need a token

How to add it to aqua1.0.py (2 lines): see HOW_TO_CONNECT.md.
Needs Streamlit 1.37+ for the 10-second auto-refresh; older versions refresh when the page reruns.
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime, timedelta, timezone

import requests

MYT = timezone(timedelta(hours=8), "MYT")   # Malaysia has no daylight saving, so a fixed offset is exact
REFRESH_SECONDS = 10                         # the bottle sends a status every 10 s
IMPORT_DAYS = 14                             # only bring in drinks from the last 14 days
MAX_DRINK_ML = 2000                          # anything bigger is a bad reading, not a sip
ONLINE_S, DELAYED_S = 45, 300                # status age: online / delayed / offline
_KEY_OK = re.compile(r"^[^.$#\[\]/]+$")       # characters Firebase allows in a key
_SYNC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aquasip_bottle_sync.json")


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------
def get_config(secrets=None) -> dict:
    """Host, bottle id and optional auth token from secrets.toml or the environment."""
    def pick(name, default=""):
        try:
            if secrets is not None and name in secrets:
                return str(secrets[name]).strip()
        except Exception:      # no secrets.toml at all
            pass
        return os.environ.get(name, default).strip()

    host = pick("FIREBASE_RTDB_HOST")
    host = host.rstrip("/")
    if host and not host.startswith(("http://", "https://")):
        host = "https://" + host
    bottle = pick("BOTTLE_ID", "AquaSip-3F2A") or "AquaSip-3F2A"
    return {
        "host": host,
        "bottle_id": bottle if _KEY_OK.match(bottle) else "",
        "auth": pick("FIREBASE_RTDB_AUTH"),
    }


# ---------------------------------------------------------------------------
# reading Firebase
# ---------------------------------------------------------------------------
def fetch(host: str, bottle_id: str, auth: str = "", timeout: float = 5.0) -> dict:
    """Returns {"events": ..., "status": ..., "error": str | None}. Never raises."""
    out = {"events": None, "status": None, "error": None}
    params = {"auth": auth} if auth else None
    try:
        for kind in ("events", "status"):
            r = requests.get(f"{host}/{kind}/{bottle_id}.json", params=params, timeout=timeout)
            if r.status_code in (401, 403):
                out["error"] = "Permission denied: check the database rules."
                return out
            if r.status_code != 200:
                out["error"] = f"Firebase replied {r.status_code}."
                return out
            out[kind] = r.json()
    except requests.exceptions.RequestException:
        out["error"] = "Can't reach Firebase. Check the internet connection."
    except ValueError:
        out["error"] = "Firebase sent something that isn't JSON. Check FIREBASE_RTDB_HOST."
    return out


def _parse_time(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None:                     # the firmware always sends UTC with a Z
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc)


def parse_events(data, now: datetime | None = None) -> list[dict]:
    """Firebase /events JSON -> clean list, oldest first. Bad records are skipped."""
    now = now or datetime.now(timezone.utc)
    if not isinstance(data, dict):
        return []
    out = []
    for key, rec in data.items():
        if not isinstance(rec, dict):
            continue
        t = _parse_time(rec.get("timestamp"))
        kind = rec.get("event")
        try:
            vol = float(rec.get("volume"))
        except (TypeError, ValueError):
            continue
        if t is None or t > now + timedelta(minutes=5) or kind not in ("drink", "pour", "refill"):
            continue
        if vol != vol or vol < 0 or vol > MAX_DRINK_ML:   # NaN or impossible
            continue
        out.append({"key": str(key), "time": t, "event": kind, "volume": int(round(vol))})
    out.sort(key=lambda e: e["time"])
    return out


def parse_status(data, now: datetime | None = None) -> dict:
    """Firebase /status JSON -> what the card needs."""
    now = now or datetime.now(timezone.utc)
    s = data if isinstance(data, dict) else {}
    seen = _parse_time(s.get("last_seen"))
    age = (now - seen).total_seconds() if seen else None
    if age is None:
        link = "none"
    elif age <= ONLINE_S:
        link = "online"
    elif age <= DELAYED_S:
        link = "delayed"
    else:
        link = "offline"

    def num(k):
        try:
            v = float(s.get(k))
            return None if v != v else v
        except (TypeError, ValueError):
            return None

    calibrated = s.get("calibrated")
    return {
        "link": link,
        "age_s": age,
        "level_ml": num("level_ml"),
        "tilt_deg": num("tilt_deg"),
        "calibrated": calibrated if isinstance(calibrated, bool) else None,
    }


# ---------------------------------------------------------------------------
# adding the bottle's drinks to the app's history
# ---------------------------------------------------------------------------
def _load_sync_state() -> dict:
    try:
        with open(_SYNC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_sync_state(state: dict) -> None:
    try:
        with open(_SYNC_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def new_drinks(events: list[dict], imported: set, now: datetime | None = None) -> list[dict]:
    """Drinks not added yet, from the last IMPORT_DAYS days."""
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(days=IMPORT_DAYS)
    return [e for e in events
            if e["event"] == "drink" and e["volume"] > 0 and e["time"] >= since and e["key"] not in imported]


def as_history_entry(drink: dict) -> dict:
    """Same shape as log_drink() writes, plus where it came from."""
    local = drink["time"].astimezone(MYT)
    return {"date": local.strftime("%Y-%m-%d"), "time": local.strftime("%H:%M"),
            "amount": int(drink["volume"]), "source": "bottle", "bottle_key": drink["key"]}


def as_session_log(drink: dict) -> dict:
    """Same shape as log_drink() puts in st.session_state.water_logs."""
    local = drink["time"].astimezone(MYT)
    return {"time": local.strftime("%I:%M:%S %p").lower(), "amount": int(drink["volume"]),
            "timestamp": drink["time"].timestamp()}


def _time_of_day(log: dict) -> str:
    try:
        return datetime.strptime(log.get("time", ""), "%I:%M:%S %p").strftime("%H:%M:%S")
    except ValueError:
        return ""


def merge_into_today(water_logs: list, drinks: list[dict], today_str: str) -> list:
    """Adds today's bottle drinks to the on-screen log, newest first, keeping existing entries."""
    todays = [as_session_log(d) for d in drinks
              if d["time"].astimezone(MYT).strftime("%Y-%m-%d") == today_str]
    merged = list(water_logs) + todays
    merged.sort(key=_time_of_day, reverse=True)
    return merged


def sync_drinks(events: list[dict], user_key: str, get_history, save_history) -> list[dict]:
    """Adds new bottle drinks to the history. Returns the drinks that were added.

    The keys already added are remembered in aquasip_bottle_sync.json, so a drink
    is never added twice, even after "Reset Water" clears today's history.
    """
    state = _load_sync_state()
    imported = set(state.get(user_key, []))
    fresh = new_drinks(events, imported)
    if not fresh:
        return []
    hist = get_history()
    for d in fresh:
        hist.append(as_history_entry(d))
        imported.add(d["key"])
    hist.sort(key=lambda e: (e.get("date", ""), e.get("time", "")))
    save_history(hist)
    state[user_key] = sorted(imported)[-5000:]
    _save_sync_state(state)
    return fresh


# ---------------------------------------------------------------------------
# the card
# ---------------------------------------------------------------------------
_LINK = {
    "online": ("#16A34A", "Online"),
    "delayed": ("#D97706", "Delayed"),
    "offline": ("#DC2626", "Offline"),
    "none": ("#94A3B8", "No signal yet"),
}


def _ago(seconds) -> str:
    if seconds is None:
        return ""
    s = max(0, int(seconds))
    if s < 60:
        return f"{s} s ago"
    if s < 3600:
        return f"{s // 60} min ago"
    if s < 86400:
        return f"{s // 3600} h ago"
    return f"{s // 86400} d ago"


def card_html(status: dict | None, error: str | None, bottle_id: str) -> str:
    esc = html.escape
    if error:
        body = f'<div style="font-size:13px;color:#B91C1C !important;font-weight:600;">{esc(error)}</div>'
        dot, label, when = "#94A3B8", "Not connected", ""
    else:
        dot, label = _LINK[status["link"]]
        when = _ago(status["age_s"])
        if status["calibrated"] is False:
            water = '<span style="color:#64748B !important;font-weight:600;font-size:13px;">Not calibrated yet</span>'
        elif status["level_ml"] is not None:
            water = f'{int(round(status["level_ml"]))} <span style="font-size:12px;font-weight:600;color:#64748B !important;">ml</span>'
        else:
            water = '<span style="color:#64748B !important;font-weight:600;font-size:13px;">-</span>'
        tilt = "-" if status["tilt_deg"] is None else f'{status["tilt_deg"]:.0f}°'
        body = (
            '<div style="display:flex;gap:10px;margin-top:10px;">'
            '<div style="flex:1;background:#F1F5F9;border-radius:12px;padding:10px 12px;">'
            '<div style="font-size:11px;font-weight:700;color:#64748B !important;text-transform:uppercase;letter-spacing:.04em;">In bottle</div>'
            f'<div style="font-size:18px;font-weight:800;color:#0F172A !important;margin-top:2px;">{water}</div></div>'
            '<div style="flex:1;background:#F1F5F9;border-radius:12px;padding:10px 12px;">'
            '<div style="font-size:11px;font-weight:700;color:#64748B !important;text-transform:uppercase;letter-spacing:.04em;">Tilt</div>'
            f'<div style="font-size:18px;font-weight:800;color:#0F172A !important;margin-top:2px;">{tilt}</div></div>'
            '</div>'
        )
    return (
        '<div class="app-card" style="padding:14px 18px;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        '<div style="font-size:14px;font-weight:800;color:#0F172A !important;">💧 Your bottle '
        f'<span style="font-size:11px;font-weight:600;color:#64748B !important;">{esc(bottle_id)}</span></div>'
        f'<div style="display:flex;align-items:center;gap:6px;font-size:12px;font-weight:700;color:{dot} !important;">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{dot};display:inline-block;"></span>{label}'
        f'<span style="color:#94A3B8 !important;font-weight:600;">{esc(when)}</span></div>'
        '</div>'
        f'{body}'
        '</div>'
    )


_cached_fetch = None


def render_bottle(get_history, save_history, user_key: str = "guest") -> None:
    """Call this near the top of render_home(). See HOW_TO_CONNECT.md."""
    import streamlit as st

    global _cached_fetch
    if _cached_fetch is None:
        _cached_fetch = st.cache_data(ttl=REFRESH_SECONDS - 1, show_spinner=False)(fetch)

    cfg = get_config(getattr(st, "secrets", None))
    if not cfg["host"] or not cfg["bottle_id"]:
        st.markdown(card_html(None, "Bottle not set up: add FIREBASE_RTDB_HOST to .streamlit/secrets.toml.",
                              cfg["bottle_id"] or "-"), unsafe_allow_html=True)
        return

    def _body():
        data = _cached_fetch(cfg["host"], cfg["bottle_id"], cfg["auth"])
        status = None if data["error"] else parse_status(data["status"])
        st.markdown(card_html(status, data["error"], cfg["bottle_id"]), unsafe_allow_html=True)
        if data["error"]:
            return
        added = sync_drinks(parse_events(data["events"]), user_key, get_history, save_history)
        if added:
            st.session_state.water_logs = merge_into_today(
                st.session_state.get("water_logs", []), added, datetime.now().strftime("%Y-%m-%d"))
            total = sum(d["volume"] for d in added)
            st.session_state["bottle_sync_msg"] = (
                f"Added {total} ml from your bottle" + (f" ({len(added)} sips)" if len(added) > 1 else ""))
            st.rerun()   # redraw the whole page so the totals include the new drinks

    msg = st.session_state.pop("bottle_sync_msg", None)
    if msg and hasattr(st, "toast"):
        st.toast(msg, icon="💧")

    if hasattr(st, "fragment"):          # Streamlit 1.37+: refresh this card by itself every 10 s
        st.fragment(run_every=REFRESH_SECONDS)(_body)()
    else:                                # older Streamlit: refreshes whenever the page reruns
        _body()
