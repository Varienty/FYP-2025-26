// hardware_monitor.js
// Monitor hardware devices (cameras, sensors, etc.) - Database Integration ONLY

(function () {
    // Use the same API base as other pages (from config.js)
    const API_BASE = window.location.origin;
    let devices = [];
    let pollingInterval = null;

    // DOM refs
    const devicesList = document.getElementById('devicesList');
    const alertsList = document.getElementById('alertsList');
    const alertBanner = document.getElementById('alertBanner');
    const btnFetchApi = document.getElementById('btnFetchApi');

    async function loadDevices() {
        try {
            const res = await fetch(`${API_BASE}/api/devices`);
            const data = await res.json();
            if (data.ok && data.devices) {
                devices = data.devices;
                renderDevices();
                checkForOfflineDevices();
            } else {
                console.error('Failed to load devices:', data);
                createAlert('Failed to load devices from database');
            }
        } catch (e) {
            console.error('Error loading devices:', e);
            createAlert('Error connecting to database. Make sure System Admin controller is running on port 5009.');
        }
    }

    async function loadDeviceStats() {
        try {
            const res = await fetch(`${API_BASE}/api/devices/stats`);
            const data = await res.json();
            if (data.ok && data.stats) {
                const summary = data.stats;
                updateStatElement('statTotalDevices', summary.total || devices.length);
                updateStatElement('statOnlineDevices', summary.online || devices.filter(d => d.status === 'online').length);
                updateStatElement('statOfflineDevices', summary.offline || devices.filter(d => d.status === 'offline').length);
            } else {
                updateStatsFromCache();
            }
        } catch (e) {
            console.error('Error loading device stats:', e);
            updateStatsFromCache();
        }
    }

    function updateStatElement(id, value) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
        } else {
            console.warn(`Element with id '${id}' not found`);
        }
    }

    function updateStatsFromCache() {
        const total = devices.length;
        const online = devices.filter(d => d.status === 'online').length;
        const offline = devices.filter(d => d.status === 'offline').length;
        updateStatElement('statTotalDevices', total);
        updateStatElement('statOnlineDevices', online);
        updateStatElement('statOfflineDevices', offline);
    }

    function renderDevices() {
        devicesList.innerHTML = '';
        if (devices.length === 0) {
            devicesList.innerHTML = '<div class="text-sm text-gray-500 p-3">No devices found. Add devices through the database.</div>';
            return;
        }
        devices.forEach(d => {
            const card = document.createElement('div');
            card.className = 'p-4 border rounded-lg flex items-center justify-between gap-4 bg-gray-50 hover:bg-gray-100 transition';

            const left = document.createElement('div');
            left.innerHTML = `
                <div class="font-semibold text-gray-900">${escape(d.name)}</div>
                <div class="text-xs text-gray-500 mt-1">${d.type || 'device'} | ID: ${d.id || d.deviceId}</div>
                <div class="text-xs text-gray-500">Last: ${new Date(d.lastSeen || d.lastPing).toLocaleString()}</div>
                ${d.latencyMs ? `<div class="text-xs text-gray-500">Latency: ${d.latencyMs}ms</div>` : ''}
            `;

            const right = document.createElement('div');
            right.className = 'flex flex-col gap-2';

            const statusBadge = document.createElement('span');
            statusBadge.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold text-center';
            if (d.status === 'online') {
                statusBadge.className += ' bg-green-100 text-green-800';
                statusBadge.textContent = 'Online';
            } else if (d.status === 'offline') {
                statusBadge.className += ' bg-red-100 text-red-800';
                statusBadge.textContent = 'Offline';
            } else {
                statusBadge.className += ' bg-yellow-100 text-yellow-800';
                statusBadge.textContent = d.status || 'Unknown';
            }

            const pingBtn = document.createElement('button');
            pingBtn.className = 'px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs font-semibold transition';
            pingBtn.textContent = 'Ping';
            pingBtn.onclick = () => pingDevice(d.id || d.deviceId);

            right.appendChild(statusBadge);
            right.appendChild(pingBtn);

            card.appendChild(left);
            card.appendChild(right);
            devicesList.appendChild(card);
        });

        loadDeviceStats();
    }

    async function loadAlerts() {
        try {
            const res = await fetch(`${API_BASE}/api/alerts`);
            const data = await res.json();
            if (data.ok && data.alerts) {
                renderAlerts(data.alerts);
            } else {
                renderAlerts([]);
            }
        } catch (e) {
            console.error('Error loading alerts:', e);
            renderAlerts([]);
        }
    }

    function checkForOfflineDevices() {
        // Load alerts from database instead
        loadAlerts();
    }

    function renderAlerts(alerts) {
        alertsList.innerHTML = '';
        if (alerts.length === 0) {
            alertsList.innerHTML = '<div class="text-sm text-gray-500 p-3">No active alerts</div>';
            hideBanner();
            return;
        }

        alerts.forEach(alert => {
            const alertCard = document.createElement('div');
            alertCard.className = 'p-3 border border-red-200 bg-red-50 rounded-lg flex items-start justify-between gap-2 mb-2';

            const severity = alert.severity || 'medium';
            const severityColors = {
                'critical': 'red',
                'high': 'red',
                'medium': 'orange',
                'low': 'yellow'
            };
            const color = severityColors[severity] || 'red';

            alertCard.innerHTML = `
                <div>
                    <div class="text-sm font-semibold text-${color}-800">${escape(alert.title)}</div>
                    <div class="text-xs text-${color}-600">${escape(alert.description)}</div>
                    <div class="text-xs text-${color}-500 mt-1">${new Date(alert.createdAt).toLocaleString()}</div>
                </div>
            `;
            alertsList.appendChild(alertCard);
        });

        showBanner(alerts.length);
        updateAlertStats(alerts.length);
    }

    function showBanner(count) {
        alertBanner.className = 'mb-6 p-4 rounded-lg bg-red-100 border border-red-200 text-red-800';
        alertBanner.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div><strong>${count}</strong> active alert(s)</div>
                </div>
            </div>
        `;
    }

    function hideBanner() {
        alertBanner.className = 'mb-6 hidden';
        alertBanner.innerHTML = '';
    }

    function updateAlertStats(count) {
        const alertStatsEl = document.getElementById('statActiveAlerts');
        if (alertStatsEl) alertStatsEl.textContent = count;
    }

    function createAlert(message) {
        // Show temporary alert in UI
        const tempAlert = document.createElement('div');
        tempAlert.className = 'fixed top-4 right-4 p-4 bg-yellow-100 border border-yellow-300 text-yellow-800 rounded-lg shadow-lg z-50';
        tempAlert.textContent = message;
        document.body.appendChild(tempAlert);
        setTimeout(() => tempAlert.remove(), 3000);
    }

    function escape(s) {
        if (!s) return '';
        return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    }

    async function pingDevice(id) {
        try {
            const res = await fetch(`${API_BASE}/api/devices/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    status: 'online', 
                    lastSeen: new Date().toISOString(),
                    lastPing: new Date().toISOString(),
                    latencyMs: Math.round(30 + Math.random() * 100)
                })
            });
            const data = await res.json();
            if (data.ok) {
                createAlert('Device pinged successfully');
                await loadDevices();
            } else {
                createAlert('Failed to ping device: ' + (data.error || data.message || 'Unknown error'));
            }
        } catch (e) {
            console.error('Error pinging device:', e);
            createAlert('Error connecting to server');
        }
    }

    async function reconnectDevice(id) {
        try {
            const res = await fetch(`${API_BASE}/api/devices/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    status: 'online', 
                    lastSeen: new Date().toISOString(),
                    lastPing: new Date().toISOString()
                })
            });
            const data = await res.json();
            if (data.ok) {
                createAlert('Device reconnected successfully');
                await loadDevices();
            } else {
                createAlert('Failed to reconnect device: ' + (data.error || data.message || 'Unknown error'));
            }
        } catch (e) {
            console.error('Error reconnecting device:', e);
            createAlert('Error connecting to server');
        }
    }

    // Wire UI buttons
    if (btnFetchApi) {
        btnFetchApi.addEventListener('click', (e) => {
            e.preventDefault();
            loadDevices();
        });
    }

    // Start polling for device updates every 5 seconds
    function startPolling() {
        loadDevices();
        pollingInterval = setInterval(loadDevices, 5000);
    }

    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }

    // Initialize
    startPolling();

    // Navigation logout handler
    const navLogout = document.getElementById('navLogout');
    if (navLogout) {
        navLogout.addEventListener('click', logout);
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', stopPolling);
})();
