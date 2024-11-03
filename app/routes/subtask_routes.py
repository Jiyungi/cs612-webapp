from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Task, db
from app.forms import AddSubtaskForm

subtask_bp = Blueprint('subtask', __name__)

@subtask_bp.route('/task/<int:task_id>/add_subtask', methods=['POST'])
@login_required
def add_subtask(task_id):
    """Add a new subtask to a specified task."""
    form = AddSubtaskForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        print(f"Received subtask title: '{title}'")  # Debug line

        if title:
            # Fetch the parent task to get the correct list_id
            parent_task = Task.query.get(task_id)
            if parent_task is None:
                flash('Error: Parent task not found.', 'danger')
                return redirect(url_for('list.dashboard'))

            # Create the new subtask with the correct list_id
            new_subtask = Task(
                name=title,
                title=title,
                is_completed=False,
                parent_id=task_id,  # Associate with parent task
                list_id=parent_task.list_id,  # Inherit list_id from parent task
                user_id=current_user.id
            )

            print(f"Adding Subtask: Name: {new_subtask.name}, Parent ID: {new_subtask.parent_id}, List ID: {new_subtask.list_id}")  # Debug line
            db.session.add(new_subtask)
            db.session.commit()
            flash('Subtask added successfully!', 'success')
        else:
            flash('Error: Subtask title is required.', 'danger')

    return redirect(url_for('list.dashboard'))

@subtask_bp.route('/task/<int:subtask_id>/rename_subtask', methods=['POST'])
@login_required
def rename_subtask(subtask_id):
    """Rename an existing subtask."""
    subtask = Task.query.get_or_404(subtask_id)
    
    # Ensure current user is the owner of the subtask
    if subtask.user_id != current_user.id:
        flash('You do not have permission to rename this subtask.', 'danger')
        return redirect(url_for('list.dashboard'))
    
    # Get the new title from the form input
    new_title = request.form.get('new_title', '').strip()
    if new_title:
        subtask.title = new_title
        subtask.name = new_title  # Update both title and name for consistency
        db.session.commit()
        flash('Subtask renamed successfully!', 'success')
    else:
        flash('Error: New subtask name is required.', 'danger')

    return redirect(url_for('list.dashboard'))

@subtask_bp.route('/subtask/<int:subtask_id>/delete', methods=['POST'])
@login_required
def delete_subtask(subtask_id):
    """Delete a specific subtask."""
    subtask = Task.query.get_or_404(subtask_id)
    
    # Ensure only the owner can delete the subtask
    if subtask.user_id != current_user.id:
        flash('You do not have permission to delete this subtask.', 'danger')
        return redirect(url_for('list.dashboard'))

    db.session.delete(subtask)
    db.session.commit()
    flash('Subtask deleted successfully!', 'success')
    
    return redirect(url_for('list.dashboard'))