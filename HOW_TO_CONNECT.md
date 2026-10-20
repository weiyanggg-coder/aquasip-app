# Connecting the AquaPod bottle to the AquaSip app

`bottle_sync.py` adds two things to the Home screen:

- A **"Your bottle" card** showing Online / Delayed / Offline, the water left in the bottle and its tilt. It refreshes by itself every 10 seconds.
- **Automatic drink logging.** Every sip the bottle detects is added to the drink history, just as if the user had tapped Quick Drink. The totals, history, AI coach and forecasts then use real bottle data. Pours and refills are never counted as intake.

It only **reads** from the Firebase Realtime Database: `/events/<BOTTLE_ID>` and `/status/<BOTTLE_ID>`, written by the ESP32. It never writes to Firebase.

## Setup (5 minutes)

### 1. Copy the file
Put `bottle_sync.py` in the same folder as `aqua1.0.py`.

### 2. Add the settings
In `.streamlit/secrets.toml`, which is the same file that holds `GEMINI_API_KEY`, add:

```toml
FIREBASE_RTDB_HOST = "aquasip-app-default-rtdb.asia-southeast1.firebasedatabase.app"
BOTTLE_ID = "AquaSip-3F2A"
```

Use the host only: no `https://` and no `/` at the end. `BOTTLE_ID` must match `BOTTLE_ID` in the ESP32 code.

### 3. Add 2 lines to `aqua1.0.py`

**a)** Under `import aquasip_smart as smart`:
```python
import bottle_sync  # AquaPod bottle: live card + automatic drink logging
```

**b)** In `render_home()`, right after the Switch Cup check:
```python
def render_home():
    if st.session_state.sub_page == "Switch Cup":
        render_switch_cup()
        return

    # AquaPod bottle: shows the bottle card and adds the bottle's drinks to today's log
    bottle_sync.render_bottle(get_history, _save_history_to_disk, _user_key())
```

That's all. `aqua1.0_bottle.py` is the version Zara sent with these lines already added, if you'd rather compare.

### 4. Recommended fix in `load_todays_water_logs()`
At the moment, drinks loaded from the history file get `"timestamp": 0`. After the app restarts, "drinks in the last 2 hours" can't see them. Replace that line with a real time:

```python
        try:
            ts = datetime.strptime(f"{e.get('date')} {e.get('time', '00:00')}", "%Y-%m-%d %H:%M").timestamp()
        except Exception:
            ts = 0
        logs.append({
            "time": time_display,
            "amount": int(e.get("amount", 0)),
            "timestamp": ts,
        })
```

This is also already done in `aqua1.0_bottle.py`.

## Good to know

- **Don't double count.** When the bottle is connected, sips are logged automatically. Quick Drink is only for drinks from other cups.
- Bottle drinks are saved in `aquasip_history.json` with `"source": "bottle"`, so you can tell them apart from manual ones.
- `aquasip_bottle_sync.json` (created automatically) remembers which bottle drinks were already added, so none are added twice, even after **Reset Water**. Don't delete it. If you do, drinks from the last 14 days are added again.
- Needs **Streamlit 1.37 or newer** for the 10-second auto-refresh. On older versions the card updates whenever the page reruns, for example when a button is tapped.
- **Until the load cell is calibrated**, the bottle only sends tilt. The card shows "Not calibrated yet" and no drinks arrive yet. That's expected.
- **Database rules:** the database is in test mode, so anyone with the link can read and write it, and test mode stops after 30 days. Before demo day, tighten the rules. If reads then need a token, add `FIREBASE_RTDB_AUTH = "..."` to `secrets.toml`.

## If the card shows an error

| Card says | Fix |
|---|---|
| Bottle not set up | `FIREBASE_RTDB_HOST` is missing from `.streamlit/secrets.toml` |
| Can't reach Firebase | Internet connection, or a typo in the host |
| Firebase replied 404 | Wrong host. Copy it from the Realtime Database **Data** tab. |
| Permission denied | The database rules block reading. Check the **Rules** tab, or set `FIREBASE_RTDB_AUTH`. |
| No signal yet | The bottle hasn't sent a status. Is the ESP32 on and connected to Wi-Fi? |
| Offline | The last status is more than 5 minutes old. The bottle is off or out of Wi-Fi. |
