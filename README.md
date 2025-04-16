# Ukombozini Management System

![](https://github.com/ANDREW-SIGEI/ukombozini-women-table-banking/actions/workflows/1-create-a-branch.yml/badge.svg)
![](https://github.com/ANDREW-SIGEI/ukombozini-women-table-banking/actions/workflows/2-commit-a-file.yml/badge.svg)
![](https://github.com/ANDREW-SIGEI/ukombozini-women-table-banking/actions/workflows/3-open-a-pull-request.yml/badge.svg)
![](https://github.com/ANDREW-SIGEI/ukombozini-women-table-banking/actions/workflows/4-merge-your-pull-request.yml/badge.svg)

A comprehensive management system for microfinance and savings groups.

## Features

- Member management
- Group management and tracking
- Loan disbursement and repayment
- Savings collection and tracking
- Meeting scheduling and management
- Field officer rotation and assignment
- Reporting and analytics

## Standalone Dashboard

The system includes a standalone dashboard that provides a quick overview of key metrics and activities. This dashboard can be accessed without the full system setup.

### Running the Standalone Dashboard

To run the standalone dashboard:

```bash
python simple_dashboard_app.py
```

The dashboard will be available at http://localhost:5001

### Dashboard Features

The standalone dashboard provides:

- Overview metrics (members, loans, savings, meetings)
- Recent activities feed
- Upcoming meetings display
- Responsive design for desktop and mobile use

## Main Application

To run the full application:

```bash
python run.py
```

The main application will be available at http://localhost:5000

## Requirements

All requirements are specified in the requirements.txt file. Install them with:

```bash
pip install -r requirements.txt
```

## Project Structure

- `app/` - Main application modules
  - `models/` - Database models
  - `routes/` - API and web routes
  - `templates/` - HTML templates
  - `static/` - Static assets (CSS, JS, images)
- `migrations/` - Database migration files
- `tests/` - Test cases
- `simple_dashboard_app.py` - Standalone dashboard application
- `run.py` - Main application entry point

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/ukombozini
JWT_SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
flask run
```

## API Documentation

### Authentication
- POST /auth/register - Register a new user
- POST /auth/login - Login and get JWT token
- POST /auth/refresh - Refresh JWT token

### Users
- GET /users - Get all users (admin only)
- GET /users/<id> - Get user details
- PUT /users/<id> - Update user details
- DELETE /users/<id> - Delete user (admin only)

### Groups
- GET /groups - Get all groups
- POST /groups - Create a new group
- GET /groups/<id> - Get group details
- PUT /groups/<id> - Update group details
- DELETE /groups/<id> - Delete group
- POST /groups/<id>/members - Add members to group
- DELETE /groups/<id>/members/<user_id> - Remove member from group

### Meetings
- GET /meetings - Get all meetings with optional filters
- POST /meetings - Create a new meeting
- GET /meetings/<id> - Get meeting details
- PUT /meetings/<id> - Update meeting details
- POST /meetings/<id>/cancel - Cancel a meeting
- POST /meetings/<id>/attendance - Record meeting attendance
- GET /meetings/stats - Get meeting statistics
- GET /meetings/upcoming - Get upcoming meetings for current user

## Development

To run tests:
```bash
flask test
```

To run the development server with debug mode:
```bash
flask run --debug
```

## License

This project is licensed under the MIT License.
