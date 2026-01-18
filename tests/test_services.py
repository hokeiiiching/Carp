"""Tests for service layer."""
import pytest
from app import db
from app.models import Participant, Event, Registration
from app.services import (
    get_or_create_participant,
    register_for_event,
    get_event_registration_count
)


class TestGetOrCreateParticipant:
    """Tests for the Smart Upsert pattern."""
    
    def test_creates_new_participant(self, app):
        """Test creating a new participant."""
        with app.app_context():
            participant = get_or_create_participant('S1234567A', 'John Doe')
            
            assert participant.id is not None
            assert participant.nric == 'S1234567A'
            assert participant.full_name == 'John Doe'
    
    def test_returns_existing_participant(self, app):
        """Test that existing participant is returned without duplication."""
        with app.app_context():
            p1 = get_or_create_participant('S1234567A', 'John Doe')
            p2 = get_or_create_participant('S1234567A', 'John Different Name')
            
            assert p1.id == p2.id
            # Original name is preserved
            assert p2.full_name == 'John Doe'
    
    def test_nric_sanitization(self, app):
        """Test that NRIC is trimmed and uppercased."""
        with app.app_context():
            p1 = get_or_create_participant('  s1234567a  ', 'Test User')
            
            assert p1.nric == 'S1234567A'
            
            # Should match the same normalized NRIC
            p2 = get_or_create_participant('S1234567A', 'Another Name')
            assert p1.id == p2.id


class TestRegisterForEvent:
    """Tests for the Safe Registration Pipeline."""
    
    def test_successful_registration(self, app, sample_event):
        """Test a successful registration."""
        with app.app_context():
            participant = get_or_create_participant('S1111111A', 'Test Person')
            success, message = register_for_event(sample_event, participant.id)
            
            assert success is True
            assert 'successful' in message.lower()
    
    def test_capacity_enforcement(self, app, sample_event):
        """Test that capacity is enforced."""
        with app.app_context():
            # Register up to capacity (5)
            for i in range(5):
                p = get_or_create_participant(f'S000000{i}A', f'Person {i}')
                success, _ = register_for_event(sample_event, p.id)
                assert success is True
            
            # Next registration should fail
            p_extra = get_or_create_participant('S9999999Z', 'Extra Person')
            success, message = register_for_event(sample_event, p_extra.id)
            
            assert success is False
            assert 'fully booked' in message.lower()
    
    def test_duplicate_prevention(self, app, sample_event):
        """Test that duplicate registrations are prevented."""
        with app.app_context():
            participant = get_or_create_participant('S2222222B', 'Duplicate Test')
            
            # First registration succeeds
            success1, _ = register_for_event(sample_event, participant.id)
            assert success1 is True
            
            # Second registration fails
            success2, message = register_for_event(sample_event, participant.id)
            assert success2 is False
            assert 'already registered' in message.lower()
    
    def test_registration_count(self, app, sample_event):
        """Test registration count helper."""
        with app.app_context():
            assert get_event_registration_count(sample_event) == 0
            
            p = get_or_create_participant('S3333333C', 'Counter Test')
            register_for_event(sample_event, p.id)
            
            assert get_event_registration_count(sample_event) == 1
