"""Route definitions for CARP application."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Event, Participant
from app.services import (
    get_or_create_participant,
    register_for_event,
    get_all_events_with_counts,
    get_all_registrations,
    get_participant_for_user
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Public event catalog view."""
    events_data = get_all_events_with_counts()
    
    # Get participant linked to current user if logged in
    linked_participant = None
    if current_user.is_authenticated:
        linked_participant = get_participant_for_user(current_user.id)
    
    return render_template(
        'index.html',
        events_data=events_data,
        linked_participant=linked_participant
    )


@main_bp.route('/register/<int:event_id>', methods=['POST'])
def register(event_id: int):
    """Handle event registration."""
    if current_user.is_authenticated:
        # Use linked participant for logged-in users
        participant = get_participant_for_user(current_user.id)
        if not participant:
            flash('No participant profile linked to your account.', 'danger')
            return redirect(url_for('main.index'))
    else:
        # Guest registration - require NRIC and name
        nric = request.form.get('nric', '').strip()
        name = request.form.get('name', '').strip()
        
        if not nric or not name:
            flash('NRIC and Name are required for guest registration.', 'danger')
            return redirect(url_for('main.index'))
        
        participant = get_or_create_participant(nric, name)
    
    # Attempt registration
    success, message = register_for_event(event_id, participant.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Staff dashboard view - admin only."""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get filter parameter
    event_filter = request.args.get('event_id', type=int)
    
    # Get all events for filter dropdown
    events = db.session.execute(db.select(Event)).scalars().all()
    
    # Get registrations (filtered if specified)
    registrations = get_all_registrations(event_filter)
    
    return render_template(
        'dashboard.html',
        registrations=registrations,
        events=events,
        selected_event=event_filter
    )


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login view."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


# ============================================================================
# CLI Commands for Database Seeding
# ============================================================================

@main_bp.cli.command('seed')
def seed_database():
    """Seed database with sample data for development."""
    from datetime import datetime, timedelta
    
    # Create admin user
    admin = User(email='admin@carp.local', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create caregiver user with linked participant
    caregiver = User(email='caregiver@carp.local', role='caregiver')
    caregiver.set_password('caregiver123')
    db.session.add(caregiver)
    db.session.flush()  # Get IDs
    
    # Create linked participant
    participant = Participant(
        nric='S1234567A',
        full_name='John Doe',
        user_id=caregiver.id
    )
    db.session.add(participant)
    
    # Create sample events
    events = [
        Event(
            title='Morning Yoga',
            description='Gentle yoga session for all ages. Mats provided.',
            max_capacity=15,
            start_time=datetime.now() + timedelta(days=3)
        ),
        Event(
            title='Community Gardening',
            description='Help tend the community garden. Tools and refreshments provided.',
            max_capacity=20,
            start_time=datetime.now() + timedelta(days=5)
        ),
        Event(
            title='Art Workshop',
            description='Learn watercolor painting basics. All materials included.',
            max_capacity=10,
            start_time=datetime.now() + timedelta(days=7)
        ),
    ]
    db.session.add_all(events)
    
    db.session.commit()
    print('Database seeded successfully!')
