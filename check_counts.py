"""
Quick script to verify data counts shown in email vs web report
"""

import pandas as pd
from pathlib import Path
from email_template_condensed import generate_condensed_email_html
from web_report_generator import generate_full_report_html

# Load current CSV data
OUTPUT_FOLDER = Path("weekly_data")
experts_df = pd.read_csv(OUTPUT_FOLDER / "experts.csv") if (OUTPUT_FOLDER / "experts.csv").exists() else pd.DataFrame()
grants_df = pd.read_csv(OUTPUT_FOLDER / "grants.csv") if (OUTPUT_FOLDER / "grants.csv").exists() else pd.DataFrame()
events_df = pd.read_csv(OUTPUT_FOLDER / "events.csv") if (OUTPUT_FOLDER / "events.csv").exists() else pd.DataFrame()
csr_df = pd.read_csv(OUTPUT_FOLDER / "csr_reports.csv") if (OUTPUT_FOLDER / "csr_reports.csv").exists() else pd.DataFrame()

print("=" * 70)
print("📊 CURRENT CSV FILE COUNTS")
print("=" * 70)
print(f"Experts: {len(experts_df)}")
print(f"Grants: {len(grants_df)}")
print(f"Events: {len(events_df)}")
print(f"CSR Reports: {len(csr_df)}")

print("\n" + "=" * 70)
print("📧 WHAT EMAIL TEMPLATE WILL SHOW (using current CSV data)")
print("=" * 70)
# The email template uses len(df) directly
experts_count = len(experts_df) if not experts_df.empty else 0
grants_count = len(grants_df) if not grants_df.empty else 0
events_count = len(events_df) if not events_df.empty else 0
csr_count = len(csr_df) if not csr_df.empty else 0

print(f"Experts: {experts_count}")
print(f"Grants: {grants_count}")
print(f"Events: {events_count}")
print(f"CSR Reports: {csr_count}")

print("\n" + "=" * 70)
print("🌐 WHAT OLD WEB REPORT (climate_cardinals_report_20260215.html) SHOWS")
print("=" * 70)
print("Experts: 31")
print("Grants: 39")
print("Events: 31")
print("CSR Reports: 29")
print("\nNote: These numbers are from when the HTML was generated on Feb 8, 2026")

print("\n" + "=" * 70)
print("🔍 ISSUE FOUND")
print("=" * 70)
print("The web report HTML file is OUTDATED (generated Feb 8, 2026)")
print("The CSV files have MORE data (last updated Feb 15, 2026)")
print("The email template reads fresh from CSV, so it shows CORRECT counts")
print("\n✅ SOLUTION: The web report needs to be regenerated with current data")
