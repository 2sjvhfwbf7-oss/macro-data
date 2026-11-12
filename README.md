# macro-data

Monthly indicator fetch for the "Financial" Claude Project's macro weather report.

- **Schedule:** GitHub Actions, 1st of each month ~6am Pacific (`.github/workflows/fetch.yml`).
- **Output:** `latest.txt` (newest fetch) and `data/YYYY-MM-DD.{txt,json}` (archive).
- **Secret:** `FRED_API_KEY` under Settings → Secrets and variables → Actions.
- **Manual run:** Actions tab → "Monthly macro fetch" → Run workflow.
- **Indicators:** edit `tickers.py`. Thresholds live in the Project (`claude/framework.md`), not here.
- **Failure:** if >5 live indicators error, the run fails and GitHub emails you; partial data is still committed.

The Claude scheduled task (3rd of each month) reads `latest.txt` from here and writes the report into the Project.
