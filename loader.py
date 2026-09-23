"""
data_processing/loader.py

Loads a CSV into a normalized pandas DataFrame with intelligent column
mapping, so the app can accept slightly different real-world CSV headers
without breaking.

Canonical schema after loading:
    Date, Time, Appliance, Power_Watts, Duration_Hours, Energy_kWh, Cost

If Energy_kWh is missing but Power_Watts + Duration_Hours are present,
it is derived: Energy_kWh = Power_Watts * Duration_Hours / 1000.
If Cost is missing, it is left blank here -- cost is always computed
downstream via utils.currency so it matches the active language/currency,
never trusted verbatim from an arbitrary uploaded CSV.
"""

from __future__ import annotations
import pandas as pd
from pathlib import Path

# Maps lowercased/normalized incoming header -> canonical column name.
COLUMN_ALIASES = {
    "date": "Date",
    "time": "Time",
    "appliance": "Appliance",
    "appliance name": "Appliance",
    "appliance_name": "Appliance",
    "device": "Appliance",
    "power": "Power_Watts",
    "power_watts": "Power_Watts",
    "power (w)": "Power_Watts",
    "watts": "Power_Watts",
    "duration": "Duration_Hours",
    "duration_hours": "Duration_Hours",
    "duration (hrs)": "Duration_Hours",
    "hours": "Duration_Hours",
    "energy": "Energy_kWh",
    "energy_kwh": "Energy_kWh",
    "energy (kwh)": "Energy_kWh",
    "kwh": "Energy_kWh",
    "cost": "Cost",
    "price": "Cost",
}

REQUIRED_CANONICAL = {"Date", "Appliance"}
CANONICAL_ORDER = ["Date", "Time", "Appliance", "Power_Watts", "Duration_Hours", "Energy_kWh", "Cost"]


class LoadError(Exception):
    """Raised when a CSV cannot be loaded or mapped to the canonical schema."""


def _normalize_header(col: str) -> str:
    return str(col).strip().lower().replace("-", " ").replace("_", " ").strip()


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename incoming columns to the canonical schema using COLUMN_ALIASES."""
    rename_map = {}
    for col in df.columns:
        norm = _normalize_header(col)
        norm_key = norm.replace(" ", "_")
        canonical = COLUMN_ALIASES.get(norm) or COLUMN_ALIASES.get(norm_key)
        if canonical:
            rename_map[col] = canonical
    return df.rename(columns=rename_map)


def load_csv(path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file and map it to the canonical WattWise schema.
    Raises LoadError for missing files, empty files, or files missing
    the minimum required columns (Date, Appliance).
    """
    path = Path(path)
    if not path.exists():
        raise LoadError(f"File not found: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise LoadError("The selected file is empty.")
    except Exception as exc:  # noqa: BLE001 - surfaced as a friendly LoadError
        raise LoadError(f"Could not read CSV: {exc}") from exc

    if df.empty:
        raise LoadError("The selected file is empty.")

    df = map_columns(df)

    missing_required = REQUIRED_CANONICAL - set(df.columns)
    if missing_required:
        raise LoadError(
            f"This file is missing required columns: {', '.join(sorted(missing_required))}"
        )

    # Ensure all canonical columns exist (fill absent optional ones with NA).
    for col in CANONICAL_ORDER:
        if col not in df.columns:
            df[col] = pd.NA

    # Derive Energy_kWh from Power_Watts * Duration_Hours where missing.
    power = pd.to_numeric(df["Power_Watts"], errors="coerce")
    duration = pd.to_numeric(df["Duration_Hours"], errors="coerce")
    energy = pd.to_numeric(df["Energy_kWh"], errors="coerce")
    derivable = energy.isna() & power.notna() & duration.notna()
    df.loc[derivable, "Energy_kWh"] = (power[derivable] * duration[derivable] / 1000).round(3)

    df = df[CANONICAL_ORDER]
    return df


def load_multiple(paths: list[str | Path]) -> pd.DataFrame:
    """Load and concatenate multiple monthly CSVs (multi-month / full-year analysis)."""
    frames = [load_csv(p) for p in paths]
    if not frames:
        raise LoadError("No files provided.")
    return pd.concat(frames, ignore_index=True)
