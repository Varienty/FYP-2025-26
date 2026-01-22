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

    window.logout = function() {
        try {
            // Clear session immediately
            sessionStorage.removeItem('auth_user');
            sessionStorage.removeItem('isAuthenticated');
            localStorage.removeItem('lecturer_active_session');
            localStorage.removeItem('lecturer_notifications');
            
            // Clear all sessionStorage and localStorage
            sessionStorage.clear();
            
            // Try to notify server (non-blocking)
            const apiBase = window.location.origin || '';
            fetch(apiBase + '/api/auth/logout', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            }).catch(() => console.log('Server logout notification failed'));
            
            // Redirect to login page - use relative path or absolute path
            const loginPath = window.location.origin ? window.location.origin + '/' : '/';
            window.location.replace(loginPath);
        } catch (e) {
            console.error('Logout error:', e);
            // Still try to redirect even if error
            window.location.replace(window.location.origin ? window.location.origin + '/' : '/');
        }
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
