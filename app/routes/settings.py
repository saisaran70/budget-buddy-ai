from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.settings import UserSettings

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def index():
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    return render_template('settings/index.html', settings=settings)


@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)

    try:
        settings.monthly_budget = float(request.form.get('monthly_budget', 0))
        settings.monthly_saving_goal = float(request.form.get('monthly_saving_goal', 0))
        settings.ai_alerts_enabled = request.form.get('ai_alerts_enabled') == 'on'
        settings.notifications_enabled = request.form.get('notifications_enabled') == 'on'

        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.currency = request.form.get('currency', current_user.currency)
        current_user.city = request.form.get('city', current_user.city or '').strip()

        db.session.commit()
        flash('Settings updated successfully.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('settings.index'))
