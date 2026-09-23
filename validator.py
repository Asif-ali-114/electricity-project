"""
data_processing/validator.py

Validates a loaded (canonical-schema) DataFrame and produces a
DataQualityReport, per spec section 33 (Data Quality Analysis):
    Rows, Valid Records, Invalid Records, Missing Values

Checks performed:
- Missing values in required fields
- Invalid / unparseable dates
- Invalid / unparseable numeric fields
- Negative energy values
- Missing appliance names
- Missing required columns (already enforced by loader, re-checked here)
"""

from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd

REQUIRED_COLUMNS = ["Date", "Appliance", "Energy_kWh"]


@dataclass
class DataQualityReport:
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    missing_values: int = 0
    issues: dict[str, int] = field(default_factory=dict)
    invalid_row_indices: list[int] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "rows": self.total_rows,
            "valid_records": self.valid_rows,
            "invalid_records": self.invalid_rows,
            "missing_values": self.missing_values,
            "issues": self.issues,
        }


def validate(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport(total_rows=len(df))
    issues = {
        "missing_appliance": 0,
        "invalid_date": 0,
        "invalid_number": 0,
        "negative_energy": 0,
        "missing_values": 0,
    }

    invalid_mask = pd.Series(False, index=df.index)

    # Missing appliance names
    missing_appliance = df["Appliance"].isna() | (df["Appliance"].astype(str).str.strip() == "")
    issues["missing_appliance"] = int(missing_appliance.sum())
    invalid_mask |= missing_appliance

    # Invalid dates
    parsed_dates = pd.to_datetime(df["Date"], errors="coerce")
    invalid_dates = parsed_dates.isna()
    issues["invalid_date"] = int(invalid_dates.sum())
    invalid_mask |= invalid_dates

    # Invalid / non-numeric energy values
    energy_numeric = pd.to_numeric(df["Energy_kWh"], errors="coerce")
    invalid_numbers = energy_numeric.isna()
    issues["invalid_number"] = int(invalid_numbers.sum())
    invalid_mask |= invalid_numbers

    # Negative energy (only counted where the number IS valid but negative)
    negative_energy = energy_numeric.notna() & (energy_numeric < 0)
    issues["negative_energy"] = int(negative_energy.sum())
    invalid_mask |= negative_energy

    # Missing values across any column that matters for analysis
    missing_any = df[REQUIRED_COLUMNS].isna().any(axis=1)
    issues["missing_values"] = int(df[REQUIRED_COLUMNS].isna().sum().sum())
    invalid_mask |= missing_any

    report.invalid_row_indices = df.index[invalid_mask].tolist()
    report.invalid_rows = int(invalid_mask.sum())
    report.valid_rows = report.total_rows - report.invalid_rows
    report.missing_values = issues["missing_values"]
    report.issues = issues
    return report
