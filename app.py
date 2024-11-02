from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

app = Flask(__name__)

# Set the secret key
app.secret_key = 'b7f3c9a8d1e4f5b6c7d8e9f0a1b2c3d4'
# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  # Name of your database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects to login page if not authenticated

# Initialize Flask-Migrate
migrate = Migrate(app, db)


# Define your database models here
class User(db.Model, UserMixin):
    # Define fields for the User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    # Additional fields and relationships
    lists = db.relationship('TodoList', backref='owner', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)


class TodoList(db.Model):
    # Define fields for the TodoList model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='list', lazy=True)


class Task(db.Model):
    # Define fields for the Task model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    # Additional fields and relationships
    is_completed = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]), lazy=True)    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()
        # Verify the password
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    # Retrieve the user's todo lists
    todo_lists = TodoList.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', todo_lists=todo_lists)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/add_list', methods=['GET', 'POST'])
@login_required
def add_list():
    if request.method == 'POST':
        # Retrieve the list name from the form
        name = request.form['name']
        # Create a new TodoList object
        new_list = TodoList(name=name, user_id=current_user.id)
        # Add to the database
        db.session.add(new_list)
        db.session.commit()
        flash('New list created!')
        return redirect(url_for('dashboard'))
    return render_template('add_list.html')


@app.route('/list/<int:list_id>')
@login_required
def view_list(list_id):
    # Retrieve the list and ensure it belongs to the current user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    # Retrieve top-level tasks
    tasks = Task.query.filter_by(list_id=list_id, parent_id=None).all()
    return render_template('view_list.html', todo_list=todo_list, tasks=tasks)


@app.route('/list/<int:list_id>/add_task', methods=['GET', 'POST'])
@login_required
def add_task(list_id):
    # Ensure the list belongs to the current user
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        # Retrieve the task title from the form
        title = request.form['title']
        # Create a new Task object
        new_task = Task(title=title, list_id=list_id, user_id=current_user.id)
        # Add to the database
        db.session.add(new_task)
        db.session.commit()
        flash('Task added!')
        return redirect(url_for('view_list', list_id=list_id))
    return render_template('add_task.html', todo_list=todo_list)


def get_task_depth(task):
    depth = 1
    while task.parent_id is not None:
        task = Task.query.get(task.parent_id)
        depth += 1
    return depth


@app.route('/task/<int:task_id>/add_subtask', methods=['GET', 'POST'])
@login_required
def add_subtask(task_id):
    # Retrieve the parent task
    parent_task = Task.query.get_or_404(task_id)
    # Ensure the task belongs to the current user
    if parent_task.user_id != current_user.id:
        flash('You do not have permission to add a subtask to this task.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Retrieve the subtask title from the form
        title = request.form['title']
        # Check the depth of the task
        depth = get_task_depth(parent_task)
        if depth >= 3:
            flash('Maximum subtask depth reached.')
            return redirect(url_for('view_list', list_id=parent_task.list_id))
        # Create a new Subtask object
        new_subtask = Task(title=title, parent_id=task_id, list_id=parent_task.list_id, user_id=current_user.id)
        # Add to the database
        db.session.add(new_subtask)
        db.session.commit()
        flash('Subtask added!')
        return redirect(url_for('view_list', list_id=parent_task.list_id))
    return render_template('add_subtask.html', task=parent_task)


@app.route('/task/<int:task_id>/move', methods=['GET', 'POST'])
@login_required
def move_task(task_id):
    # Retrieve the task
    task = Task.query.get_or_404(task_id)
    # Ensure the task belongs to the current user and is a top-level task
    if task.user_id != current_user.id:
        flash('You do not have permission to move this task.')
        return redirect(url_for('dashboard'))
    if task.parent_id is not None:
        flash('Only top-level tasks can be moved.')
        return redirect(url_for('view_list', list_id=task.list_id)) 
    # Retrieve the user's lists for selection
    lists = TodoList.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        # Retrieve the new list ID from the form
        new_list_id = int(request.form['new_list_id'])
        # Update the task's list_id
        task.list_id = new_list_id
        db.session.commit()
        flash('Task moved successfully!')
        return redirect(url_for('view_list', list_id=new_list_id))
    return render_template('move_task.html', task=task, lists=lists)


@app.route('/list/<int:list_id>/rename', methods=['GET', 'POST'])
@login_required
def rename_list(list_id):
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        new_name = request.form['name']
        todo_list.name = new_name
        db.session.commit()
        flash('List renamed successfully!')
        return redirect(url_for('view_list', list_id=list_id))
    return render_template('rename_list.html', todo_list=todo_list)


@app.route('/reorder_lists', methods=['POST'])
@login_required
def reorder_lists():
    order = request.json.get('order')
    for index, list_id in enumerate(order):
        todo_list = TodoList.query.get(list_id)
        if todo_list and todo_list.user_id == current_user.id:
            todo_list.order = index
    db.session.commit()
    return jsonify({'status': 'success'})


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('dashboard'))

    # Recursively delete all subtasks
    def delete_subtasks(task):
        for subtask in task.subtasks:
            delete_subtasks(subtask)
            db.session.delete(subtask)
    delete_subtasks(task)
    db.session.delete(task)
    db.session.commit()
    flash('Task and all associated subtasks deleted successfully!')
    return redirect(url_for('view_list', list_id=task.list_id))


def update_task_completion(task):
    # Check if all subtasks are completed
    all_completed = all(subtask.is_completed for subtask in task.subtasks)
    task.is_completed = all_completed
    db.session.commit()

    # Propagate changes to parent task
    if task.parent:
        update_task_completion(task.parent)


@app.route('/list/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(list_id):
    todo_list = TodoList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    # Delete all tasks associated with this list
    Task.query.filter_by(list_id=list_id).delete()
    # Now delete the list
    db.session.delete(todo_list)
    db.session.commit()
    flash('List and all associated tasks deleted successfully!')
    return redirect(url_for('dashboard'))


@app.route('/task/<int:task_id>/rename', methods=['GET', 'POST'])
@login_required
def rename_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to rename this task.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        new_title = request.form['title']
        task.title = new_title
        db.session.commit()
        flash('Task renamed successfully!')
        return redirect(url_for('view_list', list_id=task.list_id))
    return render_template('rename_task.html', task=task)


@app.route('/task/<int:task_id>/toggle_complete', methods=['POST'])
@login_required
def toggle_task_completion(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task.')
        return redirect(url_for('dashboard'))
    # Toggle the completion status
    task.is_completed = not task.is_completed
    db.session.commit()
    # Update the completion status of parent tasks if necessary
    update_task_completion(task)
    return jsonify({'status': 'success', 'is_completed': task.is_completed})


if __name__ == '__main__':
    app.run(debug=True)
