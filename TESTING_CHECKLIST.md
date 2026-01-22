# Testing Checklist - Database Connection Fixes

## 🔧 Deployment Status
- ✅ Commit 38b201c: Connection pool & try-finally fixes deployed
- ✅ Commit 3a297d1: Enhanced debug page deployed
- ✅ Environment: Green health status
- ✅ Time: 2026-01-22 15:44:56

---

## 📋 Debug Page Tests (Section 6)

### System Admin Endpoints
- [ ] Click "Test /api/policies" → Should show "X records returned"
- [ ] Click "Test /api/users" → Should show "X records returned"

### Student Service Admin Endpoints
- [ ] Click "Test /api/ssa/modules" → Should show "X records returned"
- [ ] Click "Test /api/ssa/lecturers" → Should show "X records returned"
- [ ] Click "Test /api/ssa/students" → Should show "X records returned" (750+)
- [ ] Click "Test /api/ssa/timetable" → Should show "X records returned"

### Attendance Endpoints
- [ ] Click "Test /api/attendance/classes" → Should show "X records returned"
- [ ] Click "Test /api/attendance/daily-summary" → Should show "X records returned"

### Lecturer Endpoints
- [ ] Click "Test /api/lecturer/classes" → Should show "X records returned"
- [ ] Click "Test /api/lecturer/attendance" → Should show "X records returned"
- [ ] Click "Test /api/lecturer/reports" → Should show "X records returned"
- [ ] Click "Test /api/lecturer/dashboard/stats" → Should show "1 records returned"

---

## 🌐 Application Page Tests

### System Administrator
- [ ] Login with `admin@attendance.com` / `password`
- [ ] Navigate to "Attendance Policies"
- [ ] Verify policies load WITHOUT error
- [ ] Check console for errors

### Student Service Administrator
- [ ] Login with `ssa@attendance.com` / `password`
- [ ] Navigate to "Timetable Management"
- [ ] Verify timetable loads WITHOUT error
- [ ] Navigate to "Upload Class List"
- [ ] Verify modules/students load WITHOUT error
- [ ] Check console for errors

### Lecturer
- [ ] Login with `lecturer1@attendance.com` / `password`
- [ ] Navigate to "Class Schedule"
- [ ] Verify schedule loads WITHOUT error
- [ ] Navigate to "Real-time Attendance List"
- [ ] Check console for errors

### Student
- [ ] Login with `student1@attendance.com` / `password`
- [ ] Verify dashboard loads WITHOUT error
- [ ] Check console for errors

---

## 🔍 Error Monitoring

While running tests, watch browser console (F12) for:
- [ ] NO "pool exhausted" errors
- [ ] NO "Failed getting connection" messages
- [ ] NO "INTERNAL SERVER ERROR" in responses
- [ ] NO 500 status codes in Network tab

---

## 📊 Expected Data Counts

From database (750+ records imported):
- Policies: ~10 records
- Users: ~23 records (admin, SSA, lecturers)
- Modules: ~15 records
- Lecturers: ~9 records
- Students: 750+ records
- Timetable: ~45 records
- Attendance Records: 717+ records
- Daily Summary: ~30 days of data

---

## ✅ Success Indicators

- [ ] All debug page tests show "X records returned" (no errors)
- [ ] All application pages load data without "pool exhausted" errors
- [ ] System Admin can manage policies
- [ ] SSA can view and manage all data
- [ ] Lecturers can see their classes and attendance
- [ ] Browser console is clean (no errors)
- [ ] No "Failed to load" messages on any page

---

## 📸 Screenshots Needed

Please share screenshots of:
1. Debug page Section 6 after running all database tests
2. System Admin → Attendance Policies page
3. SSA → Timetable Management page
4. Browser console (F12 → Console tab) showing no errors

---

## 🚨 If Issues Occur

If you see any errors, check:
1. **Error message** - Note exact text
2. **Which page/endpoint** - Record the URL
3. **Browser console** - F12 → Console tab, copy error
4. **Network tab** - F12 → Network, check API response
5. **Which role** - System Admin, SSA, Lecturer, or Student

Then share:
- Screenshot of the error
- Browser console output
- Network tab showing failed request response

---

## 📞 Support

If all tests pass: ✅ System is working correctly!

If tests fail: Check error details above and share with full context.

---

**Test Date:** _______________  
**Tester Name:** _______________  
**Result:** ✅ PASS / ❌ FAIL  

