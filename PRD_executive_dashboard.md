# PRD: TRUEFAM Welfare Executive Dashboard

**Author:** Business Intelligence Team
**Date:** 2026-03-25
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

An interactive Quarto dashboard that connects directly to the TRUEFAM production PostgreSQL database and presents key welfare-organisation metrics to the executive team in a clear, consumable format.

## 2. Objectives

- Provide a single-page, at-a-glance view of organisational health
- Pull data live from the production database (read-only) so figures are always current
- Require zero manual data entry or CSV imports
- Be renderable as a self-contained HTML file for easy sharing

## 3. Data Sources Assessed

All data comes from the TRUEFAM production PostgreSQL database via `PRODUCTION_DATABASE_URL`. The following tables and fields are available and will be used:

### 3.1 Membership & Demographics (accounts_user + members_member)

| Field | Source Table | Usage |
|---|---|---|
| first_name, last_name | accounts_user | Member identification |
| email, phone_number | accounts_user | Contact info |
| date_joined | accounts_user | Registration timeline |
| is_active | accounts_user | Account status |
| date_of_birth, gender | members_member | Demographics |
| nationality, country_of_origin, country_of_residence | members_member | Geography |
| city, state_region, postal_code | members_member | Location |
| occupation, marital_status | members_member | Demographics |
| member_id | members_member | Unique identifier |
| membership_start_date, membership_renewal_date | members_member | Membership lifecycle |
| group_id | members_member | Group assignment |

### 3.2 Enrollment Pipeline (enrollment_enrollmentapplication)

| Field | Usage |
|---|---|
| status (pending / under_review / information_needed / resubmission_pending / payment_pending / approved / rejected / suspended / resigned) | Enrollment funnel analysis |
| submitted_at, processed_at, updated_at | Processing time metrics |
| is_complete | Completion tracking |
| selected_plan_id | Plan distribution |

### 3.3 Groups (members_membergroup)

| Field | Usage |
|---|---|
| name, group_country | Group identification |
| capacity, current_member_count | Capacity utilisation |
| is_active | Active groups count |

### 3.4 Claims & Bereavement (claims_claim, claims_claimitem)

| Field | Usage |
|---|---|
| status (pending / approved / declined / reviewed) | Claims pipeline |
| submitted_at, processed_at | Processing time |
| group_id | Claims by group |

### 3.5 Contribution Campaigns (claims_contributioncampaign, claims_contributionobligation)

| Field | Usage |
|---|---|
| status (open / closed / cancelled / paused) | Campaign status |
| obligations_count, paid_count | Collection rate |
| total_expected_cents, total_collected_cents | Revenue metrics |
| amount_cents, status, paid_at | Obligation fulfilment |

### 3.6 Payments & Subscriptions (payments_payment, payments_membersubscription, payments_annualsubscriptionplan)

| Field | Usage |
|---|---|
| amount_usd, status, date | Revenue tracking |
| plan_id, status (active/paid/pending) | Plan distribution |
| annual_subscription_price, member_contribution_per_campaign | Plan economics |

### 3.7 Beneficiaries (members_beneficiary)

| Field | Usage |
|---|---|
| relationship, claim_status, is_deceased | Beneficiary demographics |
| percentage | Allocation analysis |

### 3.8 Referrals (referrals_referral)

| Field | Usage |
|---|---|
| status, referral_date | Referral pipeline |
| reward_granted | Reward metrics |

## 4. Dashboard Sections & KPIs

### Section 1: Headline KPIs (Value Boxes)
- **Total Active Members** (enrollment status = approved)
- **Total Revenue Collected** (sum of payments with status = paid)
- **Open Claims** (claims with status = pending)
- **Campaign Collection Rate** (total_collected / total_expected across open+closed campaigns)
- **Pending Applications** (enrollment status in pending, under_review)
- **Member Groups Active** (count of active groups)

### Section 2: Membership Growth
- Line chart: cumulative approved members over time (by membership_start_date, monthly)
- Bar chart: new registrations per month (by date_joined)

### Section 3: Enrollment Funnel
- Horizontal bar chart showing count at each enrollment status stage
- Metric: average processing time (submitted_at to processed_at for approved applications)

### Section 4: Geographic Distribution
- Bar chart: members by country_of_residence
- Table: top 10 countries with member counts

### Section 5: Demographics
- Pie/donut chart: gender distribution
- Histogram: age distribution (calculated from date_of_birth)
- Bar chart: marital status distribution

### Section 6: Financial Overview
- Total revenue (sum of paid payments)
- Revenue by month (bar chart)
- Plan distribution (pie chart of active subscriptions by plan)
- Campaign collection rates (bar chart per campaign)

### Section 7: Claims Overview
- Claims by status (bar chart)
- Claims over time (monthly trend)
- Average claim processing time

### Section 8: Referral Programme
- Total referrals by status
- Referral conversion rate (approved / total)

## 5. Technical Approach

- **Framework:** Quarto Dashboard (`.qmd` with `format: dashboard`)
- **Language:** Python (pandas + plotly)
- **Database:** PostgreSQL via psycopg2, using existing `PRODUCTION_DATABASE_URL` from `.env`
- **Output:** Self-contained HTML (`embed-resources: true`)
- **Connection:** Read-only, SSL required
- **File structure:**
  ```
  reports/
    PRD_executive_dashboard.md    # This document
    db_connection.py              # Shared DB helper
    executive_dashboard.qmd       # The Quarto dashboard
  ```

## 6. Non-Functional Requirements

- Report must render in under 60 seconds
- All database connections are read-only
- No credentials stored in source files (reads from `.env`)
- Output is a single `.html` file for easy distribution

## 7. UAT Acceptance Criteria

1. Dashboard renders without errors
2. All 8 sections display with charts and metrics
3. KPI value boxes show non-null, plausible numbers
4. Charts are interactive (hover tooltips work)
5. No database credentials visible in rendered output
6. Report loads and displays correctly in a browser
