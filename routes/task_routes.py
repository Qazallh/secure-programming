from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from models import db, Task, User
from routes import login_required

task_bp = Blueprint('task_bp', __name__)


@task_bp.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '')

    if search_query:
        tasks = Task.query.filter(Task.title.like(f'%{search_query}%'), Task.user_id == session['user_id']).all()
    else:
        tasks = Task.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', tasks=tasks, search_query=search_query)


@task_bp.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()

        if not title or len(title) > 100:
            flash('Title is required and must be 100 characters or fewer.')
            return redirect(url_for('task_bp.create_task'))

        if len(description) > 2000:
            flash('Description must be 2000 characters or fewer.')
            return redirect(url_for('task_bp.create_task'))

        new_task = Task(
            title=title,
            description=description,
            user_id=session['user_id']
        )

        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!')
        return redirect(url_for('task_bp.dashboard'))

    return render_template('create_task.html')


@task_bp.route('/task/update/<int:task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != session.get('user_id'):
        abort(403)

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()

        if not title or len(title) > 100:
            flash('Title is required and must be 100 characters or fewer.')
            return redirect(url_for('task_bp.update_task', task_id=task.id))

        if len(description) > 2000:
            flash('Description must be 2000 characters or fewer.')
            return redirect(url_for('task_bp.update_task', task_id=task.id))

        task.title = title
        task.description = description
        task.completed = 'completed' in request.form

        db.session.commit()

        flash('Task updated successfully!')
        return redirect(url_for('task_bp.dashboard'))

    return render_template('update_task.html', task=task)