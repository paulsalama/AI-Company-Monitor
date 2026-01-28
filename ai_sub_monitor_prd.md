# Product Requirements Document: AI Subscription Economics Monitor

## Overview

### Problem Statement
The leading AI companies (Anthropic, OpenAI) are operating consumer subscription businesses that appear structurally unprofitable due to adverse selection — power users who are motivated to pay are precisely the users who cost the most to serve. Sam Altman has confirmed that ChatGPT Pro ($200/month) is unprofitable despite the high price point.

We want to monitor leading indicators that would signal:
1. Worsening unit economics (tightening rate limits, price increases)
2. Strategic pivots (enterprise vs consumer emphasis)
3. Market correction risk (funding pressure, growth stalling)

### Goals
1. **Track rate limit changes** — The primary lever companies use to control costs
2. **Monitor pricing and tier changes** — Signals of margin pressure or monetization attempts
3. **Aggregate community sentiment** — Early warning from power users hitting limits
4. **Compile financial signals** — Revenue, funding, profitability timeline updates
5. **Generate periodic reports** — Weekly/monthly summaries of key changes

### Non-Goals (v1)
- Real-time alerting (batch processing is fine)
- Predictive modeling (descriptive/diagnostic first)
- Coverage of all AI companies (focus on Anthropic + OpenAI)
- Mobile app or web dashboard (CLI + markdown reports)

---

## Data Sources

### Tier 1: High Signal (Monitor Daily)

#### 1.1 Reddit
- **Subreddits:** r/ClaudeAI, r/ChatGPT, r/ClaudeCode, r/LocalLLaMA
- **What to capture:**
  - Posts mentioning "rate limit", "usage limit", "throttle", "cap"
  - Posts mentioning "price", "subscription", "Pro", "Max", "Plus"
  - Post score, comment count, sentiment
- **API:** Reddit API (or PRAW library) — requires OAuth app registration
- **Rate limits:** 100 requests/minute with OAuth

#### 1.2 GitHub Issues
- **Repositories:** 
  - `anthropics/claude-code`
  - `openai/openai-python` (for API issues)
- **What to capture:**
  - Issues mentioning rate limits, usage, billing
  - Issue volume over time
  - Labels, open/closed status
- **API:** GitHub REST API — 5000 requests/hour authenticated

#### 1.3 Official Pricing Pages
- **URLs:**
  - https://www.anthropic.com/pricing
  - https://openai.com/chatgpt/pricing
  - https://www.anthropic.com/api (API pricing)
  - https://openai.com/api/pricing
- **What to capture:**
  - Full page content (for diff detection)
  - Specific price points, tier names, feature lists
- **Method:** HTTP fetch + diff against previous snapshot
- **Storage:** Archive each version with timestamp

#### 1.4 Official Documentation (Rate Limits)
- **URLs:**
  - https://docs.anthropic.com/en/api/rate-limits
  - https://platform.openai.com/docs/guides/rate-limits
  - https://support.anthropic.com (help articles on usage)
- **What to capture:**
  - Rate limit specifications
  - Any changes to documented limits
- **Method:** HTTP fetch + diff detection

### Tier 2: Medium Signal (Monitor Weekly)

#### 2.1 News/Financial Sources
- **Sources:**
  - The Information (requires subscription — manual or RSS)
  - TechCrunch (RSS feed available)
  - WSJ Tech section
  - Ars Technica / The Register
- **What to capture:**
  - Articles mentioning Anthropic/OpenAI + revenue/funding/valuation
  - Key financial figures mentioned
- **Method:** RSS feeds + keyword filtering, or web search API

#### 2.2 Twitter/X
- **Accounts to monitor:**
  - @AnthropicAI, @OpenAI, @sama, @DarioAmodei
  - Key AI researchers/commentators
- **What to capture:**
  - Announcements about pricing, features, limits
  - Community complaints (search: "Claude rate limit", "ChatGPT limit")
- **API:** X API v2 (limited free tier, or paid)
- **Alternative:** Nitter instances or manual spot checks

#### 2.3 App Store Data
- **Sources:**
  - Sensor Tower (paid)
  - data.ai (paid)
  - Manual checks of App Store / Play Store ratings
- **What to capture:**
  - App ratings over time
  - Review sentiment (especially 1-star mentioning limits/price)
  - Download estimates if available
- **Method:** For v1, manual monthly checks; automate later if valuable

### Tier 3: Lower Frequency (Monitor Monthly)

#### 3.1 Funding/Valuation Data
- **Sources:**
  - Crunchbase
  - PitchBook (paid)
  - SEC filings (when applicable)
  - Press releases
- **What to capture:**
  - Funding rounds, amounts, valuations
  - Investor names
  - Any debt financing

#### 3.2 Technical Analysis Sources
- **Sources:**
  - SemiAnalysis newsletter
  - Epoch AI reports
  - Academic papers on LLM costs
- **What to capture:**
  - Cost per token estimates
  - Infrastructure cost analyses
  - Energy consumption studies
- **Method:** Manual review + structured note-taking

---

## Data Model

### Core Entities

```
Company
├── id: string (anthropic | openai)
├── name: string
└── metadata: JSON

PricingSnapshot
├── id: uuid
├── company_id: string
├── captured_at: timestamp
├── tier_name: string (free | pro | max_5x | max_20x | plus | pro_200)
├── price_monthly: decimal
├── price_annual: decimal (if applicable)
├── features: JSON
├── rate_limits_stated: JSON
└── raw_html: text (for diff)

RateLimitChange
├── id: uuid
├── company_id: string
├── detected_at: timestamp
├── source: string (official_docs | community_report | pricing_page)
├── tier_affected: string
├── previous_limit: JSON
├── new_limit: JSON
├── change_description: text
└── evidence_urls: JSON array

CommunitySignal
├── id: uuid
├── company_id: string
├── source: string (reddit | github | twitter | discord)
├── source_id: string (post ID, issue number, etc.)
├── captured_at: timestamp
├── content: text
├── url: string
├── sentiment: float (-1 to 1)
├── keywords_matched: JSON array
├── score: int (upvotes, reactions)
└── comment_count: int

FinancialEvent
├── id: uuid
├── company_id: string
├── event_date: date
├── event_type: string (funding | revenue_report | valuation | acquisition)
├── amount: decimal (if applicable)
├── valuation: decimal (if applicable)
├── source_url: string
├── notes: text
└── raw_data: JSON

WeeklyReport
├── id: uuid
├── week_start: date
├── week_end: date
├── generated_at: timestamp
├── summary: text (markdown)
├── rate_limit_changes: int
├── pricing_changes: int
├── community_signal_volume: JSON (by source)
├── sentiment_trend: float
└── key_events: JSON array
```

### Storage

For v1, use SQLite database stored locally:
- Simple, no server required
- Easy to query and backup
- Can migrate to Postgres later if needed

File structure:
```
ai-sub-monitor/
├── data/
│   ├── monitor.db (SQLite)
│   ├── snapshots/ (raw HTML archives)
│   └── reports/ (generated markdown reports)
├── src/
│   ├── collectors/
│   ├── analyzers/
│   ├── reporters/
│   └── utils/
├── config/
│   └── sources.yaml
└── outputs/
    └── reports/
```

---

## Features

### F1: Pricing Page Monitor
**Description:** Daily fetch of official pricing pages, detect and log changes.

**Inputs:**
- List of URLs to monitor (from config)

**Process:**
1. Fetch each URL
2. Extract structured pricing data (tier, price, features)
3. Compare to previous snapshot
4. If changed, create PricingSnapshot record and flag for report

**Outputs:**
- New PricingSnapshot records
- Change detection flag

**Acceptance Criteria:**
- [ ] Detects any text change on pricing pages
- [ ] Extracts structured price/tier data for Anthropic and OpenAI
- [ ] Stores historical snapshots for comparison

### F2: Reddit Sentiment Collector
**Description:** Daily collection of relevant posts from target subreddits.

**Inputs:**
- Subreddit list
- Keyword list (rate limit, usage, price, subscription, throttle, cap, etc.)
- Lookback period (default: 24 hours)

**Process:**
1. Query Reddit API for recent posts in each subreddit
2. Filter by keyword matches in title or selftext
3. Calculate basic sentiment score
4. Store as CommunitySignal records

**Outputs:**
- CommunitySignal records
- Daily signal volume counts

**Acceptance Criteria:**
- [ ] Captures posts from r/ClaudeAI, r/ChatGPT, r/ClaudeCode
- [ ] Filters to relevant keywords
- [ ] Stores post content, score, URL, timestamp
- [ ] Basic sentiment scoring (positive/negative/neutral)

### F3: GitHub Issue Tracker
**Description:** Monitor issue activity on key repositories.

**Inputs:**
- Repository list
- Keyword/label filters

**Process:**
1. Query GitHub API for recent issues
2. Filter by keywords in title/body
3. Track issue volume over time
4. Store as CommunitySignal records

**Outputs:**
- CommunitySignal records
- Issue volume trends

**Acceptance Criteria:**
- [ ] Monitors anthropics/claude-code repository
- [ ] Captures issues mentioning rate limits, usage, billing
- [ ] Tracks open/closed status

### F4: Documentation Diff Detector
**Description:** Weekly check of official documentation for rate limit changes.

**Inputs:**
- Documentation URLs

**Process:**
1. Fetch documentation pages
2. Extract rate limit specifications
3. Compare to previous version
4. If changed, create RateLimitChange record

**Outputs:**
- RateLimitChange records
- Diff output for manual review

**Acceptance Criteria:**
- [ ] Detects changes to rate limit documentation
- [ ] Captures before/after values
- [ ] Generates human-readable diff

### F5: Financial Event Logger
**Description:** Manual or semi-automated logging of financial events.

**Inputs:**
- News article URL
- Event details (date, type, amounts)

**Process:**
1. Accept manual input or parse from article
2. Validate and store as FinancialEvent
3. Update company financial summary

**Outputs:**
- FinancialEvent records

**Acceptance Criteria:**
- [ ] CLI interface for adding financial events
- [ ] Stores funding rounds, revenue reports, valuations
- [ ] Links to source URLs

### F6: Weekly Report Generator
**Description:** Generate a markdown summary report of the week's signals.

**Inputs:**
- Date range (default: last 7 days)

**Process:**
1. Query all data sources for the period
2. Aggregate metrics (signal volume, sentiment trends)
3. Highlight key changes (pricing, rate limits)
4. Generate markdown report

**Outputs:**
- WeeklyReport record
- Markdown file in outputs/reports/

**Report Sections:**
1. Executive Summary (1-2 paragraphs)
2. Rate Limit Changes (if any)
3. Pricing Changes (if any)
4. Community Sentiment
   - Volume by source
   - Sentiment trend
   - Top posts/issues
5. Financial Updates
6. Key Quotes/Excerpts
7. Data Tables (from spreadsheet models)

**Acceptance Criteria:**
- [ ] Generates readable markdown report
- [ ] Includes all data sources
- [ ] Highlights significant changes
- [ ] Can be run via CLI: `python -m monitor report --week 2026-01-20`

### F7: Spreadsheet Integration
**Description:** Update the subscription economics models with new data.

**Inputs:**
- subscription_economics.xlsx
- subscriber_mix_model.xlsx
- New pricing/financial data

**Process:**
1. Load spreadsheet templates
2. Update with latest pricing data
3. Recalculate formulas
4. Save updated versions

**Outputs:**
- Updated spreadsheet files
- Change summary

**Acceptance Criteria:**
- [ ] Can update API pricing in subscription_economics.xlsx
- [ ] Can update subscription prices if they change
- [ ] Preserves formulas and formatting

---

## Technical Approach

### Language & Framework
- **Python 3.11+** — Best library support for APIs and data processing
- **SQLite** — Simple persistence, no server needed
- **Click** — CLI framework
- **HTTPX** — Async HTTP client
- **BeautifulSoup** — HTML parsing
- **PRAW** — Reddit API wrapper
- **PyGithub** — GitHub API wrapper
- **openpyxl** — Excel file manipulation
- **Jinja2** — Report templating

### Project Structure
```
ai-sub-monitor/
├── pyproject.toml
├── README.md
├── config/
│   ├── sources.yaml          # URLs, subreddits, repos to monitor
│   └── keywords.yaml         # Keyword lists for filtering
├── data/
│   ├── monitor.db            # SQLite database
│   ├── snapshots/            # Raw HTML archives (by date)
│   └── models/               # Spreadsheet templates
│       ├── subscription_economics.xlsx
│       └── subscriber_mix_model.xlsx
├── src/
│   └── ai_sub_monitor/
│       ├── __init__.py
│       ├── cli.py            # Click CLI entrypoint
│       ├── config.py         # Configuration loading
│       ├── db.py             # Database models and connection
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── pricing.py    # Pricing page collector
│       │   ├── reddit.py     # Reddit collector
│       │   ├── github.py     # GitHub issue collector
│       │   └── docs.py       # Documentation collector
│       ├── analyzers/
│       │   ├── __init__.py
│       │   ├── diff.py       # Text diff analysis
│       │   └── sentiment.py  # Basic sentiment scoring
│       ├── reporters/
│       │   ├── __init__.py
│       │   ├── weekly.py     # Weekly report generator
│       │   └── templates/
│       │       └── weekly_report.md.j2
│       └── utils/
│           ├── __init__.py
│           └── http.py       # HTTP utilities
└── tests/
    └── ...
```

### CLI Commands
```bash
# Initialize database
ai-sub-monitor init

# Run all collectors
ai-sub-monitor collect --all

# Run specific collector
ai-sub-monitor collect --source reddit
ai-sub-monitor collect --source pricing
ai-sub-monitor collect --source github
ai-sub-monitor collect --source docs

# Add financial event manually
ai-sub-monitor add-event --company anthropic --type funding --amount 2000000000 --date 2025-09-02 --source "https://..."

# Generate weekly report
ai-sub-monitor report --week 2026-01-20
ai-sub-monitor report --latest

# View recent signals
ai-sub-monitor signals --days 7 --source reddit

# Check for pricing changes
ai-sub-monitor diff --type pricing --days 30

# Update spreadsheet models
ai-sub-monitor update-models
```

### Scheduling
For v1, use cron or manual execution:
```cron
# Daily collectors (6 AM)
0 6 * * * cd /path/to/ai-sub-monitor && python -m ai_sub_monitor collect --all

# Weekly report (Monday 8 AM)
0 8 * * 1 cd /path/to/ai-sub-monitor && python -m ai_sub_monitor report --latest
```

Future: Could add a simple scheduler daemon or integrate with task runners.

---

## Configuration

### sources.yaml
```yaml
companies:
  anthropic:
    name: "Anthropic"
    pricing_urls:
      - https://www.anthropic.com/pricing
      - https://www.anthropic.com/api
    docs_urls:
      - https://docs.anthropic.com/en/api/rate-limits
      - https://support.anthropic.com/en/articles/8324991-about-claude-s-pro-plan-usage
    github_repos:
      - anthropics/claude-code
    subreddits:
      - ClaudeAI
      - ClaudeCode

  openai:
    name: "OpenAI"
    pricing_urls:
      - https://openai.com/chatgpt/pricing
      - https://openai.com/api/pricing
    docs_urls:
      - https://platform.openai.com/docs/guides/rate-limits
    github_repos:
      - openai/openai-python
    subreddits:
      - ChatGPT
      - OpenAI

general:
  subreddits:
    - LocalLLaMA  # For competitive/market context
```

### keywords.yaml
```yaml
rate_limits:
  - "rate limit"
  - "usage limit"
  - "throttle"
  - "throttled"
  - "cap"
  - "capped"
  - "quota"
  - "hit limit"
  - "reached limit"
  - "limit reached"
  - "out of messages"
  - "usage reset"

pricing:
  - "price"
  - "pricing"
  - "subscription"
  - "Pro plan"
  - "Max plan"
  - "Plus"
  - "tier"
  - "upgrade"
  - "downgrade"
  - "cancel"
  - "cancelled"
  - "refund"

sentiment_negative:
  - "unusable"
  - "frustrated"
  - "disappointed"
  - "waste of money"
  - "not worth"
  - "switching to"
  - "cancelled my"
  - "unsubscribed"

sentiment_positive:
  - "worth it"
  - "love"
  - "amazing"
  - "great value"
  - "upgraded"
  - "happy with"
```

---

## Success Metrics

### v1 Launch Criteria
1. [ ] Can collect data from Reddit, GitHub, pricing pages
2. [ ] Detects pricing page changes within 24 hours
3. [ ] Generates readable weekly report
4. [ ] Stores 30+ days of historical data
5. [ ] CLI is functional for all core commands

### Ongoing Metrics
- **Coverage:** % of rate limit changes detected vs. reported in news
- **Timeliness:** Average time between change and detection
- **Signal quality:** % of captured posts that are actually relevant
- **Report usefulness:** Subjective assessment of weekly report value

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Reddit API changes/restrictions | Medium | High | Cache aggressively, have scraping fallback |
| Rate limiting by sources | Medium | Medium | Respect rate limits, implement backoff |
| HTML structure changes break parsing | High | Medium | Use flexible selectors, alert on parse failures |
| False positives in sentiment | High | Low | Manual review in reports, tune keywords |
| Missing important signals | Medium | High | Diversify sources, manual spot checks |

---

## Future Enhancements (v2+)

1. **Discord monitoring** — Scrape or use bot for Claude Discord
2. **Twitter/X integration** — If API access is viable
3. **Automated financial data** — Integrate Crunchbase/PitchBook APIs
4. **Alerting** — Email/Slack notifications for significant changes
5. **Dashboard** — Simple web UI for data exploration
6. **ML sentiment** — Replace keyword-based with trained classifier
7. **Competitive expansion** — Add Google (Gemini), Cohere, etc.
8. **Predictive signals** — Model correction probability from indicators

---

## Appendix

### Reference Files
- `subscription_economics.xlsx` — Unit economics model by user segment
- `subscriber_mix_model.xlsx` — Profitability scenarios by subscriber mix
- `ai_subscription_monitoring.md` — Background analysis and signal framework

### Key External Sources
- Simon P. Couch blog post on Claude Code energy usage
- The Information (subscription required) — Best AI financial reporting
- Ed Zitron's "Where's Your Ed At" — Critical OpenAI financial analysis
- Sacra — Startup financial analysis

### Baseline Data Points (as of January 2026)
- Anthropic Pro: $20/month
- Anthropic Max 5x: $100/month
- Anthropic Max 20x: $200/month
- OpenAI Plus: $20/month
- OpenAI Pro: $200/month
- Anthropic break-even target: 2028
- OpenAI break-even target: 2029-2030
- ChatGPT Pro confirmed unprofitable (per Sam Altman)
