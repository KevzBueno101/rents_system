// ══════════════════════════════════════════════════════════════
//  room-features.js  —  fully corrected
//
//  ID MAP (must match room_list.html exactly):
//
//  Add Room modal:
//    containers : #dynamicInclusions      #dynamicAppliances
//    buttons    : #addInclusionBtnAdd     #addApplianceBtnAdd
//    checkbox   :  add_inclusion_{id}      add_appliance_{id}
//
//  Edit Room modal:
//    containers : #dynamicInclusionsEdit  #dynamicAppliancesEdit
//    buttons    : #addInclusionBtn        #addApplianceBtn
//    checkbox   :  edit_inclusion_{id}     edit_appliance_{id}
// ══════════════════════════════════════════════════════════════

let currentRoomId = null;
let allInclusions  = [];
let allAppliances  = [];
let roomInclusions = [];
let roomAppliances = [];
let activeModal    = 'edit'; // 'add' or 'edit'

// ── LOAD ALL FEATURES FROM BACKEND ───────────────────────────────────────────
async function loadAvailableFeatures() {
    try {
        const [iRes, aRes] = await Promise.all([
            fetch('/get-all-inclusions/'),
            fetch('/get-all-appliances/'),
        ]);
        if (iRes.ok) allInclusions = await iRes.json();
        if (aRes.ok) allAppliances = await aRes.json();
    } catch (e) {
        console.error('loadAvailableFeatures error:', e);
    }
}

// ── BUTTON LISTENERS ─────────────────────────────────────────────────────────

document.getElementById('addInclusionBtnAdd')?.addEventListener('click', function () {
    activeModal = 'add';
    openMiniModal('inclusion');
});

document.getElementById('addApplianceBtnAdd')?.addEventListener('click', function () {
    activeModal = 'add';
    openMiniModal('appliance');
});

document.getElementById('addInclusionBtn')?.addEventListener('click', function () {
    activeModal = 'edit';
    openMiniModal('inclusion');
});

document.getElementById('addApplianceBtn')?.addEventListener('click', function () {
    activeModal = 'edit';
    openMiniModal('appliance');
});

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
                        Add New ${type === 'inclusion' ? 'Inclusion' : 'Appliance'}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-control" id="${inputId}"
                           placeholder="${type === 'inclusion' ? 'e.g. Parking, Kitchen Access' : 'e.g. Microwave, Water Heater'}">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary"
                            onclick="saveNewFeature('${type}', '${inputId}')">
                        Add ${type === 'inclusion' ? 'Inclusion' : 'Appliance'}
                    </button>
                </div>
            </div>
        </div>`;
    document.body.appendChild(div);
    new bootstrap.Modal(div).show();
    div.addEventListener('hidden.bs.modal', () => div.remove());
}

// ── SAVE NEW FEATURE TO BACKEND ──────────────────────────────────────────────
async function saveNewFeature(type, inputId) {
    const input = document.getElementById(inputId);
    const name  = input ? input.value.trim() : '';

    if (!name) { alert('Please enter a name'); return; }

    const csrf = getCsrfToken();
    if (!csrf) { alert('Security token missing — please refresh.'); return; }

    const url = type === 'inclusion'
        ? '/add-inclusion-management/'
        : '/add-appliance-management/';

    try {
        const res    = await fetch(url, {
            method : 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrf },
            body   : `name=${encodeURIComponent(name)}`,
        });
        const result = await res.json();
        const prefix = activeModal === 'add' ? 'add' : 'edit';

        if (result.success) {
            if (type === 'inclusion') {
                if (!allInclusions.some(i => i.id == result.id))
                    allInclusions.push({ id: result.id, name: result.name });
            } else {
                if (!allAppliances.some(a => a.id == result.id))
                    allAppliances.push({ id: result.id, name: result.name });
            }
            injectFeatureRow(type, result.id, result.name, prefix, true);
            synchronizeFeatureAcrossModals(type, result.id, result.name, prefix);
            closeMiniModal();

        } else if (result.error && result.error.toLowerCase().includes('already exists')) {
            // Feature exists in DB — just show it checked in the current modal
            if (type === 'inclusion') {
                const found = allInclusions.find(i => i.name.toLowerCase() === name.toLowerCase());
                if (found) { injectFeatureRow('inclusion', found.id, found.name, prefix, true); closeMiniModal(); return; }
            } else {
                const found = allAppliances.find(a => a.name.toLowerCase() === name.toLowerCase());
                if (found) { injectFeatureRow('appliance', found.id, found.name, prefix, true); closeMiniModal(); return; }
            }
            alert(result.error);
        } else {
            alert(result.error || `Failed to add ${type}`);
        }
    } catch (e) {
        console.error('saveNewFeature error:', e);
        alert(`Failed to add ${type}. Check console.`);
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
        'add-appliance' : 'dynamicAppliances',
        'edit-inclusion': 'dynamicInclusionsEdit',
        'edit-appliance': 'dynamicAppliancesEdit',
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
        if (type === 'inclusion') roomInclusions = roomInclusions.filter(x => x.id != id);
        else                      roomAppliances = roomAppliances.filter(x => x.id != id);
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

    // Populate Add Room modal each time it opens
    const addRoomModalEl = document.getElementById('addRoomModal');
    if (addRoomModalEl) {
        addRoomModalEl.addEventListener('show.bs.modal', function () {
            activeModal = 'add';
            const incContainer = document.getElementById('dynamicInclusions');
            const appContainer = document.getElementById('dynamicAppliances');
            if (incContainer) incContainer.innerHTML = '';
            if (appContainer) appContainer.innerHTML = '';
            allInclusions.forEach(i => injectFeatureRow('inclusion', i.id, i.name, 'add', false));
            allAppliances.forEach(a => injectFeatureRow('appliance', a.id, a.name, 'add', false));
        });
    }

    // Populate Edit Room modal when an edit button is clicked
    document.querySelectorAll('.edit-room-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            currentRoomId = this.dataset.id;
            activeModal   = 'edit';
            loadRoomFeatures(currentRoomId);
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
        roomAppliances = data.appliances || [];

        activeModal = 'edit';

        const incEdit = document.getElementById('dynamicInclusionsEdit');
        const appEdit = document.getElementById('dynamicAppliancesEdit');
        if (incEdit) incEdit.innerHTML = '';
        if (appEdit) appEdit.innerHTML = '';

        allInclusions.forEach(inc => {
            const checked = roomInclusions.some(r => r.id == inc.id);
            injectFeatureRow('inclusion', inc.id, inc.name, 'edit', checked);
        });
        allAppliances.forEach(app => {
            const checked = roomAppliances.some(r => r.id == app.id);
            injectFeatureRow('appliance', app.id, app.name, 'edit', checked);
        });

    } catch (e) {
        console.error('loadRoomFeatures error:', e);
    }
}

// ── SYNCHRONIZE FEATURE ACROSS ALL MODALS ───────────────────────────────────────
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
    
    // Also sync with the appliance container if needed
    if (type === 'appliance') {
        const otherAppContainerId = `${otherPrefix === 'add' ? 'dynamicAppliances' : 'dynamicAppliancesEdit'}`;
        const otherAppContainer = document.getElementById(otherAppContainerId);
        if (otherAppContainer) {
            const existingAppCheckbox = document.getElementById(`${otherPrefix}_${type}_${id}`);
            if (!existingAppCheckbox) {
                injectFeatureRow(type, id, name, otherPrefix, false);
            }
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