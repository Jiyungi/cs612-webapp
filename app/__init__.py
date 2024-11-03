from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect  # Import CSRFProtect for CSRF protection
from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()  # Initialize CSRFProtect
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)  # Enable CSRF protection
    login_manager.init_app(app)
    Migrate(app, db)

    # Import and register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.list_routes import list_bp
    from app.routes.task_routes import task_bp
    from app.routes.subtask_routes import subtask_bp
    from app.routes.main_routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(list_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(subtask_bp)
    app.register_blueprint(main_bp)

    # Move load_user here to avoid circular imports
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app