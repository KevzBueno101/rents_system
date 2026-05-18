// dashboard.js - Handles interactivity for the admin dashboard,
// including modals, sidebar, and dynamic room features display

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

    // ── GLOBAL BACKDROP CLEANUP ───────────────────────
    // Fires after any modal closes — only cleans up when NO modal is open
    document.addEventListener('hidden.bs.modal', function () {
        const anyStillOpen = document.querySelector('.modal.show');
        if (!anyStillOpen) {
            document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        }
    });

    // ── HANDLE EDIT ROOM FORM SUBMISSION ─────────────────
    const editRoomForm = document.getElementById('editRoomForm');
    if (editRoomForm) {
        editRoomForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const action   = this.action;

            let roomId = null;
            const match = action.match(/\/edit-room\/(\d+)/);
            if (match) {
                roomId = match[1];
            } else if (typeof currentRoomId !== 'undefined' && currentRoomId) {
                roomId = currentRoomId;
            } else {
                alert('Error: Could not determine room. Please close and try again.');
                return;
            }

            fetch(`/edit-room/${roomId}/`, {
                method : 'POST',
                body   : formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('Error saving room. Please try again.');
                    return;
                }

                // ✅ Close using existing instance only
                const editRoomModalEl = document.getElementById('editRoomModal');
                const editModal = bootstrap.Modal.getInstance(editRoomModalEl);
                if (editModal) editModal.hide();

                // Update inclusion icons on the card
                const container = document.getElementById(`room-inclusions-${roomId}`);
                if (container) {
                    const dynList = (data.dynamic_inclusions || []).map((name, i) => ({ id: i, name }));
                    container.dataset.dynamicInclusions = JSON.stringify(dynList);
                    container.dataset.water       = data.water ? '1' : '0';
                    container.dataset.electricity = data.elec  ? '1' : '0';
                    container.dataset.wifi        = data.wifi  ? '1' : '0';
                    container.dataset.sink        = data.sink  ? '1' : '0';
                    renderRoomInclusions(container);
                }

                // Update info modal if open
                const infoModal = document.getElementById('roomInfoModal');
                if (infoModal && infoModal.classList.contains('show')) {
                    updateRoomInfoModal(data);
                }
            })
            .catch(err => {
                console.error('Error saving room:', err);
                alert('Error saving room. Please try again.');
            });
        });
    }

    // ── ROOM INFO MODAL ───────────────────────────────
    document.querySelectorAll('.info-room-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const roomId = this.dataset.id;

            fetch(`/api/room-data/${roomId}/`)
                .then(r => {
                    if (!r.ok) throw new Error('Failed to load room data');
                    const ct = r.headers.get('content-type');
                    if (!ct || !ct.includes('application/json')) throw new Error('Invalid response format');
                    return r.json();
                })
                .then(data => {
                    document.getElementById('infoRoomCode').textContent = data.code;

                    const photoEl = document.getElementById('infoRoomPhoto');
                    photoEl.innerHTML = data.photo
                        ? `<img src="${data.photo}" style="width:100%;height:200px;object-fit:cover;">`
                        : `<div style="width:100%;height:120px;background:#f4f6f9;display:flex;align-items:center;justify-content:center;">
                               <i class="bi bi-door-open" style="font-size:40px;color:#ccc;"></i>
                           </div>`;

                    const statusEl        = document.getElementById('infoStatus');
                    statusEl.textContent  = data.status;
                    statusEl.style.background = data.status === 'Occupied' ? '#e53935' : '#1db954';

                    const suffix = n => n==1?'st':n==2?'nd':n==3?'rd':'th';
                    document.getElementById('infoFloor').textContent     = `${data.floor}${suffix(data.floor)} Floor`;
                    document.getElementById('infoOccupancy').textContent = `${data.occupied} / ${data.capacity} beds`;
                    document.getElementById('infoRate').textContent      = `₱${parseFloat(data.rate).toLocaleString()}`;
                    document.getElementById('infoArea').textContent      = data.area ? `${data.area} sqm` : '—';
                    document.getElementById('infoCR').textContent        = data.cr + ' CR';
                    document.getElementById('infoBedType').textContent   = data.bedtype;

                    const inclusions = [];
                    if (data.sink)  inclusions.push('Sink');
                    if (data.water) inclusions.push('Water');
                    if (data.elec)  inclusions.push('Electricity');
                    if (data.wifi)  inclusions.push('WiFi');
                    (data.dynamic_inclusions || []).forEach(name => inclusions.push(name));

                    document.getElementById('infoInclusions').innerHTML = inclusions.length
                        ? inclusions.map(i =>
                            `<span class="badge bg-light text-dark border me-1 mb-1" style="font-size:12px;">
                                <i class="bi bi-check2"></i> ${i}
                             </span>`).join('')
                        : '<span class="text-muted" style="font-size:13px;">None</span>';

                    document.getElementById('infoTenants').innerHTML = data.tenants && data.tenants.length
                        ? data.tenants.map(t =>
                            `<span class="badge bg-light text-dark border me-1 mb-1" style="font-size:12px;">
                                <i class="bi bi-person"></i> ${t}
                             </span>`).join('')
                        : '<span class="text-muted" style="font-size:13px;">No tenants yet</span>';

                    // ✅ Always reuse existing instance
                    const roomInfoEl    = document.getElementById('roomInfoModal');
                    const roomInfoModal = bootstrap.Modal.getInstance(roomInfoEl) || new bootstrap.Modal(roomInfoEl);
                    roomInfoModal.show();
                })
                .catch(err => {
                    console.error('Error loading room info:', err);
                    alert('Failed to load room information. Please try again.');
                });
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

    // ── PROFILE MODAL ─────────────────────────────────
    window.openProfileModal = function () {
        // ✅ Always reuse existing instance
        const el    = document.getElementById('profileModal');
        const modal = bootstrap.Modal.getInstance(el) || new bootstrap.Modal(el);
        modal.show();
    };

    window.toggleProfilePassword = function () {
        const currentPass = document.getElementById('currentPassword');
        const newPass     = document.getElementById('newPassword');
        const confirmPass = document.getElementById('confirmPassword');
        const icon        = document.getElementById('profileEyeIcon');

        if (currentPass.type === 'password') {
            currentPass.type = 'text';
            newPass.type     = 'text';
            confirmPass.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            currentPass.type = 'password';
            newPass.type     = 'password';
            confirmPass.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    };

    window.previewProfilePhoto = function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                document.getElementById('profilePreview').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    };

    // ── INITIALIZE ROOM INCLUSION ICONS ──────────────────
    document.querySelectorAll('[id^="room-inclusions-"]').forEach(containerEl => {
        renderRoomInclusions(containerEl);
    });

    // ── CLICKABLE ROOM CARDS ──────────────────────────
    // Make entire room card clickable to show info modal
    document.querySelectorAll('.clickable-room-card').forEach(function(card) {
        card.addEventListener('click', function(e) {
            // Ignore if clicked on image carousel or buttons/links
            if (e.target.closest('img') || e.target.closest('.edit-room-btn') || e.target.closest('form') || e.target.closest('.btn-outline-danger') || e.target.closest('button')) {
                return;
            }
            const btn = card.querySelector('.info-room-btn');
            if (btn && !btn.contains(e.target)) {
                btn.click();
            }
        });
    });

});


// ── UPDATE ROOM INCLUSIONS DISPLAY ───────────────────
window.updateRoomInclusionsDisplay = function (roomId) {
    const container = document.getElementById(`room-inclusions-${roomId}`);
    if (container) renderRoomInclusions(container);
};

// ── UPDATE ROOM INFO MODAL WITH NEW DATA ─────────────
window.updateRoomInfoModal = function (roomData) {
    if (!roomData) return;

    document.getElementById('infoFloor').textContent     = `${roomData.floor}${getSuffix(roomData.floor)} Floor`;
    document.getElementById('infoOccupancy').textContent = `${roomData.occupied} / ${roomData.capacity} beds`;
    document.getElementById('infoRate').textContent      = `₱${parseFloat(roomData.rate).toLocaleString()}`;
    document.getElementById('infoArea').textContent      = roomData.area ? `${roomData.area} sqm` : '—';
    document.getElementById('infoCR').textContent        = roomData.cr + ' CR';
    document.getElementById('infoBedType').textContent   = roomData.bedtype;

    const inclusions = [];
    if (roomData.sink  === true || roomData.sink  === 'True') inclusions.push('Sink');
    if (roomData.water === true || roomData.water === 'True') inclusions.push('Water');
    if (roomData.elec  === true || roomData.elec  === 'True') inclusions.push('Electricity');
    if (roomData.wifi  === true || roomData.wifi  === 'True') inclusions.push('WiFi');
    (roomData.dynamic_inclusions || []).forEach(inc => inclusions.push(inc));

    document.getElementById('infoInclusions').innerHTML = inclusions.length
        ? inclusions.map(i =>
            `<span class="badge bg-light text-dark border me-1 mb-1" style="font-size:12px;">
                <i class="bi bi-check2"></i> ${i}
             </span>`).join('')
        : '<span class="text-muted" style="font-size:13px;">None</span>';
};

// ── HELPER: ordinal suffix ────────────────────────────
function getSuffix(num) {
    const n = parseInt(num);
    if (n === 1) return 'st';
    if (n === 2) return 'nd';
    if (n === 3) return 'rd';
    return 'th';
}