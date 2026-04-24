// Manage Features JavaScript

// Get CSRF token
function getCsrfToken() {
    let token = getCookie('csrftoken');
    if (!token) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            token = metaTag.getAttribute('content');
        }
    }
    if (!token) {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) {
            token = input.value;
        }
    }
    return token;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add Inclusion
async function addInclusion() {
    const name = document.getElementById('newInclusionName').value.trim();
    
    if (!name) {
        alert('Please enter an inclusion name');
        return;
    }
    
    try {
        const response = await fetch('/add-inclusion-management/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `name=${encodeURIComponent(name)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('addInclusionModal')).hide();
            location.reload();
        } else {
            alert(result.error || 'Failed to add inclusion');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add inclusion');
    }
}

// Edit Inclusion
function openEditInclusionModal(id, name) {
    document.getElementById('editInclusionId').value = id;
    document.getElementById('editInclusionName').value = name;
    new bootstrap.Modal(document.getElementById('editInclusionModal')).show();
}

async function updateInclusion() {
    const id = document.getElementById('editInclusionId').value;
    const name = document.getElementById('editInclusionName').value.trim();
    
    if (!name) {
        alert('Please enter an inclusion name');
        return;
    }
    
    try {
        const response = await fetch(`/edit-inclusion/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `name=${encodeURIComponent(name)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('editInclusionModal')).hide();
            location.reload();
        } else {
            alert(result.error || 'Failed to update inclusion');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update inclusion');
    }
}

// Delete Inclusion
async function deleteInclusion(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This will remove it from all rooms that use it.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/delete-inclusion/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            location.reload();
        } else {
            alert(result.error || 'Failed to delete inclusion');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete inclusion');
    }
}

// Add Appliance
async function addAppliance() {
    const name = document.getElementById('newApplianceName').value.trim();
    
    if (!name) {
        alert('Please enter an appliance name');
        return;
    }
    
    try {
        const response = await fetch('/add-appliance-management/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `name=${encodeURIComponent(name)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('addApplianceModal')).hide();
            location.reload();
        } else {
            alert(result.error || 'Failed to add appliance');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add appliance');
    }
}

// Edit Appliance
function openEditApplianceModal(id, name) {
    document.getElementById('editApplianceId').value = id;
    document.getElementById('editApplianceName').value = name;
    new bootstrap.Modal(document.getElementById('editApplianceModal')).show();
}

async function updateAppliance() {
    const id = document.getElementById('editApplianceId').value;
    const name = document.getElementById('editApplianceName').value.trim();
    
    if (!name) {
        alert('Please enter an appliance name');
        return;
    }
    
    try {
        const response = await fetch(`/edit-appliance/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `name=${encodeURIComponent(name)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Close modal and refresh page
            bootstrap.Modal.getInstance(document.getElementById('editApplianceModal')).hide();
            location.reload();
        } else {
            alert(result.error || 'Failed to update appliance');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update appliance');
    }
}

// Delete Appliance
async function deleteAppliance(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This will remove it from all rooms that use it.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/delete-appliance/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            location.reload();
        } else {
            alert(result.error || 'Failed to delete appliance');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete appliance');
    }
}
