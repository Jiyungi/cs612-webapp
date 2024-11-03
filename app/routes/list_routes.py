from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import TodoList, Task, db
from app.forms import AddListForm, AddTaskForm
from sqlalchemy.orm import joinedload

list_bp = Blueprint('list', __name__)

@list_bp.route('/dashboard')
@login_required
def dashboard():
    """Retrieve todo lists with their associated top-level tasks for the dashboard view."""
    # Retrieve lists and their tasks, loading only for the current user
    todo_lists = (
        TodoList.query.options(joinedload(TodoList.tasks))
        .filter_by(user_id=current_user.id)
        .all()
    )
    
    # Attach only top-level tasks to each list for easier access in the template
    for todo_list in todo_lists:
        todo_list.top_level_tasks = [task for task in todo_list.tasks if task.parent_id is None]
        print(f"List: {todo_list.name}, Top-Level Tasks: {[task.name for task in todo_list.top_level_tasks]}")  # Debugging line

    form = AddTaskForm()
    return render_template('dashboard.html', todo_lists=todo_lists, form=form)

@list_bp.route('/add_list', methods=['GET', 'POST'])
@login_required
def add_list():
    """Add a new list for the current user."""
    form = AddListForm()
    if form.validate_on_submit():
        # Create and save the new list
        new_list = TodoList(name=form.name.data, user_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        flash('New list created!', 'success')
        return redirect(url_for('list.dashboard'))
    
    return render_template('add_list.html', form=form)

@list_bp.route('/list/<int:list_id>')
@login_required
def view_list(list_id):
    """View a specific list with its top-level tasks."""
    # Ensure the list belongs to the user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    top_level_tasks = Task.query.filter_by(list_id=list_id, parent_id=None).all()
    return render_template('view_list.html', todo_list=todo_list, tasks=top_level_tasks)

@list_bp.route('/list/<int:list_id>/rename', methods=['POST'])
@login_required
def rename_list(list_id):
    """Rename an existing list."""
    # Ensure the list belongs to the user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    new_name = request.form.get('new_name')  # Updated to match form field 'new_name'

    if new_name:
        # Update the name and save
        todo_list.name = new_name
        db.session.commit()
        flash('List renamed successfully!', 'success')
    else:
        flash('Error: List name cannot be empty.', 'danger')
    
    return redirect(url_for('list.dashboard'))

@list_bp.route('/list/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(list_id):
    """Delete a list and all associated tasks."""
    # Ensure the list belongs to the user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    # Delete the list; cascade should handle associated tasks if set up correctly in models
    db.session.delete(todo_list)
    db.session.commit()
    
    flash('List and all associated tasks deleted successfully!', 'success')
    return redirect(url_for('list.dashboard'))