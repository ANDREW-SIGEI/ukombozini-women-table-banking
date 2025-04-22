from flask import Flask, render_template, jsonify, url_for, flash, redirect, g, make_response
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='app/templates', static_folder='static')
app.config['SECRET_KEY'] = 'temporarysecretkey'

@app.route('/')
def home():
    return "Ukombozini Management System is running!"

@app.route('/api/test')
def test_api():
    return jsonify({"status": "success", "message": "API is working"})

@app.route('/member/dashboard')
def member_dashboard_page():
    """Render the member dashboard page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Member Dashboard - Ukombozini Management System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .stat-card {
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                transition: transform 0.3s ease;
                height: 100%;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .chart-container {
                height: 300px;
                margin-bottom: 20px;
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">UKOMBOZINI</a>
            </div>
        </nav>
        
        <div class="container-fluid px-4 pt-4">
            <h1 class="h3 mb-2">Member Dashboard</h1>
            <p class="mb-4">Welcome to your personal dashboard. Monitor your loans, savings, and upcoming meetings.</p>

            <!-- Member Stats Cards -->
            <div class="row mb-4">
                <div class="col-md-3 mb-4">
                    <div class="card border-primary stat-card">
                        <div class="card-body">
                            <h5 class="card-title">Current Loans</h5>
                            <h3 id="current-loans-count">0</h3>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card border-success stat-card">
                        <div class="card-body">
                            <h5 class="card-title">Savings Balance</h5>
                            <h3 id="savings-balance">KSh 0</h3>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card border-info stat-card">
                        <div class="card-body">
                            <h5 class="card-title">Next Payment</h5>
                            <h3 id="next-payment">N/A</h3>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card border-warning stat-card">
                        <div class="card-body">
                            <h5 class="card-title">Upcoming Meetings</h5>
                            <h3 id="upcoming-meetings">0</h3>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Content Row -->
            <div class="row">
                <!-- Loans Overview -->
                <div class="col-lg-6 mb-4">
                    <div class="card shadow mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="m-0">My Loans</h5>
                        </div>
                        <div class="card-body">
                            <div id="no-loans" class="text-center py-4 d-none">
                                <p class="text-muted mb-0">You don't have any active loans.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-bordered" id="loans-table">
                                    <thead>
                                        <tr>
                                            <th>Loan Type</th>
                                            <th>Amount</th>
                                            <th>Balance</th>
                                            <th>Due Date</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="loans-body">
                                        <!-- Loans will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Savings Activity -->
                <div class="col-lg-6 mb-4">
                    <div class="card shadow mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="m-0">Savings Activity</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="savingsChart"></canvas>
                            </div>
                            <div class="table-responsive mt-3">
                                <table class="table table-bordered" id="savings-table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Transaction</th>
                                            <th>Amount</th>
                                            <th>Balance</th>
                                        </tr>
                                    </thead>
                                    <tbody id="savings-body">
                                        <!-- Savings transactions will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Content Row -->
            <div class="row">
                <!-- Upcoming Meetings -->
                <div class="col-lg-6 mb-4">
                    <div class="card shadow mb-4">
                        <div class="card-header">
                            <h5 class="m-0">Upcoming Meetings</h5>
                        </div>
                        <div class="card-body">
                            <div id="no-meetings" class="text-center py-4 d-none">
                                <p class="text-muted mb-0">No upcoming meetings scheduled.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-bordered" id="meetings-table">
                                    <thead>
                                        <tr>
                                            <th>Group</th>
                                            <th>Date</th>
                                            <th>Time</th>
                                            <th>Location</th>
                                        </tr>
                                    </thead>
                                    <tbody id="meetings-body">
                                        <!-- Upcoming meetings will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Payment Schedule -->
                <div class="col-lg-6 mb-4">
                    <div class="card shadow mb-4">
                        <div class="card-header">
                            <h5 class="m-0">Payment Schedule</h5>
                        </div>
                        <div class="card-body">
                            <div id="no-payments" class="text-center py-4 d-none">
                                <p class="text-muted mb-0">No upcoming payments scheduled.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-bordered" id="payments-table">
                                    <thead>
                                        <tr>
                                            <th>Due Date</th>
                                            <th>Loan</th>
                                            <th>Amount</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="payments-body">
                                        <!-- Payment schedule will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Fetch member dashboard data when page loads
            document.addEventListener('DOMContentLoaded', function() {
                fetchDashboardData();
            });

            function fetchDashboardData() {
                fetch('/api/dashboard/member')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                });
            }

            function updateDashboard(data) {
                // Update stats cards
                document.getElementById('current-loans-count').textContent = data.loans.count;
                document.getElementById('savings-balance').textContent = 'KSh ' + new Intl.NumberFormat().format(data.savings.balance);
                document.getElementById('upcoming-meetings').textContent = data.meetings.count;
                
                if (data.next_payment) {
                    document.getElementById('next-payment').textContent = new Date(data.next_payment.due_date).toLocaleDateString();
                }

                // Populate loans table
                const loansBody = document.getElementById('loans-body');
                loansBody.innerHTML = '';
                
                if (data.loans.count === 0) {
                    document.getElementById('no-loans').classList.remove('d-none');
                    document.getElementById('loans-table').classList.add('d-none');
                } else {
                    document.getElementById('no-loans').classList.add('d-none');
                    document.getElementById('loans-table').classList.remove('d-none');
                    
                    data.loans.data.forEach(loan => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${loan.type}</td>
                            <td>KSh ${new Intl.NumberFormat().format(loan.amount)}</td>
                            <td>KSh ${new Intl.NumberFormat().format(loan.balance)}</td>
                            <td>${loan.due_date ? new Date(loan.due_date).toLocaleDateString() : 'N/A'}</td>
                            <td><span class="badge bg-${loan.status === 'active' ? 'success' : 'secondary'}">${loan.status}</span></td>
                        `;
                        loansBody.appendChild(row);
                    });
                }

                // Populate savings transactions
                const savingsBody = document.getElementById('savings-body');
                savingsBody.innerHTML = '';
                
                data.savings.recent_transactions.forEach(transaction => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(transaction.date).toLocaleDateString()}</td>
                        <td>${transaction.type}</td>
                        <td>KSh ${new Intl.NumberFormat().format(transaction.amount)}</td>
                        <td>KSh ${new Intl.NumberFormat().format(transaction.balance)}</td>
                    `;
                    savingsBody.appendChild(row);
                });

                // Populate meetings table
                const meetingsBody = document.getElementById('meetings-body');
                meetingsBody.innerHTML = '';
                
                if (data.meetings.count === 0) {
                    document.getElementById('no-meetings').classList.remove('d-none');
                    document.getElementById('meetings-table').classList.add('d-none');
                } else {
                    document.getElementById('no-meetings').classList.add('d-none');
                    document.getElementById('meetings-table').classList.remove('d-none');
                    
                    data.meetings.data.forEach(meeting => {
                        const meetingDate = new Date(meeting.date);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${meeting.group}</td>
                            <td>${meetingDate.toLocaleDateString()}</td>
                            <td>${meeting.time}</td>
                            <td>${meeting.location}</td>
                        `;
                        meetingsBody.appendChild(row);
                    });
                }

                // Populate payment schedule
                const paymentsBody = document.getElementById('payments-body');
                paymentsBody.innerHTML = '';
                
                if (data.payment_schedule.length === 0) {
                    document.getElementById('no-payments').classList.remove('d-none');
                    document.getElementById('payments-table').classList.add('d-none');
                } else {
                    document.getElementById('no-payments').classList.add('d-none');
                    document.getElementById('payments-table').classList.remove('d-none');
                    
                    data.payment_schedule.forEach(payment => {
                        const paymentDate = new Date(payment.due_date);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${paymentDate.toLocaleDateString()}</td>
                            <td>${payment.loan_name}</td>
                            <td>KSh ${new Intl.NumberFormat().format(payment.amount)}</td>
                            <td><span class="badge bg-warning">${payment.status}</span></td>
                        `;
                        paymentsBody.appendChild(row);
                    });
                }

                // Initialize Savings Chart
                const chartData = {
                    labels: data.savings.chart_data.map(item => item.month),
                    data: data.savings.chart_data.map(item => item.amount)
                };
                initializeSavingsChart(chartData);
            }

            function initializeSavingsChart(chartData) {
                const ctx = document.getElementById('savingsChart').getContext('2d');
                
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: chartData.labels,
                        datasets: [{
                            label: 'Savings Balance',
                            data: chartData.data,
                            backgroundColor: 'rgba(40, 167, 69, 0.2)',
                            borderColor: 'rgba(40, 167, 69, 1)',
                            borderWidth: 2,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return 'KSh ' + value.toLocaleString();
                                    }
                                }
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return 'KSh ' + context.parsed.y.toLocaleString();
                                    }
                                }
                            }
                        }
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/dashboard/member')
def member_dashboard():
    today = datetime.utcnow().date()
    
    # Create sample data similar to what our real API would return
    response = {
        'user': {
            'id': 1,
            'name': "John Doe",
            'phone': "1234567890",
            'email': "john.doe@example.com"
        },
        'loans': {
            'count': 2,
            'data': [
                {
                    'id': 1,
                    'type': 'Personal Loan',
                    'amount': 5000.0,
                    'balance': 3500.0,
                    'due_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'status': 'active'
                },
                {
                    'id': 2,
                    'type': 'Business Loan',
                    'amount': 10000.0,
                    'balance': 8000.0,
                    'due_date': (today + timedelta(days=60)).strftime('%Y-%m-%d'),
                    'status': 'active'
                }
            ]
        },
        'savings': {
            'balance': 12500.0,
            'accounts': [
                {
                    'id': 1,
                    'type': 'Primary Savings',
                    'balance': 12500.0
                }
            ],
            'chart_data': [
                {'month': 'Jan 2025', 'amount': 2000.0},
                {'month': 'Feb 2025', 'amount': 2500.0},
                {'month': 'Mar 2025', 'amount': 3000.0},
                {'month': 'Apr 2025', 'amount': 2000.0},
                {'month': 'May 2025', 'amount': 1500.0},
                {'month': 'Jun 2025', 'amount': 1500.0}
            ],
            'recent_transactions': [
                {
                    'date': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'type': 'deposit',
                    'amount': 1000.0,
                    'balance': 12500.0
                },
                {
                    'date': (today - timedelta(days=3)).strftime('%Y-%m-%d'),
                    'type': 'withdrawal',
                    'amount': 500.0,
                    'balance': 11500.0
                },
                {
                    'date': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
                    'type': 'deposit',
                    'amount': 2000.0,
                    'balance': 12000.0
                }
            ]
        },
        'meetings': {
            'count': 2,
            'data': [
                {
                    'id': 1,
                    'group': 'Village Savings Group',
                    'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'time': '10:00',
                    'location': 'Community Center'
                },
                {
                    'id': 2,
                    'group': 'Business Development Group',
                    'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                    'time': '14:00',
                    'location': 'Town Hall'
                }
            ]
        },
        'payment_schedule': [
            {
                'loan_id': 1,
                'loan_name': 'Personal Loan',
                'due_date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'amount': 500.0,
                'status': 'upcoming'
            },
            {
                'loan_id': 2,
                'loan_name': 'Business Loan',
                'due_date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),
                'amount': 800.0,
                'status': 'upcoming'
            }
        ],
        'next_payment': {
            'loan_id': 1,
            'loan_name': 'Personal Loan',
            'due_date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'amount': 500.0,
            'status': 'upcoming'
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True) 