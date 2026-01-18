"""Tests for database models."""
import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Participant, Event, Registration


class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(email='test@example.com', role='caregiver')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'test@example.com'
            assert user.role == 'caregiver'
    
    def test_password_hashing(self, app):
        """Test password is properly hashed."""
        with app.app_context():
            user = User(email='test@example.com')
            user.set_password('mypassword')
            
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')
    
    def test_email_uniqueness(self, app):
        """Test that duplicate emails are rejected."""
        with app.app_context():
            user1 = User(email='same@example.com', role='caregiver')
            user1.set_password('pass1')
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(email='same@example.com', role='admin')
            user2.set_password('pass2')
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()


class TestParticipantModel:
    """Tests for Participant model."""
    
    def test_create_participant(self, app):
        """Test participant creation."""
        with app.app_context():
            participant = Participant(nric='S1234567A', full_name='John Doe')
            db.session.add(participant)
            db.session.commit()
            
            assert participant.id is not None
            assert participant.nric == 'S1234567A'
    
    def test_nric_uniqueness(self, app):
        """Test that duplicate NRICs are rejected."""
        with app.app_context():
            p1 = Participant(nric='S1234567A', full_name='Person One')
            db.session.add(p1)
            db.session.commit()
            
            p2 = Participant(nric='S1234567A', full_name='Person Two')
            db.session.add(p2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()


class TestRegistrationModel:
    """Tests for Registration model."""
    
    def test_unique_constraint(self, app, sample_event):
        """Test that duplicate registrations are rejected at DB level."""
        from datetime import datetime, timedelta
        
        with app.app_context():
            # Create participant
            participant = Participant(nric='S9999999Z', full_name='Test Person')
            db.session.add(participant)
            db.session.commit()
            
            # First registration succeeds
            reg1 = Registration(event_id=sample_event, participant_id=participant.id)
            db.session.add(reg1)
            db.session.commit()
            
            # Duplicate registration fails
            reg2 = Registration(event_id=sample_event, participant_id=participant.id)
            db.session.add(reg2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
