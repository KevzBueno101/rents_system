// Dynamic Room Features Management JavaScript
let currentRoomId = null;
let allInclusions = [];
let allAppliances = [];
let roomInclusions = [];
let roomAppliances = [];

// Load available inclusions and appliances
async function loadAvailableFeatures() {
    try {
        // Get all available inclusions and appliances
        const inclusionsResponse = await fetch('/get-all-inclusions/');
        const appliancesResponse = await fetch('/get-all-appliances/');
        
        if (inclusionsResponse.ok) {
            allInclusions = await inclusionsResponse.json();
        }
        if (appliancesResponse.ok) {
            allAppliances = await appliancesResponse.json();
        }
    } catch (error) {
        console.error('Error loading features:', error);
    }
}

// Add inclusion functionality
document.getElementById('addInclusionBtn').addEventListener('click', function() {
    const modal = createAddFeatureModal('inclusion');
    document.body.appendChild(modal);
    new bootstrap.Modal(modal).show();
});

// Add appliance functionality
document.getElementById('addApplianceBtn').addEventListener('click', function() {
    const modal = createAddFeatureModal('appliance');
    document.body.appendChild(modal);
    new bootstrap.Modal(modal).show();
});

// Create modal for adding new feature
function createAddFeatureModal(type) {
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="bi bi-plus-circle"></i> Add New ${type.charAt(0).toUpperCase() + type.slice(1)}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Name</label>
                        <input type="text" class="form-control" id="newFeatureName" placeholder="Enter ${type} name">
                        <div class="form-text">e.g., ${type === 'inclusion' ? 'Parking, Kitchen Access, Cable TV' : 'Microwave, Water Heater, Rice Cooker'}</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="addNewFeature('${type}')">Add ${type.charAt(0).toUpperCase() + type.slice(1)}</button>
                </div>
            </div>
        </div>
    `;
    return modalDiv;
}

// Add new feature
async function addNewFeature(type) {
    const nameInput = document.getElementById('newFeatureName');
    const name = nameInput.value.trim();
    
    console.log('Adding feature:', type, name);
    
    if (!name) {
        alert('Please enter a name');
        return;
    }
    
    try {
        const url = type === 'inclusion' ? '/add-inclusion-management/' : '/add-appliance-management/';
        const csrfToken = getCsrfToken();
        
        console.log('CSRF Token:', csrfToken);
        console.log('URL:', url);
        
        if (!csrfToken) {
            console.error('No CSRF token found');
            alert('Security token not found. Please refresh the page and try again.');
            return;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `name=${encodeURIComponent(name)}`
        });
        
        console.log('Response status:', response.status);
        
        const result = await response.json();
        console.log('Response data:', result);
        
        if (result.success) {
            // Add to the appropriate list
            if (type === 'inclusion') {
                // Check if it's already in the list
                if (!allInclusions.some(inc => inc.id == result.id)) {
                    allInclusions.push({id: result.id, name: result.name});
                }
                addDynamicInclusion(result.id, result.name);
                // Check the newly added inclusion
                document.getElementById(`inclusion_${result.id}`).checked = true;
            } else {
                // Check if it's already in the list
                if (!allAppliances.some(app => app.id == result.id)) {
                    allAppliances.push({id: result.id, name: result.name});
                }
                addDynamicAppliance(result.id, result.name);
                // Check the newly added appliance
                document.getElementById(`appliance_${result.id}`).checked = true;
            }
            
            // Close modal
            const modal = nameInput.closest('.modal');
            bootstrap.Modal.getInstance(modal).hide();
            modal.remove();
        } else {
            console.error('Backend error:', result.error);
            // If the inclusion already exists, try to find and show it
            if (result.error && result.error.includes('already exists')) {
                const name = nameInput.value.trim();
                if (type === 'inclusion') {
                    const existing = allInclusions.find(inc => inc.name.toLowerCase() === name.toLowerCase());
                    if (existing) {
                        addDynamicInclusion(existing.id, existing.name);
                        document.getElementById(`inclusion_${existing.id}`).checked = true;
                        // Close modal
                        const modal = nameInput.closest('.modal');
                        bootstrap.Modal.getInstance(modal).hide();
                        modal.remove();
                        return;
                    }
                } else {
                    const existing = allAppliances.find(app => app.name.toLowerCase() === name.toLowerCase());
                    if (existing) {
                        addDynamicAppliance(existing.id, existing.name);
                        document.getElementById(`appliance_${existing.id}`).checked = true;
                        // Close modal
                        const modal = nameInput.closest('.modal');
                        bootstrap.Modal.getInstance(modal).hide();
                        modal.remove();
                        return;
                    }
                }
            }
            alert(result.error || 'Failed to add ' + type);
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Failed to add ' + type + '. Check console for details.');
    }
}

// Add dynamic inclusion to the form
function addDynamicInclusion(id, name) {
    const container = document.getElementById('dynamicInclusions');
    const div = document.createElement('div');
    div.className = 'col-6';
    
    // Create the inner structure
    const innerDiv = document.createElement('div');
    innerDiv.className = 'd-flex align-items-center';
    
    // Create checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input me-2';
    checkbox.name = 'dynamic_inclusion_' + id;
    checkbox.id = 'inclusion_' + id;
    
    // Create label
    const label = document.createElement('label');
    label.className = 'form-check-label me-2';
    label.style.fontSize = '13px';
    label.htmlFor = 'inclusion_' + id;
    label.textContent = name;
    
    // Create remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger';
    removeBtn.style.padding = '1px 4px';
    removeBtn.style.fontSize = '9px';
    removeBtn.style.lineHeight = '1';
    removeBtn.innerHTML = '<i class="bi bi-x"></i>';
    removeBtn.addEventListener('click', function() {
        removeInclusionFromRoom(id, name);
    });
    
    // Assemble the elements
    innerDiv.appendChild(checkbox);
    innerDiv.appendChild(label);
    innerDiv.appendChild(removeBtn);
    div.appendChild(innerDiv);
    container.appendChild(div);
}

// Add dynamic appliance to the form
function addDynamicAppliance(id, name) {
    const container = document.getElementById('dynamicAppliances');
    const div = document.createElement('div');
    div.className = 'col-6';
    
    // Create the inner structure
    const innerDiv = document.createElement('div');
    innerDiv.className = 'd-flex align-items-center';
    
    // Create checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input me-2';
    checkbox.name = 'dynamic_appliance_' + id;
    checkbox.id = 'appliance_' + id;
    
    // Create label
    const label = document.createElement('label');
    label.className = 'form-check-label me-2';
    label.style.fontSize = '13px';
    label.htmlFor = 'appliance_' + id;
    label.textContent = name;
    
    // Create remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger';
    removeBtn.style.padding = '1px 4px';
    removeBtn.style.fontSize = '9px';
    removeBtn.style.lineHeight = '1';
    removeBtn.innerHTML = '<i class="bi bi-x"></i>';
    removeBtn.addEventListener('click', function() {
        removeApplianceFromRoom(id, name);
    });
    
    // Assemble the elements
    innerDiv.appendChild(checkbox);
    innerDiv.appendChild(label);
    innerDiv.appendChild(removeBtn);
    div.appendChild(innerDiv);
    container.appendChild(div);
}

// Get CSRF token
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

// Remove inclusion from room
function removeInclusionFromRoom(inclusionId, inclusionName) {
    if (!confirm('Remove "' + inclusionName + '" from this room?')) {
        return;
    }
    
    // Find and remove the entire element from the modal
    const checkbox = document.getElementById('inclusion_' + inclusionId);
    if (checkbox) {
        // Get the parent div (col-6) and remove it
        const colDiv = checkbox.closest('.col-6');
        if (colDiv) {
            colDiv.remove();
        }
    }
    
    // Remove from the room's inclusions list
    roomInclusions = roomInclusions.filter(inc => inc.id != inclusionId);
    
    console.log('Removed inclusion ' + inclusionName + ' from room');
}

// Remove appliance from room
function removeApplianceFromRoom(applianceId, applianceName) {
    if (!confirm('Remove "' + applianceName + '" from this room?')) {
        return;
    }
    
    // Find and remove the entire element from the modal
    const checkbox = document.getElementById('appliance_' + applianceId);
    if (checkbox) {
        // Get the parent div (col-6) and remove it
        const colDiv = checkbox.closest('.col-6');
        if (colDiv) {
            colDiv.remove();
        }
    }
    
    // Remove from the room's appliances list
    roomAppliances = roomAppliances.filter(app => app.id != applianceId);
    
    console.log('Removed appliance ' + applianceName + ' from room');
}

// Get CSRF token with fallback
function getCsrfToken() {
    // Try to get from cookie first
    let token = getCookie('csrftoken');
    
    // Fallback: try to get from meta tag
    if (!token) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            token = metaTag.getAttribute('content');
        }
    }
    
    // Fallback: try to get from hidden input
    if (!token) {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) {
            token = input.value;
        }
    }
    
    return token;
}

// Load room features when edit modal is opened
document.addEventListener('DOMContentLoaded', function() {
    loadAvailableFeatures();
    
    // Edit room button click handler
    document.querySelectorAll('.edit-room-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            currentRoomId = this.dataset.id;
            loadRoomFeatures(currentRoomId);
        });
    });
});

// Load room's current features
async function loadRoomFeatures(roomId) {
    try {
        // Load all available features first
        await loadAvailableFeatures();
        
        // Get room's current features
        const response = await fetch(`/get-room-features/?room_id=${roomId}`);
        if (response.ok) {
            const data = await response.json();
            roomInclusions = data.inclusions || [];
            roomAppliances = data.appliances || [];
            
            // Clear dynamic sections
            document.getElementById('dynamicInclusions').innerHTML = '';
            document.getElementById('dynamicAppliances').innerHTML = '';
            
            // Add ALL available inclusions and check the ones assigned to this room
            allInclusions.forEach(inclusion => {
                addDynamicInclusion(inclusion.id, inclusion.name);
                // Check if this inclusion is assigned to the room
                const isChecked = roomInclusions.some(roomInc => roomInc.id == inclusion.id);
                document.getElementById(`inclusion_${inclusion.id}`).checked = isChecked;
            });
            
            // Add ALL available appliances and check the ones assigned to this room
            allAppliances.forEach(appliance => {
                addDynamicAppliance(appliance.id, appliance.name);
                // Check if this appliance is assigned to the room
                const isChecked = roomAppliances.some(roomApp => roomApp.id == appliance.id);
                document.getElementById(`appliance_${appliance.id}`).checked = isChecked;
            });
        }
    } catch (error) {
        console.error('Error loading room features:', error);
    }
}
