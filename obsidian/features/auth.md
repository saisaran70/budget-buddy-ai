---
title: Feature — Authentication
updated: 2026-05-26
---

# Authentication

[[home]] | [[routes]] | [[models/user]] | [[decisions#DEC-006]] | [[decisions#DEC-007]]

---

## What It Does

Handles user registration, login, and logout. All other pages require authentication.

---

## User Flow

```
/auth/register → fill form → POST → create User + UserSettings → redirect to /auth/login
/auth/login    → fill form → POST → set session → redirect to /
/auth/logout   → GET → clear session → redirect to /auth/login
```

---

## Route File

[app/routes/auth.py](../../app/routes/auth.py)

### Register (`POST /auth/register`)

1. Validate: username, email, password, confirm_password
2. Check email not already taken (`User.query.filter_by(email=...).first()`)
3. Hash password with Werkzeug: `generate_password_hash(password)`
4. Create `User` row
5. Create `UserSettings` row (one-to-one, created here automatically)
6. Flash success, redirect to login

### Login (`POST /auth/login`)

1. Find user by email
2. `check_password_hash(user.password_hash, password)`
3. `login_user(user)` — sets Flask-Login session
4. Redirect to `next` param or `/`

### Logout (`GET /auth/logout`)

1. `logout_user()` — clears session
2. Redirect to `/auth/login`

---

## Security

| Concern | Implementation |
|---------|---------------|
| Password storage | Werkzeug `pbkdf2:sha256` — never plaintext |
| CSRF | Flask-WTF token in every form |
| Session | Signed cookie, invalidated on logout |
| Brute force | No rate limiting yet (Phase 12 todo) |

See [[decisions#DEC-006]] and [[decisions#DEC-007]].

---

## Templates

- `app/templates/auth/login.html` — Dark fintech login page
- `app/templates/auth/register.html` — Register with confirm password

Both extend `base.html` and include `{{ csrf_token() }}` in the form.

---

## Model

[[models/user]] — `User` with `password_hash`, `set_password()`, `check_password()`

---

## Related Notes

- [[models/user]] — User model detail
- [[models/settings]] — UserSettings created on register
- [[decisions#DEC-006]] — Auth strategy choice
- [[decisions#DEC-007]] — CSRF protection choice
