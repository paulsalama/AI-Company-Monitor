# AI Company Monitor

Monitor subscription economics signals for leading AI companies (Anthropic and OpenAI). Repository holds planning documents and spreadsheets outlining data sources, tracking cadence, and unit economics assumptions.

## Contents
- `ai_sub_monitor_prd.md` — product requirements document outlining goals, signals, and data sources.
- `ai_subscription_background.md` — background context and research notes.
- `subscriber_mix_model.xlsx` — spreadsheet modeling subscriber mix and usage.
- `subscription_economics.xlsx` — spreadsheet modeling unit economics and margins.

## Getting Started
1. Install Git and create a new GitHub repository named `AI-Company-Monitor` (or your preferred name).
2. In this folder run:
   ```sh
   git remote add origin https://github.com/<your-user>/AI-Company-Monitor.git
   git branch -M main
   git push -u origin main
   ```
3. If you prefer SSH, swap the remote URL accordingly.

## Next Steps
- Add scripts to pull pricing/rate-limit snapshots from Anthropic/OpenAI.
- Add Reddit/GitHub issue ingestion (e.g., via PRAW and GitHub REST API).
- Automate weekly/monthly reporting from the collected data.

## Local Setup (Python)
1. Ensure Python 3.11+ is installed.
2. Install dependencies in editable mode:
   ```sh
   pip install -e ".[dev]"
   ```
3. Initialize folders and database (also seeds companies from `config/sources.yaml`):
   ```sh
   ai-sub-monitor init
   ```
4. Run a collector (pricing/docs already make HTTP fetches):
   ```sh
   ai-sub-monitor collect --source pricing
   ```
5. Generate a skeleton weekly report:
   ```sh
   ai-sub-monitor report --latest
   ```
6. Update spreadsheet copies with latest pricing (writes sheet `LatestPricing` in `data/models/*.xlsx`):
   ```sh
   ai-sub-monitor update-models
   ```

Configuration lives in `config/sources.yaml` and `config/keywords.yaml`.

### Credentials for collectors
- Reddit: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` (optional).
- GitHub: `GITHUB_TOKEN` (with `repo` read scope).

### Collector notes
- Pricing/docs collectors fetch HTML, archive to `data/snapshots/`, and log snapshots to the DB.
- Reddit collector scans configured subreddits (last 24h, keyword-filtered) and stores `CommunitySignal` rows with sentiment.
- GitHub collector scans configured repos' issues updated in the last 24h (skips PRs), keyword-filters, and stores `CommunitySignal` rows.
- Pricing/docs collectors skip writes when content hashes match the latest snapshot; when changed they flag `is_change=True` for reporting.

### How the original four files fit
- `ai_sub_monitor_prd.md` drives the feature list; collectors/reporting map to F1–F7.
- `ai_subscription_background.md` holds the baseline economics and hypotheses that inform what we monitor; keep it updated as facts change.
- `subscriber_mix_model.xlsx` and `subscription_economics.xlsx` are treated as canonical models. The `ai-sub-monitor init` command copies them into `data/models/` for safekeeping; future scripts (F7) will write updates back to those copies.
