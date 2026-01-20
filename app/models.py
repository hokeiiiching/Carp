"""Database models for CARP application."""
from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Index
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    User model for authentication.
    
    Represents caregivers and staff who can log in to the system.
    """
    __tablename__ = 'user'
    
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(256), nullable=False)  # scrypt hashes are ~162 chars
    role: str = db.Column(db.String(20), default='caregiver', nullable=False)
    display_name: Optional[str] = db.Column(db.String(100), nullable=True)  # User's own name
    
    # Relationship to participants (one user can have multiple dependents)
    participants = db.relationship('Participant', back_populates='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Load user by ID for Flask-Login."""
    return db.session.get(User, int(user_id))


class Participant(db.Model):
    """
    Participant model representing a real human attending events.
    
    Key Concept: A participant might be linked to a User (Caregiver) 
    OR exist independently (Shadow Profile/Walk-in).
    """
    __tablename__ = 'participant'
    
    id: int = db.Column(db.Integer, primary_key=True)
    nric: str = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name: str = db.Column(db.String(100), nullable=False)
    user_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='participants')
    registrations = db.relationship('Registration', back_populates='participant', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<Participant {self.full_name} ({self.nric})>'


class Event(db.Model):
    """
    Event model representing an activity that participants can register for.
    """
    __tablename__ = 'event'
    
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(100), nullable=False)
    description: Optional[str] = db.Column(db.Text, nullable=True)
    max_capacity: int = db.Column(db.Integer, default=20, nullable=False)
    start_time: datetime = db.Column(db.DateTime, nullable=False)
    
    # Relationship to registrations
    registrations = db.relationship('Registration', back_populates='event', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<Event {self.title}>'


class Registration(db.Model):
    """
    Registration model representing the transaction of a participant registering for an event.
    
    Constraint: UniqueConstraint prevents physical double-booking at the DB level.
    """
    __tablename__ = 'registration'
    
    id: int = db.Column(db.Integer, primary_key=True)
    event_id: int = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    participant_id: int = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    timestamp: datetime = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    source: str = db.Column(db.String(20), default='online', nullable=False)  # 'online' or 'walkin'
    
    # Relationships
    event = db.relationship('Event', back_populates='registrations')
    participant = db.relationship('Participant', back_populates='registrations')
    
    # Critical constraint: prevent duplicate registrations
    __table_args__ = (
        UniqueConstraint('event_id', 'participant_id', name='uq_participant_event'),
    )
    
    def __repr__(self) -> str:
        return f'<Registration Event:{self.event_id} Participant:{self.participant_id}>'
