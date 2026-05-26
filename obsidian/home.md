---
title: Budget Buddy AI — Home
updated: 2026-05-26
---

# Budget Buddy AI

> AI-powered personal finance tracker. Track expenses, set goals, get AI insights.
> Built with Python + Flask + SQLite. Running at `http://127.0.0.1:5000`.

---

## Quick Navigation

### Project
- [[architecture]] — System design and layer overview
- [[stack]] — Tech stack choices and why
- [[setup]] — How to run the project locally
- [[roadmap]] — Remaining features to build
- [[decisions]] — All architectural decisions (DEC-001 to DEC-013)
- [[progress]] — Session-by-session build log

### Features
- [[features/auth]] — Register, Login, Logout
- [[features/dashboard]] — Summary cards, charts, recent expenses
- [[features/expenses]] — Add, edit, delete, filter expenses
- [[features/analytics]] — Category breakdown, monthly trends
- [[features/goals]] — Savings goals with progress tracking
- [[features/ai-insights]] — OpenRouter AI analysis
- [[features/settings]] — Profile, budget limits, notifications
- [[features/recurring-bills]] — Recurring expense scheduler (Phase 8)

### Data Models
- [[models/user]] — User account + authentication
- [[models/expense]] — Expense + ExpenseCategory
- [[models/goal]] — Savings goal
- [[models/settings]] — User preferences
- [[models/ai-insight]] — Stored AI recommendations
- [[models/recurring]] — Recurring bill definition

### Code Layers
- [[routes]] — All HTTP endpoints by blueprint
- [[services]] — Business logic (analytics + AI)
- [[database]] — Schema, relationships, migrations

---

## Project Status

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Project Setup + Database | ✅ Done |
| 2 | Authentication | ✅ Done |
| 3 | Dashboard | ✅ Done |
| 4 | Expense Tracking | ✅ Done |
| 5 | Analytics | ✅ Done |
| 6 | Savings Goals | ✅ Done |
| 7 | AI Insights | ✅ Done |
| 8 | Recurring Bills | 🔲 Next |
| 9 | Money Score | 🔲 Planned |
| 10 | Voice Logging | 🔲 Planned |
| 11 | Bank Statement Import | 🔲 Planned |
| 12 | Deployment | 🔲 Planned |

---

## Key Links

- Test login: `test@budgetbuddy.com` / `test1234`
- App entry point: [[setup#Running the app]]
- Stack decisions: [[decisions#DEC-001]] through [[decisions#DEC-013]]
