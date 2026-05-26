---
title: Budget Buddy AI — Decision Log
updated: 2026-05-26
---

# Budget Buddy AI — Decision Log

[[home]] | [[architecture]] | [[stack]] | [[progress]]

> Every architectural, technical, or product decision made during the build.
> Auto-updated at the end of every Claude Code session.

---

## DEC-001 · Tech Stack — Backend
**Date:** 2026-05-26
**Decision:** Python + Flask
**Alternatives considered:** Node.js + Express (was in original build.md), Django
**Reason:** PRD explicitly specified Python/Flask. User is in a Python practice workspace. Simpler for a solo project — no compile step, minimal boilerplate.
**Impact:** All backend code is Python. ORM = SQLAlchemy. Auth = Flask-Login. Templates = Jinja2.
**See:** [[stack#Backend]] | [[architecture]]

---

## DEC-002 · Tech Stack — Frontend
**Date:** 2026-05-26
**Decision:** Vanilla HTML + CSS + JavaScript (no framework)
**Alternatives considered:** React + Next.js (was in design.md), Vue.js
**Reason:** PRD specified Vanilla JS. Avoids build toolchain (npm, webpack, bundler). Faster to ship. Chart.js handles the only heavy UI component (charts).
**Impact:** No component system — templates are Jinja2. State management is plain JS + AJAX fetch calls.
**See:** [[stack#Frontend]]

---

## DEC-003 · Tech Stack — Database
**Date:** 2026-05-26
**Decision:** SQLite for development, PostgreSQL-ready architecture
**Alternatives considered:** PostgreSQL from day one, MongoDB
**Reason:** SQLite requires zero setup — ideal for local development. SQLAlchemy ORM abstracts the DB so switching to PostgreSQL in production only requires changing `DATABASE_URL` in `.env`.
**Impact:** `instance/budget_buddy.db` is the dev database file. Production deployment will use `DATABASE_URL=postgresql://...`
**See:** [[stack#Database]] | [[database]]

---

## DEC-004 · Tech Stack — AI Provider
**Date:** 2026-05-26
**Decision:** OpenRouter API
**Alternatives considered:** OpenAI API directly, Anthropic API, local Ollama models
**Reason:** PRD specified OpenRouter. Free-tier models available. Single API key gives access to multiple models. Can switch models without code changes.
**Impact:** Model is configurable via `OPENROUTER_MODEL` in `.env`. Fallback rule-based insights run if API is unavailable or key is missing.
**See:** [[features/ai-insights]] | [[services#ai_service]]

---

## DEC-005 · AI Model
**Date:** 2026-05-26
**Decision:** `openai/gpt-oss-20b:free`
**Alternatives considered:** `mistralai/mistral-7b-instruct:free`, other free-tier models on OpenRouter
**Reason:** User explicitly set this model in `.env`. Free tier, good instruction-following for structured JSON output.
**Impact:** Configurable — changing `OPENROUTER_MODEL` in `.env` switches the model with no code changes.
**See:** [[stack#AI / External APIs]]

---

## DEC-006 · Authentication Strategy
**Date:** 2026-05-26
**Decision:** Flask-Login session-based auth + Werkzeug PBKDF2 password hashing
**Alternatives considered:** JWT tokens, OAuth/social login
**Reason:** Flask-Login is the standard for Flask server-side apps. Sessions are simpler than JWT for a server-rendered app. No need for stateless tokens when the frontend is Jinja2 templates.
**Impact:** Passwords stored as `pbkdf2:sha256` hashes. Session stored in signed cookie (`SECRET_KEY`). All protected routes use `@login_required` decorator.
**See:** [[features/auth]] | [[models/user]]

---

## DEC-007 · CSRF Protection
**Date:** 2026-05-26
**Decision:** Flask-WTF CSRFProtect (app-wide)
**Alternatives considered:** Manual CSRF tokens, no CSRF (insecure)
**Reason:** Flask-WTF provides automatic CSRF protection for all POST forms with minimal setup. Required for security on all state-changing endpoints.
**Impact:** Every form must include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`. AJAX POST requests send the token via `X-CSRFToken` header.
**See:** [[features/auth]] | [[architecture#Security Layers]]

---

## DEC-008 · CSS Approach
**Date:** 2026-05-26
**Decision:** Hand-written CSS design system in `static/css/main.css`
**Alternatives considered:** Tailwind CSS, Bootstrap, Material UI
**Reason:** PRD specified no Bootstrap/framework styling. Full control over the dark fintech aesthetic. No build step needed. Tailwind requires Node.js/PostCSS.
**Impact:** Custom CSS variables (`--bg-primary`, `--mint`, etc.), reusable utility classes. Design closely follows the color palette from `design.md` (`#0F172A` background, `#5EF2D6` mint accent).
**See:** [[stack#Design System]]

---

## DEC-009 · Chart Library
**Date:** 2026-05-26
**Decision:** Chart.js (CDN)
**Alternatives considered:** Recharts (React-only), D3.js (too complex), Plotly
**Reason:** PRD specified Chart.js. Vanilla JS compatible. CDN delivery — no npm install. Excellent donut and line chart support.
**Impact:** Loaded via CDN only on pages that need it (analytics, dashboard). Not bundled into main.js.
**See:** [[features/analytics]] | [[features/dashboard]]

---

## DEC-010 · Database Migrations
**Date:** 2026-05-26
**Decision:** Flask-Migrate (Alembic)
**Alternatives considered:** Manual SQL scripts, SQLAlchemy `create_all()`
**Reason:** Flask-Migrate enables version-controlled schema changes. `create_all()` is fine for dev but can't evolve a production schema safely.
**Impact:** Run `flask db migrate` + `flask db upgrade` for every schema change. Migration files live in `migrations/versions/`.
**See:** [[database]] | [[setup#Database Setup]]

---

## DEC-011 · Model Import Strategy
**Date:** 2026-05-26
**Decision:** Import all models explicitly in `app/__init__.py` inside `create_app()`
**Alternatives considered:** Lazy imports, separate `models/__init__.py` re-exports
**Reason:** SQLAlchemy requires all models to be registered before relationships are resolved. Without explicit imports, `RecurringExpense` in `User.recurring_expenses` raised `InvalidRequestError` at startup.
**Impact:** Line `from app.models import user, expense, goal, settings, ai_insight, recurring` in `create_app()` must be kept. Any new model file must be added here.
**See:** [[models/user]] | [[models/recurring]] | [[architecture#Application Factory Pattern]]

---

## DEC-012 · Fallback AI Insights
**Date:** 2026-05-26
**Decision:** Rule-based fallback when OpenRouter is unavailable
**Alternatives considered:** Show error message to user, skip insights entirely
**Reason:** App should work fully offline or when API key is missing. Budget tracking is the core feature — AI is an enhancement. Fallback checks budget usage %, top spending category, and month-end projection.
**Impact:** `_fallback_insights()` in `ai_service.py` always produces 3 insights. Users never see a blank AI section.
**See:** [[features/ai-insights]] | [[services#_fallback_insights]]

---

## DEC-013 · Obsidian Integration
**Date:** 2026-05-26
**Decision:** Create dedicated vault at `budget-buddy-ai/obsidian/`
**Alternatives considered:** Use existing vault at `python practise/app/obsidian/`, external Notion/Confluence
**Reason:** User chose self-contained vault inside the project repo. Keeps project documentation co-located with code. Can be opened directly in Obsidian as a vault.
**Impact:** `obsidian/progress.md` and `obsidian/decisions.md` are auto-updated by the Claude Code Stop hook at the end of every session. Script at `scripts/update_obsidian.py`.
**See:** [[home]] | [[progress]]

---

*Last updated: 2026-05-26 | Total decisions logged: 13*
