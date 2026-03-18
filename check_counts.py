#!/usr/bin/env python3
"""
Validate consistency between CSV data, latest web report, email output, and index links.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from email_template_condensed import generate_condensed_email_html

OUTPUT_FOLDER = Path("weekly_data")
REPORT_GLOB = "climate_cardinals_report_*.html"


def load_csv_counts() -> dict[str, int]:
    experts_df = pd.read_csv(OUTPUT_FOLDER / "experts.csv") if (OUTPUT_FOLDER / "experts.csv").exists() else pd.DataFrame()
    grants_df = pd.read_csv(OUTPUT_FOLDER / "grants.csv") if (OUTPUT_FOLDER / "grants.csv").exists() else pd.DataFrame()
    events_df = pd.read_csv(OUTPUT_FOLDER / "events.csv") if (OUTPUT_FOLDER / "events.csv").exists() else pd.DataFrame()
    csr_df = pd.read_csv(OUTPUT_FOLDER / "csr_reports.csv") if (OUTPUT_FOLDER / "csr_reports.csv").exists() else pd.DataFrame()

    return {
        "experts": len(experts_df),
        "grants": len(grants_df),
        "events": len(events_df),
        "csr": len(csr_df),
    }, experts_df, grants_df, events_df, csr_df


def find_latest_report_file() -> Path | None:
    reports = sorted(OUTPUT_FOLDER.glob(REPORT_GLOB), key=lambda p: p.name)
    return reports[-1] if reports else None


def parse_report_counts(report_path: Path) -> dict[str, int]:
    soup = BeautifulSoup(report_path.read_text(encoding="utf-8"), "html.parser")
    stat_nodes = soup.select(".stats-grid .stat-number")
    if len(stat_nodes) < 4:
        raise ValueError(f"Could not find 4 stat numbers in {report_path}")

    values = [int(node.get_text(strip=True)) for node in stat_nodes[:4]]
    return {
        "experts": values[0],
        "grants": values[1],
        "events": values[2],
        "csr": values[3],
    }


def parse_email_counts(email_html: str) -> dict[str, int]:
    patterns = {
        "experts": r">\s*(\d+)\s*</div>\s*<div[^>]*>\s*EXPERTS\s*</div>",
        "grants": r">\s*(\d+)\s*</div>\s*<div[^>]*>\s*GRANTS\s*</div>",
        "events": r">\s*(\d+)\s*</div>\s*<div[^>]*>\s*EVENTS\s*</div>",
        "csr": r">\s*(\d+)\s*</div>\s*<div[^>]*>\s*REPORTS\s*</div>",
    }
    out = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, email_html, flags=re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not parse {key} count from rendered email HTML")
        out[key] = int(match.group(1))
    return out


def parse_index_latest_link(index_path: Path) -> str | None:
    soup = BeautifulSoup(index_path.read_text(encoding="utf-8"), "html.parser")
    latest_btn = soup.find("a", class_="btn")
    if latest_btn:
        return latest_btn.get("href")
    return None


def normalize_for_template(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty and "Organization" in df.columns:
        return df.rename(columns={"Organization": "Domain"})
    return df


def main() -> int:
    print("=" * 80)
    print("CONSISTENCY CHECK")
    print("=" * 80)

    csv_counts, experts_df, grants_df, events_df, csr_df = load_csv_counts()
    print("\nCSV counts (source of truth):")
    print(f"  Experts: {csv_counts['experts']}")
    print(f"  Grants: {csv_counts['grants']}")
    print(f"  Events: {csv_counts['events']}")
    print(f"  CSR Reports: {csv_counts['csr']}")

    latest_report = find_latest_report_file()
    if not latest_report:
        print("\nFAIL: No report files found in weekly_data/")
        return 1

    report_counts = parse_report_counts(latest_report)
    print(f"\nLatest report file: {latest_report.name}")
    print(f"  Experts: {report_counts['experts']}")
    print(f"  Grants: {report_counts['grants']}")
    print(f"  Events: {report_counts['events']}")
    print(f"  CSR Reports: {report_counts['csr']}")

    email_html = generate_condensed_email_html(
        experts_df,
        normalize_for_template(grants_df),
        normalize_for_template(events_df),
        normalize_for_template(csr_df),
        base_url="",
        report_filename=latest_report.name,
    )
    email_counts = parse_email_counts(email_html)
    print("\nRendered email counts:")
    print(f"  Experts: {email_counts['experts']}")
    print(f"  Grants: {email_counts['grants']}")
    print(f"  Events: {email_counts['events']}")
    print(f"  CSR Reports: {email_counts['csr']}")

    index_path = OUTPUT_FOLDER / "index.html"
    index_latest = parse_index_latest_link(index_path) if index_path.exists() else None
    print(f"\nindex.html latest link: {index_latest or 'MISSING'}")

    ok = True
    if report_counts != csv_counts:
        ok = False
        print("\nFAIL: Latest report counts do not match CSV counts.")

    if email_counts != csv_counts:
        ok = False
        print("FAIL: Email counts do not match CSV counts.")

    if index_latest != latest_report.name:
        ok = False
        print("FAIL: index.html latest link does not point to latest report file.")

    if ok:
        print("\nPASS: CSV, report, email, and index latest link are consistent.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
