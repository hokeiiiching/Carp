/**
 * API client for CARP backend
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling
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

export async function getEvents() {
    return apiFetch('/events');
}

export async function registerForEvent(eventId, guestData = null) {
    return apiFetch(`/events/${eventId}/register`, {
        method: 'POST',
        body: JSON.stringify(guestData || {}),
    });
}

// --- Auth APIs ---

export async function getCurrentUser() {
    return apiFetch('/auth/me');
}

export async function login(email, password) {
    return apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
}

export async function logout() {
    return apiFetch('/auth/logout', {
        method: 'POST',
    });
}

export async function register(userData) {
    return apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
    });
}

// --- Admin APIs ---

export async function getRegistrations(eventId = null) {
    const query = eventId ? `?event_id=${eventId}` : '';
    return apiFetch(`/registrations${query}`);
}
