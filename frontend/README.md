# CARP Frontend

React-based frontend for the Community Activity Registration Portal. Built with Vite for fast development.

## Overview

This frontend provides a modern, responsive interface for:
- **Event Catalog** — Browse and register for community activities
- **User Authentication** — Login/register as caregiver or staff
- **Admin Dashboard** — View and manage all registrations (admin only)

## Tech Stack

- **React 18** — UI library
- **Vite** — Build tool and dev server
- **Lucide React** — Icon library
- **Vanilla CSS** — Custom styling with modern design system

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on `http://127.0.0.1:5000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at **http://localhost:5173**

### Development

The Vite dev server proxies API requests to the Flask backend (configured in `vite.config.js`).

```bash
# Run with hot module replacement
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx         # Main application component
│   ├── api.js          # API client functions
│   ├── index.css       # Global styles and design system
│   ├── main.jsx        # React entry point
│   └── assets/         # Static assets
├── public/             # Public static files
├── index.html          # HTML entry point
├── vite.config.js      # Vite configuration
├── eslint.config.js    # ESLint configuration
└── package.json        # Dependencies and scripts
```

## Architecture

### State Management

The app uses React's built-in `useState` and `useEffect` hooks for state management. Key state includes:

| State | Type | Description |
|-------|------|-------------|
| `view` | string | Current view: 'catalog', 'dashboard', 'auth' |
| `currentUser` | object/null | Authenticated user info |
| `events` | array | List of available events |
| `registrations` | array | Admin-only: all registrations |
| `selectedEvent` | object/null | Event being registered for (modal) |

### API Layer

All backend communication goes through `api.js`, which provides:
- Automatic JSON serialization
- Session-based authentication (credentials: 'include')
- Consistent error handling

### Styling

The design system in `index.css` features:
- Modern glassmorphism effects
- Smooth animations and transitions
- Fully responsive layout
- Dark navigation with clean content areas

## Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@carp.local` | `admin123` |
| Caregiver | `caregiver@carp.local` | `caregiver123` |

## API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events` | List all events |
| POST | `/api/events/:id/register` | Register for event |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/auth/register` | Create account |
| GET | `/api/registrations` | List registrations (admin) |
