// Global API Configuration
// Set API_BASE to your backend server base URLs

// For same-origin deployments, leave as ''
// window.API_BASE = '';

// Development Flask servers - different ports for different roles
window.API_ENDPOINTS = {
    lecturer: 'http://localhost:5003',
    'lecturer-auth': 'http://localhost:5003',
    'lecturer-attendance': 'http://localhost:5004',
    'lecturer-reports': 'http://localhost:5005',
    'lecturer-schedule': 'http://localhost:5006',
    'lecturer-notifications': 'http://localhost:5007',
    'student-service-admin': 'http://localhost:5008',
    'system-admin': 'http://localhost:5009'
};

// Legacy support - default to lecturer port
window.API_BASE = 'http://localhost:5003';

// API endpoint mapping for convenience
window.API_ROUTES = {
    // Lecturer endpoints
    getSchedule: '/api/lecturer/schedule',
    getTodaySchedule: '/api/lecturer/schedule/today',
    getDashboardStats: '/api/lecturer/dashboard/stats',
    startSession: '/api/lecturer/session/start',
    stopSession: '/api/lecturer/session/stop',
    updateSession: '/api/lecturer/session/update',
    getRecords: '/api/lecturer/attendance/records',
    filterRecords: '/api/lecturer/attendance/filter',
    generateReport: '/api/lecturer/report/generate',
    downloadReport: '/api/lecturer/report/download',
    subscribeNotifications: '/api/lecturer/notification/subscribe',
    unsubscribeNotifications: '/api/lecturer/notification/unsubscribe',
    getNotifications: '/api/lecturer/notifications',
    
    // System Admin endpoints
    getUsers: '/api/users',
    addUser: '/api/users',
    updateUser: '/api/users',
    deleteUser: '/api/users',
    getPolicies: '/api/policies',
    addPolicy: '/api/policies',
    updatePolicy: '/api/policies',
    deletePolicy: '/api/policies',
    getDevices: '/api/devices',
    
    // SSA endpoints
    getClasses: '/api/attendance/classes',
    markAttendance: '/api/attendance/mark',
    getDailySummary: '/api/attendance/daily-summary'
};

// Helper: build full URL given endpoint key or path
window.getApiUrl = function(endpointKeyOrPath, role) {
    // Check if it's a key in API_ROUTES
    let path = endpointKeyOrPath;
    if (window.API_ROUTES && window.API_ROUTES[endpointKeyOrPath]) {
        path = window.API_ROUTES[endpointKeyOrPath];
    }
    
    // If role specified, use role-specific endpoint
    if (role && window.API_ENDPOINTS && window.API_ENDPOINTS[role]) {
        return window.API_ENDPOINTS[role] + path;
    }
    
    // Default to API_BASE
    const base = window.API_BASE || '';
    return base + path;
};
