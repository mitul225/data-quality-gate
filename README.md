# Data Quality Gate
<i>Validate data quality before it reaches analytics</i></br></br>

Data Quality Gate is a lightweight, audit-style data quality assessment tool built for working data engineers, analytics engineers, and technical teams who regularly deal with CSV datasets from multiple sources.

The goal is simple:
👉 Identify data risks early, clearly, and with evidence — before dashboards and decisions are impacted.

## Why Data Quality Gate Exists

In practice, many analytics issues are not caused by SQL errors or broken dashboards, but by datasets that were never properly validated before use.

CSV files often arrive from:

* Business teams
* Vendors
* Exports from tools and legacy systems

They may look clean, but frequently contain:

* Duplicate records
* Invalid or placeholder dates
* Partially or fully empty columns
* Misleading schema inference
* Inconsistent naming patterns

These issues don’t always cause failures — they cause <b>quietly wrong results.</b>

Data Quality Gate introduces a <b>pre-analytics checkpoint</b> to surface these risks early.

## What the Tool Does

Data Quality Gate performs a focused, practical set of checks designed around real data engineering workflows.

### Core Quality Indicators
* Completeness – missing value analysis per column.
* Uniqueness – detection of duplicate records with row-level evidence.
* Row & column sanity – dataset shape validation.

### Analytics Readiness Checks
* Schema & data type validation
  * Flags fully empty columns
  * Validates date-like columns against actual data
* Date coverage & validity
  * Min / max date detection
  * Invalid date percentage and row samples
* Column naming & governance review
  * Identifies naming standard violations
  * Highlights maintainability and governance risks

### Evidence-First Reporting

* Sample rows for duplicates and invalid dates.
* Audit-style PDF reports with observations and recommendations.
* Optional executive summary for leadership review.

## Reporting

The tool generates:
* A <b>professional PDF report</b> suitable for sharing with:
  * Senior Management
  * Tech leads
  * Analytics managers
  * Head of Data
* Clear observations and <b>actionable recommendations/<b>

## Privacy & Data Handling

Data Quality Gate is designed with privacy in mind.

* Uploaded CSV files are processed in-memory only
* No files are stored, logged, or shared
* No data is written to disk
* No third-party services receive user data
* Files are automatically discarded when the session ends

This makes the tool safe for exploratory use with sensitive datasets.

📌 Note: Data is uploaded to the app server for processing (this is required for any web app), but it is not persisted beyond the active session.

## Getting Started (Local)

<b>Requirements</b>

* Python 3.9+
* See requirements.txt for dependencies

Run locally
  * pip install -r requirements.txt
  * streamlit run App.py

## Who This Is For

If you’ve ever received a dataset and wondered “Can I trust this?”, this tool is for you.

Data Quality Gate is helpful for:
* Data engineers checking new or external datasets
* Analysts and analytics engineers preparing data for BI tools
* Tech leads reviewing data quality before sign-off
* Product or business teams who depend on accurate numbers
* Anyone tired of debugging data issues after reports are already live

## Feedback & Contributions

The goal of Data Quality Gate is not perfection — it’s early clarity. 

* Upload a CSV. 
* Review the risks. 
* Fix problems before analytics begins. 

I’m sharing this publicly to learn from real-world use cases, exchange ideas with the data community, and evolve this into a more reliable data-quality checkpoint over time.

Try It, Share Feedback, Improve It. 


## 👤 Author

Built by a Data Engineer focused on data quality and analytics reliability.

🔗 LinkedIn: https://www.linkedin.com/in/mitul-luhar

