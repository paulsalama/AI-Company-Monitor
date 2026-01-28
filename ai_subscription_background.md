# AI Subscription Economics: Background Analysis

> This document provides the analytical foundation for the AI Subscription Economics Monitor. 
> It summarizes the research, hypotheses, and baseline data that inform the monitoring strategy.
> See `ai_sub_monitor_prd.md` for implementation details.

---

## Executive Summary

Consumer AI subscriptions appear structurally unprofitable due to **adverse selection**:

1. **Light users** don't need to upgrade from free tiers
2. **Power users** who upgrade cost more to serve than they pay
3. **Rate limits** are the only lever to contain losses, but cause churn
4. **Sam Altman confirmed** ChatGPT Pro ($200/month) is unprofitable

This creates a dynamic where the more successfully a company converts engaged users, the worse their unit economics become. We hypothesize that consumer AI subscriptions are being subsidized by either:
- Enterprise/API revenue (Anthropic model: 80% enterprise)
- VC funding during growth phase (OpenAI model: burning $17B/year)

A market correction becomes likely when funding tightens or growth stalls.

---

## The Adverse Selection Problem

### How It Works

Traditional subscription businesses (Netflix, Spotify, gyms) benefit from light users who pay but don't consume much. AI subscriptions have the opposite dynamic:

| User Type | Behavior | Cost to Serve | Subscription Value | Profitable? |
|-----------|----------|---------------|-------------------|-------------|
| Dormant | Rarely uses | ~$1/mo | $20 (Pro) | ✅ Very |
| Light | Casual chat | ~$5/mo | $20 (Pro) | ✅ Yes |
| Moderate | Regular use | ~$25/mo | $20 (Pro) | ⚠️ Marginal |
| Heavy | Hits limits | ~$60/mo | $20 (Pro) | ❌ No |
| Power | At limits constantly | ~$120/mo | $100 (Max 5x) | ❌ No |
| Extreme | Would use more if allowed | ~$250+/mo | $200 (Max 20x) | ❌ No |

### Why Upgrades Make It Worse

The decision to upgrade (Pro → Max) is triggered by hitting rate limits. By definition, upgraders are the most expensive users. This is classic adverse selection: the customers most eager to buy are the worst risks.

### Evidence

1. **Sam Altman confirmed** ChatGPT Pro ($200) is unprofitable "due to high usage patterns"
2. **Rate limits keep tightening** — January 2026 saw 60% reductions reported by Claude Code users
3. **Holiday capacity experiment** — Anthropic doubled limits Dec 25-31 using idle enterprise capacity, revealing consumer runs on "leftover" compute
4. **User complaints correlate with subscriber tiers** — Power users are vocal about limits

---

## Unit Economics Analysis

### API Pricing as Cost Proxy

API pricing is competitive (B2B market) and likely reflects true costs plus margin. We use it to estimate subscription profitability.

**Anthropic API Pricing (per million tokens):**
| Model | Input | Cache Read | Output |
|-------|-------|------------|--------|
| Opus 4.5 | $5.00 | $0.50 | $25.00 |
| Sonnet 4.5 | $3.00 | $0.30 | $15.00 |
| Haiku 4.5 | $1.00 | $0.10 | $5.00 |

### Real-World Usage Data

From Simon P. Couch's analysis of his Claude Code usage:
- **Median session:** ~592K tokens, ~$1.70 API cost
- **Daily workday:** ~$17.50 API equivalent
- **Monthly (22 days):** ~$385 API equivalent

This is ~20x what a Max 20x subscription costs ($200/month).

### Break-Even Analysis

| Plan | Price | Break-even Usage | % of "Simon Level" |
|------|-------|------------------|-------------------|
| Pro ($20) | $20 | $20 API-equivalent | ~5% |
| Max 5x ($100) | $100 | $100 API-equivalent | ~26% |
| Max 20x ($200) | $200 | $200 API-equivalent | ~52% |

**Implication:** Rate limits must cap users at roughly these usage levels to break even.

---

## Subscriber Mix Scenarios

The profitability of each tier depends on the mix of light vs. heavy users.

### Pro Plan ($20/month)

| Scenario | Light Users % | Weighted Profit/Sub | Gross Margin |
|----------|---------------|---------------------|--------------|
| Gym Model | 75% | +$9.85 | +49% |
| Moderate Mix | 55% | +$1.15 | +6% |
| Power Shift | 40% | -$6.15 | -31% |
| Adverse Selection | 30% | -$12.85 | -64% |

### Max 20x Plan ($200/month)

| Scenario | Description | Weighted Profit/Sub | Gross Margin |
|----------|-------------|---------------------|--------------|
| Optimistic | Light user skew (unlikely) | +$68.25 | +34% |
| Base Case | Moderate heavy users | +$41.65 | +21% |
| Realistic | Heavy user majority | +$20.65 | +10% |
| Adverse Selection | Power user dominated | -$3.65 | -2% |

**Key insight:** Max plan is structurally challenged because upgraders are, by definition, the expensive users.

---

## Company Financial Positions

### Anthropic
- **2025 Revenue:** ~$9-10B ARR target
- **Burn Rate:** ~$3B/year
- **Revenue Mix:** 80% enterprise, 20% consumer
- **Break-even Target:** 2028
- **Strategy:** Disciplined enterprise SaaS, avoid expensive consumer products (no video gen)

### OpenAI
- **2025 Revenue:** ~$12-20B ARR
- **Burn Rate:** ~$17B/year
- **Revenue Mix:** 30% enterprise, 70% consumer
- **Break-even Target:** 2029-2030
- **Strategy:** Bet on dominance, diversify (Sora, hardware, shopping, ads)

### Key Difference
Anthropic is running a sustainable enterprise playbook. OpenAI is making an all-in bet that requires continued hypergrowth and funding.

---

## Market Correction Triggers

### Immediate Warning Signs
1. Rate limits tightened significantly without announcement
2. Price increases without corresponding feature improvements
3. Subscription tier consolidation
4. Marketing pivot to enterprise-only
5. Funding round delays or down rounds

### Medium-Term Warning Signs
1. Conversion rates stagnating (<5% → 8.5% is OpenAI's target)
2. Churn rates increasing
3. Revenue growth slowing while costs remain high
4. Enterprise retention dropping below 80%

### Structural Risks
1. Open source models reach "good enough" (Llama, Mistral, DeepSeek)
2. Cloud providers commoditize inference
3. Hardware improvements don't translate to lower costs
4. Regulatory pressure increases costs

---

## Key Metrics to Track

### Leading Indicators (Monitor Daily/Weekly)
1. **Rate limit complaints** — Reddit, Discord, GitHub Issues
2. **Pricing page changes** — Detected via diff
3. **Documentation changes** — Rate limit specs
4. **Community sentiment** — Post volume and tone

### Lagging Indicators (Monitor Monthly/Quarterly)
1. **Subscriber estimates** — From revenue / price
2. **Conversion rates** — % of MAU paying
3. **Funding events** — Rounds, valuations
4. **Profitability timeline updates** — From investor reports

---

## Data Sources Summary

| Source | Signal Type | Frequency | Automation |
|--------|-------------|-----------|------------|
| Reddit (r/ClaudeAI, r/ChatGPT) | Community sentiment | Daily | API |
| GitHub Issues | Bug reports, complaints | Daily | API |
| Pricing pages | Price/tier changes | Daily | Scraping |
| Documentation | Rate limit changes | Weekly | Scraping |
| The Information | Financial reporting | Weekly | Manual |
| Crunchbase | Funding events | Monthly | Manual/API |
| App stores | Ratings, reviews | Monthly | Manual |

---

## Baseline Data (January 2026)

### Subscription Pricing
| Company | Tier | Price | Notes |
|---------|------|-------|-------|
| Anthropic | Pro | $20/mo | ~45 msgs/5hr chat, 10-40 CC prompts |
| Anthropic | Max 5x | $100/mo | 5x Pro limits |
| Anthropic | Max 20x | $200/mo | 20x Pro limits |
| OpenAI | Plus | $20/mo | GPT-4o access |
| OpenAI | Pro | $200/mo | Unlimited*, confirmed unprofitable |

### User/Subscriber Estimates
| Metric | Anthropic | OpenAI |
|--------|-----------|--------|
| Monthly Active Users | ~19M | ~800M weekly |
| Paying Subscribers | ~2.6M (est.) | ~35M |
| Conversion Rate | Unknown | ~5% |

### Financial Position
| Metric | Anthropic | OpenAI |
|--------|-----------|--------|
| 2025 Revenue | ~$9B ARR | ~$12-20B ARR |
| 2025 Burn | ~$3B | ~$17B |
| Break-even Target | 2028 | 2029-2030 |
| Last Valuation | $350B | $500B |

---

## References

1. Simon P. Couch, "Electricity use of AI coding agents" (January 2026)
2. The Information — Anthropic/OpenAI financial reporting
3. Ed Zitron, "Where's Your Ed At" — OpenAI financial analysis
4. Sacra — Anthropic company profile
5. The Register — Claude Code usage limit reporting (January 2026)
6. Various: Backlinko, Business of Apps, TechCrunch statistics

---

## Appendix: Spreadsheet Models

Two Excel models support this analysis:

1. **subscription_economics.xlsx**
   - API pricing reference
   - Subscription tier comparison
   - Break-even analysis by tier
   - Energy cost estimates (from Couch analysis)

2. **subscriber_mix_model.xlsx**
   - User segment definitions
   - Profitability scenarios by mix
   - Sensitivity analysis
   - Margin calculations

These models should be updated when pricing changes are detected.
