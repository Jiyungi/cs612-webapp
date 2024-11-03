from flask import Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Task, db
from app.forms import AddTaskForm

task_bp = Blueprint('task', __name__)

@task_bp.route('/add_task/<int:list_id>', methods=['POST'])
@login_required
def add_task(list_id):
    """Add a new task to a specified list."""
    form = AddTaskForm()
    if form.validate_on_submit():
        task_title = form.task_name.data.strip()
        if task_title:
            new_task = Task(name=task_title, title=task_title, list_id=list_id, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            # Update parent task status if a new subtask is added to a completed task
            if new_task.parent and new_task.parent.is_completed:
                update_task_completion_status(new_task.parent, False)
        else:
            flash('Error: Task name cannot be empty.', 'danger')
    else:
        flash('Form validation failed. Please check your input.', 'danger')
    
    return redirect(url_for('list.dashboard'))

@task_bp.route('/task/<int:task_id>/rename', methods=['POST'])
@login_required
def rename_task(task_id):
    """Rename an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to rename this task.', 'danger')
        return redirect(url_for('list.dashboard'))
    
    new_title = request.form.get('new_title', '').strip()
    if new_title:
        task.title = new_title
        task.name = new_title
        db.session.commit()
        flash('Task renamed successfully!', 'success')
    else:
        flash('Error: New task name is required.', 'danger')
    
    return redirect(url_for('list.dashboard'))

@task_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task and all associated subtasks."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('list.dashboard'))
    
    def delete_subtasks_recursively(task):
        for subtask in task.subtasks:
            delete_subtasks_recursively(subtask)
            db.session.delete(subtask)
    
    delete_subtasks_recursively(task)
    db.session.delete(task)
    db.session.commit()
    flash('Task and all associated subtasks deleted successfully!', 'success')
    
    return redirect(url_for('list.dashboard'))

@task_bp.route('/task/<int:task_id>/move', methods=['POST'])
@login_required
def move_task(task_id):
    """Move a task to a different list."""
    task = Task.query.get(task_id)
    
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Expected JSON format"}), 400

    data = request.get_json()
    new_list_id = data.get('list_id')
    
    if not new_list_id:
        return jsonify({"error": "Missing 'list_id' in request data"}), 400

    if task.user_id != current_user.id:
        return jsonify({"error": "Permission denied"}), 403

    try:
        task.list_id = new_list_id
        db.session.commit()
        return jsonify({"message": "Task moved successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to move task"}), 500

@task_bp.route('/task/<int:task_id>/toggle_complete', methods=['POST'])
@login_required
def toggle_task_complete(task_id):
    """Toggle the completion status of a task."""
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id:
        return jsonify({"error": "Permission denied"}), 403

    # Get the completion status from the request
    data = request.get_json()
    is_completed = data.get('is_completed', False)

    # Update task's completion status recursively
    update_task_completion_status(task, is_completed)

    # Check for deletion criteria: if marked as completed, delete the task
    if is_completed:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True, 'task_id': task_id, 'deleted': True})

    db.session.commit()
    return jsonify({'success': True, 'task_id': task_id, 'is_completed': is_completed, 'deleted': False})
def update_task_completion_status(task, is_completed):
    """
    Recursively update the completion status of a task's parents and children based on rules:
    - If all subtasks of a task are completed, the task is marked as complete.
    - If a new subtask is added to a completed task, the task is marked as incomplete.
    """
    tasks_to_update = []

    def update_status_recursive(task, is_completed):
        task.is_completed = is_completed
        tasks_to_update.append(task)
        
        # If marking incomplete, also mark all subtasks as incomplete
        if not is_completed:
            for subtask in task.subtasks:
                if subtask.is_completed:
                    update_status_recursive(subtask, False)
        
        # Update parent if all siblings are completed
        parent = task.parent
        if parent:
            all_completed = all(child.is_completed for child in parent.subtasks)
            if all_completed != parent.is_completed:
                update_status_recursive(parent, all_completed)

    update_status_recursive(task, is_completed)
    for task in tasks_to_update:
        db.session.add(task)
    db.session.commit()