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


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
