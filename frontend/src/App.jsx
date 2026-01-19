/**
 * CARP Frontend - Main Application Component
 * 
 * A single-page application for the Community Activity Registration Portal.
 * Provides event browsing, user authentication, and admin functionality.
 * 
 * @fileoverview Main App component managing all application state and views.
 * 
 * Views:
 *   - 'catalog': Public event listing and registration
 *   - 'auth': Login and account registration forms
 *   - 'dashboard': Admin-only registration management
 * 
 * State Structure:
 *   - view: Current active view ('catalog' | 'auth' | 'dashboard')
 *   - authMode: Auth form mode ('login' | 'register')
 *   - userRole: Selected role during registration ('caregiver' | 'admin')
 *   - currentUser: Authenticated user object or null
 *   - events: Array of available events from backend
 *   - registrations: Array of registrations (admin only)
 *   - flash: Flash message object { message, type } or null
 *   - selectedEvent: Event being registered for (shows modal) or null
 *   - loading: Initial data loading state
 * 
 * @module App
 */
import { useState, useEffect } from 'react';
import {
  User, Users, ClipboardList, LogOut, CheckCircle,
  AlertCircle, Calendar, Clock, MapPin, X,
  ArrowRight, Heart, Shield, Mail, Lock, Fingerprint, Trash2, UserPlus
} from 'lucide-react';
import * as api from './api';
import './index.css';

/**
 * Main application component.
 * 
 * Handles all routing, authentication, and event registration logic.
 * Uses session-based authentication via cookies for API requests.
 * 
 * @returns {JSX.Element} The rendered application
 */
export default function App() {
  // --- State ---
  // View management
  const [view, setView] = useState('catalog'); // catalog, dashboard, auth
  const [authMode, setAuthMode] = useState('login'); // login, register
  const [userRole, setUserRole] = useState('caregiver');

  // Data state
  const [currentUser, setCurrentUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [registrations, setRegistrations] = useState([]);

  // UI state
  const [flash, setFlash] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  // Guest registration form state
  const [guestName, setGuestName] = useState('');
  const [guestNRIC, setGuestNRIC] = useState('');

  // Seniors management state (for caregivers)
  const [seniors, setSeniors] = useState([]);
  const [selectedSeniorId, setSelectedSeniorId] = useState(null);
  const [newSeniorName, setNewSeniorName] = useState('');
  const [newSeniorNRIC, setNewSeniorNRIC] = useState('');

  // Admin filter state
  const [selectedEventFilter, setSelectedEventFilter] = useState(null);

  // --- Effects ---
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load seniors when caregiver logs in, or self for seniors
  useEffect(() => {
    if (currentUser?.role === 'caregiver' || currentUser?.role === 'senior') {
      loadSeniors();
    }
  }, [currentUser]);

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

  const loadRegistrations = async (eventId = null) => {
    try {
      const data = await api.getRegistrations(eventId);
      setRegistrations(data);
    } catch (err) {
      showFlash('Failed to load registrations', 'danger');
    }
  };

  const handleEventFilterChange = async (eventId) => {
    const newFilter = eventId ? Number(eventId) : null;
    setSelectedEventFilter(newFilter);
    await loadRegistrations(newFilter);
  };

  const loadSeniors = async () => {
    try {
      const data = await api.getSeniors();
      setSeniors(data);
      // Auto-select first senior if available
      if (data.length > 0 && !selectedSeniorId) {
        setSelectedSeniorId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load seniors:', err);
    }
  };

  const openSeniors = async () => {
    setView('seniors');
    await loadSeniors();
  };

  const handleAddSenior = async () => {
    if (!newSeniorName.trim() || !newSeniorNRIC.trim()) {
      showFlash('Name and NRIC are required.', 'danger');
      return;
    }
    try {
      const result = await api.addSenior(newSeniorNRIC, newSeniorName);
      showFlash(result.message);
      setNewSeniorName('');
      setNewSeniorNRIC('');
      await loadSeniors();
    } catch (err) {
      showFlash(err.message, 'danger');
    }
  };

  const handleRemoveSenior = async (seniorId) => {
    try {
      const result = await api.removeSenior(seniorId);
      showFlash(result.message);
      await loadSeniors();
    } catch (err) {
      showFlash(err.message, 'danger');
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

      // For caregivers, pass the selected senior ID
      const seniorId = currentUser ? selectedSeniorId : null;
      await api.registerForEvent(event.id, guestData, seniorId);

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
          <div>
            <h1>CARP</h1>
            <span className="nav-logo-tagline">Community Activity Registration</span>
          </div>
        </div>

        <div className="nav-links">
          <button
            onClick={() => setView('catalog')}
            className={`nav-link ${view === 'catalog' ? 'active' : ''}`}
          >
            Catalog
          </button>

          {currentUser?.role === 'caregiver' && (
            <button
              onClick={openSeniors}
              className={`nav-link ${view === 'seniors' ? 'active' : ''}`}
            >
              My Seniors
            </button>
          )}

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
                    { id: 'senior', icon: Users, label: 'Senior' },
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

              {authMode === 'register' && (userRole === 'caregiver' || userRole === 'senior') && (
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
              ) : currentUser?.role === 'senior' ? (
                // Seniors register themselves directly
                <div>
                  {seniors.length === 0 ? (
                    <div className="guest-warning">
                      <AlertCircle size={20} />
                      <p>
                        Your profile is not set up. Please contact support.
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className="modal-event-info" style={{ background: '#f0fdf4', marginBottom: '1.5rem' }}>
                        <p style={{ fontWeight: 700, color: '#16a34a', marginBottom: '0.25rem' }}>Registering as:</p>
                        <p style={{ fontWeight: 900, color: '#15803d', fontSize: '1.125rem' }}>{seniors[0]?.name}</p>
                        <p style={{ fontWeight: 600, color: '#22c55e', fontFamily: 'monospace', fontSize: '0.75rem' }}>{seniors[0]?.nric}</p>
                      </div>
                      <button onClick={handleRegister} className="form-btn primary">
                        Complete Registration
                      </button>
                    </>
                  )}
                </div>
              ) : (
                // Caregivers select from their linked seniors
                <div>
                  {seniors.length === 0 ? (
                    <div className="guest-warning">
                      <AlertCircle size={20} />
                      <p>
                        No seniors linked to your account. <button onClick={() => { setSelectedEvent(null); openSeniors(); }}>Add a senior</button> first.
                      </p>
                    </div>
                  ) : (
                    <>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#64748b', marginBottom: '0.5rem' }}>
                        Select Senior to Register
                      </label>
                      <select
                        value={selectedSeniorId || ''}
                        onChange={e => setSelectedSeniorId(Number(e.target.value))}
                        className="form-input"
                        style={{ marginBottom: '1.5rem' }}
                      >
                        {seniors.map(s => (
                          <option key={s.id} value={s.id}>
                            {s.name} ({s.nric})
                          </option>
                        ))}
                      </select>
                      <button onClick={handleRegister} className="form-btn primary">
                        Complete Registration
                      </button>
                    </>
                  )}
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
            {/* Hero Section - Only show for guests or first visit */}
            {!currentUser && (
              <section className="hero">
                <div className="hero-content">
                  <div className="hero-badge">Community Activity Registration Platform</div>
                  <h1 className="hero-title">
                    Welcome to <span className="hero-highlight">CARP</span>
                  </h1>
                  <p className="hero-subtitle">
                    Your one-stop platform for discovering and registering for community activities,
                    workshops, and social gatherings designed for seniors and their caregivers.
                  </p>

                  <div className="hero-features">
                    <div className="hero-feature">
                      <div className="hero-feature-icon">
                        <Calendar size={20} />
                      </div>
                      <div>
                        <h4>Easy Registration</h4>
                        <p>Browse and sign up for events in just a few clicks</p>
                      </div>
                    </div>
                    <div className="hero-feature">
                      <div className="hero-feature-icon">
                        <Users size={20} />
                      </div>
                      <div>
                        <h4>Family Friendly</h4>
                        <p>Caregivers can register their loved ones remotely</p>
                      </div>
                    </div>
                    <div className="hero-feature">
                      <div className="hero-feature-icon">
                        <Heart size={20} />
                      </div>
                      <div>
                        <h4>Community First</h4>
                        <p>Stay connected with meaningful activities</p>
                      </div>
                    </div>
                  </div>

                  <div className="hero-actions">
                    <button onClick={() => setView('auth')} className="hero-btn primary">
                      Get Started <ArrowRight size={18} />
                    </button>
                    <button onClick={() => document.getElementById('events-section')?.scrollIntoView({ behavior: 'smooth' })} className="hero-btn secondary">
                      Browse Events
                    </button>
                  </div>
                </div>
                <div className="hero-stats">
                  <div className="hero-stat">
                    <span className="hero-stat-number">{events.length}</span>
                    <span className="hero-stat-label">Active Events</span>
                  </div>
                  <div className="hero-stat">
                    <span className="hero-stat-number">{events.reduce((sum, e) => sum + e.signups, 0)}</span>
                    <span className="hero-stat-label">Registrations</span>
                  </div>
                  <div className="hero-stat">
                    <span className="hero-stat-number">{events.filter(e => e.signups < e.max_capacity).length}</span>
                    <span className="hero-stat-label">Open Spots</span>
                  </div>
                </div>
              </section>
            )}

            <header id="events-section" className="header">
              <div>
                <h2>{currentUser ? 'Active Catalog' : 'Upcoming Events'}</h2>
                <p>Discover workshops, sessions, and social gatherings in your community.</p>
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
              <div className="filter-container">
                <label htmlFor="eventFilter" style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginRight: '0.5rem' }}>
                  Filter by Event:
                </label>
                <select
                  id="eventFilter"
                  value={selectedEventFilter || ''}
                  onChange={(e) => handleEventFilterChange(e.target.value)}
                  className="form-input"
                  style={{ width: 'auto', minWidth: '200px' }}
                >
                  <option value="">All Events</option>
                  {events.map(event => (
                    <option key={event.id} value={event.id}>
                      {event.title} ({event.date})
                    </option>
                  ))}
                </select>
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

        {view === 'seniors' && currentUser?.role === 'caregiver' && (
          <div>
            <header className="header">
              <div>
                <h2>My Seniors</h2>
                <p>Manage seniors linked to your account for event registration.</p>
              </div>
            </header>

            {/* Add Senior Form */}
            <div className="seniors-form">
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', color: '#1e293b' }}>
                <UserPlus size={18} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                Link a Senior
              </h3>
              <div className="seniors-form-row">
                <input
                  type="text"
                  value={newSeniorName}
                  onChange={e => setNewSeniorName(e.target.value)}
                  placeholder="Senior's Full Name"
                  className="form-input"
                />
                <input
                  type="text"
                  value={newSeniorNRIC}
                  onChange={e => setNewSeniorNRIC(e.target.value)}
                  placeholder="NRIC (e.g. S1234567A)"
                  className="form-input uppercase"
                />
                <button onClick={handleAddSenior} className="form-btn primary">
                  Add Senior
                </button>
              </div>
            </div>

            {/* Seniors List */}
            {seniors.length === 0 ? (
              <div className="empty-state">
                <Users size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <h3>No seniors linked yet</h3>
                <p>Add a senior above to register them for events.</p>
              </div>
            ) : (
              <div className="seniors-grid">
                {seniors.map(senior => (
                  <div key={senior.id} className="senior-card">
                    <div className="senior-info">
                      <div className="senior-name">{senior.name}</div>
                      <div className="senior-nric">{senior.nric}</div>
                    </div>
                    <button
                      onClick={() => handleRemoveSenior(senior.id)}
                      className="senior-remove"
                      title="Remove senior"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
