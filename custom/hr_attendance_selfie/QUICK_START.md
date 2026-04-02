# 🚀 Quick Start - Employee Attendance Portal

Portal untuk employee check-in/out dengan **selfie + GPS** sudah siap!

---

## ⚡ **Install & Test (5 Minutes)**

### **1. Restart Odoo**
```bash
cd /Users/rizkidwisaputra/erp-ptpgp-dev
docker-compose restart web
```

### **2. Upgrade Module**
- Login ke Odoo (admin)
- **Apps** → Search `hr_attendance_selfie`
- Click **Upgrade**
- Wait ~30 seconds

### **3. Grant Portal Access**
Employee harus punya **portal access**:

- **Settings** → **Users** → Find employee user
- Check **Portal** group
- Save

### **4. Test Portal**

Buka di browser (sebagai employee):
```
http://localhost:8069/my/attendance
```

**Atau production:**
```
https://your-domain.com/my/attendance
```

---

## 📱 **Portal Features**

✅ **URL:** `/my/attendance`
✅ **Camera selfie** otomatis (front camera)
✅ **GPS auto-detect** (browser geolocation)
✅ **Mobile-responsive** design
✅ **Attendance history** (30 hari)

---

## 🎯 **User Flow**

1. Employee buka `/my/attendance` di smartphone
2. Login dengan portal credentials
3. Camera & GPS auto-start
4. Capture selfie
5. Click "Submit Check-In"
6. ✅ Done!

---

## 📋 **What Was Created**

```
✅ controllers/portal_attendance.py    - Routes & API
✅ views/portal_templates.xml          - Portal HTML
✅ static/src/js/portal_attendance.js  - Camera + GPS
✅ static/src/css/portal_attendance.css - Styling
✅ PORTAL_SETUP.md                     - Full documentation
```

---

## ⚠️ **Important**

**Browser Requirements:**
- 🔒 **HTTPS** (atau localhost untuk dev)
- 📷 **Camera permission** harus di-allow
- 📍 **Location permission** harus di-allow

**Supported Browsers:**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari iOS 11+
- Chrome Android

---

## 🐛 **Troubleshooting**

**Page not found (404)?**
```bash
# Restart & clear cache
docker-compose restart web
# Hard refresh browser: Ctrl+Shift+R
```

**Camera not working?**
- Pastikan HTTPS (bukan HTTP)
- Allow camera permission di browser
- Camera tidak digunakan app lain

**GPS not detected?**
- Allow location permission
- Wait 5-10 detik (first GPS lock)
- Indoor bisa lambat

---

## 📖 **Full Documentation**

Lihat [PORTAL_SETUP.md](PORTAL_SETUP.md) untuk:
- Detailed setup instructions
- Testing checklist
- Troubleshooting guide
- Customization options

---

## ✅ **Ready to Test!**

1. Upgrade module ✅
2. Grant portal access to employee ✅
3. Open `/my/attendance` in browser ✅
4. Check-in with selfie + GPS ✅

**Selamat mencoba!** 🎉
