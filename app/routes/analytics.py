from datetime import date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.services.analytics_service import (
    get_category_breakdown, get_monthly_trends, get_fixed_cost_analysis
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    breakdown = get_category_breakdown(current_user)
    return render_template('analytics/index.html', breakdown=breakdown, now=date.today())


@analytics_bp.route('/categories')
@login_required
def categories():
    return jsonify(get_category_breakdown(current_user))


@analytics_bp.route('/trends')
@login_required
def trends():
    return jsonify(get_monthly_trends(current_user))


@analytics_bp.route('/fixed-costs')
@login_required
def fixed_costs():
    return jsonify(get_fixed_cost_analysis(current_user))
