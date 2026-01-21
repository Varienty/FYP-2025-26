(function() {
    'use strict';

    window.requireAuth = function(requiredRole = 'lecturer') {
        const authUser = sessionStorage.getItem('auth_user');
        const isAuthenticated = sessionStorage.getItem('isAuthenticated');
        if (!isAuthenticated || isAuthenticated !== 'true') {
            window.location.href = '../../common/login.html';
            return false;
        }
        try {
            const user = JSON.parse(authUser);
            if (user.role !== requiredRole) {
                alert('Access denied. Insufficient permissions.');
                window.location.href = '../../common/login.html';
                return false;
            }
            return true;
        } catch (e) {
            console.error('Auth error:', e);
            window.location.href = '../../common/login.html';
            return false;
        }
    };

    window.getCurrentUser = function() {
        const authUser = sessionStorage.getItem('auth_user');
        if (!authUser) return null;
        try { return JSON.parse(authUser); } catch (e) { console.error('Failed to parse user data:', e); return null; }
    };

    window.logout = function(role = 'lecturer') {
        const apiBase = window.API_BASE || '';
        const endpoint = role === 'lecturer' ? '/api/lecturer/auth/logout'
                        : role === 'system_admin' ? '/api/admin/logout'
                        : role === 'student_service_admin' ? '/api/ssa/logout'
                        : '/api/lecturer/auth/logout';
        fetch(apiBase + endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
        .catch(() => console.log('Server logout failed, clearing local session'))
        .finally(() => {
            sessionStorage.removeItem('auth_user');
            sessionStorage.removeItem('isAuthenticated');
            localStorage.removeItem('lecturer_active_session');
            localStorage.removeItem('lecturer_notifications');
            alert('Logged out successfully');
            window.location.href = '../../common/login.html';
        });
    };

    window.displayUserInfo = function() {
        const user = getCurrentUser();
        if (!user) return;
        const userNameElement = document.getElementById('userName');
        const userEmailElement = document.getElementById('userEmail');
        if (userNameElement) { userNameElement.textContent = user.email || user.username || 'User'; }
        if (userEmailElement) { userEmailElement.textContent = user.email || ''; }
    };

    document.addEventListener('DOMContentLoaded', function() {
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', function(e) { e.preventDefault(); logout(); });
        });
        displayUserInfo();
    });
})();
