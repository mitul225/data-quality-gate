import streamlit as st
import pandas as pd
import re
from io import BytesIO
from report import generate_pdf
from functions import infer_schema_type, detect_date_columns, validate_column_naming, is_date_like_column, validate_date_column, add_sr_no

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Data Quality Gate",
    page_icon="🛡️",
    layout="wide"
)

# =================================================
# CSS
# =================================================
st.markdown("""
<style>
body { font-family: Inter, sans-serif; }
h1, h2, h3 { letter-spacing: -0.4px; }
small { color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# =================================================
# HEADER
# =================================================
st.markdown("## Data Quality Gate")
st.markdown(
    "<small>Validate data quality before it reaches analytics.</small>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# =================================================
# HELPER FUNCTIONS
# =================================================

def compute_date_range(df, col):
    parsed = pd.to_datetime(df[col], errors="coerce")
    return {
        "column": col,
        "min_date": parsed.min().date() if parsed.notna().any() else None,
        "max_date": parsed.max().date() if parsed.notna().any() else None,
        "span_days": (parsed.max() - parsed.min()).days if parsed.notna().any() else None,
        "invalid_pct": round(parsed.isna().mean() * 100, 2),
        "invalid_date_count": parsed.isna().sum()
    }

def load_csv_universal(uploaded_file):
    """
    Universal CSV loader that handles:
    - Unknown encodings
    - Excel BOM files
    - Dirty rows
    - Mixed datatypes
    """

    encodings_to_try = [
        "utf-8",
        "utf-8-sig",   # Excel BOM
        "cp1252",      # Windows default
        "latin-1"      # Ultimate fallback (never fails)
    ]

    last_exception = None

    for enc in encodings_to_try:
        try:
            df = pd.read_csv(
                uploaded_file,
                encoding=enc,
                low_memory=False,
                on_bad_lines="skip"   # skip only broken rows
            )
            return df, enc
        except Exception as e:
            last_exception = e
            uploaded_file.seek(0)
            
    # If everything fails (extremely rare)
    raise ValueError(
        "Unable to read CSV file. The file may be severely corrupted."
    ) from last_exception
    
    
st.info(
    "Privacy note: Uploaded files are processed in-memory for analysis only. "
    "No data is stored, logged, or shared. Files are discarded automatically "
    "when the session ends."
)

# =================================================
# MAIN LOGIC
# =================================================
if uploaded_file:
    
    df, detected_encoding = load_csv_universal(uploaded_file)
    st.caption(f"Detected file encoding: {detected_encoding}")
    total_rows = len(df)
    
    st.markdown("### Data Preview (Top 5 Sample Rows)")
    st.caption("Showing first 5 rows only")
    df.index = range(1, len(df) + 1)
    st.dataframe(df.head(5), width="stretch")

    missing_pct = df.isnull().mean() * 100
    avg_missing = missing_pct.mean()
    
    #=========================================  
    # Total rows involved in duplication (including first occurrence)
    duplicate_mask = df.duplicated(keep='first')
    dup_rows = duplicate_mask.sum()
    
    total_rows = total_rows - dup_rows
    
    #=========================================

    st.markdown("### Quality Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completeness", f"{100 - int(avg_missing)}%")
    
    
    if dup_rows > 0:
        c2.metric(
            label="Duplicate Rows",
            value=dup_rows,
            delta="Duplicates Found",
            delta_color="inverse"   # red
        )
    else:
        c2.metric("Duplicate Rows", dup_rows)
    
    c3.metric("Total Columns", len(df.columns))
    c4.metric("Total Rows (Unique)", total_rows)

    # ---------------- DATE RANGE ----------------
    st.markdown("### Date Range Profiler (Format: YYYY-MM-DD)")
    date_cols = detect_date_columns(df)

    date_profile = None
    if date_cols:
        selected_col = st.selectbox("Select date column", date_cols)
        date_profile = compute_date_range(df, selected_col)

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Min Date (YYYY-MM-DD)", str(date_profile["min_date"]))
        d2.metric("Max Date (YYYY-MM-DD)", str(date_profile["max_date"]))
        d3.metric("Date Span (days)", date_profile["span_days"])
        
        
        if date_profile['invalid_pct'] > 0:
            d4.metric(
                label="Invalid Dates %",
                value=f"{date_profile['invalid_pct']}%",
                delta="Invalid Dates Found",
                delta_color="inverse"   # red
            )
        else:
            d4.metric("Invalid Dates %", f"{date_profile['invalid_pct']}%")
        
    else:
        st.info("No reliable date columns detected.")

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Completeness",
        "Schema & Types",
        "Uniqueness",
        "Naming Standards"
    ])

    with tab1:
        completeness_df = pd.DataFrame({
            "Column": missing_pct.index,
            "Missing %": missing_pct.values.round(2)
        })
        completeness_df.index = range(1, len(completeness_df) + 1)
        st.dataframe(completeness_df, width="stretch")

    with tab2:
        schema_df = pd.DataFrame({
            "Column": df.columns,
            "Detected Type": [
                (
                    "empty (no data)"
                    if df[c].isna().all()
                    else (
                        validate_date_column(df[c])
                        if is_date_like_column(c)
                        else infer_schema_type(c, d)
                    )
                )
                for c, d in zip(df.columns, df.dtypes)
            ]
        })
        empty_columns = schema_df[
            schema_df["Detected Type"] == "empty (no data)"
        ]["Column"].tolist()
        schema_df.index = range(1, len(schema_df) + 1)
        st.dataframe(schema_df, width="stretch")

    with tab3:
        st.write(f"Duplicate rows detected: {dup_rows}")

    with tab4:
        naming_df, violating_columns, missing_audit = validate_column_naming(df)
        naming_df.index = range(1, len(naming_df) + 1)
        st.dataframe(naming_df, width="stretch")
        
        if missing_audit:
            st.warning(
                "Missing mandatory audit columns: "
                + ", ".join(sorted(missing_audit))
            )

    # ---------------- RECOMMENDATIONS ----------------
    st.markdown("### Recommendations")
    recommendations = []

    if avg_missing > 20:
        recommendations.append("High missing-value columns detected.")
        
    if dup_rows > 0:
        recommendations.append(f"{dup_rows} duplicate records detected.")
        
    if date_profile is not None and date_profile['invalid_date_count'] > 0:
        recommendations.append(f"{date_profile['invalid_date_count']} records with invalid '{date_profile['column']}' detected.")
        
    if violating_columns:
        recommendations.append(
            "Column naming standards violated for: "
            + ", ".join(sorted(violating_columns)) 
        )
        
    if missing_audit:
        recommendations.append(
            "Mandatory audit columns missing: "
            + ", ".join(sorted(missing_audit))
            + ". Required for governance and traceability."
        )
        
    if empty_columns:
        recommendations.append(
            "The following columns contain no populated values: "
            f"{', '.join(empty_columns)}. This typically indicates an upstream data issue, "
            "a deprecated field, or an unused attribute. "
        )


    for r in recommendations:
        st.warning(r)

       
    summary = {
        "Completeness": f"{100 - int(avg_missing)}%",
        "Duplicate Rows": dup_rows,
        "Total Columns": len(df.columns),
        "Total Rows (Unique)": total_rows
    }

    # pdf = generate_pdf(
        # summary=summary,
        # completeness_df=completeness_df,
        # schema_df=schema_df,
        # uniqueness_info={
            # "duplicate_rows": dup_rows
            # "uniqueness_pct": round(100 - dup_pct, 2)
        # },
        # naming_df=naming_df,
        # recommendations=recommendations,
        # date_profile=date_profile
    # )
    
    pdf = generate_pdf(
        summary=summary,
        completeness_df=add_sr_no(completeness_df),
        schema_df=add_sr_no(schema_df),
        uniqueness_info={
            "duplicate_rows": dup_rows
        },
        naming_df=add_sr_no(naming_df),
        recommendations=recommendations,
        date_profile=date_profile
    )


    st.download_button(
        "📄 Download Summary (PDF)",
        data=pdf,
        file_name="data_auality_gate_report.pdf",
        mime="application/pdf"
    )

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#6b7280; font-size:12px;">
        Built by a Data Engineer focused on data quality and analytics reliability.
        <br/>
        <a href="https://www.linkedin.com/in/mitul-luhar" target="_blank"
           style="text-decoration:none; color:#2563eb;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"
                 width="14"
                 style="vertical-align:middle; margin-right:6px;" />
            linkedin.com/in/mitul-luhar
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


