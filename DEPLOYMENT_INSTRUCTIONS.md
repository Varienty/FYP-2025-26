# 🚀 AWS Deployment - Simplified Instructions

## ⏳ Step 1: Delete Stuck Environment (Do This Now)

1. Go to: https://console.aws.amazon.com/elasticbeanstalk
2. **Top right** - Change region to **ap-southeast-1**
3. Click on **attendance-prod** environment
4. Click **Actions** dropdown (top right)
5. Click **"Terminate environment"**
6. Type the environment name **attendance-prod** and confirm
7. **Wait 5-10 minutes for deletion**

**Status check (in PowerShell):**
```powershell
cd c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26
eb status
# Should show: No environment found (once deleted)
```

---

## ✅ Step 2: Once Deleted, Create Fresh Environment

After the environment is deleted, run this:

```powershell
cd c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26

# Remove old EB config
Remove-Item .elasticbeanstalk -Recurse -Force -ErrorAction SilentlyContinue

# Re-initialize
eb init -p python-3.11 attendance-system --region ap-southeast-1

# Create new environment (MUCH SIMPLER NOW)
eb create attendance-prod --instance-type t2.micro
```

This will take 5-10 minutes. The new environment should launch cleanly because:
- ✅ Simplified main.py (no complex imports)
- ✅ Simplified python.config (minimal settings)
- ✅ No database issues (we'll add that later if needed)

---

## ✅ Step 3: Once Environment is Ready

Check status:
```powershell
eb status
# Should show: Status: Ready, Health: Green
```

Test your app:
```powershell
eb open
# Opens your live app in browser

# Or test the health endpoint
$url = eb open --print-url
curl "$url/health"
```

---

## 📝 Files We've Simplified

✅ **main.py** - Now just 30 lines, very clean  
✅ **.ebextensions/python.config** - Minimal, only essentials  
✅ **Removed** - rds.config (causing errors)

---

## 🎯 Next: Add the Real Controllers

Once environment is Ready, we can gradually add back your actual Flask controllers one at a time.

---

## 📞 Quick Help

**Environment still stuck?**
- Wait 10 more minutes and try `eb status` again
- If still stuck, delete from AWS Console manually

**Deployment failed?**
```powershell
eb logs
```

**Need to start completely over?**
```powershell
eb terminate --all --force  # Deletes everything
rm .elasticbeanstalk -r -fo  # Remove config
# Then start from step above
```

---

**Status: Ready for fresh deployment** ✅
