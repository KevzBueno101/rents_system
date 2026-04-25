// ══════════════════════════════════════════════════════════════
//  room-features.js  —  Inclusions Only (Simplified)
//
//  ID MAP (must match room_list.html exactly):
//
//  Add Room modal:
//    container  : #dynamicInclusions
//    button     : #addInclusionBtnAdd
//    checkbox   : add_inclusion_{id}
//
//  Edit Room modal:
//    container  : #dynamicInclusionsEdit
//    button     : #addInclusionBtn
//    checkbox   : edit_inclusion_{id}
// ══════════════════════════════════════════════════════════════

let currentRoomId = null;
let allInclusions  = [];
let roomInclusions = [];
let activeModal    = 'edit'; // 'add' or 'edit'

// ── LOAD ALL INCLUSIONS FROM BACKEND ───────────────────────────────────────────
async function loadAvailableFeatures() {
    try {
        const iRes = await fetch('/get-all-inclusions/');
        if (iRes.ok) allInclusions = await iRes.json();
    } catch (e) {
        console.error('loadAvailableFeatures error:', e);
    }
}

// ── MINI-MODAL ────────────────────────────────────────────────────────────────
function openMiniModal(type) {
    const existing = document.getElementById('roomFeatureMiniModal');
    if (existing) existing.remove();

    const inputId = `miniFeatureInput_${Date.now()}`;
    const div = document.createElement('div');
    div.className = 'modal fade';
    div.id = 'roomFeatureMiniModal';
    div.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="bi bi-plus-circle"></i>
                        Add New Inclusion
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-control" id="${inputId}"
                           placeholder="e.g. Parking, Kitchen Access">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary"
                            onclick="saveNewFeature('inclusion', '${inputId}')">
                        Add Inclusion
                    </button>
                </div>
            </div>
        </div>`;
    document.body.appendChild(div);
    new bootstrap.Modal(div).show();
    div.addEventListener('hidden.bs.modal', () => div.remove());
}

// ── SAVE NEW INCLUSION TO BACKEND ──────────────────────────────────────────────
async function saveNewFeature(type, inputId) {
    const input = document.getElementById(inputId);
    const name  = input ? input.value.trim() : '';

    if (!name) { alert('Please enter a name'); return; }

    const csrf = getCsrfToken();
    if (!csrf) { alert('Security token missing — please refresh.'); return; }

    const url = '/add-inclusion-management/';

    try {
        const res    = await fetch(url, {
            method : 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrf },
            body   : `name=${encodeURIComponent(name)}`,
        });
        const result = await res.json();
        const prefix = activeModal === 'add' ? 'add' : 'edit';

        if (result.success) {
            if (!allInclusions.some(i => i.id == result.id))
                allInclusions.push({ id: result.id, name: result.name });
            injectFeatureRow('inclusion', result.id, result.name, prefix, true);
            synchronizeFeatureAcrossModals('inclusion', result.id, result.name, prefix);
            closeMiniModal();

        } else if (result.error && result.error.toLowerCase().includes('already exists')) {
            // Feature exists in DB — just show it checked in the current modal
            const found = allInclusions.find(i => i.name.toLowerCase() === name.toLowerCase());
            if (found) { injectFeatureRow('inclusion', found.id, found.name, prefix, true); closeMiniModal(); return; }
            alert(result.error);
        } else {
            alert(result.error || 'Failed to add inclusion');
        }
    } catch (e) {
        console.error('saveNewFeature error:', e);
        alert('Failed to add inclusion. Check console.');
    }
}

function closeMiniModal() {
    const el = document.getElementById('roomFeatureMiniModal');
    if (!el) return;
    const inst = bootstrap.Modal.getInstance(el);
    if (inst) inst.hide();
    // hidden.bs.modal listener removes the element
}

// ── INJECT A CHECKBOX ROW ────────────────────────────────────────────────────
// Removes only from the modal list — NEVER deletes from the DB / Inclusion Manager.
function injectFeatureRow(type, id, name, prefix, checked) {
    const containerMap = {
        'add-inclusion' : 'dynamicInclusions',
        'edit-inclusion': 'dynamicInclusionsEdit',
    };
    const container = document.getElementById(containerMap[`${prefix}-${type}`]);
    if (!container) return;

    const checkboxId = `${prefix}_${type}_${id}`;

    // If row already exists just update its checked state
    const existing = document.getElementById(checkboxId);
    if (existing) { existing.checked = checked; return; }

    const col     = document.createElement('div');
    col.className = 'col-6';

    const wrap     = document.createElement('div');
    wrap.className = 'd-flex align-items-center gap-1';

    const cb       = document.createElement('input');
    cb.type        = 'checkbox';
    cb.className   = 'form-check-input';
    cb.name        = `dynamic_${type}_${id}`;
    cb.id          = checkboxId;
    cb.checked     = checked;

    const lbl       = document.createElement('label');
    lbl.className   = 'form-check-label me-1';
    lbl.style.fontSize = '13px';
    lbl.htmlFor     = checkboxId;
    lbl.textContent = name;

    // ✕ button — removes row from this modal only, does NOT touch DB
    const rmBtn     = document.createElement('button');
    rmBtn.type      = 'button';
    rmBtn.className = 'btn btn-sm btn-outline-danger p-0 d-flex align-items-center justify-content-center';
    rmBtn.style.cssText = 'width:18px;height:18px;font-size:10px;line-height:1;flex-shrink:0;';
    rmBtn.innerHTML = '<i class="bi bi-x"></i>';
    rmBtn.title     = `Remove "${name}" from this room (does not delete from Inclusion Manager)`;
    rmBtn.addEventListener('click', function () {
        col.remove();
        roomInclusions = roomInclusions.filter(x => x.id != id);
    });

    wrap.appendChild(cb);
    wrap.appendChild(lbl);
    wrap.appendChild(rmBtn);
    col.appendChild(wrap);
    container.appendChild(col);
}

// ── ON PAGE LOAD ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async function () {
    await loadAvailableFeatures();

    // Add button listeners for +Add buttons
    const addInclusionBtnAdd = document.getElementById('addInclusionBtnAdd');
    if (addInclusionBtnAdd) {
        addInclusionBtnAdd.addEventListener('click', function () {
            activeModal = 'add';
            openMiniModal('inclusion');
        });
    }

    const addInclusionBtn = document.getElementById('addInclusionBtn');
    if (addInclusionBtn) {
        addInclusionBtn.addEventListener('click', function () {
            activeModal = 'edit';
            openMiniModal('inclusion');
        });
    }

    // Populate Add Room modal each time it opens
    const addRoomModalEl = document.getElementById('addRoomModal');
    if (addRoomModalEl) {
        addRoomModalEl.addEventListener('show.bs.modal', function () {
            activeModal = 'add';
            const incContainer = document.getElementById('dynamicInclusions');
            if (incContainer) incContainer.innerHTML = '';
            allInclusions.forEach(i => injectFeatureRow('inclusion', i.id, i.name, 'add', false));
        });
    }

    // Populate Edit Room modal when an edit button is clicked
    document.querySelectorAll('.edit-room-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            currentRoomId = this.dataset.id;
            activeModal   = 'edit';
            
            // Populate form fields from data attributes
            document.getElementById('editFloor').value = this.dataset.floor;
            document.getElementById('editRoomNumber').value = this.dataset.room;
            document.getElementById('editCapacity').value = this.dataset.capacity;
            document.getElementById('editMonthlyRate').value = this.dataset.rate;
            document.getElementById('editArea').value = this.dataset.area;
            document.getElementById('editNumCR').value = this.dataset.cr;
            document.getElementById('editBedType').value = this.dataset.bedtype;
            
            // Set inclusion checkboxes
            document.getElementById('editSink').checked = this.dataset.sink === 'True';
            document.getElementById('editWater').checked = this.dataset.water === 'True';
            document.getElementById('editElec').checked = this.dataset.elec === 'True';
            document.getElementById('editWifi').checked = this.dataset.wifi === 'True';
            
            // Load dynamic inclusions
            loadRoomFeatures(currentRoomId);
            
            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('editRoomModal'));
            editModal.show();
        });
    });
});

// ── LOAD ROOM'S FEATURES INTO EDIT MODAL ─────────────────────────────────────
async function loadRoomFeatures(roomId) {
    try {
        await loadAvailableFeatures();

        const res = await fetch(`/get-room-features/?room_id=${roomId}`);
        if (!res.ok) return;

        const data     = await res.json();
        roomInclusions = data.inclusions || [];

        activeModal = 'edit';

        const incEdit = document.getElementById('dynamicInclusionsEdit');
        if (incEdit) incEdit.innerHTML = '';

        allInclusions.forEach(inc => {
            const checked = roomInclusions.some(r => r.id == inc.id);
            injectFeatureRow('inclusion', inc.id, inc.name, 'edit', checked);
        });

    } catch (e) {
        console.error('loadRoomFeatures error:', e);
    }
}

// ── SYNCHRONIZE INCLUSION ACROSS ALL MODALS ───────────────────────────────────────
function synchronizeFeatureAcrossModals(type, id, name, currentPrefix) {
    // Add to the other modal if it's open
    const otherPrefix = currentPrefix === 'add' ? 'edit' : 'add';
    const otherContainerId = `${otherPrefix === 'add' ? 'dynamicInclusions' : 'dynamicInclusionsEdit'}`;
    const otherContainer = document.getElementById(otherContainerId);
    
    if (otherContainer) {
        // Check if the feature already exists in the other modal
        const existingCheckbox = document.getElementById(`${otherPrefix}_${type}_${id}`);
        if (!existingCheckbox) {
            injectFeatureRow(type, id, name, otherPrefix, false);
        }
    }
}

// ── CSRF HELPERS ─────────────────────────────────────────────────────────────
function getCookie(name) {
    if (!document.cookie) return null;
    for (const c of document.cookie.split(';')) {
        const t = c.trim();
        if (t.startsWith(name + '='))
            return decodeURIComponent(t.slice(name.length + 1));
    }
    return null;
}

function getCsrfToken() {
    return getCookie('csrftoken')
        || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
        || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value
        || null;
}
