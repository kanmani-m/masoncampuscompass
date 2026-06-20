from flask import Blueprint, render_template
from flask_login import login_required, current_user
from webapp import create_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - only accessible when logged in"""
    return render_template('dashboard.html', username=current_user.username)

@main_bp.route('/academicResource')
@login_required
def academicResource():
    """Academic resource page"""
    return render_template('academicResources.html')

@main_bp.route('/dining')
@login_required
def dining():
    """Dining and food resources page"""
    return render_template('dining.html')

@main_bp.route('/wellness-resources')
@login_required
def wellness_resources():
    """Wellness resources page"""
    return render_template('wellnessResources.html')


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
