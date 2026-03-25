# PRD: GA4 Web Analytics Report — truefamwel.com

## 1. Executive Summary

This Product Requirements Document defines the full specification for an automated, executive-grade web traffic analytics report for TRUEFAM Welfare (www.truefamwel.com). All data powering this report is sourced exclusively from Google Analytics 4 (GA4). No other analytics platform, database, or third-party data source is used.

The report is built using Quarto and pulls live data directly from the GA4 Data API on each render cycle. It is designed to give executive leadership a clear, reproducible, and data-driven view of digital performance, audience engagement, member acquisition trends, and enrollment funnel health, all derived from GA4 event and session data collected on truefamwel.com.

## 2. Objectives & Strategic Goals

### 2.1 Primary Objectives

- Deliver a single automated report powered entirely by GA4 data for www.truefamwel.com
- Replace manual, ad-hoc analytics review with a reproducible Quarto document that re-renders on demand or on schedule
- Give executive leadership a headline view of traffic, audience, engagement, and enrollment conversion — all from GA4
- Identify which channels, geographies, and content drive the most enrolled members, using GA4 acquisition and conversion data
- Establish GA4 as the authoritative, standardized data source for all digital performance reporting at TRUEFAM Welfare

### 2.2 Success Metrics

| Success Criterion | Target / Definition |
|---|---|
| Report generation time | < 2 minutes from GA4 API pull to rendered output |
| Data freshness | Within 24 hours — GA4 API provides up to previous day's data |
| GA4 coverage | All required dimensions, metrics, and custom events flowing correctly |
| Executive readability | No raw API JSON; all GA4 metrics visualized as charts or KPI cards |
| Scheduling | Auto-rendered weekly + monthly via GitHub Actions or cron |

## 3. Stakeholders & Audience

| Stakeholder | Role | GA4 Data They Need |
|---|---|---|
| Leon Awiti | Director / GA4 Property Owner | Full report — all GA4 dimensions and metrics |
| Shane | AI & Dashboard Lead | GA4 conversion events, funnel drop-off rates |
| Executive Leadership | Decision Makers | GA4 headline KPIs — 1-page snapshot |
| Marketing Team | Content & Outreach | GA4 channel, top pages, geographic audience data |
| Board / Advisors | Governance | GA4 enrollment conversion trends and user growth |

## 4. Scope

### 4.1 In Scope

- All web traffic data pulled exclusively from the GA4 Data API for www.truefamwel.com
- GA4 standard reports: Acquisition, Engagement, Retention, Demographics, Tech
- GA4 custom events: membership application starts, CTA clicks, form completions, scroll depth
- Quarto report rendered as HTML (interactive) and PDF (executive email distribution)
- Automated GA4 data refresh on each Quarto render — no cached or static datasets
- Period-over-period comparisons using GA4 date range parameters
- GA4 funnel exploration data for enrollment conversion tracking

### 4.2 Out of Scope

- Any data source other than Google Analytics 4
- Real-time dashboards — GA4 API data is available up to the previous day
- Social media platform analytics beyond what GA4 captures as referral/social sessions
- Paid advertising attribution modeling — future phase
- Internal member portal or CRM data — separate system, separate report

## 5. Google Analytics 4 Configuration Requirements

### 5.1 GA4 Property Setup

- GA4 property created and linked to www.truefamwel.com
- GA4 tracking code (G-XXXXXXXXXX) installed on all pages
- Reporting time zone: Central Time (America/Chicago)
- Google Signals enabled for enhanced demographic and cross-device data

### 5.2 GA4 Data API Authentication

- Enable Google Analytics Data API v1 in Google Cloud Console
- Service Account with Viewer role on GA4 property
- JSON key stored as environment variable: `GOOGLE_APPLICATION_CREDENTIALS`
- GitHub Actions secret: `GA_CREDENTIALS`

| Config Item | Value / Action |
|---|---|
| GA4 Property ID | Numeric ID from GA4 Admin > Property Settings |
| API Scope | `https://www.googleapis.com/auth/analytics.readonly` |
| Auth Method | Service Account (JSON key) — NOT OAuth browser flow |
| Secret Storage | GitHub Actions secret (GA_CREDENTIALS) for CI/CD |
| Rate Limits | GA4 Data API: 10 queries/second, 1,000 requests/day (free tier) |

### 5.3 Required GA4 Custom Events

| GA4 Event Name | GTM Trigger | Event Parameters | Priority |
|---|---|---|---|
| apply_now_click | Click on any Apply Now CTA | button_location, nationality | HIGH |
| nationality_selected | User selects nationality in enrollment form | country_selected | HIGH |
| form_submit | Membership application form submitted | form_name, status | HIGH |
| membership_confirmed | User lands on confirmation page | membership_tier | HIGH |
| scroll_depth_75 | User scrolls 75% down homepage | page_path | MEDIUM |
| cta_engagement | Any secondary CTA interaction | cta_label, page_path | MEDIUM |

### 5.4 GA4 Key Events (Conversions)

- Mark `form_submit` and `membership_confirmed` as Key Events
- Mark `apply_now_click` as Key Event for top-of-funnel intent

## 6. Report Structure & GA4 Data Mapping

### 6.1 Section 1 — Executive Snapshot (Page 1)

| KPI Card | GA4 Metric | GA4 Dimension | Visualization |
|---|---|---|---|
| Total Users | totalUsers | — | Value box + % change arrow |
| New vs Returning | newUsers / returningUsers | newVsReturning | Donut chart |
| Total Sessions | sessions | — | Value box + sparkline |
| Avg. Engagement Time | averageSessionDuration | — | Value box + benchmark line |
| Enrollment Applications | eventCount | eventName = apply_now_click | Value box + conversion % |
| Bounce Rate | bounceRate | — | Gauge chart with RAG status |
| Engagement Rate | engagementRate | — | Value box + trend line |

### 6.2 Section 2 — Traffic Acquisition

- Channel breakdown: Organic Search, Direct, Social, Referral, Email, Paid
- Top 10 referring sources by sessions, engagement rate, and conversion rate
- Session volume over time by channel — stacked area chart
- GA4 Dimensions: sessionDefaultChannelGroup, sessionSource, sessionMedium, sessionCampaignName
- GA4 Metrics: sessions, engagedSessions, engagementRate, conversions, sessionConversionRate

### 6.3 Section 3 — Audience & Demographics

- Geographic distribution: Country and City breakdown — map visualization
- Language breakdown aligned to TRUEFAM nationality groups
- Device split: Mobile vs Desktop vs Tablet
- New user growth trend over reporting period
- Age and gender breakdown (requires Google Signals)

### 6.4 Section 4 — Engagement & Content Performance

- Top 10 pages by screenPageViews, avgSessionDuration, engagementRate
- Entry page analysis — landingPage dimension
- Exit page analysis — exitPage dimension
- Enrollment page performance: /apply, /membership pages
- Custom event counts: scroll_depth_75, cta_engagement

### 6.5 Section 5 — Enrollment Conversion Funnel

| Step | Funnel Stage | GA4 Event / Dimension | GA4 Metric |
|---|---|---|---|
| 1 | Site Entry | session_start | sessions |
| 2 | Enrollment Page View | pagePath = /apply or /membership | screenPageViews |
| 3 | Application Initiated | apply_now_click | eventCount |
| 4 | Nationality Selected | nationality_selected | eventCount |
| 5 | Form Submitted | form_submit (Key Event) | conversions |
| 6 | Membership Confirmed | membership_confirmed (Key Event) | conversions |

### 6.6 Section 6 — Period-over-Period Trend Analysis

- Week-over-week and month-over-month comparison
- 30 / 60 / 90-day rolling trend charts
- YoY comparison when 12+ months of GA4 data is available
- Annotated timeline with TRUEFAM campaign overlays

## 7. Technical Specifications

### 7.1 Technology Stack

| Component | Tool / Technology | Notes |
|---|---|---|
| Data Source | Google Analytics 4 (GA4) ONLY | All data via GA4 Data API v1 |
| GA4 API Client | google-analytics-data (Python) | BetaAnalyticsDataClient |
| Report Framework | Quarto (v1.5+) | Python kernel |
| Visualization | plotly / Chart.js | Interactive HTML |
| Output Formats | HTML (primary), PDF (executive share) | Quarto multi-format render |
| Scheduling | GitHub Actions or cron | Weekly + monthly auto-render |
| Hosting | GitHub Pages | Existing TRUEFAM reports infra |
| Auth / Secrets | Service Account JSON — GitHub Secret | GA_CREDENTIALS env variable |

### 7.2 GA4 API Query Parameters

| Parameter | Default Value |
|---|---|
| GA4 Property ID | Set in .env |
| Date Range Start | 28 days ago |
| Date Range End | Yesterday |
| Comparison Period | Prior equivalent period |
| Currency | USD |
| Timezone | America/Chicago (Central) |

## 8. Deliverables

| # | Deliverable | Format | Owner |
|---|---|---|---|
| 1 | Quarto .qmd source file with GA4 API calls | .qmd | Leon |
| 2 | Rendered interactive HTML report | .html (GitHub Pages) | Auto-rendered |
| 3 | Rendered executive PDF report | .pdf | Auto-rendered |
| 4 | GA4 property audit & custom event validation | Markdown | Leon |
| 5 | GTM custom event implementation guide | Google Doc | Shane |
| 6 | GitHub Actions workflow for scheduled rendering | .yml | Shane |
| 7 | Service account setup & GA4 API credentials guide | README.md | Leon |

## 9. Project Milestones & Timeline

| # | Milestone | Owner | Target | Status |
|---|---|---|---|---|
| 1 | PRD approved by executive leadership | Leon | Week 1 | Pending |
| 2 | GA4 property confirmed + tracking code verified | Leon | Week 1 | Pending |
| 3 | GA4 Data API + Service Account credentials configured | Leon | Week 2 | Pending |
| 4 | GTM custom events implemented and verified | Shane | Week 2 | Pending |
| 5 | GA4 Key Events marked in property | Leon | Week 2 | Pending |
| 6 | Quarto skeleton report with live GA4 API data pull | Leon | Week 3 | Pending |
| 7 | All 6 report sections developed using GA4 data | Leon | Week 4 | Pending |
| 8 | GitHub Actions scheduling pipeline deployed | Shane | Week 5 | Pending |
| 9 | Executive review, sign-off, and first live delivery | Leadership | Week 6 | Pending |

## 10. Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| GA4 property not set up or no tracking code | HIGH | Audit in Week 1 using GA4 Realtime view |
| Insufficient GA4 historical data | MEDIUM | Use all available data; add YoY once 12 months accumulate |
| Custom GA4 events not firing correctly | MEDIUM | Use GA4 DebugView + GTM Preview mode to validate |
| GA4 API quota limits (1,000 req/day free tier) | LOW | Cache API responses; batch all calls per render |
| Service account credentials exposed in repo | HIGH | Store only in GitHub Secrets or .env; never commit JSON key |
