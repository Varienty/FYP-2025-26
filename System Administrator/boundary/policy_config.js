// policy_config.js
// Attendance Policy Manager - Database Integration ONLY

(function () {
    const API_BASE = window.API_ENDPOINTS?.['system-admin'] || window.API_BASE || 'http://localhost:5009';
    const SSA_API_BASE = window.API_ENDPOINTS?.['student-service-admin'] || 'http://localhost:5008';
    let policies = [];
    let modules = [];
    let editingId = null;

    // DOM refs
    const policiesList = document.getElementById('policiesList');
    const btnAdd = document.getElementById('btnAddPolicy');
    const formContainer = document.getElementById('policyFormContainer');
    const formTitle = document.getElementById('formTitle');
    const inputModuleId = document.getElementById('module_id');
    const inputGrace = document.getElementById('grace_period');
    const inputLate = document.getElementById('late_threshold');
    const btnSave = document.getElementById('btnSavePolicy');
    const btnCancel = document.getElementById('btnCancelPolicy');

    async function loadModules() {
        try {
            const res = await fetch(`${SSA_API_BASE}/api/ssa/modules`);
            const data = await res.json();
            if (data.ok && data.modules) {
                modules = data.modules;
                populateModules();
            } else {
                console.error('Failed to load modules:', data);
            }
        } catch (e) {
            console.error('Error loading modules:', e);
        }
    }

    function populateModules() {
        inputModuleId.innerHTML = '<option value="">Select a module...</option>';
        modules.forEach(m => {
            const option = document.createElement('option');
            option.value = m.id;
            option.textContent = `${m.module_code} - ${m.module_name}`;
            inputModuleId.appendChild(option);
        });
    }

    async function loadPolicies() {
        try {
            const res = await fetch(`${API_BASE}/api/policies`);
            const data = await res.json();
            if (data.ok && data.policies) {
                policies = data.policies;
                renderPolicies();
            } else {
                console.error('Failed to load policies:', data);
                alert('Failed to load policies from database');
            }
        } catch (e) {
            console.error('Error loading policies:', e);
            alert('Error connecting to database. Make sure the System Admin controller is running on port 5009.');
        }
    }

    function renderPolicies() {
        policiesList.innerHTML = '';
        if (policies.length === 0) {
            policiesList.innerHTML = '<div class="text-sm text-gray-500 p-3">No policies found. Create one to get started.</div>';
            return;
        }

        policies.forEach(p => {
            const card = document.createElement('div');
            card.className = 'border rounded p-3 bg-gray-50';
            const status = p.isActive ? '<span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>' : '<span class="text-xs bg-gray-300 text-gray-700 px-2 py-1 rounded">Inactive</span>';

            // Find module name
            const module = modules.find(m => m.id == p.moduleId);
            const moduleName = module ? `${module.module_code} - ${module.module_name}` : 'Unknown Module';

            card.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold">${escape(moduleName)}</h3>
                    ${status}
                </div>
                <div class="text-xs text-gray-700 space-y-1">
                    <div><strong>Grace Period:</strong> ${p.gracePeriod} minutes</div>
                    <div><strong>Late Threshold:</strong> ${p.lateThreshold} minutes</div>
                </div>
                <div class="flex gap-2 mt-2">
                    <button class="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm" onclick="window.editPolicy('${p.id || p.policyId}')">Edit</button>
                    <button class="px-3 py-1 bg-red-100 text-red-800 rounded text-sm" onclick="window.deletePolicy('${p.id || p.policyId}')">Delete</button>
                </div>
            `;
            policiesList.appendChild(card);
        });
    }

    function escape(s) {
        if (!s) return '';
        return String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
    }

    function openForm(id) {
        editingId = id || null;
        if (editingId) {
            formTitle.textContent = 'Edit Policy';
            const p = policies.find(x => (x.id || x.policyId) === editingId);
            if (p) {
                inputModuleId.value = p.moduleId || '';
                inputGrace.value = p.gracePeriod;
                inputLate.value = p.lateThreshold;
            }
        } else {
            formTitle.textContent = 'New Policy';
            inputModuleId.value = '';
            inputGrace.value = '10';
            inputLate.value = '15';
        }
        formContainer.classList.remove('hidden');
    }

    function closeForm() {
        editingId = null;
        formContainer.classList.add('hidden');
    }

    async function savePolicy() {
        const moduleId = parseInt(inputModuleId.value);
        const gracePeriod = parseInt(inputGrace.value);
        const lateThreshold = parseInt(inputLate.value);

        if (!moduleId || isNaN(gracePeriod) || isNaN(lateThreshold)) {
            alert('Please fill in all required fields with valid values');
            return;
        }

        const policyData = {
            moduleId,
            gracePeriod,
            lateThreshold,
            isActive: true
        };

        try {
            if (editingId) {
                const res = await fetch(`${API_BASE}/api/policies/${editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(policyData)
                });
                const data = await res.json();
                if (!data.ok) {
                    alert('Failed to update policy: ' + (data.error || data.message || 'Unknown error'));
                    return;
                }
                alert('Policy updated successfully');
            } else {
                const res = await fetch(`${API_BASE}/api/policies`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(policyData)
                });
                const data = await res.json();
                if (!data.ok) {
                    alert('Failed to create policy: ' + (data.error || data.message || 'Unknown error'));
                    return;
                }
                alert('Policy created successfully');
            }
            await loadPolicies();
            closeForm();
        } catch (e) {
            console.error('Error saving policy:', e);
            alert('Error connecting to server');
        }
    }

    async function deletePolicy(id) {
        if (!confirm('Are you sure you want to delete this policy?')) return;
        try {
            const res = await fetch(`${API_BASE}/api/policies/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if (!data.ok) {
                alert('Failed to delete policy: ' + (data.error || data.message || 'Unknown error'));
                return;
            }
            alert('Policy deleted successfully');
            await loadPolicies();
        } catch (e) {
            console.error('Error deleting policy:', e);
            alert('Error connecting to server');
        }
    }

    btnAdd.addEventListener('click', (e) => { e.preventDefault(); openForm(); });
    btnCancel.addEventListener('click', (e) => { e.preventDefault(); closeForm(); });
    btnSave.addEventListener('click', (e) => { e.preventDefault(); savePolicy(); });

    window.editPolicy = openForm;
    window.deletePolicy = deletePolicy;

    // Navigation logout handler
    const navLogout = document.getElementById('navLogout');
    if (navLogout) {
        navLogout.addEventListener('click', logout);
    }

    // Initialize: Load modules first, then policies
    async function initialize() {
        await loadModules();
        await loadPolicies();
    }

    initialize();
})();
