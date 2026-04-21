document.addEventListener('DOMContentLoaded', function () {

    // ── TOPBAR DATE ──────────────────────────────────
    const d = new Date();
    document.getElementById('currentDate').textContent = d.toLocaleDateString('en-US', {
        weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
    });

    // ── MOBILE SIDEBAR TOGGLE ─────────────────────────
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.querySelector('[onclick="toggleSidebar()"]');

    window.toggleSidebar = function () {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
    };

    // ── CLOSE SIDEBAR ON OVERLAY CLICK ───────────────
    overlay.addEventListener('click', function () {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
    });

});

// ── ADMIN PASSWORD TOGGLE ─────────────────────────────
window.toggleAdminPassword = function () {
    const pass = document.getElementById('adminPassword');
    const icon = document.getElementById('adminEyeIcon');
    if (pass.type === 'password') {
        pass.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
        pass.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
    }
};

// ── EDIT TENANT MODAL ─────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.edit-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id         = this.dataset.id;
            const fullName   = this.dataset.fullname;
            const email      = this.dataset.email;
            const phone      = this.dataset.phone;
            const roomNumber = this.dataset.room;

            document.getElementById('editFullName').value   = fullName;
            document.getElementById('editEmail').value      = email;
            document.getElementById('editPhone').value      = phone;
            document.getElementById('editRoomNumber').value = roomNumber;
            document.getElementById('editTenantForm').action = '/edit-tenant/' + id + '/';

            new bootstrap.Modal(document.getElementById('editTenantModal')).show();
        });
    });
});