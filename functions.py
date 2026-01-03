import pandas as pd
import re

# =================================================
# CONSTANTS
# =================================================
REQUIRED_AUDIT_COLUMNS = {
    "created_at", "updated_at", "created_by",
    "updated_by", "is_deleted", "deleted_at"
}

COMMON_ABBREVIATIONS = {"qty", "amt", "num", "cnt", "val"}

# =================================================
# HELPER FUNCTIONS
# =================================================

def add_sr_no(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out.insert(0, "Sr No", range(1, len(df_out) + 1))
    return df_out
    
def is_date_like_column(col_name: str) -> bool:
    col = col_name.lower()
    return bool(
        re.search(r"(date|_dt$|_at$|timestamp)", col)
    )

def validate_date_column(series: pd.Series) -> str:
    """
    Validates whether a column actually contains date-like values.
    Returns a human-readable status for audit reporting.
    """

    # Case 1: Fully empty column
    if series.isna().all():
        return "date-like name, but column is empty"

    # Try parsing dates
    parsed = pd.to_datetime(series, errors="coerce")

    valid_ratio = parsed.notna().mean()

    # Case 2: Mostly invalid dates
    if valid_ratio < 0.5:
        return "date-like name, but values are not dates"

    # Case 3: Looks valid
    return "date (validated)"
    
def infer_schema_type(col_name, pandas_dtype):
    name = col_name.lower()
    if "date" in name or name.endswith("_dt"):
        return "date"
    if name.startswith("is_"):
        return "boolean"
    return str(pandas_dtype)


def detect_date_columns(df):
    candidates = []
    for col in df.columns:
        col_l = col.lower()
        if any(x in col_l for x in ["date", "_dt", "_at"]):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > 0.6:
                candidates.append(col)
    return candidates


def validate_column_naming(df):
    rows = []
    violating_columns = []

    for col in df.columns:
        issues = []

        if " " in col:
            issues.append("Contains spaces")
        if "-" in col:
            issues.append("Contains dash (-)")
        if '"' in col:
            issues.append('Contains double quotes (")')
        if col.lower() != col:
            issues.append("Must be lowercase")
        if not re.match(r"^[a-z][a-z0-9_]*$", col):
            issues.append("Not snake_case")
        if re.search(r"[A-Z]", col):
            issues.append("camelCase detected")
        if re.search(r"\d$", col):
            issues.append("Numeric suffix detected")
        if any(t in COMMON_ABBREVIATIONS for t in col.split("_")):
            issues.append("Ambiguous abbreviation")

        if issues:
            violating_columns.append(col)

        rows.append({
            "Column": col,
            "Naming Issues": ", ".join(issues) if issues else "OK"
        })

    missing_audit = REQUIRED_AUDIT_COLUMNS - set(df.columns)
    return pd.DataFrame(rows), violating_columns, missing_audit
    
