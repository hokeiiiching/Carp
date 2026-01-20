/**
 * API client for CARP backend.
 * 
 * Provides functions for interacting with the Flask REST API.
 * All functions handle JSON serialization and include credentials for session-based auth.
 * 
 * @module api
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling.
 * 
 * Automatically sets JSON headers and includes credentials for session auth.
 * Throws an Error with the server's error message if the request fails.
 * 
 * @param {string} endpoint - API endpoint path (e.g., '/events')
 * @param {Object} [options={}] - Fetch options (method, body, headers, etc.)
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} When the request fails with the server's error message
 * @private
 */
async function apiFetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        credentials: 'include',
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Request failed');
    }

    return data;
}

// --- Event APIs ---

/**
 * Fetch all events with their current registration counts.
 * 
 * @returns {Promise<Array<Object>>} Array of event objects with properties:
 *   - id {number} - Event ID
 *   - title {string} - Event title
 *   - description {string} - Event description
 *   - max_capacity {number} - Maximum attendees allowed
 *   - signups {number} - Current registration count
 *   - date {string} - Date in YYYY-MM-DD format
 *   - time {string} - Time in HH:MM AM/PM format
 *   - venue {string} - Event location
 */
export async function getEvents() {
    return apiFetch('/events');
}

/**
 * Register a participant for an event.
 * 
 * For authenticated caregivers, can specify seniorId to register a specific senior.
 * For guests, requires name and NRIC in guestData.
 * 
 * @param {number} eventId - The ID of the event to register for
 * @param {Object|null} [guestData=null] - Guest registration data (null for logged-in users)
 * @param {string} guestData.name - Guest's full name
 * @param {string} guestData.nric - Guest's NRIC (e.g., 'S1234567A')
 * @param {number|null} [seniorId=null] - For caregivers: specific senior ID to register
 * @returns {Promise<Object>} Response with 'message' on success
 * @throws {Error} When registration fails (event full, already registered, etc.)
 */
export async function registerForEvent(eventId, guestData = null, seniorId = null) {
    const body = guestData || {};
    if (seniorId) {
        body.senior_id = seniorId;
    }
    return apiFetch(`/events/${eventId}/register`, {
        method: 'POST',
        body: JSON.stringify(body),
    });
}

/**
 * Get event IDs that the current user is registered for.
 * 
 * @returns {Promise<Array<number>>} Array of event IDs the user is registered for
 */
export async function getMyRegistrations() {
    return apiFetch('/my-registrations');
}

/**
 * Unregister from an event.
 * 
 * @param {number} eventId - The event ID to unregister from
 * @param {number|null} [seniorId=null] - For caregivers: specific senior ID to unregister
 * @returns {Promise<Object>} Response with 'message' on success
 */
export async function unregisterFromEvent(eventId, seniorId = null) {
    const body = seniorId ? { senior_id: seniorId } : {};
    return apiFetch(`/events/${eventId}/unregister`, {
        method: 'POST',
        body: JSON.stringify(body),
    });
}

// --- Auth APIs ---

/**
 * Get the currently authenticated user's information.
 * 
 * @returns {Promise<Object|null>} User object if authenticated, null otherwise
 *   - id {number} - User ID
 *   - email {string} - User's email address
 *   - role {string} - 'admin' or 'caregiver'
 *   - name {string} - Full name (from linked participant or email)
 *   - nric {string|null} - NRIC if participant is linked
 */
export async function getCurrentUser() {
    return apiFetch('/auth/me');
}

/**
 * Authenticate a user with email and password.
 * 
 * Establishes a session cookie on success.
 * 
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Authenticated user object
 * @throws {Error} When credentials are invalid
 */
export async function login(email, password) {
    return apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
}

/**
 * Log out the current user.
 * 
 * Clears the session cookie.
 * 
 * @returns {Promise<Object>} Response with 'message' on success
 */
export async function logout() {
    return apiFetch('/auth/logout', {
        method: 'POST',
    });
}

/**
 * Register a new user account.
 * 
 * Automatically logs in the user and creates a linked participant profile
 * if NRIC is provided.
 * 
 * @param {Object} userData - Registration data
 * @param {string} userData.email - Email address
 * @param {string} userData.password - Password
 * @param {string} userData.name - Full name
 * @param {string} [userData.nric] - NRIC (required for caregivers)
 * @param {string} [userData.role='caregiver'] - 'admin' or 'caregiver'
 * @param {string} [userData.accessCode] - Required for admin role ('STAFF123')
 * @returns {Promise<Object>} Newly created user object
 * @throws {Error} When email exists or access code is invalid
 */
export async function register(userData) {
    return apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
    });
}

// --- Admin APIs ---

/**
 * Get all registrations (admin only).
 * 
 * Can optionally filter by event ID.
 * 
 * @param {number|null} [eventId=null] - Filter by event ID, or null for all
 * @returns {Promise<Array<Object>>} Array of registration objects:
 *   - id {number} - Registration ID
 *   - event_id {number} - Associated event's ID
 *   - name {string} - Participant's full name
 *   - nric {string} - Participant's NRIC
 *   - source {string} - 'online' or 'walkin'
 *   - timestamp {string} - ISO 8601 timestamp
 * @throws {Error} When user is not admin (403)
 */
export async function getRegistrations(eventId = null) {
    const query = eventId ? `?event_id=${eventId}` : '';
    return apiFetch(`/registrations${query}`);
}

// --- Seniors (Caregiver) APIs ---

/**
 * Get all seniors linked to the current caregiver.
 * 
 * @returns {Promise<Array<Object>>} Array of senior objects:
 *   - id {number} - Participant ID
 *   - nric {string} - Senior's NRIC
 *   - name {string} - Senior's full name
 */
export async function getSeniors() {
    return apiFetch('/seniors');
}

/**
 * Link a new senior to the caregiver's account.
 * 
 * @param {string} nric - Senior's NRIC
 * @param {string} name - Senior's full name
 * @returns {Promise<Object>} Response with message and senior object
 * @throws {Error} When senior is already linked to another caregiver
 */
export async function addSenior(nric, name) {
    return apiFetch('/seniors', {
        method: 'POST',
        body: JSON.stringify({ nric, name }),
    });
}

/**
 * Unlink a senior from the caregiver's account.
 * 
 * The participant record is preserved for event history.
 * 
 * @param {number} seniorId - ID of the senior to unlink
 * @returns {Promise<Object>} Response with message
 * @throws {Error} When senior is not found or not authorized
 */
export async function removeSenior(seniorId) {
    return apiFetch(`/seniors/${seniorId}`, {
        method: 'DELETE',
    });
}
