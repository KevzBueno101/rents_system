document.addEventListener('DOMContentLoaded', function () {

    // ── TOPBAR DATE ──────────────────────────────────
    const dateEl = document.getElementById('currentDate');
    if (dateEl) {
        const d = new Date();
        dateEl.textContent = d.toLocaleDateString('en-US', {
            weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
        });
    }

    // ── SIDEBAR ───────────────────────────────────────
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    window.toggleSidebar = function () {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
    };

    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // ── EDIT TENANT MODAL ─────────────────────────────
    document.querySelectorAll('.edit-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            document.getElementById('editFullName').value    = this.dataset.fullname;
            document.getElementById('editEmail').value       = this.dataset.email;
            document.getElementById('editPhone').value       = this.dataset.phone;
            document.getElementById('editRoomNumber').value  = this.dataset.room;
            document.getElementById('editTenantForm').action = '/edit-tenant/' + this.dataset.id + '/';
            new bootstrap.Modal(document.getElementById('editTenantModal')).show();
        });
    });

    // ── EDIT ROOM MODAL ───────────────────────────────
    document.querySelectorAll('.edit-room-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            document.getElementById('editRoomNumber').value  = this.dataset.room;
            document.getElementById('editFloor').value       = this.dataset.floor;
            document.getElementById('editCapacity').value    = this.dataset.capacity;
            document.getElementById('editMonthlyRate').value = this.dataset.rate;
            document.getElementById('editArea').value        = this.dataset.area;
            document.getElementById('editNumCR').value       = this.dataset.cr;
            document.getElementById('editBedType').value     = this.dataset.bedtype;

            // Checkboxes
            document.getElementById('editSink').checked   = this.dataset.sink === 'True';
            document.getElementById('editWater').checked  = this.dataset.water === 'True';
            document.getElementById('editElec').checked   = this.dataset.elec === 'True';
            document.getElementById('editWifi').checked   = this.dataset.wifi === 'True';
            document.getElementById('editFan').checked    = this.dataset.fan === 'True';
            document.getElementById('editAircon').checked = this.dataset.aircon === 'True';
            document.getElementById('editRef').checked    = this.dataset.ref === 'True';
            document.getElementById('editTv').checked     = this.dataset.tv === 'True';

            document.getElementById('editRoomForm').action = '/edit-room/' + this.dataset.id + '/';
            new bootstrap.Modal(document.getElementById('editRoomModal')).show();
        });
    });

    // ── ROOM INFO MODAL ───────────────────────────────
    document.querySelectorAll('.info-room-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const code     = this.dataset.code;
            const floor    = this.dataset.floor;
            const occupied = this.dataset.occupied;
            const capacity = this.dataset.capacity;
            const rate     = this.dataset.rate;
            const status   = this.dataset.status;
            const photo    = this.dataset.photo;
            const tenants  = this.dataset.tenants;
            const area     = this.dataset.area;
            const cr       = this.dataset.cr;
            const bedtype  = this.dataset.bedtype;

            // Room code
            document.getElementById('infoRoomCode').textContent = code;

            // Photo
            const photoEl = document.getElementById('infoRoomPhoto');
            if (photo) {
                photoEl.innerHTML = `<img src="${photo}" style="width:100%; height:200px; object-fit:cover;">`;
            } else {
                photoEl.innerHTML = `<div style="width:100%; height:120px; background:#f4f6f9; display:flex; align-items:center; justify-content:center;"><i class="bi bi-door-open" style="font-size:40px; color:#ccc;"></i></div>`;
            }

            // Status
            const statusEl = document.getElementById('infoStatus');
            statusEl.textContent = status;
            statusEl.style.background = status === 'Occupied' ? '#e53935' : '#1db954';

            // Details
            const floorNum = parseInt(floor);
            const suffix = floorNum === 1 ? 'st' : floorNum === 2 ? 'nd' : floorNum === 3 ? 'rd' : 'th';
            document.getElementById('infoFloor').textContent     = `${floorNum}${suffix} Floor`;
            document.getElementById('infoOccupancy').textContent = `${occupied} / ${capacity} beds`;
            document.getElementById('infoRate').textContent      = `₱${parseFloat(rate).toLocaleString()}`;
            document.getElementById('infoArea').textContent      = area ? `${area} sqm` : '—';
            document.getElementById('infoCR').textContent        = cr + ' CR';
            document.getElementById('infoBedType').textContent   = bedtype;

            // Inclusions
            const inclusions = [];
            if (this.dataset.sink   === 'True') inclusions.push('Sink');
            if (this.dataset.water  === 'True') inclusions.push('Water');
            if (this.dataset.elec   === 'True') inclusions.push('Electricity');
            if (this.dataset.wifi   === 'True') inclusions.push('WiFi');
            if (this.dataset.fan    === 'True') inclusions.push('Fan');
            if (this.dataset.aircon === 'True') inclusions.push('Aircon');
            if (this.dataset.ref    === 'True') inclusions.push('Refrigerator');
            if (this.dataset.tv     === 'True') inclusions.push('TV');

            const inclusionsEl = document.getElementById('infoInclusions');
            if (inclusions.length > 0) {
                inclusionsEl.innerHTML = inclusions.map(i =>
                    `<span class="badge bg-light text-dark border me-1 mb-1" style="font-size:12px;">
                        <i class="bi bi-check2"></i> ${i}
                    </span>`
                ).join('');
            } else {
                inclusionsEl.innerHTML = '<span class="text-muted" style="font-size:13px;">None</span>';
            }

            // Tenants
            const tenantsEl = document.getElementById('infoTenants');
            if (tenants) {
                const list = tenants.split('|').map(t =>
                    `<span class="badge bg-light text-dark border me-1 mb-1" style="font-size:12px;">
                        <i class="bi bi-person"></i> ${t}
                    </span>`
                ).join('');
                tenantsEl.innerHTML = list;
            } else {
                tenantsEl.innerHTML = '<span class="text-muted" style="font-size:13px;">No tenants yet</span>';
            }

            new bootstrap.Modal(document.getElementById('roomInfoModal')).show();
        });
    });

    // ── ADMIN PASSWORD TOGGLE ─────────────────────────
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

    // ── PROFILE MODAL FUNCTIONS ─────────────────────────
    window.openProfileModal = function () {
        new bootstrap.Modal(document.getElementById('profileModal')).show();
    };

    window.toggleProfilePassword = function () {
        const currentPass = document.getElementById('currentPassword');
        const newPass = document.getElementById('newPassword');
        const confirmPass = document.getElementById('confirmPassword');
        const icon = document.getElementById('profileEyeIcon');
        
        if (currentPass.type === 'password') {
            currentPass.type = 'text';
            newPass.type = 'text';
            confirmPass.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            currentPass.type = 'password';
            newPass.type = 'password';
            confirmPass.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    };

    window.previewProfilePhoto = function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const preview = document.getElementById('profilePreview');
                preview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    };

});