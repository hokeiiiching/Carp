"""Business logic services for CARP application."""
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Participant, Event, Registration


def get_or_create_participant(
    nric: str, 
    name: str, 
    user_id: Optional[int] = None
) -> Participant:
    """
    Smart Upsert: Get existing participant by NRIC or create new one.
    
    Args:
        nric: National Registration Identity Card number (unique identifier)
        name: Full name of the participant
        user_id: Optional User ID to link this participant to a caregiver
    
    Returns:
        Participant object (existing or newly created)
    """
    # Sanitize NRIC: trim whitespace and uppercase
    nric_clean = nric.strip().upper()
    
    # Query for existing participant
    participant = db.session.execute(
        db.select(Participant).filter_by(nric=nric_clean)
    ).scalar_one_or_none()
    
    if not participant:
        # Create new participant
        participant = Participant(
            nric=nric_clean, 
            full_name=name, 
            user_id=user_id
        )
        db.session.add(participant)
        db.session.commit()
    
    return participant


def get_event_registration_count(event_id: int) -> int:
    """
    Get the current registration count for an event.
    
    Args:
        event_id: The event ID to count registrations for
    
    Returns:
        Number of registrations for the event
    """
    count = db.session.scalar(
        db.select(func.count(Registration.id)).filter_by(event_id=event_id)
    )
    return count or 0


def register_for_event(
    event_id: int, 
    participant_id: int,
    source: str = 'online'
) -> tuple[bool, str]:
    """
    Safe Registration Pipeline: Register a participant for an event.
    
    Performs capacity check and handles duplicate prevention via DB constraint.
    
    Args:
        event_id: The event to register for
        participant_id: The participant to register
        source: Registration source ('online' or 'walkin')
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # 1. Capacity Check
    event = db.session.get(Event, event_id)
    if not event:
        return False, "Event not found."
    
    current_count = get_event_registration_count(event_id)
    
    if current_count >= event.max_capacity:
        return False, "Event is fully booked."
    
    # 2. Attempt Registration
    try:
        reg = Registration(
            event_id=event_id, 
            participant_id=participant_id,
            source=source
        )
        db.session.add(reg)
        db.session.commit()
        return True, "Registration successful."
    except IntegrityError:
        db.session.rollback()
        return False, "Participant is already registered for this event."


def get_all_events_with_counts() -> list[dict]:
    """
    Get all events with their current registration counts.
    
    Returns:
        List of dicts containing event info and registration count
    """
    events = db.session.execute(db.select(Event)).scalars().all()
    result = []
    
    for event in events:
        count = get_event_registration_count(event.id)
        result.append({
            'event': event,
            'count': count,
            'is_full': count >= event.max_capacity
        })
    
    return result


def get_all_registrations(event_id: Optional[int] = None) -> list[Registration]:
    """
    Get all registrations, optionally filtered by event.
    
    Args:
        event_id: Optional event ID to filter by
    
    Returns:
        List of Registration objects
    """
    query = db.select(Registration).order_by(Registration.timestamp.desc())
    
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    return db.session.execute(query).scalars().all()


def get_participant_for_user(user_id: int) -> Optional[Participant]:
    """
    Get the primary participant associated with a user.
    
    For MVP, returns the first participant linked to the user.
    
    Args:
        user_id: The user ID to find participant for
    
    Returns:
        Participant object or None
    """
    return db.session.execute(
        db.select(Participant).filter_by(user_id=user_id)
    ).scalar_one_or_none()
