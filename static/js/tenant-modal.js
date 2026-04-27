// tenant-modal.js - Handles all tenant modal interactions (edit, etc.)

document.addEventListener('DOMContentLoaded', function () {

    const editTenantModal = document.getElementById('editTenantModal');
    if (!editTenantModal) return; // only runs on pages that have the tenant modal

    // ── EDIT TENANT MODAL ─────────────────────────────
    document.querySelectorAll('.edit-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            document.getElementById('editFullName').value    = this.dataset.fullname;
            document.getElementById('editEmail').value       = this.dataset.email;
            document.getElementById('editPhone').value       = this.dataset.phone;
            document.getElementById('editRoomNumber').value  = this.dataset.room;
            document.getElementById('editTenantForm').action = '/edit-tenant/' + this.dataset.id + '/';

            const modal = new bootstrap.Modal(editTenantModal);
            modal.show(this); // pass button as relatedTarget so shown.bs.modal works correctly
        });
    });

    // ── SHOWN EVENT (fires after modal is fully visible) ──
    editTenantModal.addEventListener('shown.bs.modal', function(event) {
        const button = event.relatedTarget;
        if (!button) return; // guard: ignore programmatic opens with no relatedTarget
        // add any extra logic here if needed in the future
    });

});