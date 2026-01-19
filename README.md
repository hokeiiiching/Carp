# CARP - Community Activity Registration Portal

A centralized activity registration system built on the **"Single Source of Truth"** principle. Eliminate data duplication via strict database constraints while minimizing user friction through intelligent profile resolution.

![Event Catalog](https://img.shields.io/badge/Flask-2.3+-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple) ![React](https://img.shields.io/badge/React-18-61dafb)

## Features

- **Smart Participant Resolution** — NRIC-based identity anchoring with automatic profile lookup
- **Capacity Management** — Real-time capacity tracking with visual progress bars
- **Duplicate Prevention** — Database-level constraints prevent double-booking
- **Role-Based Access** — Admin dashboard for staff, simplified registration for guests
- **Shadow Profiles** — Walk-in participants without requiring account creation
- **Dual Interface** — Traditional Jinja2 templates + modern React SPA

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Node.js 18+ (for React frontend)

### Backend Installation

#### Windows

```powershell
# Clone the repository
git clone <repository-url>
cd Carp

# Install Python dependencies
py -m pip install -r requirements.txt

# Initialize the database with sample data
py -m flask main seed

# Run the development server
py run.py
```

#### macOS / Linux

```bash
# Clone the repository
git clone <repository-url>
cd Carp

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize the database with sample data
flask main seed

# Run the development server
python run.py
```

The backend will be available at **http://127.0.0.1:5000**

### Frontend Installation (React)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Run the development server
npm run dev
```

The React frontend will be available at **http://localhost:5173**

The frontend dev server automatically proxies API requests to the Flask backend.

---

## Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@carp.local` | `admin123` |
| Caregiver | `caregiver@carp.local` | `caregiver123` |

---

## CLI Commands

```bash
# Seed database with sample data (idempotent)
flask main seed

# Reset database and clear all data
flask main reset

# Run tests
pytest tests/ -v
```

---

## Project Structure

```
/Carp
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── models.py        # SQLAlchemy models (User, Participant, Event, Registration)
│   ├── services.py      # Business logic (Smart Upsert, Safe Registration)
│   ├── routes.py        # Route definitions + CLI commands
│   ├── api.py           # REST API endpoints for React frontend
│   └── templates/
│       ├── base.html       # Bootstrap 5.3 master layout
│       ├── index.html      # Public event catalog
│       ├── dashboard.html  # Admin registration view
│       ├── login.html      # Authentication form
│       └── macros.html     # Reusable Jinja2 components
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── api.js          # API client functions
│   │   └── index.css       # Styles and design system
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite build configuration
├── tests/
│   ├── conftest.py      # Pytest fixtures
│   ├── test_models.py   # Model constraint tests
│   ├── test_services.py # Business logic tests
│   └── test_routes.py   # Route/auth tests
├── config.py            # Dev/Prod configuration
├── run.py               # Application entry point
└── requirements.txt     # Python dependencies
```

---

## REST API Reference

All API endpoints are prefixed with `/api`.

### Events

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/events` | List all events with registration counts | Public |
| POST | `/api/events/:id/register` | Register for an event | Public |

**Register Request Body (guest):**
```json
{
  "nric": "S1234567A",
  "name": "John Doe"
}
```

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user info (null if not logged in) |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/logout` | Logout current session |
| POST | `/api/auth/register` | Create new user account |

**Login Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Register Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "nric": "S1234567A",
  "role": "caregiver",
  "accessCode": "STAFF123"  
}
```

### Admin

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/registrations` | List all registrations | Admin |
| GET | `/api/registrations?event_id=1` | Filter by event | Admin |

---

## Configuration

Set environment variables to customize behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_CONFIG` | `development` | Config profile (`development` or `production`) |
| `SECRET_KEY` | `dev-secret-key...` | Session encryption key (change in production) |
| `DATABASE_URL` | `sqlite:///carp.db` | Database connection string |

---

## Development

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_services.py -v

# Run with coverage
pytest tests/ --cov=app
```

### Database Reset

If you need to start fresh:

```bash
# Windows
py -m flask main reset
py -m flask main seed

# macOS/Linux
flask main reset
flask main seed
```

### Architecture Notes

**Backend:**
- Flask app factory pattern in `app/__init__.py`
- Service layer (`services.py`) separates business logic from routes
- SQLAlchemy models with database-level constraints
- Flask-Login for session management
- CORS enabled for React frontend development

**Frontend:**
- Vite-based React SPA
- Vanilla CSS with modern design system
- API client with automatic error handling
- Session-based auth via cookies

---

## License

MIT License - See LICENSE file for details.
