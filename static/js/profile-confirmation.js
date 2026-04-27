// profile-confirmation.js
// Handles profile edit confirmation with proper Bootstrap modal stacking

(function () {
    'use strict';

    let originalValues = {};

    function initializeProfileConfirmation() {
        const form = document.getElementById('profileForm');
        if (!form) return;

        // Capture original values on load
        originalValues = {
            username: (document.getElementById('usernameInput')  || {}).value || '',
            fullName: (document.getElementById('fullNameInput')  || {}).value || '',
            email   : (document.getElementById('emailInput')     || {}).value || '',
            phone   : (document.getElementById('phoneInput')     || {}).value || '',
        };

        form.addEventListener('submit', handleFormSubmit);
    }

    function handleFormSubmit(event) {
        event.preventDefault();

        const currentValues = {
            username       : document.getElementById('usernameInput').value,
            fullName       : document.getElementById('fullNameInput').value,
            email          : document.getElementById('emailInput').value,
            phone          : document.getElementById('phoneInput').value,
            currentPassword: document.getElementById('currentPassword').value,
            newPassword    : document.getElementById('newPassword').value,
            photoFile      : document.getElementById('profilePhotoInput').files[0],
        };

        const changes = buildChangesList(currentValues);

        if (changes.length === 0) {
            alert('No changes detected. Please update at least one field.');
            return;
        }

        showConfirmationModal(changes);
    }

    function buildChangesList(currentValues) {
        const changes = [];

        if (currentValues.fullName !== originalValues.fullName)
            changes.push({ field: 'Full Name', from: originalValues.fullName, to: currentValues.fullName });

        if (currentValues.username !== originalValues.username)
            changes.push({ field: 'Username', from: originalValues.username, to: currentValues.username });

        if (currentValues.email !== originalValues.email)
            changes.push({ field: 'Email', from: originalValues.email, to: currentValues.email });

        if (currentValues.phone !== originalValues.phone)
            changes.push({ field: 'Phone', from: originalValues.phone, to: currentValues.phone });

        if (currentValues.photoFile)
            changes.push({ field: 'Profile Photo', from: 'Current photo', to: currentValues.photoFile.name });

        if (currentValues.currentPassword || currentValues.newPassword)
            changes.push({ field: 'Password', from: '••••••••', to: '(updated)' });

        return changes;
    }

    function showConfirmationModal(changes) {
        const summaryEl = document.getElementById('confirmationSummary');
        summaryEl.innerHTML = changes.map(c => `
            <div class="mb-2 p-2 border-bottom">
                <strong style="color:#495057;">${escapeHtml(c.field)}:</strong><br>
                <small class="text-muted">
                    <span style="color:#dc3545;">${escapeHtml(c.from)}</span>
                    <i class="bi bi-arrow-right mx-1" style="color:#6c757d;"></i>
                    <span style="color:#198754;">${escapeHtml(c.to)}</span>
                </small>
            </div>
        `).join('');

        // ✅ Always reuse instance — never create a new one if one exists
        const confirmEl       = document.getElementById('confirmProfileChangeModal');
        const confirmInstance = bootstrap.Modal.getInstance(confirmEl) || new bootstrap.Modal(confirmEl, {
            backdrop: 'static',
            keyboard: false,
        });

        confirmInstance.show();

        // ✅ Wire up confirm button — replace onclick to avoid stacking listeners
        const confirmBtn   = document.getElementById('confirmSaveBtn');
        confirmBtn.onclick = function () {
            confirmInstance.hide();
            // Wait for modal hide animation to finish, then submit
            confirmEl.addEventListener('hidden.bs.modal', function submitOnce() {
                confirmEl.removeEventListener('hidden.bs.modal', submitOnce);
                document.getElementById('profileForm').submit();
            });
        };
    }

    function escapeHtml(text) {
        if (!text) return '';
        return String(text).replace(/[&<>"']/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
        }[m]));
    }

    document.addEventListener('DOMContentLoaded', initializeProfileConfirmation);

})();