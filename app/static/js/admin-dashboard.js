// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initAdminDashboard();
    
    // Set up event listeners for interaction
    setupEventListeners();
    
    // Create charts
    createPerformanceChart();
});

/**
 * Initialize the admin dashboard by fetching and displaying data
 */
function initAdminDashboard() {
    fetchDashboardData()
        .then(updateDashboardUI)
        .catch(error => {
            console.error('Error initializing dashboard:', error);
            showErrorMessage('Failed to load dashboard data. Please refresh the page or try again later.');
        });
}

/**
 * Fetch dashboard data from the API
 */
function fetchDashboardData() {
    return fetch('/api/dashboard/admin', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${getAuthToken()}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    });
}

/**
 * Update the dashboard UI with the fetched data
 */
function updateDashboardUI(data) {
    // Update overview cards
    document.getElementById('field-officers-count').textContent = data.field_officers.length;
    document.getElementById('total-groups').textContent = data.total_groups;
    document.getElementById('meetings-count').textContent = data.meetings_this_week;
    document.getElementById('unassigned-groups').textContent = data.unassigned_groups.length;
    
    // Update field officers table
    updateFieldOfficersTable(data.field_officers);
    
    // Update upcoming rotations table
    updateRotationsTable(data.upcoming_rotations);
    
    // Update unassigned groups table
    updateUnassignedGroupsTable(data.unassigned_groups);
    
    // Update recent activity logs
    updateActivityLogs(data.recent_activities);
    
    // Update the performance chart with new data
    updatePerformanceChart(data.field_officers);
}

/**
 * Update the field officers table
 */
function updateFieldOfficersTable(officers) {
    const tableBody = document.getElementById('field-officers-tbody');
    tableBody.innerHTML = '';
    
    if (officers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" class="text-center">No field officers found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    officers.forEach(officer => {
        const row = document.createElement('tr');
        
        // Format the assigned groups
        const assignedGroupsCount = officer.assigned_groups.length;
        const assignedGroupsText = assignedGroupsCount > 0 
            ? `${assignedGroupsCount} groups` 
            : 'No groups assigned';
        
        // Format the last rotation date
        const lastRotation = officer.last_rotation 
            ? new Date(officer.last_rotation).toLocaleDateString() 
            : 'Never rotated';
        
        // Format upcoming rotation
        const upcomingRotation = officer.upcoming_rotation 
            ? `${new Date(officer.upcoming_rotation.date).toLocaleDateString()} - ${officer.upcoming_rotation.current_group} to ${officer.upcoming_rotation.new_group}` 
            : 'No rotation scheduled';
        
        row.innerHTML = `
            <td>${officer.name}</td>
            <td>${assignedGroupsText}</td>
            <td>
                <span class="badge ${getPerformanceBadgeClass(officer.performance_score)}">
                    ${officer.performance_score.toFixed(1)}
                </span>
            </td>
            <td>${lastRotation}</td>
            <td>${upcomingRotation}</td>
            <td>
                <button class="btn btn-sm btn-primary view-officer" data-id="${officer.id}">
                    View
                </button>
                <button class="btn btn-sm btn-info rotate-officer" data-id="${officer.id}">
                    Rotate
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update the rotations table
 */
function updateRotationsTable(rotations) {
    const tableBody = document.getElementById('rotations-tbody');
    tableBody.innerHTML = '';
    
    if (rotations.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No upcoming rotations scheduled</td>';
        tableBody.appendChild(row);
        return;
    }
    
    rotations.forEach(rotation => {
        const row = document.createElement('tr');
        const rotationDate = new Date(rotation.rotation_date).toLocaleDateString();
        
        row.innerHTML = `
            <td>${rotation.officer_name}</td>
            <td>${rotation.current_group}</td>
            <td>${rotation.new_group}</td>
            <td>${rotationDate}</td>
            <td>
                <button class="btn btn-sm btn-danger cancel-rotation" data-id="${rotation.id}">
                    Cancel
                </button>
                <button class="btn btn-sm btn-warning reschedule-rotation" data-id="${rotation.id}">
                    Reschedule
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update the unassigned groups table
 */
function updateUnassignedGroupsTable(groups) {
    const tableBody = document.getElementById('unassigned-groups-tbody');
    tableBody.innerHTML = '';
    
    if (groups.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No unassigned groups</td>';
        tableBody.appendChild(row);
        return;
    }
    
    groups.forEach(group => {
        const row = document.createElement('tr');
        const createdAt = group.created_at 
            ? new Date(group.created_at).toLocaleDateString() 
            : 'Unknown';
        
        row.innerHTML = `
            <td>${group.name}</td>
            <td>${group.location}</td>
            <td>${group.member_count}</td>
            <td>
                <button class="btn btn-sm btn-success assign-group" data-id="${group.id}">
                    Assign
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update the activity logs section
 */
function updateActivityLogs(activities) {
    const logsContainer = document.getElementById('activity-logs');
    logsContainer.innerHTML = '';
    
    if (activities.length === 0) {
        logsContainer.innerHTML = '<p class="text-center">No recent activity</p>';
        return;
    }
    
    activities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item mb-2 p-2 border-bottom';
        
        const timestamp = new Date(activity.timestamp).toLocaleString();
        
        activityItem.innerHTML = `
            <div class="d-flex justify-content-between">
                <span class="badge ${getActivityBadgeClass(activity.type)}">${activity.type}</span>
                <small class="text-muted">${timestamp}</small>
            </div>
            <p class="mb-1">${activity.description}</p>
            <small class="text-muted">By: ${activity.user}</small>
        `;
        
        logsContainer.appendChild(activityItem);
    });
}

/**
 * Create the performance comparison chart
 */
function createPerformanceChart() {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    
    window.performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // Will be filled with officer names
            datasets: [{
                label: 'Performance Score',
                data: [], // Will be filled with performance scores
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Performance Score (0-10)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Field Officer Performance Comparison'
                },
                legend: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Update the performance chart with new data
 */
function updatePerformanceChart(officers) {
    const labels = officers.map(officer => officer.name);
    const scores = officers.map(officer => officer.performance_score);
    const backgroundColor = scores.map(score => getPerformanceColor(score));
    const borderColor = scores.map(score => getBorderColor(score));
    
    window.performanceChart.data.labels = labels;
    window.performanceChart.data.datasets[0].data = scores;
    window.performanceChart.data.datasets[0].backgroundColor = backgroundColor;
    window.performanceChart.data.datasets[0].borderColor = borderColor;
    
    window.performanceChart.update();
}

/**
 * Set up event listeners for dashboard interactions
 */
function setupEventListeners() {
    // Field Officer Actions
    document.addEventListener('click', function(event) {
        // View officer details
        if (event.target.classList.contains('view-officer')) {
            const officerId = event.target.getAttribute('data-id');
            viewOfficerDetails(officerId);
        }
        
        // Rotate officer
        if (event.target.classList.contains('rotate-officer')) {
            const officerId = event.target.getAttribute('data-id');
            showRotationModal(officerId);
        }
        
        // Cancel rotation
        if (event.target.classList.contains('cancel-rotation')) {
            const rotationId = event.target.getAttribute('data-id');
            confirmCancelRotation(rotationId);
        }
        
        // Reschedule rotation
        if (event.target.classList.contains('reschedule-rotation')) {
            const rotationId = event.target.getAttribute('data-id');
            showRescheduleModal(rotationId);
        }
        
        // Assign group
        if (event.target.classList.contains('assign-group')) {
            const groupId = event.target.getAttribute('data-id');
            showAssignGroupModal(groupId);
        }
    });
    
    // Manual refresh button
    const refreshButton = document.getElementById('refresh-dashboard');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            initAdminDashboard();
        });
    }
}

// Helper Functions

/**
 * Get auth token from local storage
 */
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

/**
 * Show an error message on the dashboard
 */
function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const dashboardContainer = document.querySelector('.dashboard-container');
    dashboardContainer.prepend(alertDiv);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Get performance badge class based on score
 */
function getPerformanceBadgeClass(score) {
    if (score >= 8.5) return 'bg-success';
    if (score >= 7) return 'bg-info';
    if (score >= 5.5) return 'bg-warning';
    return 'bg-danger';
}

/**
 * Get activity badge class based on activity type
 */
function getActivityBadgeClass(type) {
    switch (type) {
        case 'rotation':
            return 'bg-primary';
        case 'assignment':
            return 'bg-success';
        case 'meeting':
            return 'bg-info';
        default:
            return 'bg-secondary';
    }
}

/**
 * Get performance color for chart based on score
 */
function getPerformanceColor(score) {
    if (score >= 8.5) return 'rgba(40, 167, 69, 0.6)'; // success
    if (score >= 7) return 'rgba(23, 162, 184, 0.6)';  // info
    if (score >= 5.5) return 'rgba(255, 193, 7, 0.6)'; // warning
    return 'rgba(220, 53, 69, 0.6)'; // danger
}

/**
 * Get border color for chart based on score
 */
function getBorderColor(score) {
    if (score >= 8.5) return 'rgb(40, 167, 69)'; // success
    if (score >= 7) return 'rgb(23, 162, 184)';  // info
    if (score >= 5.5) return 'rgb(255, 193, 7)'; // warning
    return 'rgb(220, 53, 69)'; // danger
}

// Action Functions (Placeholders for future implementation)

function viewOfficerDetails(officerId) {
    window.location.href = `/field-officers/${officerId}`;
}

function showRotationModal(officerId) {
    // Implementation to be added later
    console.log('Show rotation modal for officer ID:', officerId);
}

function confirmCancelRotation(rotationId) {
    if (confirm('Are you sure you want to cancel this rotation?')) {
        cancelRotation(rotationId);
    }
}

function cancelRotation(rotationId) {
    // Implementation to be added later
    console.log('Cancel rotation ID:', rotationId);
}

function showRescheduleModal(rotationId) {
    // Implementation to be added later
    console.log('Show reschedule modal for rotation ID:', rotationId);
}

function showAssignGroupModal(groupId) {
    // Implementation to be added later
    console.log('Show assign group modal for group ID:', groupId);
} 