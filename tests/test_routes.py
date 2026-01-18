"""Tests for routes."""
import pytest


class TestPublicRoutes:
    """Tests for public-facing routes."""
    
    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Upcoming Events' in response.data
    
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data


class TestAuthentication:
    """Tests for authentication routes."""
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        assert b'Invalid email or password' in response.data
    
    def test_login_success(self, client, app, admin_user):
        """Test successful login."""
        response = client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'Logged in successfully' in response.data
    
    def test_logout(self, client, app, admin_user):
        """Test logout."""
        # Login first
        client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert b'logged out' in response.data


class TestRegistration:
    """Tests for registration route."""
    
    def test_guest_registration_success(self, client, sample_event):
        """Test guest registration with NRIC and name."""
        response = client.post(f'/register/{sample_event}', data={
            'nric': 'S7777777G',
            'name': 'Guest User'
        }, follow_redirects=True)
        
        assert b'Registration successful' in response.data
    
    def test_guest_registration_missing_fields(self, client, sample_event):
        """Test guest registration fails without required fields."""
        response = client.post(f'/register/{sample_event}', data={
            'nric': '',
            'name': ''
        }, follow_redirects=True)
        
        assert b'required' in response.data


class TestDashboard:
    """Tests for admin dashboard."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects to login."""
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Login' in response.data
    
    def test_dashboard_requires_admin(self, client, app):
        """Test dashboard requires admin role."""
        from app import db
        from app.models import User
        
        with app.app_context():
            user = User(email='caregiver@test.com', role='caregiver')
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()
        
        client.post('/login', data={
            'email': 'caregiver@test.com',
            'password': 'pass123'
        })
        
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Access denied' in response.data
    
    def test_dashboard_admin_access(self, client, admin_user):
        """Test admin can access dashboard."""
        client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Staff Dashboard' in response.data
