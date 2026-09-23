"""
data_processing/cleaner.py

Cleans a canonical-schema DataFrame based on the issues found by
validator.validate(), producing an analysis-ready DataFrame plus a
human-readable log of what was done. The raw/original data is never
mutated in place -- clean_data() always returns a new DataFrame.
"""

from __future__ import annotations
import pandas as pd

from data_processing.validator import validate


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Returns (cleaned_df, log) where log is a list of human-readable
    strings describing each cleaning action taken (used in the Data
    Explorer / Data Quality UI).
    """
    log: list[str] = []
    working = df.copy()

    before_report = validate(working)
    log.append(
        f"Loaded {before_report.total_rows} rows "
        f"({before_report.valid_rows} valid, {before_report.invalid_rows} flagged)."
    )

    # 1. Drop rows with missing/blank appliance name.
    blank_appliance = working["Appliance"].isna() | (working["Appliance"].astype(str).str.strip() == "")
    dropped_appliance = int(blank_appliance.sum())
    working = working[~blank_appliance]
    if dropped_appliance:
        log.append(f"Removed {dropped_appliance} row(s) with a missing appliance name.")

    # 2. Drop rows with unparseable dates.
    parsed_dates = pd.to_datetime(working["Date"], errors="coerce")
    bad_dates = parsed_dates.isna()
    dropped_dates = int(bad_dates.sum())
    working = working[~bad_dates]
    parsed_dates = parsed_dates[~bad_dates]
    working["Date"] = parsed_dates
    if dropped_dates:
        log.append(f"Removed {dropped_dates} row(s) with an invalid date.")

    # 3. Coerce numeric columns; drop rows where Energy_kWh is unparseable.
    for col in ["Power_Watts", "Duration_Hours", "Energy_kWh", "Cost"]:
        working[col] = pd.to_numeric(working[col], errors="coerce")

    bad_energy = working["Energy_kWh"].isna()
    dropped_energy = int(bad_energy.sum())
    working = working[~bad_energy]
    if dropped_energy:
        log.append(f"Removed {dropped_energy} row(s) with a non-numeric energy value.")

    # 4. Negative energy values -> treat as data-entry errors, take absolute value
    #    (flagged in the log rather than silently discarded, since the session
    #    itself is likely real, just mis-signed).
    negative_mask = working["Energy_kWh"] < 0
    fixed_negative = int(negative_mask.sum())
    working.loc[negative_mask, "Energy_kWh"] = working.loc[negative_mask, "Energy_kWh"].abs()
    if fixed_negative:
        log.append(f"Corrected {fixed_negative} row(s) with negative energy values (sign flipped).")

    # 5. Fill missing Duration_Hours / Power_Watts from Energy_kWh where derivable,
    #    otherwise leave NaN (not required for most analyses).
    derivable = working["Duration_Hours"].isna() & working["Power_Watts"].notna() & (working["Power_Watts"] > 0)
    working.loc[derivable, "Duration_Hours"] = (
        working.loc[derivable, "Energy_kWh"] * 1000 / working.loc[derivable, "Power_Watts"]
    ).round(2)

    # 6. Add helper columns used throughout the analysis layer.
    working["Date"] = pd.to_datetime(working["Date"])
    working["Month"] = working["Date"].dt.month
    working["Day"] = working["Date"].dt.day
    working["Weekday"] = working["Date"].dt.day_name()
    working["Hour"] = pd.to_datetime(working["Time"], format="%H:%M", errors="coerce").dt.hour
    working["Hour"] = working["Hour"].fillna(12).astype(int)

    working = working.reset_index(drop=True)
    log.append(f"Cleaning complete: {len(working)} analysis-ready rows.")
    return working, log
