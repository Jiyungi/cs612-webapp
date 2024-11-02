from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='../my-todo-app/build', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# Define your database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    lists = db.relationship('TodoList', backref='owner', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            # Do not include the password
        }


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='list', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order': self.order,
            'tasks': [task.to_dict() for task in self.tasks],
        }


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'is_completed': self.is_completed,
            'parent_id': self.parent_id,
            'list_id': self.list_id,
            'user_id': self.user_id,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks],
        }


# User Registration Endpoint
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required.'}), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username already exists.'}), 409

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful.'}), 201
    except Exception as e:
        print(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Registration failed due to server error.'}), 500


# User Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password.'}), 401


# Get User's Todo Lists
@app.route('/api/lists', methods=['GET'])
@jwt_required()
def get_lists():
    user_id = get_jwt_identity()
    todo_lists = TodoList.query.filter_by(user_id=user_id).order_by(TodoList.order).all()
    todo_lists_data = [todo_list.to_dict() for todo_list in todo_lists]
    return jsonify({'todo_lists': todo_lists_data}), 200


# Add a New Todo List
@app.route('/api/lists', methods=['POST'])
@jwt_required()
def add_list():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'message': 'List name is required.'}), 400

    new_list = TodoList(name=name, user_id=user_id)
    db.session.add(new_list)
    db.session.commit()

    return jsonify({'message': 'List created successfully.', 'list': new_list.to_dict()}), 201


# Rename a Todo List
@app.route('/api/lists/<int:list_id>', methods=['PUT'])
@jwt_required()
def rename_list(list_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_name = data.get('name')

    todo_list = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()

    if not new_name:
        return jsonify({'message': 'List name is required.'}), 400

    todo_list.name = new_name
    db.session.commit()

    return jsonify({'message': 'List renamed successfully.', 'list': todo_list.to_dict()}), 200


# Delete a Todo List
@app.route('/api/lists/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    user_id = get_jwt_identity()
    todo_list = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()

    # Delete all tasks associated with this list
    Task.query.filter_by(list_id=list_id).delete()
    db.session.delete(todo_list)
    db.session.commit()

    return jsonify({'message': 'List deleted successfully.'}), 200


# Get Tasks in a List
@app.route('/api/lists/<int:list_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(list_id):
    user_id = get_jwt_identity()
    todo_list = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    tasks = Task.query.filter_by(list_id=list_id, parent_id=None).all()
    tasks_data = [task.to_dict() for task in tasks]
    return jsonify({'tasks': tasks_data}), 200


# Add a Task to a List
@app.route('/api/lists/<int:list_id>/tasks', methods=['POST'])
@jwt_required()
def add_task(list_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'message': 'Task title is required.'}), 400

    todo_list = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    new_task = Task(title=title, list_id=list_id, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task added successfully.', 'task': new_task.to_dict()}), 201


# Add a Subtask to a Task
@app.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
@jwt_required()
def add_subtask(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'message': 'Subtask title is required.'}), 400

    parent_task = Task.query.get_or_404(task_id)
    if parent_task.user_id != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    # Check the depth of the task
    depth = get_task_depth(parent_task)
    if depth >= 3:
        return jsonify({'message': 'Maximum subtask depth reached.'}), 400

    new_subtask = Task(
        title=title,
        parent_id=task_id,
        list_id=parent_task.list_id,
        user_id=user_id
    )
    db.session.add(new_subtask)
    db.session.commit()

    return jsonify({'message': 'Subtask added successfully.', 'subtask': new_subtask.to_dict()}), 201


def get_task_depth(task):
    depth = 1
    while task.parent_id is not None:
        task = Task.query.get(task.parent_id)
        depth += 1
    return depth


# Delete a Task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)

    if task.user_id != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    # Recursively delete all subtasks
    def delete_subtasks(task):
        for subtask in task.subtasks:
            delete_subtasks(subtask)
            db.session.delete(subtask)

    delete_subtasks(task)
    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task and subtasks deleted successfully.'}), 200


# Rename a Task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def rename_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_title = data.get('title')

    if not new_title:
        return jsonify({'message': 'Task title is required.'}), 400

    task = Task.query.get_or_404(task_id)
    if task.user_id != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    task.title = new_title
    db.session.commit()

    return jsonify({'message': 'Task renamed successfully.', 'task': task.to_dict()}), 200


# Toggle Task Completion
@app.route('/api/tasks/<int:task_id>/toggle_complete', methods=['POST'])
@jwt_required()
def toggle_task_completion(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)

    if task.user_id != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    task.is_completed = not task.is_completed
    db.session.commit()
    update_task_completion(task)

    return jsonify({'message': 'Task completion status updated.', 'is_completed': task.is_completed}), 200


def update_task_completion(task):
    # Check if all subtasks are completed
    if task.subtasks:
        all_completed = all(subtask.is_completed for subtask in task.subtasks)
        task.is_completed = all_completed
        db.session.commit()

    # Propagate changes to parent task
    if task.parent:
        update_task_completion(task.parent)


# Move a Task to a Different List
@app.route('/api/tasks/<int:task_id>/move', methods=['PUT'])
@jwt_required()
def move_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_list_id = data.get('new_list_id')

    if not new_list_id:
        return jsonify({'message': 'New list ID is required.'}), 400

    task = Task.query.get_or_404(task_id)
    if task.user_id != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    if task.parent_id is not None:
        return jsonify({'message': 'Only top-level tasks can be moved.'}), 400

    new_list = TodoList.query.filter_by(id=new_list_id, user_id=user_id).first_or_404()
    task.list_id = new_list_id
    db.session.commit()

    return jsonify({'message': 'Task moved successfully.', 'task': task.to_dict()}), 200


# Reorder Lists
@app.route('/api/lists/reorder', methods=['POST'])
@jwt_required()
def reorder_lists():
    user_id = get_jwt_identity()
    order = request.json.get('order')

    if not order:
        return jsonify({'message': 'Order data is required.'}), 400

    for index, list_id in enumerate(order):
        todo_list = TodoList.query.get(list_id)
        if todo_list and todo_list.user_id == user_id:
            todo_list.order = index
    db.session.commit()
    return jsonify({'message': 'Lists reordered successfully.'}), 200


# Serve the React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
