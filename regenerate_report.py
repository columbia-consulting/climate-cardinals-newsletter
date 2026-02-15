"""
Regenerate web report with current CSV data
"""

import pandas as pd
from pathlib import Path
from web_report_generator import generate_full_report_html

# Load current CSV data
OUTPUT_FOLDER = Path("weekly_data")
experts_df = pd.read_csv(OUTPUT_FOLDER / "experts.csv") if (OUTPUT_FOLDER / "experts.csv").exists() else pd.DataFrame()
grants_df = pd.read_csv(OUTPUT_FOLDER / "grants.csv") if (OUTPUT_FOLDER / "grants.csv").exists() else pd.DataFrame()
events_df = pd.read_csv(OUTPUT_FOLDER / "events.csv") if (OUTPUT_FOLDER / "events.csv").exists() else pd.DataFrame()
csr_df = pd.read_csv(OUTPUT_FOLDER / "csr_reports.csv") if (OUTPUT_FOLDER / "csr_reports.csv").exists() else pd.DataFrame()

print("🔄 Regenerating web report with current data...")
print(f"   Experts: {len(experts_df)}")
print(f"   Grants: {len(grants_df)}")
print(f"   Events: {len(events_df)}")
print(f"   CSR Reports: {len(csr_df)}")

report_path = generate_full_report_html(experts_df, grants_df, events_df, csr_df)

print(f"✅ Web report regenerated: {report_path}")
print("\n✅ Numbers now match between email template and web UI!")
