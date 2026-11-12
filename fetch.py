"""
Monthly fetch for Simon's macro weather report (GitHub Actions edition).

Replaces the Mac's fetch_only.py + launchd. Runs on GitHub's servers on a
schedule (see .github/workflows/fetch.yml) and commits:
  latest.txt              - same format the old latest_data.txt used
  data/YYYY-MM-DD.txt     - dated copy (permanent archive)
  data/YYYY-MM-DD.json    - same data, machine-readable

The FRED key comes from the FRED_API_KEY repo secret.
Exits with an error (so GitHub emails you) if too many indicators fail.

Run by hand: python fetch.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fetch_data import fetch_all

ROOT = Path(__file__).parent
MAX_ERRORS = 5  # more than this many live indicators failing = treat the run as failed


def format_data(results):
    """Identical to report.py's format_data so the analysis sees the same layout."""
    lines = []
    current_section = None
    for r in results:
        if r["section"] != current_section:
            current_section = r["section"]
            lines.append(f"\n## {current_section}")
        if r["source"] == "disabled":
            lines.append(f"- {r['name']}: NO DATA ({r['note']})")
        elif r["error"]:
            lines.append(f"- {r['name']}: ERROR ({r['error']})")
        else:
            lines.append(
                f"- {r['name']}: now={r['value']:,.4f} "
                f"(as of {r['date']}) | "
                f"1mo ago={r['value_1mo_ago']:,.4f} | "
                f"3mo ago={r['value_3mo_ago']:,.4f} | "
                f"6mo ago={r['value_6mo_ago']:,.4f} | "
                f"6mo range: {r['min_6mo']:,.4f} to {r['max_6mo']:,.4f}"
            )
    return "\n".join(lines)


def main():
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== Macro data fetch (GitHub edition) -- {stamp} UTC ===", flush=True)

    results = fetch_all()
    text = f"Fetched: {stamp}\n{format_data(results)}\n"

    (ROOT / "data").mkdir(exist_ok=True)
    day = now.strftime("%Y-%m-%d")
    (ROOT / "latest.txt").write_text(text)
    (ROOT / "data" / f"{day}.txt").write_text(text)
    (ROOT / "data" / f"{day}.json").write_text(
        json.dumps({"fetched_utc": stamp, "results": results}, indent=2)
    )

    errors = [r["name"] for r in results if r["error"] and r["source"] != "disabled"]
    print(text)
    print(f"{len(errors)} errors: {', '.join(errors) or 'none'}")
    if len(errors) > MAX_ERRORS:
        print(f"FAILED: more than {MAX_ERRORS} indicators errored", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
