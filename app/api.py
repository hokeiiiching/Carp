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
    get_participant_for_user,
    get_participants_for_user,
    link_participant_to_user,
    unlink_participant_from_user
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


# --- Helper Functions ---

def event_to_dict(event, count: int) -> dict:
    """
    Serialize an Event model instance to a dictionary for API responses.
    
    Args:
        event: Event model instance to serialize
        count: Current number of registrations for this event
    
    Returns:
        Dictionary containing event data formatted for frontend consumption:
        - id, title, description, max_capacity, signups
        - date (YYYY-MM-DD), time (HH:MM AM/PM), venue
    """
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'max_capacity': event.max_capacity,
        'signups': count,
        'date': event.start_time.strftime('%Y-%m-%d') if event.start_time else None,
        'time': event.start_time.strftime('%I:%M %p') if event.start_time else None,
        'venue': 'Community Center'  # TODO: Add venue field to Event model
    }


def user_to_dict(user) -> dict:
    """
    Serialize a User model instance to a dictionary for API responses.
    
    Includes linked participant data if available (name and NRIC).
    Falls back to email username if no participant is linked.
    
    Args:
        user: User model instance to serialize
    
    Returns:
        Dictionary containing: id, email, role, name, nric (if available)
    """
    participant = get_participant_for_user(user.id)
    return {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'name': participant.full_name if participant else user.email.split('@')[0],
        'nric': participant.nric if participant else None,
    }


def registration_to_dict(reg) -> dict:
    """
    Serialize a Registration model instance to a dictionary for API responses.
    
    Flattens participant data into the response for admin dashboard display.
    
    Args:
        reg: Registration model instance to serialize
    
    Returns:
        Dictionary containing: id, event_id, name, nric, source, timestamp (ISO format)
    """
    return {
        'id': reg.id,
        'event_id': reg.event_id,
        'name': reg.participant.full_name,
        'nric': reg.participant.nric,
        'source': reg.source,
        'timestamp': reg.timestamp.isoformat() if reg.timestamp else None
    }


def participant_to_dict(participant) -> dict:
    """
    Serialize a Participant (senior) model to dictionary for API responses.
    
    Args:
        participant: Participant model instance
    
    Returns:
        Dictionary containing: id, nric, name
    """
    return {
        'id': participant.id,
        'nric': participant.nric,
        'name': participant.full_name
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
    """
    Register a participant for an event.
    
    For caregivers: Can specify senior_id to register a specific linked senior.
    For guests: Must provide nric and name in request body.
    """
    data = request.get_json() or {}
    
    if current_user.is_authenticated:
        # Check if specific senior is selected
        senior_id = data.get('senior_id')
        
        if senior_id:
            # Verify senior is linked to this user
            participant = db.session.get(Participant, senior_id)
            if not participant or participant.user_id != current_user.id:
                return jsonify({'error': 'Invalid senior selection.'}), 400
        else:
            # Fall back to first linked participant
            participant = get_participant_for_user(current_user.id)
            if not participant:
                return jsonify({'error': 'No senior linked to your account. Please add a senior first.'}), 400
    else:
        # Guest registration
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


@api_bp.route('/my-registrations', methods=['GET'])
@login_required
def get_my_registrations():
    """
    Get event IDs that the current user's participants are registered for.
    
    Returns list of event IDs for quick lookup in frontend.
    """
    from app.models import Registration
    
    # Get all participants linked to this user
    participants = get_participants_for_user(current_user.id)
    participant_ids = [p.id for p in participants]
    
    if not participant_ids:
        return jsonify([])
    
    # Get all registrations for these participants
    registrations = db.session.execute(
        db.select(Registration.event_id).filter(Registration.participant_id.in_(participant_ids))
    ).scalars().all()
    
    return jsonify(list(set(registrations)))


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
    try:
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
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({'error': f'Login failed: {str(e)}', 'details': error_details}), 500


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


@api_bp.route('/registrations/export', methods=['GET'])
@login_required
def export_registrations():
    """
    Export registrations to CSV format (admin only).
    
    Query params:
        event_id: Optional event ID to filter by
    
    Returns:
        CSV file download with columns: Name, NRIC, Event, Date, Time, Venue, Source, Registered At
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied.'}), 403
    
    import csv
    from io import StringIO
    from flask import Response
    
    event_filter = request.args.get('event_id', type=int)
    registrations = get_all_registrations(event_filter)  # Uses eager loading
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'NRIC', 'Event', 'Date', 'Time', 'Venue', 'Source', 'Registered At'])
    
    # Write data rows (using preloaded event/participant data)
    for reg in registrations:
        event = reg.event  # Already loaded via joinedload
        writer.writerow([
            reg.participant.full_name,
            reg.participant.nric,
            event.title if event else 'Unknown',
            event.start_time.strftime('%Y-%m-%d') if event else '',
            event.start_time.strftime('%I:%M %p') if event else '',
            'Activity Centre',  # Default venue
            reg.source,
            reg.timestamp.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Create response with CSV
    output.seek(0)
    
    # Generate filename
    if event_filter:
        event = db.session.get(Event, event_filter)
        filename = f"registrations_{event.title.replace(' ', '_') if event else event_filter}.csv"
    else:
        filename = "all_registrations.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# --- Seniors (Caregiver) Endpoints ---

@api_bp.route('/seniors', methods=['GET'])
@login_required
def get_seniors():
    """
    Get all seniors linked to the current caregiver.
    
    Returns list of participant objects linked to this user.
    """
    seniors = get_participants_for_user(current_user.id)
    return jsonify([participant_to_dict(s) for s in seniors])


@api_bp.route('/seniors', methods=['POST'])
@login_required
def add_senior():
    """
    Link a new senior to the caregiver's account.
    
    Request body: { nric: string, name: string }
    """
    data = request.get_json() or {}
    nric = data.get('nric', '').strip()
    name = data.get('name', '').strip()
    
    if not nric or not name:
        return jsonify({'error': 'NRIC and Name are required.'}), 400
    
    success, message, participant = link_participant_to_user(nric, name, current_user.id)
    
    if success:
        return jsonify({
            'message': message,
            'senior': participant_to_dict(participant)
        }), 201
    else:
        return jsonify({'error': message}), 400


@api_bp.route('/seniors/<int:senior_id>', methods=['DELETE'])
@login_required
def remove_senior(senior_id: int):
    """
    Unlink a senior from the caregiver's account.
    
    The participant record is preserved for event history.
    """
    success, message = unlink_participant_from_user(senior_id, current_user.id)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400


# --- Database Seed Endpoint (Protected) ---

import os

@api_bp.route('/seed', methods=['POST'])
def seed_database():
    """
    Seed the database with demo data.
    
    Protected by SEED_SECRET environment variable.
    
    Request body: { "secret": "your-seed-secret" }
    
    To use:
    1. Set SEED_SECRET environment variable in Vercel
    2. POST to /api/seed with { "secret": "your-secret-value" }
    
    This will CLEAR all existing data and populate with demo data.
    """
    data = request.get_json() or {}
    provided_secret = data.get('secret', '')
    
    # Get the seed secret from environment
    seed_secret = os.environ.get('SEED_SECRET', '')
    
    # Validate secret
    if not seed_secret:
        return jsonify({
            'error': 'SEED_SECRET not configured. Set it in Vercel environment variables.'
        }), 500
    
    if provided_secret != seed_secret:
        return jsonify({'error': 'Invalid secret.'}), 403
    
    try:
        from app.seed_data import seed_database as do_seed
        summary = do_seed()
        
        return jsonify({
            'message': 'Database seeded successfully!',
            'summary': summary
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Seeding failed: {str(e)}'
        }), 500

