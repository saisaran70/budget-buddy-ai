from datetime import date, timedelta
from sqlalchemy import func
from app import db
from app.models.expense import Expense, ExpenseCategory


def _current_month_range():
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start, end


def get_dashboard_summary(user):
    start, end = _current_month_range()
    settings = user.settings

    total_spent = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user.id,
        Expense.expense_date >= start,
        Expense.expense_date <= end,
    ).scalar() or 0
    total_spent = float(total_spent)

    monthly_budget = float(settings.monthly_budget) if settings else 0
    saving_goal = float(settings.monthly_saving_goal) if settings else 0
    remaining = monthly_budget - total_spent
    budget_used_pct = round(total_spent / monthly_budget * 100, 1) if monthly_budget > 0 else 0

    recent_expenses = (Expense.query
                       .filter_by(user_id=user.id)
                       .order_by(Expense.expense_date.desc())
                       .limit(5)
                       .all())

    category_data = get_category_breakdown(user)

    return {
        'total_spent': total_spent,
        'monthly_budget': monthly_budget,
        'remaining': remaining,
        'saving_goal': saving_goal,
        'budget_used_pct': budget_used_pct,
        'month_label': start.strftime('%B %Y'),
        'recent_expenses': [e.to_dict() for e in recent_expenses],
        'category_breakdown': category_data,
        'currency': user.currency or 'INR',
    }


def get_category_breakdown(user):
    start, end = _current_month_range()

    rows = db.session.query(
        ExpenseCategory.name,
        ExpenseCategory.color,
        func.sum(Expense.amount).label('total')
    ).join(Expense, Expense.category_id == ExpenseCategory.id
    ).filter(
        Expense.user_id == user.id,
        Expense.expense_date >= start,
        Expense.expense_date <= end,
    ).group_by(ExpenseCategory.name, ExpenseCategory.color
    ).order_by(func.sum(Expense.amount).desc()
    ).all()

    grand_total = sum(float(r.total) for r in rows)

    return [
        {
            'category': r.name,
            'color': r.color,
            'amount': float(r.total),
            'percentage': round(float(r.total) / grand_total * 100, 1) if grand_total > 0 else 0,
        }
        for r in rows
    ]


def get_monthly_trends(user):
    today = date.today()
    results = []

    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        total = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user.id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        ).scalar() or 0

        results.append({
            'month': start.strftime('%b %Y'),
            'total': float(total),
        })

    return results


def get_fixed_cost_analysis(user):
    from app.models.recurring import RecurringExpense
    recurring = RecurringExpense.query.filter_by(user_id=user.id).all()
    return [
        {
            'title': r.title,
            'amount': float(r.amount),
            'billing_cycle': r.billing_cycle,
            'next_due_date': r.next_due_date.strftime('%d %b %Y') if r.next_due_date else None,
            'category': r.category.name if r.category else 'Other',
        }
        for r in recurring
    ]


def get_chart_data(user):
    return {
        'category_breakdown': get_category_breakdown(user),
        'monthly_trends': get_monthly_trends(user),
    }
