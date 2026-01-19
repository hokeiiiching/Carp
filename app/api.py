"""REST API endpoints for React frontend."""
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Participant
from app.services import (
    get_or_create_participant,
    register_for_event,
    get_all_events_with_counts,
    get_all_registrations,
    get_participant_for_user
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


# --- Helper Functions ---

def event_to_dict(event, count: int) -> dict:
    """Serialize Event model to dictionary."""
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'max_capacity': event.max_capacity,
        'signups': count,
        'date': event.start_time.strftime('%Y-%m-%d') if event.start_time else None,
        'time': event.start_time.strftime('%I:%M %p') if event.start_time else None,
        'venue': 'Community Center'  # Could add venue field to Event model later
    }


def user_to_dict(user) -> dict:
    """Serialize User model to dictionary."""
    participant = get_participant_for_user(user.id)
    return {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'name': participant.full_name if participant else user.email.split('@')[0],
        'nric': participant.nric if participant else None,
    }


def registration_to_dict(reg) -> dict:
    """Serialize Registration model to dictionary."""
    return {
        'id': reg.id,
        'event_id': reg.event_id,
        'name': reg.participant.full_name,
        'nric': reg.participant.nric,
        'source': reg.source,
        'timestamp': reg.timestamp.isoformat() if reg.timestamp else None
    }


# --- Event Endpoints ---

@api_bp.route('/events', methods=['GET'])
def get_events():
    """Get all events with registration counts."""
    events_data = get_all_events_with_counts()
    result = [
        event_to_dict(item['event'], item['count'])
        for item in events_data
    ]
    return jsonify(result)


@api_bp.route('/events/<int:event_id>/register', methods=['POST'])
def register_event(event_id: int):
    """Register a participant for an event."""
    if current_user.is_authenticated:
        # Use linked participant for logged-in users
        participant = get_participant_for_user(current_user.id)
        if not participant:
            return jsonify({'error': 'No participant profile linked to your account.'}), 400
    else:
        # Guest registration
        data = request.get_json() or {}
        nric = data.get('nric', '').strip()
        name = data.get('name', '').strip()
        
        if not nric or not name:
            return jsonify({'error': 'NRIC and Name are required for guest registration.'}), 400
        
        participant = get_or_create_participant(nric, name)
    
    success, message = register_for_event(event_id, participant.id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400


# --- Auth Endpoints ---

@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user info."""
    if current_user.is_authenticated:
        return jsonify(user_to_dict(current_user))
    return jsonify(None)


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify(user_to_dict(user))
    
    return jsonify({'error': 'Invalid email or password.'}), 401


@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user."""
    logout_user()
    return jsonify({'message': 'Logged out successfully.'})


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register new user account."""
    data = request.get_json() or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    nric = data.get('nric', '').strip().upper()
    role = data.get('role', 'caregiver')
    access_code = data.get('accessCode', '')
    
    # Validate required fields
    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required.'}), 400
    
    # Check if email already exists
    existing = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()
    if existing:
        return jsonify({'error': 'Email already registered.'}), 400
    
    # Validate access codes for restricted roles
    if role == 'admin' and access_code != 'STAFF123':
        return jsonify({'error': 'Invalid Staff Access Code.'}), 400
    if role == 'caregiver' and access_code and access_code != 'CARE456':
        return jsonify({'error': 'Invalid Caregiver Access Code.'}), 400
    
    # Create user
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    # Create participant profile if NRIC provided
    if nric:
        participant = get_or_create_participant(nric, name, user.id)
    
    db.session.commit()
    login_user(user)
    
    return jsonify(user_to_dict(user)), 201


# --- Admin Endpoints ---

@api_bp.route('/registrations', methods=['GET'])
@login_required
def get_registrations():
    """Get all registrations (admin only)."""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied.'}), 403
    
    event_filter = request.args.get('event_id', type=int)
    registrations = get_all_registrations(event_filter)
    
    return jsonify([registration_to_dict(r) for r in registrations])
