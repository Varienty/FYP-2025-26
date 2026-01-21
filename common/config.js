// Global API Configuration
// Automatically detects environment (localhost vs AWS)

// Detect if running on localhost (development) or AWS (production)
function getApiBase() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Localhost development - use multiple ports
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:5000';  // Single unified backend
    }
    
    // AWS Elastic Beanstalk or any other domain - use same origin
    // This works because all endpoints are now unified at port 5000
    return `${protocol}//${hostname}`;
}

const API_BASE = getApiBase();

// All endpoints now point to the unified backend
window.API_ENDPOINTS = {
    lecturer: API_BASE,
    'lecturer-auth': API_BASE,
    'lecturer-attendance': API_BASE,
    'lecturer-reports': API_BASE,
    'lecturer-schedule': API_BASE,
    'lecturer-notifications': API_BASE,
    'student-service-admin': API_BASE,
    'system-admin': API_BASE
};

// Legacy support - all now use same API_BASE
window.API_BASE = API_BASE;

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
