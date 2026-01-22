# Button/Link Issues Analysis & Debug Guide

## 🔍 What I Found

After extensive analysis of the entire repository, here are the key issues affecting buttons/links on the live server:

---

## 🚨 Issue #1: Hardcoded 127.0.0.1 URLs (CRITICAL)

**Files Affected:**
- `Lecturer/boundary/real_time_list.html` (Lines 206, 322, 466)
- `Lecturer/boundary/class_schedule.html` (Line 131)

**Problem:**
```javascript
fetch(`http://127.0.0.1:5011/api/facial-recognition/sessions/current`)
```

**Impact:** These are hardcoded to localhost and will NEVER work on AWS.

**Solution:** These need to use `window.location.origin` instead of `127.0.0.1:5011`

---

## 🚨 Issue #2: Logout Button Implementation Inconsistency

**Three Different Patterns Found:**

### Pattern 1: Lecturer Dashboard ✅ WORKS
```html
<button data-action="logout">Logout</button>
```
- Uses `data-action="logout"` attribute
- auth.js automatically attaches event listener via `querySelectorAll('[data-action="logout"]')`

### Pattern 2: System Admin Dashboard ⚠️ SHOULD WORK
```html
<button id="btnLogout">Logout</button>
<script>
    document.getElementById('btnLogout').addEventListener('click', function() {
        logout();
    });
</script>
```
- Manually attaches event listener
- Calls `logout()` from auth.js

### Pattern 3: SSA Dashboard ⚠️ SHOULD WORK
```html
<button id="logoutBtn">Logout</button>
<script>
    document.getElementById('logoutBtn').addEventListener('click', () => {
        logout();
    });
</script>
```
- Manually attaches event listener
- Calls `logout()` from auth.js

**Why they might not work on AWS:**
- Scripts might be loading in wrong order
- Browser console errors blocking execution
- CORS issues preventing fetch calls

---

## 🚨 Issue #3: API Base URL Redefinition

**Found in almost EVERY HTML file:**
```javascript
// config.js is loaded in <head>
<script src="../../common/config.js"></script>

// But then REDEFINED inside the page script:
const API_BASE = window.location.origin || 'http://localhost:5000';
```

**Why this is a problem:**
- While `window.location.origin` SHOULD work on AWS, having duplicate definitions can cause confusion
- Better to use `window.API_BASE` from config.js

---

## 🛠️ Debug Tools I Created

### 1. Debug Test Page
**URL:** http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug

**What it tests:**
- ✅ Configuration (window.API_BASE, window.location.origin)
- ✅ Auth functions (logout, getCurrentUser, requireAuth)
- ✅ Session storage
- ✅ Logout buttons (both patterns)
- ✅ API endpoints (/health/db, /api/auth/login, /api/auth/logout)

### 2. Console Logging
Added detailed console logging to `auth.js`:
```javascript
console.log('[AUTH] Logout function called');
console.log('[AUTH] Clearing session storage...');
console.log('[AUTH] Redirecting to:', loginPath);
```

**To view logs:**
1. Open browser developer tools (F12)
2. Go to Console tab
3. Try clicking logout button
4. Check for `[AUTH]` prefixed messages

---

## 🧪 How to Debug

### Step 1: Access Debug Page
1. Visit: http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug
2. Check all 5 test sections
3. Note any red "✗" errors

### Step 2: Test Logout on Actual Pages
1. Login to any dashboard (System Admin, SSA, or Lecturer)
2. Open browser console (F12 → Console tab)
3. Click the Logout button
4. Check console for `[AUTH]` messages
5. Note any errors

### Step 3: Check Network Tab
1. Open browser developer tools (F12)
2. Go to Network tab
3. Click logout button
4. Look for failed requests (red status codes)
5. Click on failed request to see details

---

## 🔧 Expected Console Output (Working Logout)

```
[AUTH] Logout function called
[AUTH] Clearing session storage...
[AUTH] Session cleared
[AUTH] Notifying server at: http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/api/auth/logout
[AUTH] Redirecting to: http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/
[AUTH] Server notified
```

Then the page should redirect to login.

---

## 🚑 Common Issues & Fixes

### Issue: "logout is not defined"
**Cause:** auth.js not loaded or script error
**Fix:** Check browser console for script loading errors

### Issue: Button click does nothing
**Cause:** Event listener not attached
**Debug:**
```javascript
// In browser console:
document.getElementById('logoutBtn') // Should return the button element
window.logout // Should return: function
```

### Issue: Logout redirects but session persists
**Cause:** Session not being cleared
**Debug:**
```javascript
// In browser console after logout:
sessionStorage.getItem('isAuthenticated') // Should be null
```

### Issue: CORS errors
**Cause:** API endpoint not allowing cross-origin requests
**Fix:** Already handled in Flask with `CORS(app)` in main.py

---

## 📋 Recommended Fixes

### Fix 1: Remove Hardcoded 127.0.0.1 URLs
**Files to update:**
- `Lecturer/boundary/real_time_list.html`
- `Lecturer/boundary/class_schedule.html`

**Change from:**
```javascript
fetch(`http://127.0.0.1:5011/api/facial-recognition/...`)
```

**Change to:**
```javascript
fetch(`${window.location.origin}/api/facial-recognition/...`)
```

### Fix 2: Standardize Logout Buttons
**Recommendation:** Use `data-action="logout"` everywhere

**Replace:**
```html
<button id="logoutBtn" onclick="logout()">Logout</button>
```

**With:**
```html
<button data-action="logout" class="bg-red-500...">Logout</button>
```

This way auth.js handles it automatically.

### Fix 3: Use window.API_BASE Consistently
**Instead of redefining:**
```javascript
const API_BASE = window.location.origin || 'http://localhost:5000';
```

**Use:**
```javascript
const API_BASE = window.API_BASE || window.location.origin || 'http://localhost:5000';
```

---

## 🎯 Next Steps

1. **Test debug page first:** http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug
2. **Check console logs** when clicking logout on any dashboard
3. **Report specific error messages** from browser console
4. **Test with different browsers** (Chrome, Firefox, Edge)
5. **Check if issue is browser-specific** (cache, cookies)

---

## 📱 Browser-Specific Testing

### Clear Cache & Test
```
Chrome: Ctrl+Shift+Delete → Clear browsing data
Firefox: Ctrl+Shift+Delete → Clear history
Edge: Ctrl+Shift+Delete → Clear browsing data
```

### Incognito/Private Mode Test
- Open incognito window
- Visit site fresh
- Test logout immediately

This eliminates cached script issues.

---

*Debug tools deployed: January 22, 2026*
*Status: Awaiting user test results*
