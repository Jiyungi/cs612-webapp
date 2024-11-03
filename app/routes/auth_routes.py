from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db
from app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

# Registration route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    # Debugging statement to check if form data is being received
    if request.method == 'POST':
        print("Registration form data:", request.form)

    if form.validate_on_submit():
        print("Form validated successfully")  # Debugging statement

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print("User created successfully in the database")  # Debugging statement
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            print("Error creating user:", e)  # Debugging statement
            flash('An error occurred while registering. Please try again.', 'danger')
    
    # Check if form validation fails and log errors
    if form.errors:
        print("Form validation errors:", form.errors)  # Debugging statement
    
    return render_template('register.html', form=form)

# Login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('list.dashboard'))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        print("Login attempt with username:", username)  # Debugging statement

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('list.dashboard'))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))