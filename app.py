from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import logging

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up logging for SQLAlchemy to troubleshoot SQL operations
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models (make sure models.py uses db from this file)
from app.models import User, TodoList, Task  # Adjust according to the actual model names and paths

# Import and register blueprints (routes)
from app.routes.auth_routes import auth_bp
from app.routes.list_routes import list_bp
from app.routes.task_routes import task_bp
from app.routes.subtask_routes import subtask_bp

app.register_blueprint(auth_bp)
app.register_blueprint(list_bp)
app.register_blueprint(task_bp)
app.register_blueprint(subtask_bp)

# User loader for Login Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)