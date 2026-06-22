from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from webapp import db
from webapp.models import User
from webapp.forms import SignUpForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user sign-up"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    interest_names = [
    "academic_resources",
    "dining_services",
    "wellness_support",
    "career_services",
    "transportation",
    "campus_events",
    ]

    for name in interest_names:
        if not Interest.query.filter_by(name=name).first():
            db.session.add(Interest(name=name))

    db.session.commit()

    form = SignUpForm()
    if form.validate_on_submit():
        selected_interests = form.interests.data
        print(selected_interests)
        # Create new user
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        for interest_name in selected_interests:
            interest = Interest.query.filter_by(name=interest_name).first()

            if interest:
                user.interests.append(interest)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
