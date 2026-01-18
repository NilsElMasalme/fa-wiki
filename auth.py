from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

def init_auth(app):
    """Initialize authentication"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.home'))

        flash('Invalid username/email or password', 'error')

    return render_template('pages/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.home'))

def can_edit(page_slug, section_id=None):
    """Check if current user can edit a page/section"""
    if not current_user.is_authenticated:
        return False
    return current_user.has_permission(page_slug, section_id)

def editor_mode_active():
    """Check if editor mode is currently active"""
    return (
        current_user.is_authenticated and
        request.args.get('edit') == '1'
    )
