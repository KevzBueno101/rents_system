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
            // Close modal and update UI without reload
            bootstrap.Modal.getInstance(document.getElementById('addInclusionModal')).hide();
            // Add to the list
            addInclusionToList(result.id, result.name);
            // Clear input
            document.getElementById('newInclusionName').value = '';
            // Sync with room modals if they're open
            syncWithRoomModals('inclusion', result.id, result.name);
        } else {
            alert(result.error || 'Failed to add inclusion');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add inclusion');
    }
}

// Add inclusion to the list UI
function addInclusionToList(id, name) {
    const list = document.getElementById('inclusionsList');
    if (!list) return;
    
    const row = document.createElement('div');
    row.className = 'd-flex justify-content-between align-items-center mb-2 p-2 border rounded';
    row.id = `inclusion-${id}`;
    row.innerHTML = `
        <span>${name}</span>
        <div>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditInclusionModal(${id}, '${name}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteInclusion(${id}, '${name}')">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    list.appendChild(row);
}

// Sync with room modals
function syncWithRoomModals(type, id, name) {
    // Check if room-features.js is loaded and has the synchronization function
    if (typeof synchronizeFeatureAcrossModals === 'function') {
        // Try to sync with both add and edit modals
        try {
            synchronizeFeatureAcrossModals(type, id, name, 'add');
            synchronizeFeatureAcrossModals(type, id, name, 'edit');
        } catch (e) {
            console.log('Room modals not open or sync function not available');
        }
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
            // Close modal and update UI without reload
            bootstrap.Modal.getInstance(document.getElementById('editInclusionModal')).hide();
            // Update the list item
            const listItem = document.getElementById(`inclusion-${id}`);
            if (listItem) {
                listItem.querySelector('span').textContent = name;
            }
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
            // Remove from UI without reload
            const listItem = document.getElementById(`inclusion-${id}`);
            if (listItem) {
                listItem.remove();
            }
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
            // Close modal and update UI without reload
            bootstrap.Modal.getInstance(document.getElementById('addApplianceModal')).hide();
            // Add to the list
            addApplianceToList(result.id, result.name);
            // Clear input
            document.getElementById('newApplianceName').value = '';
            // Sync with room modals if they're open
            syncWithRoomModals('appliance', result.id, result.name);
        } else {
            alert(result.error || 'Failed to add appliance');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add appliance');
    }
}

// Add appliance to the list UI
function addApplianceToList(id, name) {
    const list = document.getElementById('appliancesList');
    if (!list) return;
    
    const row = document.createElement('div');
    row.className = 'd-flex justify-content-between align-items-center mb-2 p-2 border rounded';
    row.id = `appliance-${id}`;
    row.innerHTML = `
        <span>${name}</span>
        <div>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditApplianceModal(${id}, '${name}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteAppliance(${id}, '${name}')">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    list.appendChild(row);
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
            // Close modal and update UI without reload
            bootstrap.Modal.getInstance(document.getElementById('editApplianceModal')).hide();
            // Update the list item
            const listItem = document.getElementById(`appliance-${id}`);
            if (listItem) {
                listItem.querySelector('span').textContent = name;
            }
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
            // Remove from UI without reload
            const listItem = document.getElementById(`appliance-${id}`);
            if (listItem) {
                listItem.remove();
            }
        } else {
            alert(result.error || 'Failed to delete appliance');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete appliance');
    }
}
