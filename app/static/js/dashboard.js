// Dashboard JavaScript for Ukombozini Management System

document.addEventListener('DOMContentLoaded', function() {
  // Initialize officer performance chart
  initOfficerPerformanceChart();
  
  // Initialize meeting attendance chart
  initMeetingAttendanceChart();
  
  // Initialize search functionality
  initSearch();
  
  // Initialize modals
  initModals();
});

// Initialize officer performance chart
function initOfficerPerformanceChart() {
  const ctx = document.getElementById('officerPerformanceChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['John Doe', 'Jane Smith', 'Robert Johnson', 'Sarah Williams', 'Michael Brown'],
      datasets: [{
        label: 'Performance Score',
        data: [85, 92, 78, 88, 76],
        backgroundColor: [
          'rgba(52, 152, 219, 0.7)',
          'rgba(46, 204, 113, 0.7)',
          'rgba(155, 89, 182, 0.7)',
          'rgba(52, 152, 219, 0.7)',
          'rgba(46, 204, 113, 0.7)'
        ],
        borderColor: [
          'rgba(52, 152, 219, 1)',
          'rgba(46, 204, 113, 1)',
          'rgba(155, 89, 182, 1)',
          'rgba(52, 152, 219, 1)',
          'rgba(46, 204, 113, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Field Officer Performance (Last 30 Days)',
          font: {
            size: 14
          }
        }
      }
    }
  });
}

// Initialize meeting attendance chart
function initMeetingAttendanceChart() {
  const ctx = document.getElementById('meetingAttendanceChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      datasets: [{
        label: 'Average Attendance',
        data: [78, 82, 85, 90],
        fill: true,
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderColor: 'rgba(52, 152, 219, 1)',
        tension: 0.4,
        pointBackgroundColor: 'rgba(52, 152, 219, 1)',
        pointBorderColor: '#fff',
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            callback: function(value) {
              return value + '%';
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Meeting Attendance Trends (Last Month)',
          font: {
            size: 14
          }
        }
      }
    }
  });
}

// Initialize search functionality
function initSearch() {
  // Officer search
  const officerSearchInput = document.getElementById('officerSearch');
  if (officerSearchInput) {
    officerSearchInput.addEventListener('keyup', function() {
      const searchValue = this.value.toLowerCase();
      const officerRows = document.querySelectorAll('#officerTable tbody tr');
      
      officerRows.forEach(row => {
        const officerName = row.querySelector('td:first-child').textContent.toLowerCase();
        if (officerName.includes(searchValue)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
  
  // Unassigned groups search
  const groupSearchInput = document.getElementById('groupSearch');
  if (groupSearchInput) {
    groupSearchInput.addEventListener('keyup', function() {
      const searchValue = this.value.toLowerCase();
      const groupRows = document.querySelectorAll('#unassignedGroupsTable tbody tr');
      
      groupRows.forEach(row => {
        const groupName = row.querySelector('td:first-child').textContent.toLowerCase();
        if (groupName.includes(searchValue)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
}

// Initialize modals
function initModals() {
  // Add Officer form validation
  const addOfficerForm = document.getElementById('addOfficerForm');
  if (addOfficerForm) {
    addOfficerForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Simple validation
      const nameInput = document.getElementById('officerName');
      const emailInput = document.getElementById('officerEmail');
      const phoneInput = document.getElementById('officerPhone');
      
      if (!nameInput.value.trim()) {
        showFormError(nameInput, 'Name is required');
        return;
      }
      
      if (!emailInput.value.trim() || !isValidEmail(emailInput.value)) {
        showFormError(emailInput, 'Valid email is required');
        return;
      }
      
      if (!phoneInput.value.trim()) {
        showFormError(phoneInput, 'Phone number is required');
        return;
      }
      
      // If validation passes, we'd submit the form or call an API
      // For demonstration, we'll just show a success message and close the modal
      showSuccessAlert('Officer added successfully!');
      
      // Reset form and close modal
      addOfficerForm.reset();
      const modal = bootstrap.Modal.getInstance(document.getElementById('addOfficerModal'));
      modal.hide();
    });
  }
  
  // Assign Group form validation
  const assignGroupForm = document.getElementById('assignGroupForm');
  if (assignGroupForm) {
    assignGroupForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Simple validation
      const officerSelect = document.getElementById('assignOfficer');
      const groupSelect = document.getElementById('assignGroup');
      
      if (officerSelect.value === '') {
        showFormError(officerSelect, 'Please select an officer');
        return;
      }
      
      if (groupSelect.value === '') {
        showFormError(groupSelect, 'Please select a group');
        return;
      }
      
      // If validation passes, we'd submit the form or call an API
      showSuccessAlert('Group assigned successfully!');
      
      // Reset form and close modal
      assignGroupForm.reset();
      const modal = bootstrap.Modal.getInstance(document.getElementById('assignGroupModal'));
      modal.hide();
    });
  }
  
  // Schedule Rotation form validation
  const scheduleRotationForm = document.getElementById('scheduleRotationForm');
  if (scheduleRotationForm) {
    scheduleRotationForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Simple validation
      const fromOfficerSelect = document.getElementById('fromOfficer');
      const toOfficerSelect = document.getElementById('toOfficer');
      const groupSelect = document.getElementById('rotationGroup');
      const dateInput = document.getElementById('rotationDate');
      
      if (fromOfficerSelect.value === '') {
        showFormError(fromOfficerSelect, 'Please select current officer');
        return;
      }
      
      if (toOfficerSelect.value === '') {
        showFormError(toOfficerSelect, 'Please select new officer');
        return;
      }
      
      if (fromOfficerSelect.value === toOfficerSelect.value) {
        showFormError(toOfficerSelect, 'Current and new officer cannot be the same');
        return;
      }
      
      if (groupSelect.value === '') {
        showFormError(groupSelect, 'Please select a group');
        return;
      }
      
      if (!dateInput.value) {
        showFormError(dateInput, 'Please select a date');
        return;
      }
      
      // If validation passes, we'd submit the form or call an API
      showSuccessAlert('Rotation scheduled successfully!');
      
      // Reset form and close modal
      scheduleRotationForm.reset();
      const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleRotationModal'));
      modal.hide();
    });
  }
}

// Helper function to show form validation errors
function showFormError(inputElement, message) {
  // Remove any existing error messages
  const existingFeedback = inputElement.nextElementSibling;
  if (existingFeedback && existingFeedback.classList.contains('invalid-feedback')) {
    existingFeedback.remove();
  }
  
  // Add invalid class to input
  inputElement.classList.add('is-invalid');
  
  // Create and append error message
  const feedback = document.createElement('div');
  feedback.classList.add('invalid-feedback');
  feedback.textContent = message;
  inputElement.parentNode.appendChild(feedback);
  
  // Focus the input
  inputElement.focus();
  
  // Remove invalid state when input changes
  inputElement.addEventListener('input', function() {
    this.classList.remove('is-invalid');
    const feedback = this.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.remove();
    }
  }, { once: true });
}

// Helper function to validate email
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Helper function to show success alert
function showSuccessAlert(message) {
  // Create alert element
  const alertDiv = document.createElement('div');
  alertDiv.classList.add('alert', 'alert-success', 'alert-dismissible', 'fade', 'show', 'fixed-top', 'mx-auto', 'mt-3');
  alertDiv.style.maxWidth = '500px';
  alertDiv.style.zIndex = '9999';
  alertDiv.role = 'alert';
  
  // Add message and close button
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Append to body
  document.body.appendChild(alertDiv);
  
  // Auto dismiss after 3 seconds
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alertDiv);
    bsAlert.close();
  }, 3000);
} 