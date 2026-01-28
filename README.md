# AI Company Monitor

Monitor subscription economics signals for leading AI companies (Anthropic and OpenAI). Repository holds planning documents and spreadsheets outlining data sources, tracking cadence, and unit economics assumptions.

## Contents
- i_sub_monitor_prd.md — product requirements document outlining goals, signals, and data sources.
- i_subscription_background.md — background context and research notes.
- subscriber_mix_model.xlsx — spreadsheet modeling subscriber mix and usage.
- subscription_economics.xlsx — spreadsheet modeling unit economics and margins.

## Getting Started
1. Install Git and create a new GitHub repository named AI-Company-Monitor (or your preferred name).
2. In this folder run:
   `sh
   git remote add origin https://github.com/<your-user>/AI-Company-Monitor.git
   git branch -M main
   git push -u origin main
   `
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

Configuration lives in `config/sources.yaml` and `config/keywords.yaml`. Credentials for Reddit/GitHub collectors (not yet implemented) are expected via environment variables.
