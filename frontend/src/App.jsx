import { useState, useEffect } from 'react';
import {
  User, Users, ClipboardList, LogOut, CheckCircle,
  AlertCircle, Calendar, Clock, MapPin, X,
  ArrowRight, Heart, Shield, Mail, Lock, Fingerprint
} from 'lucide-react';
import * as api from './api';
import './index.css';

export default function App() {
  // --- State ---
  const [view, setView] = useState('catalog'); // catalog, dashboard, auth
  const [authMode, setAuthMode] = useState('login'); // login, register
  const [userRole, setUserRole] = useState('caregiver');
  const [currentUser, setCurrentUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [registrations, setRegistrations] = useState([]);
  const [flash, setFlash] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  // Form states
  const [guestName, setGuestName] = useState('');
  const [guestNRIC, setGuestNRIC] = useState('');

  // --- Effects ---
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [eventsData, userData] = await Promise.all([
        api.getEvents(),
        api.getCurrentUser()
      ]);
      setEvents(eventsData);
      setCurrentUser(userData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRegistrations = async () => {
    try {
      const data = await api.getRegistrations();
      setRegistrations(data);
    } catch (err) {
      showFlash('Failed to load registrations', 'danger');
    }
  };

  // --- Helpers ---
  const showFlash = (message, type = 'success') => {
    setFlash({ message, type });
    setTimeout(() => setFlash(null), 4000);
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
      if (authMode === 'login') {
        const user = await api.login(
          formData.get('email'),
          formData.get('password')
        );
        setCurrentUser(user);
        setView('catalog');
        showFlash(`Welcome back, ${user.name || user.email}!`);
      } else {
        const user = await api.register({
          email: formData.get('email'),
          password: formData.get('password'),
          name: formData.get('name'),
          nric: formData.get('nric'),
          role: userRole,
          accessCode: formData.get('accessCode')
        });
        setCurrentUser(user);
        setView('catalog');
        showFlash('Account created successfully!');
      }
      // Refresh events after auth
      const eventsData = await api.getEvents();
      setEvents(eventsData);
    } catch (err) {
      showFlash(err.message, 'danger');
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setCurrentUser(null);
      setView('catalog');
      showFlash('Logged out successfully');
    } catch (err) {
      showFlash(err.message, 'danger');
    }
  };

  const handleRegister = async () => {
    const event = selectedEvent;

    try {
      const guestData = currentUser ? null : {
        name: guestName,
        nric: guestNRIC
      };

      await api.registerForEvent(event.id, guestData);

      // Refresh events
      const eventsData = await api.getEvents();
      setEvents(eventsData);

      showFlash(`Successfully registered for ${event.title}!`);
      setSelectedEvent(null);
      setGuestName('');
      setGuestNRIC('');
    } catch (err) {
      showFlash(err.message, 'danger');
    }
  };

  const openDashboard = async () => {
    setView('dashboard');
    await loadRegistrations();
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="nav">
        <div className="nav-logo" onClick={() => setView('catalog')}>
          <div className="nav-logo-icon">
            <ClipboardList size={20} />
          </div>
          <h1>ActivityPortal</h1>
        </div>

        <div className="nav-links">
          <button
            onClick={() => setView('catalog')}
            className={`nav-link ${view === 'catalog' ? 'active' : ''}`}
          >
            Catalog
          </button>

          {currentUser?.role === 'admin' && (
            <button
              onClick={openDashboard}
              className={`nav-link ${view === 'dashboard' ? 'active' : ''}`}
            >
              Admin Roster
            </button>
          )}

          {!currentUser ? (
            <button onClick={() => setView('auth')} className="nav-btn">
              Login / Sign Up
            </button>
          ) : (
            <div className="nav-user">
              <div className="nav-user-info">
                <p className="nav-user-role">{currentUser.role}</p>
                <p className="nav-user-name">{currentUser.name || currentUser.email}</p>
              </div>
              <button onClick={handleLogout} className="nav-logout">
                <LogOut size={20} />
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Flash Message */}
      {flash && (
        <div className={`flash ${flash.type}`}>
          {flash.type === 'danger' ? <AlertCircle size={20} /> : <CheckCircle size={20} />}
          <span>{flash.message}</span>
        </div>
      )}

      {/* Auth View */}
      {view === 'auth' && (
        <div className="auth-container">
          <div className="auth-header">
            <h2>{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
            <p>Join our community activities today.</p>
          </div>

          <div className="auth-tabs">
            <button
              onClick={() => setAuthMode('login')}
              className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
            >
              Login
            </button>
            <button
              onClick={() => setAuthMode('register')}
              className={`auth-tab ${authMode === 'register' ? 'active' : ''}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleAuth}>
            {authMode === 'register' && (
              <>
                <label style={{ display: 'block', fontSize: '0.625rem', fontWeight: 900, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
                  I am a...
                </label>
                <div className="role-selector">
                  {[
                    { id: 'caregiver', icon: Heart, label: 'Caregiver' },
                    { id: 'admin', icon: Shield, label: 'Staff' }
                  ].map(role => (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() => setUserRole(role.id)}
                      className={`role-btn ${userRole === role.id ? 'active' : ''}`}
                    >
                      <role.icon size={24} />
                      <span>{role.label}</span>
                    </button>
                  ))}
                </div>
              </>
            )}

            <div className="form-grid cols-2">
              {authMode === 'register' && (
                <div className="col-span-2 form-input-wrapper">
                  <User className="form-input-icon" size={18} />
                  <input name="name" type="text" placeholder="Full Name" className="form-input" required />
                </div>
              )}

              <div className={authMode === 'login' ? 'col-span-2' : ''}>
                <div className="form-input-wrapper">
                  <Mail className="form-input-icon" size={18} />
                  <input name="email" type="email" placeholder="Email Address" className="form-input" required />
                </div>
              </div>

              <div className={authMode === 'login' ? 'col-span-2' : ''}>
                <div className="form-input-wrapper">
                  <Lock className="form-input-icon" size={18} />
                  <input name="password" type="password" placeholder="Password" className="form-input" required />
                </div>
              </div>

              {authMode === 'register' && userRole !== 'admin' && (
                <>
                  <div className="form-input-wrapper">
                    <Fingerprint className="form-input-icon" size={18} />
                    <input name="nric" type="text" placeholder="NRIC (S1234567A)" className="form-input uppercase" required />
                  </div>
                </>
              )}

              {authMode === 'register' && userRole === 'admin' && (
                <div className="col-span-2" style={{ marginTop: '0.5rem' }}>
                  <div className="form-input-wrapper">
                    <Shield className="form-input-icon" size={18} style={{ color: '#fbbf24' }} />
                    <input
                      name="accessCode"
                      type="text"
                      placeholder="Enter Staff Invitation Code"
                      className="form-input"
                      style={{ backgroundColor: 'rgba(251, 191, 36, 0.1)', border: '2px solid rgba(251, 191, 36, 0.2)' }}
                      required
                    />
                  </div>
                  <p className="access-code-note">
                    Staff roles require an authorized code from administration.
                  </p>
                </div>
              )}
            </div>

            <button type="submit" className="form-btn primary" style={{ marginTop: '1.5rem' }}>
              {authMode === 'login' ? 'Sign In' : 'Create My Account'} <ArrowRight size={20} style={{ display: 'inline', marginLeft: '0.5rem', verticalAlign: 'middle' }} />
            </button>
          </form>
        </div>
      )}

      {/* Registration Modal */}
      {selectedEvent && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Registration</h3>
              <button onClick={() => setSelectedEvent(null)} className="modal-close">
                <X size={24} />
              </button>
            </div>

            <div className="modal-content">
              <div className="modal-event-info">
                <h4 className="modal-event-title">{selectedEvent.title}</h4>
                <div className="modal-event-meta">
                  <span><Calendar size={14} /> {selectedEvent.date}</span>
                  <span><Clock size={14} /> {selectedEvent.time}</span>
                  <span><MapPin size={14} /> {selectedEvent.venue}</span>
                </div>
              </div>

              {!currentUser ? (
                <div>
                  <div className="guest-warning">
                    <AlertCircle size={20} />
                    <p>
                      Guests must provide details. <button onClick={() => { setSelectedEvent(null); setView('auth'); }}>Login</button> to auto-fill for future events.
                    </p>
                  </div>
                  <div className="form-group">
                    <input
                      value={guestName}
                      onChange={e => setGuestName(e.target.value)}
                      type="text"
                      placeholder="Participant Name"
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <input
                      value={guestNRIC}
                      onChange={e => setGuestNRIC(e.target.value)}
                      type="text"
                      placeholder="NRIC (e.g. S1234567A)"
                      className="form-input uppercase"
                    />
                  </div>
                  <button onClick={handleRegister} className="form-btn dark">
                    Confirm Guest Registration
                  </button>
                </div>
              ) : (
                <div style={{ textAlign: 'center' }}>
                  <p style={{ color: '#475569', fontWeight: 500, marginBottom: '1.5rem' }}>
                    You are registering as <b>{currentUser.name || currentUser.email}</b>
                  </p>
                  <button onClick={handleRegister} className="form-btn primary">
                    Complete Registration
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="main">
        {view === 'catalog' && (
          <div>
            <header className="header">
              <div>
                <h2>Active Catalog</h2>
                <p>Discover upcoming workshops, sessions, and social gatherings.</p>
              </div>
            </header>

            {events.length === 0 ? (
              <div className="empty-state">
                <h3>No events available</h3>
                <p>Check back later for new activities!</p>
              </div>
            ) : (
              <div className="events-grid">
                {events.map(event => {
                  const isFull = event.signups >= event.max_capacity;
                  const spotsLeft = event.max_capacity - event.signups;
                  return (
                    <div key={event.id} className={`event-card ${isFull ? 'full' : ''}`}>
                      <div className="event-header">
                        <h3 className="event-title">{event.title}</h3>
                        <span className={`event-badge ${isFull ? 'full' : 'available'}`}>
                          {isFull ? 'Full' : `${spotsLeft} Left`}
                        </span>
                      </div>

                      <div className="event-meta">
                        <div className="event-meta-item">
                          <Calendar size={14} /> {event.date}
                        </div>
                        <div className="event-meta-item">
                          <MapPin size={14} /> {event.venue}
                        </div>
                      </div>

                      <p className="event-description">{event.description}</p>

                      <button
                        disabled={isFull}
                        onClick={() => setSelectedEvent(event)}
                        className={`event-btn ${isFull ? 'disabled' : 'primary'}`}
                      >
                        {isFull ? 'Registration Full' : 'Register Now'}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {view === 'dashboard' && currentUser?.role === 'admin' && (
          <div>
            <header className="dashboard-header">
              <div>
                <h2>Consolidated Roster</h2>
                <p>Admin Panel • Central Attendance Management</p>
              </div>
            </header>

            <div className="table-container">
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Participant Details</th>
                      <th>Selected Activity</th>
                      <th style={{ textAlign: 'center' }}>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registrations.length === 0 ? (
                      <tr>
                        <td colSpan="3" style={{ textAlign: 'center', color: '#94a3b8' }}>
                          No registrations yet
                        </td>
                      </tr>
                    ) : (
                      registrations.map(reg => (
                        <tr key={reg.id}>
                          <td>
                            <div className="table-name">{reg.name}</div>
                            <div className="table-nric">{reg.nric}</div>
                          </td>
                          <td>
                            <div className="table-event">
                              {events.find(e => e.id === reg.event_id)?.title || `Event #${reg.event_id}`}
                            </div>
                            <div className="table-date">
                              {events.find(e => e.id === reg.event_id)?.date}
                            </div>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <span className={`table-source ${reg.source === 'walkin' ? 'guest' : 'user'}`}>
                              {reg.source}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
