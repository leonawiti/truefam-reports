# PRD: Campaign Contributions Report

## 1. Purpose

A **member-facing** Quarto report that gives every group member real-time visibility into contribution payment status for active (and recent) campaigns. The report is rendered as a self-contained HTML file, deployed to GitHub Pages, and shareable via link.

## 2. Problem Statement

When a bereavement claim is approved and a contribution campaign is opened, members currently have no single view showing who has paid and who hasn't. Group leaders resort to manual WhatsApp updates. This report eliminates that gap.

## 3. Target Audience

- Active TRUEFAM group members
- Group leaders / admins
- **Not** for external / public audiences (confidentiality notice enforced)

## 4. Key Requirements

### 4.1 Confidentiality Banner
- A prominent banner at the top of the report:
  > "CONFIDENTIAL — This report is intended solely for members of the indicated group. Sharing outside the group is strictly prohibited and may result in disciplinary action."

### 4.2 Campaign Header (per campaign)
| Field | Source |
|---|---|
| Bereaved Member Name | `ContributionCampaign.claimant_member` → `User.first_name + last_name` |
| Group Name | `ContributionCampaign.group` → `MemberGroup.name` |
| Deceased Dependent | `Campaign.claim` → `ClaimItem` → `beneficiary_full_name` (first approved item) |
| Campaign Start Date | `ContributionCampaign.started_at` |
| Campaign End Date | `ContributionCampaign.due_date` |
| Days Remaining | `max(0, due_date - today)` — show "Closed" if campaign status != open |
| Campaign Status | `ContributionCampaign.status` with colour-coded pill |

### 4.3 Contribution Table (per campaign)
| Column | Source |
|---|---|
| # | Row number |
| Member ID | `Member.member_id` |
| Member Name | `User.first_name + last_name` |
| Status | `ContributionObligation.status` — display as "Paid" / "Unpaid" |
| Amount ($) | `ContributionObligation.amount_cents / 100` |

- **Paid** rows: green background (`#E1F5EE`)
- **Unpaid** rows: red background (`#FCEBEB`)

### 4.4 Campaign Summary Footer
| Metric | Derivation |
|---|---|
| Total Members | count of obligations |
| Paid | count where status = 'paid' |
| Unpaid | count where status != 'paid' |
| Total Collected | sum of `amount_cents` where status = 'paid', formatted as USD |
| Total Expected | sum of all `amount_cents`, formatted as USD |
| Collection Rate | paid / total × 100% |

### 4.5 Multi-Campaign Support
- Multiple campaigns may be open simultaneously for the same group.
- Each campaign renders as its own card/section.
- Campaigns ordered by `started_at DESC` (newest first).
- Show all `open` campaigns + last 3 `closed` campaigns.

## 5. Data Source

- PostgreSQL production database via `db_connection.py` (read-only connection).
- All queries use the existing `query()` helper that returns pandas DataFrames.
- Tables: `claims_contributioncampaign`, `claims_contributionobligation`, `members_member`, `members_membergroup`, `accounts_user`, `claims_claim`, `claims_claimitem`.

## 6. Technical Approach

| Aspect | Choice |
|---|---|
| Format | Quarto `.qmd` → self-contained HTML |
| Language | Python (pandas, no Plotly needed — table-centric) |
| Styling | Inline CSS via Quarto `include-in-header` or raw HTML blocks |
| Deployment | Rendered HTML committed to `truefam-reports` repo → GitHub Pages |
| Data freshness | Re-render on each `quarto render` invocation |

## 7. Report Layout

```
┌─────────────────────────────────────────────────┐
│  CONFIDENTIALITY BANNER (red border)            │
├─────────────────────────────────────────────────┤
│  Report Title + Generated timestamp             │
├─────────────────────────────────────────────────┤
│  ┌─ Campaign Card ────────────────────────────┐ │
│  │  Header: Bereaved | Group | Deceased       │ │
│  │  Dates: Start | End | Days Remaining       │ │
│  │  ┌─ Contributions Table ─────────────────┐ │ │
│  │  │ #  Member ID  Name  Status  Amount    │ │ │
│  │  │ 1  001234     John  Paid    $25.00    │ │ │
│  │  │ 2  001235     Jane  Unpaid  $25.00    │ │ │
│  │  └───────────────────────────────────────┘ │ │
│  │  Footer: Total Collected | Rate            │ │
│  └────────────────────────────────────────────┘ │
│  ┌─ Campaign Card 2 ─────────────────────────┐  │
│  │  ...                                       │  │
│  └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 8. Out of Scope

- Authentication / login-gated access (future consideration)
- Push notifications for payment reminders
- Payment initiation from the report
- Historical campaign analytics / trends

## 9. Success Criteria

- Report renders correctly with live data from production DB
- Multiple simultaneous campaigns display independently
- Paid/unpaid status is immediately visually distinguishable
- Deployed to GitHub Pages and accessible via shared link
- Confidentiality notice is prominent and unambiguous
