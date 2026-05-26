---
title: Model — User
updated: 2026-05-26
---

# User Model

[[home]] | [[database]] | [[features/auth]] | [[models/settings]]

---

## File

[app/models/user.py](../../app/models/user.py)

---

## Class: `User`

Inherits `db.Model` + `UserMixin` (Flask-Login).

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `email` | String(120) UNIQUE NOT NULL | Login identifier |
| `username` | String(80) UNIQUE NOT NULL | Display name |
| `password_hash` | String(255) | PBKDF2 SHA-256 via Werkzeug |
| `created_at` | DateTime | `default=datetime.utcnow` |
| `is_active` | Boolean | Flask-Login property, default True |

### Relationships

```python
expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
ai_insights = db.relationship('AIInsight', backref='user', lazy=True, cascade='all, delete-orphan')
recurring_expenses = db.relationship('RecurringExpense', backref='user', lazy=True, cascade='all, delete-orphan')
settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
```

All relationships use `cascade='all, delete-orphan'` — deleting a user deletes all their data.

### Methods

```python
def set_password(self, password: str) -> None:
    self.password_hash = generate_password_hash(password)

def check_password(self, password: str) -> bool:
    return check_password_hash(self.password_hash, password)

def __repr__(self):
    return f'<User {self.username}>'
```

### Flask-Login Callback

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

This is defined at module level in `user.py` and registers with the `login_manager` initialized in `app/__init__.py`.

---

## Critical: Model Import Order

All models must be imported inside `create_app()` before blueprints:
```python
from app.models import user, expense, goal, settings, ai_insight, recurring
```
See [[decisions#DEC-011]].

---

## Related Notes

- [[models/settings]] — UserSettings one-to-one with User
- [[models/expense]] — User.expenses relationship
- [[models/goal]] — User.goals relationship
- [[models/ai-insight]] — User.ai_insights relationship
- [[models/recurring]] — User.recurring_expenses relationship
- [[features/auth]] — User creation and auth logic
- [[decisions#DEC-006]] — Why session auth + Werkzeug
