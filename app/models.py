from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """User model to represent users of the application."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    # Define one-to-many relationship to TodoList, cascade to delete lists owned by the user
    lists = db.relationship('TodoList', backref='owner', lazy=True, cascade="all, delete-orphan")
    # Define one-to-many relationship to Task, cascade deletion when user is deleted
    tasks = db.relationship('Task', backref='user', lazy='select', cascade="all, delete-orphan")

class TodoList(db.Model):
    """TodoList model to represent individual lists for tasks."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define relationship to Task with cascade behavior to delete associated tasks
    tasks = db.relationship('Task', backref='todo_list', lazy='select', cascade="all, delete-orphan")

class Task(db.Model):
    """Task model to represent tasks and nested subtasks within a list."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Ensure this field is used properly
    title = db.Column(db.String(150), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define recursive relationship for subtasks, with cascade delete to remove subtasks when a parent task is deleted
    subtasks = db.relationship(
        'Task',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        cascade="all, delete-orphan"
    )

    def mark_complete(self):
        """Mark this task as completed, and recursively check parents."""
        self.is_completed = True
        db.session.commit()
        # Recursively check parents
        self.check_parent_completion()

    def mark_incomplete(self):
        """Mark this task as incomplete and propagate up/down if needed."""
        self.is_completed = False
        db.session.commit()
        # Unmark parent recursively if any subtask is incomplete
        if self.parent:
            self.parent.mark_incomplete()

    def check_parent_completion(self):
        """If all subtasks are completed, mark the parent task as completed."""
        if self.parent and all(subtask.is_completed for subtask in self.parent.subtasks):
            self.parent.mark_complete()