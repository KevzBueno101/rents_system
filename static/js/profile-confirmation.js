// Profile Edit Confirmation Modal - profile-confirmation.js
// BEST FIX: Proper modal lifecycle management

(function() {
    'use strict';

    let originalValues = {};
    let editProfileModal = null;

    function initializeProfileConfirmation() {
        const form = document.getElementById('profileForm');
        if (!form) {
            console.warn('Profile form not found');
            return;
        }

        const editModalElement = document.getElementById('profileModal');
        if (editModalElement) {
            editProfileModal = bootstrap.Modal.getOrCreateInstance(editModalElement, {
                backdrop: true,
                keyboard: true
            });
        }

        originalValues = {
            username: document.getElementById('usernameInput').value,
            fullName: document.getElementById('fullNameInput').value,
            email: document.getElementById('emailInput').value,
            phone: document.getElementById('phoneInput').value
        };

        form.addEventListener('submit', handleFormSubmit);
    }

    function handleFormSubmit(event) {
        event.preventDefault();

        const currentValues = {
            username: document.getElementById('usernameInput').value,
            fullName: document.getElementById('fullNameInput').value,
            email: document.getElementById('emailInput').value,
            phone: document.getElementById('phoneInput').value,
            currentPassword: document.getElementById('currentPassword').value,
            newPassword: document.getElementById('newPassword').value,
            photoFile: document.getElementById('profilePhotoInput').files[0]
        };

        const changes = buildChangesList(currentValues);

        if (changes.length === 0) {
            showAlert('No changes detected. Please update at least one field.', 'warning');
            return;
        }

        displayConfirmationModal(changes);
    }

    function buildChangesList(currentValues) {
        const changes = [];

        if (currentValues.fullName !== originalValues.fullName) {
            changes.push({
                field: 'Full Name',
                from: originalValues.fullName,
                to: currentValues.fullName
            });
        }

        if (currentValues.username !== originalValues.username) {
            changes.push({
                field: 'Username',
                from: originalValues.username,
                to: currentValues.username
            });
        }

        if (currentValues.email !== originalValues.email) {
            changes.push({
                field: 'Email',
                from: originalValues.email,
                to: currentValues.email
            });
        }

        if (currentValues.phone !== originalValues.phone) {
            changes.push({
                field: 'Phone',
                from: originalValues.phone,
                to: currentValues.phone
            });
        }

        if (currentValues.photoFile) {
            changes.push({
                field: 'Profile Photo',
                from: 'Current photo',
                to: currentValues.photoFile.name
            });
        }

        if (currentValues.currentPassword || currentValues.newPassword) {
            changes.push({
                field: 'Password',
                from: '••••••••',
                to: '••••••••'
            });
        }

        return changes;
    }

    function displayConfirmationModal(changes) {
        const summaryHTML = changes
            .map(change => `
                <div class="mb-2 p-2 border-bottom">
                    <strong style="color: #495057;">${change.field}:</strong>
                    <br>
                    <small class="text-muted">
                        <i class="bi bi-arrow-right" style="color: #6c757d;"></i>
                        <span style="color: #dc3545;">${escapeHtml(change.from)}</span>
                        <i class="bi bi-arrow-right" style="color: #6c757d; margin: 0 4px;"></i>
                        <span style="color: #198754;">${escapeHtml(change.to)}</span>
                    </small>
                </div>
            `)
            .join('');

        document.getElementById('confirmationSummary').innerHTML = summaryHTML;

        const confirmModalElement = document.getElementById('confirmProfileChangeModal');

        // Hide the edit profile modal's backdrop
        const editBackdrop = document.querySelector('#profileModal ~ .modal-backdrop');
        if (editBackdrop) {
            editBackdrop.style.display = 'none';
        }

        // Create and show confirmation modal
        const confirmModalInstance = new bootstrap.Modal(confirmModalElement, {
            backdrop: 'static',
            keyboard: false
        });

        confirmModalInstance.show();

        // Handle confirm button
        const confirmBtn = document.getElementById('confirmSaveBtn');
        confirmBtn.onclick = function() {
            submitProfileForm(confirmModalInstance);
        };

        // Handle cancel button - restore backdrop
        const cancelBtn = confirmModalElement.querySelector('[data-bs-dismiss="modal"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                if (editBackdrop) {
                    editBackdrop.style.display = 'block';
                }
            });
        }
    }

    function submitProfileForm(modalInstance) {
        const form = document.getElementById('profileForm');
        
        if (modalInstance) {
            modalInstance.hide();
        }

        form.method = 'POST';

        const action = form.getAttribute('action');
        if (action) {
            form.action = action;
        }

        setTimeout(() => {
            form.submit();
        }, 150);
    }

    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const content = document.getElementById('confirmationSummary');
        if (content && content.parentElement) {
            content.parentElement.insertBefore(alertDiv, content);
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    document.addEventListener('DOMContentLoaded', initializeProfileConfirmation);

})();