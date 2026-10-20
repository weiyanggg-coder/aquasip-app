"""
AquaSip AI module (Ain)
-----------------------
Run this file ONCE (python aquasip_ai.py) to:
  1. make SYNTHETIC drink data  -> aquasip_synthetic_full.csv
  2. make a 50-row demo sample  -> aquasip_demo_50.csv  (bottle packet format)
  3. clean, train, compare baseline vs models (held-out USERS)
  4. save the model              -> aquasip_model.joblib

Friend (Streamlit app) then only needs:
    from aquasip_ai import get_recommendation
    result = get_recommendation(hour=14, cum_intake_ml=800,
                                events_last_2h=2, avg_event_ml_last_2h=180)
    # {"predicted_2h_ml": 190, "status": "behind_pace", "suggested_ml": 120}

NOTE: all data here is SIMULATED. Not medical advice.
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
import joblib

RNG = np.random.default_rng(7)
GOAL_ML = 2000
WAKE_HOUR, SLEEP_HOUR = 7, 22
MAX_SUGGESTION_ML = 500          # safety cap: never suggest more than this
BOTTLE_CAPACITY_ML = 750
MODEL_PATH = "aquasip_model.joblib"
FEATURES = ["hour", "cum_intake_ml", "events_last_2h", "avg_event_ml_last_2h"]


def generate_synthetic_events(n_users=12, n_days=10):
    rows, event_id = [], 0
    for user in range(n_users):
        user_scale = RNG.uniform(0.7, 1.3)
        for day in range(n_days):
            t = WAKE_HOUR
            while t < SLEEP_HOUR:
                if RNG.random() < 0.55:
                    volume = max(10, RNG.normal(180, 60) * user_scale)
                    event_id += 1
                    rows.append({"event_id": event_id, "user": user, "day": day,
                                 "hour": t, "volume_ml": round(volume)})
                t += RNG.uniform(0.5, 2.0)
    return pd.DataFrame(rows)


def clean_events(df):
    before = len(df)
    df = df.drop_duplicates(subset="event_id")
    df = df[(df["volume_ml"] > 0) & (df["volume_ml"] <= BOTTLE_CAPACITY_ML)]
    print(f"Cleaning: removed {before - len(df)} of {before} rows "
          f"({(before - len(df)) / before:.1%}).")
    return df.reset_index(drop=True)


def make_demo_sample(events, n=50):
    """First n events of user 0 in the bottle packet format
    {"id", "timestamp", "volume", "event"} (simulated dates)."""
    s = events[events["user"] == 0].sort_values(["day", "hour"]).head(n)
    start = pd.Timestamp("2026-09-24")
    ts = [(start + pd.Timedelta(days=int(d), hours=float(h))).strftime("%Y-%m-%dT%H:%M:%SZ")
          for d, h in zip(s["day"], s["hour"])]
    return pd.DataFrame({"id": s["event_id"].values, "timestamp": ts,
                         "volume": s["volume_ml"].values, "event": "drink"})


def build_feature_table(events):
    rows = []
    for (user, day), g in events.groupby(["user", "day"]):
        for cp in np.arange(WAKE_HOUR, SLEEP_HOUR, 1.0):
            so_far = g[g["hour"] <= cp]
            nxt = g[(g["hour"] > cp) & (g["hour"] <= cp + 2)]
            recent = g[(g["hour"] > cp - 2) & (g["hour"] <= cp)]
            rows.append({"user": user, "day": day, "hour": cp,
                         "cum_intake_ml": so_far["volume_ml"].sum(),
                         "events_last_2h": len(recent),
                         "avg_event_ml_last_2h": recent["volume_ml"].mean() if len(recent) else 0,
                         "target_next_2h_ml": nxt["volume_ml"].sum()})
    return pd.DataFrame(rows)


def baseline_predict(df):
    total = SLEEP_HOUR - WAKE_HOUR
    el = df["hour"] - WAKE_HOUR
    now = GOAL_ML * el / total
    plus2 = GOAL_ML * (el + 2).clip(upper=total) / total
    return (plus2 - now).clip(lower=0)


def evaluate(y_true, y_pred, label):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"{label:>24} | MAE {mae:6.1f} mL | RMSE {rmse:6.1f} mL | R2 {r2:5.2f}")


def train_and_save():
    events = clean_events(generate_synthetic_events())
    events.to_csv("aquasip_synthetic_full.csv", index=False)
    make_demo_sample(events).to_csv("aquasip_demo_50.csv", index=False)

    table = build_feature_table(events)
    X, y = table[FEATURES], table["target_next_2h_ml"]

    # hold out whole USERS so the test is fair (no same-person leakage)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=7)
    tr, te = next(gss.split(X, y, groups=table["user"]))
    print(f"Dataset: {len(table)} rows, {table['user'].nunique()} users. "
          f"Train {len(tr)} | Test {len(te)} (unseen users)\n")

    evaluate(y.iloc[te], baseline_predict(table.iloc[te]), "Baseline (even pacing)")
    lin = LinearRegression().fit(X.iloc[tr], y.iloc[tr])
    evaluate(y.iloc[te], lin.predict(X.iloc[te]), "Linear Regression")
    rf = RandomForestRegressor(n_estimators=200, random_state=7).fit(X.iloc[tr], y.iloc[tr])
    evaluate(y.iloc[te], rf.predict(X.iloc[te]), "Random Forest")

    # final model for the app: the one that did best on unseen users
    # (linear regression here), refit on all data
    final = LinearRegression().fit(X, y)
    joblib.dump(final, MODEL_PATH)
    print(f"\nSaved {MODEL_PATH}, aquasip_synthetic_full.csv, aquasip_demo_50.csv")


_model = None
def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            train_and_save()
        _model = joblib.load(MODEL_PATH)
    return _model


def get_recommendation(hour, cum_intake_ml, events_last_2h, avg_event_ml_last_2h):
    """Returns a small, stable dict for the app to display."""
    if hour < WAKE_HOUR or hour >= SLEEP_HOUR:
        return {"predicted_2h_ml": 0, "status": "outside_hours", "suggested_ml": 0}

    x = pd.DataFrame([[hour, cum_intake_ml, events_last_2h, avg_event_ml_last_2h]],
                     columns=FEATURES)
    predicted = max(0.0, float(_load_model().predict(x)[0]))

    total = SLEEP_HOUR - WAKE_HOUR
    expected_by_plus2 = GOAL_ML * min(hour - WAKE_HOUR + 2, total) / total
    shortfall = expected_by_plus2 - (cum_intake_ml + predicted)

    if shortfall < 50:
        status, suggested = "on_track", 0
    else:
        status = "behind_pace"
        suggested = int(min(shortfall, MAX_SUGGESTION_ML) // 10 * 10)

    return {"predicted_2h_ml": int(round(predicted)), "status": status,
            "suggested_ml": suggested}


if __name__ == "__main__":
    train_and_save()
    print("\nExample:", get_recommendation(14, 800, 2, 180))
