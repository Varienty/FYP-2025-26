// permissions_manager.js
// Manage staff accounts and roles using database API

(function(){
    const API_BASE = window.API_ENDPOINTS?.['system-admin'] || window.API_BASE || 'http://localhost:5009';
    const ROLES = ['system-admin','student-service-admin','lecturer'];
    const ROLE_LABELS = {
        'system-admin': 'System Administrator',
        'student-service-admin': 'Student Service Administrator',
        'lecturer': 'Lecturer'
    };
    let users = [];
    let editingId = null;

    // DOM
    const usersList = document.getElementById('usersList');
    const btnAddUser = document.getElementById('btnAddUser');
    const userFormCard = document.getElementById('userFormCard');
    const formTitle = document.getElementById('formTitle');
    const inputFirstName = document.getElementById('user_first_name');
    const inputLastName = document.getElementById('user_last_name');
    const inputEmail = document.getElementById('user_email');
    const rolesContainer = document.getElementById('rolesContainer');
    const btnSaveUser = document.getElementById('btnSaveUser');
    const btnCancelUser = document.getElementById('btnCancelUser');
    const searchInput = document.getElementById('searchInput');
    const filterRole = document.getElementById('filterRole');

    async function loadUsersFromDB(){
        try {
            const res = await fetch(`${API_BASE}/api/users`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if(data.ok && data.users){
                users = data.users;
                renderUsers();
            } else {
                console.error('Failed to load users:', data);
                alert('Failed to load users from database');
            }
        } catch(e) {
            console.error('Error loading users:', e);
            alert('Error connecting to database');
        }
    }

    function renderRoleFilters(){
        filterRole.innerHTML = '<option value="">All roles</option>' + 
            ROLES.map(r=>`<option value="${r}">${ROLE_LABELS[r]}</option>`).join('');
    }

    function renderRolesForm(selectedRole){
        rolesContainer.innerHTML = '';
        ROLES.forEach(r => {
            const id = 'role_' + r.replace(/\s+/g,'_');
            const wrapper = document.createElement('label');
            wrapper.className = 'inline-flex items-center gap-2';
            wrapper.innerHTML = `<input type="radio" name="role" value="${r}" id="${id}"> <span class="text-sm">${ROLE_LABELS[r]}</span>`;
            rolesContainer.appendChild(wrapper);
            const radio = document.getElementById(id);
            if(selectedRole === r) radio.checked = true;
        });
    }

    function renderUsers(){
        const q = (searchInput.value||'').toLowerCase();
        const roleFilter = filterRole.value;
        usersList.innerHTML = '';
        const filtered = users.filter(u => {
            const matchQ = !q || (u.name && u.name.toLowerCase().includes(q)) || (u.email && u.email.toLowerCase().includes(q));
            const matchRole = !roleFilter || u.role === roleFilter;
            return matchQ && matchRole;
        });
        if(filtered.length === 0){ 
            usersList.innerHTML = '<div class="p-3 text-sm text-gray-500">No users found.</div>'; 
            return; 
        }

        filtered.forEach(u => {
            const el = document.createElement('div');
            el.className = 'p-4 border rounded-lg flex items-center justify-between gap-3 bg-white hover:bg-gray-50 transition';
            const left = document.createElement('div');
            const statusBadge = u.isActive
                ? '<span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-lg font-semibold">Active</span>'
                : '<span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-lg font-semibold">Inactive</span>';
            left.innerHTML = `
                <div class="font-semibold text-gray-900">${escape(u.name)} ${statusBadge}</div>
                <div class="text-xs text-gray-500 mt-1">${escape(u.email)}</div>
                <div class="text-xs text-gray-600 mt-1">Role: ${ROLE_LABELS[u.role] || u.role}</div>
                <div class="text-xs text-gray-400">ID: ${escape(u.id)}</div>
            `;
            const actions = document.createElement('div');
            actions.className = 'flex gap-2';
            const edit = document.createElement('button');
            edit.className = 'px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-semibold transition';
            edit.textContent = 'Edit';
            edit.onclick = ()=> openForm(u.id);
            const del = document.createElement('button');
            del.className = 'px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-semibold transition';
            del.textContent = 'Delete';
            del.onclick = ()=> { if(confirm(`Delete user ${u.name}?`)) deleteUser(u.id); };
            actions.appendChild(edit);
            actions.appendChild(del);
            el.appendChild(left);
            el.appendChild(actions);
            usersList.appendChild(el);
        });
    }

    function escape(s){ 
        if(!s) return ''; 
        return String(s).replace(/[&<>"']/g, function (c){ 
            return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]); 
        }); 
    }

    function openForm(id){
        editingId = id || null;
        if(editingId){
            formTitle.textContent = 'Edit Staff';
            const u = users.find(x=>x.id===editingId);
            if(u) {
                // Parse name into first and last name
                const nameParts = u.name.split(' ');
                inputFirstName.value = nameParts[0] || '';
                inputLastName.value = nameParts.slice(1).join(' ') || '';
                inputEmail.value = u.email;
                renderRolesForm(u.role);
            }
        } else {
            formTitle.textContent = 'New Staff';
            inputFirstName.value='';
            inputLastName.value='';
            inputEmail.value='';
            renderRolesForm('lecturer'); // default to lecturer
        }
        userFormCard.classList.remove('hidden');
        window.scrollTo({ top: userFormCard.offsetTop - 20, behavior:'smooth' });
    }

    function closeForm(){ 
        editingId = null; 
        userFormCard.classList.add('hidden'); 
    }

    async function saveUser(){
        const firstName = (inputFirstName.value||'').trim();
        const lastName = (inputLastName.value||'').trim();
        const email = (inputEmail.value||'').trim();

        if(!firstName || !lastName || !email){
            alert('First name, last name, and email are required');
            return;
        }

        const selectedRole = rolesContainer.querySelector('input[name=role]:checked')?.value;
        if(!selectedRole) {
            alert('Please select a role');
            return;
        }

        try {
            if(editingId){
                // Update existing user
                const res = await fetch(`${API_BASE}/api/users/${editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        firstName,
                        lastName,
                        email,
                        role: selectedRole
                    })
                });
                const data = await res.json();
                if(!data.ok) {
                    alert('Failed to update user: ' + (data.error || data.message || 'Unknown error'));
                    return;
                }
                alert('User updated successfully');
            } else {
                // Add new user
                const res = await fetch(`${API_BASE}/api/users`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        firstName,
                        lastName,
                        email,
                        password: 'password', // default password
                        role: selectedRole
                    })
                });
                const data = await res.json();
                if(!data.ok) {
                    alert('Failed to add user: ' + (data.error || data.message || 'Unknown error'));
                    return;
                }
                alert('User added successfully with default password: password');
            }
            await loadUsersFromDB();
            closeForm();
        } catch(e) {
            console.error('Error saving user:', e);
            alert('Error connecting to server');
        }
    }

    async function deleteUser(id){ 
        try {
            const res = await fetch(`${API_BASE}/api/users/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if(!data.ok) {
                alert('Failed to delete user: ' + (data.error || data.message || 'Unknown error'));
                return;
            }
            alert('User deleted successfully');
            await loadUsersFromDB();
        } catch(e) {
            console.error('Error deleting user:', e);
            alert('Error connecting to server');
        }
    }

    // wire
    btnAddUser.addEventListener('click', (e)=>{ e.preventDefault(); openForm(); });
    btnCancelUser.addEventListener('click', (e)=>{ e.preventDefault(); closeForm(); });
    btnSaveUser.addEventListener('click', (e)=>{ e.preventDefault(); saveUser(); });
    searchInput.addEventListener('input', ()=> renderUsers());
    filterRole.addEventListener('change', ()=> renderUsers());

    // Navigation logout handler
    const navLogout = document.getElementById('navLogout');
    if (navLogout) {
        navLogout.addEventListener('click', logout);
    }

    // init
    renderRoleFilters(); 
    loadUsersFromDB(); // Load from database instead of localStorage

})();
