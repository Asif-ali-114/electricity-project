"""
data_processing/generate_sample_data.py

Generates 12 realistic monthly household electricity-usage CSV files
(January.csv ... December.csv) into the /data directory.

Design goals (per product spec):
- Summer months -> heavier AC/fan usage.
- Winter months -> heavier water-heater/heating usage.
- Evenings -> lights, TV, fans, AC spike.
- Mornings -> water heater, lights, kitchen appliances spike.
- Refrigerator -> fairly constant, low-variance, 24/7.
- Washing machine -> a small number of discrete sessions, not continuous.
- Computer/laptop -> concentrated in study/work hours.
- Data is NOT purely random -- it follows repeatable seasonal + daily
  behavioral curves with realistic noise layered on top.

Output columns: Date, Time, Appliance, Power_Watts, Duration_Hours, Energy_kWh, Cost
Cost is computed with the English (USD) rate at generation time; the app
recomputes cost live from utils/currency.py so it always matches the
currently selected language/currency regardless of what's in the CSV.
"""

from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from calendar import monthrange
from pathlib import Path

random.seed(42)  # reproducible "realistic" data across runs

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USD_RATE_PER_KWH = 0.14

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Northern-hemisphere-style seasonal weight for cooling (AC/fans) vs heating
# (water heater draw). 1.0 = baseline, higher = more usage that season.
COOLING_WEIGHT = {
    1: 0.25, 2: 0.30, 3: 0.45, 4: 0.65, 5: 0.90, 6: 1.30,
    7: 1.50, 8: 1.45, 9: 1.10, 10: 0.70, 11: 0.40, 12: 0.28,
}
HEATING_WEIGHT = {
    1: 1.40, 2: 1.30, 3: 1.00, 4: 0.70, 5: 0.40, 6: 0.20,
    7: 0.15, 8: 0.15, 9: 0.30, 10: 0.60, 11: 1.00, 12: 1.35,
}

# Baseline appliance definitions: (rated_watts, base_daily_hours)
APPLIANCES = {
    "Air Conditioner":     {"watts": 1500, "base_hours": 3.0, "profile": "cooling"},
    "Electric Fan":        {"watts": 75,   "base_hours": 4.0, "profile": "cooling"},
    "Water Heater":        {"watts": 2000, "base_hours": 1.2, "profile": "heating"},
    "Refrigerator":        {"watts": 150,  "base_hours": 24.0, "profile": "constant"},
    "Television":          {"watts": 120,  "base_hours": 3.5, "profile": "evening"},
    "Lights":              {"watts": 60,   "base_hours": 5.0, "profile": "evening_morning"},
    "Washing Machine":     {"watts": 500,  "base_hours": 0.75, "profile": "sessions"},
    "Water Pump":          {"watts": 750,  "base_hours": 0.5, "profile": "morning"},
    "Microwave":           {"watts": 1100, "base_hours": 0.25, "profile": "meals"},
    "Electric Oven":       {"watts": 2200, "base_hours": 0.4, "profile": "meals"},
    "Computer":            {"watts": 200,  "base_hours": 3.0, "profile": "work_hours"},
    "Laptop":              {"watts": 65,   "base_hours": 4.0, "profile": "work_hours"},
    "Iron":                {"watts": 1100, "base_hours": 0.3, "profile": "sessions"},
    "Kitchen Appliances":  {"watts": 800,  "base_hours": 1.0, "profile": "meals"},
    "Other Appliances":    {"watts": 100,  "base_hours": 2.0, "profile": "constant"},
}

# Representative start time (hour, 24h) for each profile, used to pick
# a realistic single logged Time per appliance-day entry.
PROFILE_HOUR_CHOICES = {
    "cooling": [13, 14, 15, 20, 21, 22],
    "heating": [6, 7, 19, 20],
    "constant": [0, 6, 12, 18],
    "evening": [19, 20, 21],
    "evening_morning": [6, 7, 19, 20, 21],
    "sessions": [10, 11, 16, 17],
    "morning": [6, 7, 8],
    "meals": [7, 8, 13, 19, 20],
    "work_hours": [9, 10, 14, 15, 20, 21],
}


def seasonal_multiplier(profile: str, month: int) -> float:
    if profile == "cooling":
        return COOLING_WEIGHT[month]
    if profile == "heating":
        return HEATING_WEIGHT[month]
    return 1.0


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Sat/Sun


def generate_day_rows(d: date, month: int) -> list[dict]:
    rows = []
    weekend_boost = 1.15 if is_weekend(d) else 1.0

    for name, spec in APPLIANCES.items():
        watts = spec["watts"]
        base_hours = spec["base_hours"]
        profile = spec["profile"]

        mult = seasonal_multiplier(profile, month) * weekend_boost
        noise = random.uniform(0.85, 1.15)

        if profile == "sessions":
            # Washing machine / iron: only run on some days, as discrete sessions
            runs_today = random.random() < (0.5 if name == "Washing Machine" else 0.35)
            if not runs_today:
                continue
            duration = round(base_hours * random.uniform(0.8, 1.3), 2)
            hour = random.choice(PROFILE_HOUR_CHOICES[profile])
        elif profile == "meals":
            # Kitchen-type appliances: 1-3 short sessions per day
            session_count = random.choice([1, 1, 2, 3])
            for _ in range(session_count):
                duration = round(base_hours * random.uniform(0.7, 1.3), 2)
                hour = random.choice(PROFILE_HOUR_CHOICES[profile])
                energy = round((watts * duration) / 1000, 3)
                rows.append(_row(d, hour, name, watts, duration, energy))
            continue
        else:
            raw_duration = base_hours * mult * noise
            # Constant-load appliances (e.g. fridge) run continuously and
            # must never exceed 24h/day; everything else is capped at 23h
            # to leave room for realistic partial-day usage.
            cap = 24.0 if profile == "constant" else 23.0
            duration = round(min(cap, max(0.1, raw_duration)), 2)
            hour = random.choice(PROFILE_HOUR_CHOICES.get(profile, [12]))

        energy = round((watts * duration) / 1000, 3)
        rows.append(_row(d, hour, name, watts, duration, energy))

    return rows


def _row(d: date, hour: int, appliance: str, watts: int, duration: float, energy: float) -> dict:
    cost = round(energy * USD_RATE_PER_KWH, 3)
    return {
        "Date": d.isoformat(),
        "Time": f"{hour:02d}:00",
        "Appliance": appliance,
        "Power_Watts": watts,
        "Duration_Hours": duration,
        "Energy_kWh": energy,
        "Cost": cost,
    }


def generate_month(year: int, month: int) -> list[dict]:
    days_in_month = monthrange(year, month)[1]
    all_rows = []
    for day_num in range(1, days_in_month + 1):
        d = date(year, month, day_num)
        all_rows.extend(generate_day_rows(d, month))

    # Inject a small number of intentional data-quality issues so the
    # app's validation/cleaning features have something real to catch.
    all_rows = _inject_data_quality_issues(all_rows)
    return all_rows


def _inject_data_quality_issues(rows: list[dict]) -> list[dict]:
    n = len(rows)
    issue_count = max(2, n // 150)  # small, realistic proportion
    for _ in range(issue_count):
        idx = random.randrange(n)
        issue_type = random.choice(["missing_value", "negative_energy", "blank_appliance"])
        if issue_type == "missing_value":
            rows[idx]["Cost"] = ""
        elif issue_type == "negative_energy":
            rows[idx]["Energy_kWh"] = -abs(rows[idx]["Energy_kWh"])
        elif issue_type == "blank_appliance":
            rows[idx]["Appliance"] = ""
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    fieldnames = ["Date", "Time", "Appliance", "Power_Watts", "Duration_Hours", "Energy_kWh", "Cost"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(year: int = 2025) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for month in range(1, 13):
        rows = generate_month(year, month)
        out_path = DATA_DIR / f"{MONTH_NAMES[month - 1]}.csv"
        write_csv(rows, out_path)
        print(f"Generated {out_path.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
