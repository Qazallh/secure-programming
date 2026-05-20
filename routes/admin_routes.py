from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from models import db, User, Task
from routes import admin_required

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    tasks = Task.query.all()

    return render_template('admin_dashboard.html', users=users, tasks=tasks)


@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deleting current user
    if user.id == session.get('user_id'):
        flash('Cannot delete yourself!')
        return redirect(url_for('admin_bp.admin_dashboard'))

    # Delete user's tasks first
    Task.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.username} deleted successfully!')
    return redirect(url_for('admin_bp.admin_dashboard'))


@admin_bp.route('/admin/assign_task', methods=['POST'])
@admin_required
def assign_task():
    task_id = request.form['task_id']
    user_id = request.form['user_id']

    task = Task.query.get_or_404(task_id)
    task.user_id = user_id

    db.session.commit()

    flash('Task assigned successfully!')
    return redirect(url_for('admin_bp.admin_dashboard'))


@admin_bp.route('/admin/execute_query', methods=['POST'])
@admin_required
def execute_query():
    abort(403)