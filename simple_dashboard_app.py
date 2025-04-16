"""
Ukombozini Management System - Standalone Dashboard Application

This is a standalone Flask application that provides a simplified dashboard
for the Ukombozini Management System. It includes:

1. A modern, responsive dashboard interface built with Bootstrap 5
2. Mock API endpoints for dashboard data
3. Dynamic content loading using JavaScript

To run the application:
    python simple_dashboard_app.py

The application will be available at http://localhost:5001
"""

from flask import Flask, render_template, jsonify, redirect, url_for
import os
import random
import socket
from datetime import datetime, timedelta

app = Flask(__name__)

# Sample data for the dashboard
users = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "member"},
    {"id": 3, "name": "Michael Johnson", "email": "michael@example.com", "role": "field_officer"}
]

# Dashboard routes
@app.route('/')
def dashboard():
    return render_template('standalone_dashboard.html', active_page='dashboard')

@app.route('/members')
def members():
    return render_template('standalone_dashboard.html', active_page='members', 
                          title='Members', message='Members page is under construction')

@app.route('/loans')
def loans():
    return render_template('standalone_dashboard.html', active_page='loans',
                          title='Loans', message='Loans page is under construction')

@app.route('/savings')
def savings():
    return render_template('standalone_dashboard.html', active_page='savings',
                          title='Savings', message='Savings page is under construction')

@app.route('/meetings')
def meetings():
    return render_template('standalone_dashboard.html', active_page='meetings',
                          title='Meetings', message='Meetings page is under construction')

@app.route('/reports')
def reports():
    return render_template('standalone_dashboard.html', active_page='reports',
                          title='Reports', message='Reports page is under construction')

@app.route('/settings')
def settings():
    return render_template('standalone_dashboard.html', active_page='settings',
                          title='Settings', message='Settings page is under construction')

# API endpoint for dashboard overview data
@app.route('/api/dashboard/overview')
def dashboard_overview():
    return jsonify({
        'total_members': 245,
        'total_groups': 32,
        'total_loans': 78,
        'total_savings': 156320,
        'today_meetings': 5,
        'upcoming_meetings': 12
    })

# API endpoint for recent activities
@app.route('/api/dashboard/recent-activities')
def recent_activities():
    activities = [
        {'type': 'Loan', 'description': 'John Doe approved loan #1234', 'time': '5 min ago'},
        {'type': 'Saving', 'description': 'Mary Smith deposited $500', 'time': '30 min ago'},
        {'type': 'Meeting', 'description': 'Group A meeting scheduled', 'time': '1 hour ago'},
        {'type': 'Payment', 'description': 'Late payment notification sent', 'time': '3 hours ago'},
        {'type': 'Member', 'description': 'New member registered', 'time': 'Yesterday'}
    ]
    return jsonify(activities)

# API endpoint for upcoming meetings
@app.route('/api/dashboard/upcoming-meetings')
def upcoming_meetings():
    meetings = [
        {'group': 'Group A Weekly Meeting', 'location': 'Community Center', 'time': 'Today 14:00'},
        {'group': 'Group B Weekly Meeting', 'location': 'Town Hall', 'time': 'Today 16:30'},
        {'group': 'Executive Committee', 'location': 'Main Office', 'time': 'Tomorrow 09:00'},
        {'group': 'Loan Review Committee', 'location': 'Conference Room', 'time': 'Tomorrow 13:00'},
        {'group': 'Group C Weekly Meeting', 'location': 'Community Center', 'time': 'Wed 10:00'}
    ]
    return jsonify(meetings)

# API endpoint for current user data (mock authentication)
@app.route('/api/user/current')
def current_user():
    # In a real app, this would be determined by authentication
    return jsonify(users[0])  # Return first user as the current user

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    return None

if __name__ == '__main__':
    # Try to use port 5001, but fall back to other ports if necessary
    port = int(os.environ.get('PORT', 5001))
    
    if is_port_in_use(port):
        port = find_available_port(5001)
        if port is None:
            print("Could not find an available port. Please free up port 5001 or specify a different port with the PORT environment variable.")
            exit(1)
    
    print(f"\nDashboard application started! Access it at http://localhost:{port}\n")
    try:
        app.run(host='localhost', port=port, debug=True)
    except Exception as e:
        print(f"Error starting the application: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure no other application is using port", port)
        print("2. Try running with a different port: PORT=5002 python simple_dashboard_app.py")
        print("3. Check your firewall settings to ensure Flask is allowed to accept connections") 