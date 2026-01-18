"""Pytest configuration and fixtures."""
import pytest
from app import create_app, db
from app.models import User, Participant, Event


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_event(app):
    """Create a sample event."""
    from datetime import datetime, timedelta
    
    with app.app_context():
        event = Event(
            title='Test Event',
            description='A test event',
            max_capacity=5,
            start_time=datetime.now() + timedelta(days=1)
        )
        db.session.add(event)
        db.session.commit()
        return event.id


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        user = User(email='admin@test.com', role='admin')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id
