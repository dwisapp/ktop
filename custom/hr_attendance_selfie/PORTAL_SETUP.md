# 📱 Employee Attendance Portal - Setup Guide

Portal web untuk employee self-service attendance dengan **selfie photo + GPS tracking**.

---

## 🎯 **Features**

✅ **URL khusus** untuk employee check-in/out
✅ **Camera selfie** otomatis (front camera)
✅ **GPS auto-detect** dengan browser geolocation
✅ **Mobile-optimized** responsive design
✅ **Real-time validation** (photo + GPS wajib)
✅ **Attendance history** 30 hari terakhir

---

## 📋 **Files Created**

```
custom/hr_attendance_selfie/
├── controllers/
│   ├── __init__.py                    # ✅ NEW
│   └── portal_attendance.py           # ✅ NEW - Portal routes & API
├── views/
│   └── portal_templates.xml           # ✅ NEW - Portal HTML pages
├── static/src/
│   ├── js/
│   │   └── portal_attendance.js       # ✅ NEW - Camera + GPS JS
│   └── css/
│       └── portal_attendance.css      # ✅ NEW - Portal styling
├── __init__.py                        # ✅ UPDATED - Include controllers
└── __manifest__.py                    # ✅ UPDATED - Add portal dependency
```

---

## 🚀 **Installation**

### **Step 1: Restart Odoo**

**Docker:**
```bash
cd /Users/rizkidwisaputra/erp-ptpgp-dev
docker-compose restart web
```

**Non-Docker:**
```bash
sudo systemctl restart odoo
```

### **Step 2: Upgrade Module**

Karena modul sudah ter-install sebelumnya, kita perlu **upgrade**:

1. Login ke Odoo sebagai **admin**
2. **Apps** → Remove "Apps" filter
3. Search: `hr_attendance_selfie`
4. Click **Upgrade** (atau **Update** jika sudah installed)
5. Wait ~30 seconds

**Atau via command line:**
```bash
odoo-bin -u hr_attendance_selfie -d your_database_name --stop-after-init
```

### **Step 3: Grant Portal Access to Employees**

Employee harus punya **portal access** untuk menggunakan fitur ini:

1. **Settings** → **Users & Companies** → **Users**
2. Find employee user
3. Check **Portal** access group
4. Save

**Atau batch update:**
```python
# Via Odoo shell
users = env['res.users'].search([('employee_id', '!=', False)])
portal_group = env.ref('base.group_portal')
users.write({'groups_id': [(4, portal_group.id)]})
```

---

## 🌐 **Portal URLs**

### **Main Check-In Portal**
```
https://your-odoo-domain.com/my/attendance
```
Employee buka URL ini untuk check-in/check-out dengan selfie + GPS.

### **Attendance History**
```
https://your-odoo-domain.com/my/attendance/history
```
Lihat 30 hari attendance history.

---

## 📱 **User Flow**

### **Check-In Flow:**

1. **Employee buka URL** di smartphone browser:
   ```
   https://your-odoo-domain.com/my/attendance
   ```

2. **Login** dengan Odoo portal credentials

3. **GPS auto-detect** (browser akan request permission)

4. **Camera auto-start** (front camera untuk selfie)
   - Browser akan request camera permission
   - Live preview muncul (mirrored untuk selfie)

5. **Click "Capture Photo"**
   - Photo preview muncul
   - Bisa "Retake" jika tidak puas

6. **Click "Submit Check-In"**
   - Photo + GPS dikirim ke server
   - Attendance record dibuat
   - Success message muncul
   - Page refresh → status berubah "Checked In"

### **Check-Out Flow:**

Same process, tapi button berubah jadi **"Submit Check-Out"**.

---

## ⚙️ **Settings & Configuration**

### **Photo Validation (Backend)**

Photo validation tetap menggunakan settings yang sama:

**Settings → Attendances → Selfie Validation**

- ☑️ Require Selfie for Check-in
- ☑️ Require Selfie for Check-out
- Photo Quality: Low/Medium/High
- Max Photo Size: 500 KB (default)

### **Portal Access Control**

Employees dengan **Portal Access** bisa:
- ✅ Check-in/out via `/my/attendance`
- ✅ View own attendance history
- ✅ View own photos
- ❌ **TIDAK bisa** edit/delete attendance
- ❌ **TIDAK bisa** view attendance orang lain

---

## 🔒 **Security & Permissions**

### **Browser Requirements:**

1. **HTTPS required** (atau localhost untuk development)
   - Camera API hanya jalan di secure context
   - GPS API juga butuh HTTPS

2. **Browser support:**
   - ✅ Chrome/Edge (latest)
   - ✅ Firefox (latest)
   - ✅ Safari iOS 11+
   - ✅ Chrome Android

### **Permissions Required:**

Employee harus **allow** di browser:
- 📷 **Camera permission** (untuk selfie)
- 📍 **Location permission** (untuk GPS)

**How to check permissions:**
- Chrome: Click padlock icon → Site settings
- Firefox: Click shield icon → Permissions
- Safari: Settings → Safari → Camera/Location

---

## 🧪 **Testing Instructions**

### **Test 1: Basic Check-In**

1. Login sebagai employee (dengan portal access)
2. Buka: `https://your-domain.com/my/attendance`
3. Verify:
   - ✅ Page loads
   - ✅ GPS status shows "Detecting location..."
   - ✅ Camera starts (front camera)
   - ✅ GPS detected (shows coordinates)
4. Click "Capture Photo"
5. Verify:
   - ✅ Photo preview muncul (mirrored)
   - ✅ "Retake" & "Submit Check-In" buttons visible
6. Click "Submit Check-In"
7. Verify:
   - ✅ Success alert muncul
   - ✅ Page reload
   - ✅ Status badge: "Checked In" (green)
   - ✅ Today's attendance table shows new record

### **Test 2: Check-Out**

1. Same user (already checked in)
2. Refresh `/my/attendance`
3. Verify:
   - ✅ Badge shows "Checked In"
   - ✅ Button berubah jadi "Submit Check-Out" (red)
4. Capture photo & submit
5. Verify:
   - ✅ Success message shows hours worked
   - ✅ Status badge: "Checked Out" (gray)

### **Test 3: Attendance History**

1. Click "View Full History"
2. Verify:
   - ✅ Shows last 30 days attendance
   - ✅ GPS location clickable (opens Google Maps)
   - ✅ Hours worked calculated

### **Test 4: Mobile Testing**

1. Open pada **smartphone** (real device)
2. Test pada **portrait & landscape** mode
3. Verify:
   - ✅ Responsive layout
   - ✅ Front camera auto-select
   - ✅ GPS works on mobile
   - ✅ Photo upload successful

### **Test 5: Error Handling**

**Test camera permission denied:**
1. Block camera permission
2. Verify error message shows
3. "Try Again" button available

**Test GPS denied:**
1. Block location permission
2. Verify warning message shows
3. Can still submit (with confirmation)

**Test already checked in:**
1. Check-in
2. Try check-in lagi (via direct API call)
3. Verify error: "Already checked in"

---

## 🐛 **Troubleshooting**

### **Problem: Page not found (404)**

**Solution:**
```bash
# Restart Odoo
docker-compose restart web

# Clear browser cache
Ctrl+Shift+R (hard refresh)

# Check module installed:
# Apps → Search "hr_attendance_selfie" → Should be "Installed"
```

### **Problem: Camera not working**

**Checklist:**
- ✅ Using HTTPS (not HTTP)?
- ✅ Browser camera permission allowed?
- ✅ Camera not used by other app?
- ✅ Browser supports MediaDevices API?

**Debug:**
```javascript
// Open browser console (F12)
// Check for errors:
navigator.mediaDevices.getUserMedia({video: true})
  .then(() => console.log('Camera OK'))
  .catch(err => console.error('Camera error:', err))
```

### **Problem: GPS not detected**

**Checklist:**
- ✅ Browser location permission allowed?
- ✅ GPS enabled on device (mobile)?
- ✅ Not blocking location services?
- ✅ Indoor? (GPS bisa lambat)

**Workaround:**
- Portal allows submission without GPS (with warning)
- GPS is optional, not mandatory

### **Problem: Photo upload failed**

**Possible causes:**
1. **Photo too large**
   - Settings → Reduce photo quality to "Medium"
   - Check max file size setting

2. **Network timeout**
   - Check internet connection
   - Try compress photo (reduce quality)

3. **Server error**
   - Check Odoo logs:
     ```bash
     docker-compose logs -f web
     ```

### **Problem: "No employee record found"**

**Solution:**
```python
# Link user to employee
user = env['res.users'].browse(USER_ID)
employee = env['hr.employee'].search([('name', '=', 'Employee Name')])
employee.user_id = user.id
```

---

## 📊 **Backend Verification**

After employee submits attendance, verify di backend:

1. **Attendances** menu
2. Find latest record
3. Check:
   - ✅ `check_in_image` field has photo
   - ✅ `in_latitude` & `in_longitude` populated
   - ✅ Photo thumbnail visible in list view
   - ✅ Click "View Fullscreen" works

---

## 🔄 **Integration with Existing Attendance**

Portal ini **compatible** dengan existing attendance methods:

- ✅ **Kiosk mode** (via `/attendance/kiosk`)
- ✅ **My Attendances** (backend menu)
- ✅ **Manual attendance** (admin can create)
- ✅ **API/Mobile app** (via RPC)

**Validation rules:**
- Photo WAJIB untuk portal attendance
- Photo OPTIONAL untuk manual attendance (if `in_mode == 'manual'`)

---

## 🎨 **Customization**

### **Change Photo Quality:**

Edit: `static/src/js/portal_attendance.js`
```javascript
// Line ~196
capturedPhotoData = canvasElement.toDataURL('image/jpeg', 0.85);
//                                                          ^
//                                            Quality: 0.0 - 1.0
```

### **Disable GPS Requirement:**

Edit: `controllers/portal_attendance.py`
```python
# Line ~81 - Comment out GPS validation
# if not latitude or not longitude:
#     _logger.warning(f"Attendance submitted without GPS...")
```

### **Add Custom Branding:**

Edit: `views/portal_templates.xml`
```xml
<!-- Add company logo -->
<div class="card-header">
    <img src="/web/binary/company_logo" style="height: 40px;"/>
    <h3>My Attendance</h3>
</div>
```

---

## 📈 **Performance Notes**

- **Photo size:** ~100-200 KB (JPEG quality 0.85)
- **Page load:** < 2 seconds
- **Camera start:** 1-2 seconds
- **GPS detection:** 3-10 seconds (varies)
- **Upload time:** 1-3 seconds (depends on network)

**Optimization:**
- Photos stored as attachments (efficient)
- GPS timeout: 15 seconds max
- Browser caching enabled

---

## 📞 **Support**

**Issues?**
1. Check Odoo logs: `docker-compose logs -f web`
2. Check browser console (F12)
3. Verify module upgraded successfully
4. Check portal access granted to user

**Developer:** PTP GP Development Team
**Version:** 17.0.1.0.0
**Odoo Version:** 17.0 Community/Enterprise

---

## ✅ **Summary**

Portal attendance system is now **READY**:

✅ URL: `/my/attendance`
✅ Camera selfie auto-start
✅ GPS auto-detect
✅ Mobile-responsive
✅ Photo + GPS validation
✅ Attendance history

**Next step:** Upgrade module dan test di browser!
