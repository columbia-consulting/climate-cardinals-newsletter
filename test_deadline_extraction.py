"""Test enhanced deadline extraction"""
from automated_newsletter import run_section, GRANT_KEYWORDS, write_csv
import pandas as pd

print("🔍 Testing enhanced deadline extraction...")
print("Removing old grants.csv...")
import os
if os.path.exists("weekly_data/grants.csv"):
    os.remove("weekly_data/grants.csv")

print("\n🌐 Scraping grants with enhanced date detection...")
grants = run_section(GRANT_KEYWORDS, future=True)
write_csv('grants.csv', grants)

# Analyze results
df = pd.read_csv('weekly_data/grants.csv')
print(f"\n✅ Scraped {len(df)} grants")

deadlines_found = df[df['Deadline'] != '—']
print(f"✅ {len(deadlines_found)} grants have deadline information")

if len(deadlines_found) > 0:
    print("\n📅 Grants with deadlines:")
    for idx, row in deadlines_found.iterrows():
        title = row['Title'][:55] + '...' if len(row['Title']) > 55 else row['Title']
        print(f"  • {title}")
        print(f"    → {row['Deadline']}")
else:
    print("\n⚠️  No deadlines found in search snippets")
    print("Note: Deadline information may not be available in search results")
    print("Users should visit grant pages for complete details")
