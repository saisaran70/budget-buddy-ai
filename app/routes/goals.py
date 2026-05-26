from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.goal import Goal

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')


@goals_bp.route('/')
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return render_template('goals/index.html', goals=goals)


@goals_bp.route('/add', methods=['POST'])
@login_required
def add():
    try:
        name = request.form.get('name', '').strip()
        goal_type = request.form.get('goal_type', 'savings')
        target_amount = float(request.form.get('target_amount', 0))
        current_amount = float(request.form.get('current_amount', 0))
        target_date_str = request.form.get('target_date', '')
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date() if target_date_str else None

        if not name or target_amount <= 0:
            flash('Goal name and target amount are required.', 'error')
            return redirect(url_for('goals.index'))

        goal = Goal(
            user_id=current_user.id,
            name=name,
            goal_type=goal_type,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
        )
        db.session.add(goal)
        db.session.commit()
        flash('Goal created!', 'success')
    except (ValueError, TypeError):
        flash('Invalid goal data.', 'error')

    return redirect(url_for('goals.index'))


@goals_bp.route('/<int:goal_id>/edit', methods=['POST'])
@login_required
def edit(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    try:
        goal.name = request.form.get('name', goal.name).strip()
        goal.goal_type = request.form.get('goal_type', goal.goal_type)
        goal.target_amount = float(request.form.get('target_amount', goal.target_amount))
        goal.current_amount = float(request.form.get('current_amount', goal.current_amount))
        goal.status = request.form.get('status', goal.status)
        date_str = request.form.get('target_date', '')
        if date_str:
            goal.target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Goal updated.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('goals.index'))


@goals_bp.route('/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted.', 'success')
    return redirect(url_for('goals.index'))


@goals_bp.route('/data')
@login_required
def data():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify([g.to_dict() for g in goals])
