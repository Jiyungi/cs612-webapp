# cs612-webapp

Link to Demo: https://www.loom.com/share/24bf12e21a7c43a2af3742002ccb75b7?sid=aeed460f-cf52-4041-b3b0-0543751e6398

# Hierarchical Todo List App

## Overview

This application is a hierarchical Todo List App that allows users to create and manage tasks in multiple levels of hierarchy.
Users can register, log in, and create lists with nested tasks and subtasks. Each task can be organized within lists, 
and users can add subtasks to tasks for further nesting.

## Features

- User Authentication (Register, Login, Logout)
- Hierarchical Todo List with multi-level nesting
- Dashboard view showing all lists and their tasks
- Ability to rename and delete tasks and lists
- Drag-and-drop functionality for task organization
- CSRF protection on forms
- Database-backed with SQLAlchemy and Flask-Migrate for migration

## Project Structure

- `app/`: Contains the main application code
  - `__init__.py`: Initializes the Flask application and its extensions
  - `models.py`: Defines the database models for Todo lists, tasks, and users
  - `forms.py`: Defines WTForms forms for user input
  - `routes/`: Contains Blueprint routes for handling different parts of the app
    - `auth_routes.py`: Handles user authentication routes (login, register)
    - `list_routes.py`: Manages todo list creation, renaming, and deletion
    - `task_routes.py`: Manages task creation, renaming, and deletion
    - `subtask_routes.py`: Manages subtask creation, renaming, and deletion
    - `main_routes.py`: Contains routes for the main page and static views
  - `templates/`: Contains HTML templates for the views
    - `dashboard.html`: Dashboard page showing all lists and their tasks
    - `login.html`, `register.html`: Templates for user authentication pages
    - `add_list.html`, `add_task.html`, etc.: Templates for adding or modifying tasks and lists
  - `static/`: Contains static files like CSS and JavaScript
- `config.py`: Configuration file for setting up different environments (e.g., development, testing)
- `run.py`: Starts the application
- `migrations/`: Directory for database migrations

## Setup

### Prerequisites

- Python 3.13 or later
- Flask and related dependencies

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/cs612-webapp.git
   cd cs612-webapp
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Configure the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Access the app at `http://127.0.0.1:5000`.


## Code Comments

Key files in the codebase are commented to explain the purpose of each function and section.

## License

This project is licensed under the MIT License.
