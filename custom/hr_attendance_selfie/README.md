# HR Attendance Selfie

📸 **Selfie Photo Validation for Employee Check-in and Check-out**

---

## Features

### 🎯 Core Features
- ✅ **Mandatory Selfie Photo** for check-in and check-out
- ✅ **GPS Location Tracking** using Odoo built-in fields
- ✅ **Photo Thumbnails** in attendance list view
- ✅ **Mobile & Desktop Support** - works on webcam and phone camera
- ✅ **One-Click Flow** - popup modal with live camera preview
- ✅ **Configurable Settings** - photo quality, resolution, camera preferences

### 📱 User Experience
- Camera popup with live preview
- Auto-detect GPS location (Odoo built-in)
- Front camera by default (for selfie)
- Option to retake photo
- Works on HTTPS or localhost

### ⚙️ Administrator Features
- Configurable photo quality (Low/Medium/High)
- Max file size settings
- Camera preferences (front/back)
- Access rights management
- Settings in: **Settings → Attendances → Selfie Attendance Validation**

---

## Installation

> **Note**: Module ini sudah ada di folder `/custom/hr_attendance_selfie/`. Jika Anda download dari tempat lain, copy dulu ke folder custom.

### 1. **Restart Odoo**
```bash
cd /path/to/your/odoo/project
docker-compose restart web
# or for non-docker:
sudo systemctl restart odoo
```

### 2. **Update Apps List**
- Login ke Odoo
- Go to **Apps** (main menu)
- Click **⋮** (menu button) → **Update Apps List**
- Remove "Apps" filter (click ✕ on filter)

### 3. **Install Module**
- Search: `hr_attendance_selfie`
- Click **Install**
- Wait untuk installation selesai (~30 seconds)

### 4. **Verify Installation**
- Go to **Attendances** menu
- Try create new attendance → Camera popup should appear
- Check **Settings → Attendances** → Should see "Selfie Attendance Validation" section

---

## How It Works

### Check-In Flow:
```
1. Employee clicks "Check In"
2. Camera popup appears with live preview
3. GPS location auto-detected
4. Employee captures selfie photo
5. Review photo (can retake if needed)
6. Submit → Attendance created with photo + GPS
```

### Check-Out Flow:
```
1. Employee clicks "Check Out"
2. Same camera popup appears
3. Capture selfie photo
4. Submit → Attendance updated with check-out photo + GPS
```

---

## Configuration

### Settings Location:
**Settings → Attendances → Selfie Attendance Validation**

### Available Options:

#### **Enable/Disable Features**
- ☑️ Require Selfie for Check-in (default: ON)
- ☑️ Require Selfie for Check-out (default: ON)

#### **Photo Quality**
- **Low**: 320x240 (~50KB) - untuk koneksi lambat
- **Medium**: 640x480 (~150KB) - **recommended**
- **High**: 1280x720 (~400KB) - best quality

#### **Camera Settings**
- ☑️ Use Front Camera by Default (untuk selfie)
- ☑️ Show Camera Preview
- ☑️ Allow Retake Photo

#### **GPS Settings**
- ☑️ Capture GPS Location (uses Odoo built-in fields)

#### **Access Rights**
- Employee can view: Own Photos Only / Department / All
- Manager can view: Department / All

---

## Views

### List View (Tree)
Attendance list dengan thumbnail photos:

| Employee | Check In | Check Out | Work Hours | Check-in Photo | Check-out Photo |
|----------|----------|-----------|------------|----------------|-----------------|
| John Doe | 08:00 AM | 05:00 PM  | 9.0 hrs    | [thumbnail]    | [thumbnail]     |

### Form View
Detail attendance dengan:
- Full size photo preview (200x200)
- Button "View Fullscreen" untuk lihat full resolution
- GPS coordinates display
- Link ke Google Maps

---

## Technical Details

### Models Extended:
- `hr.attendance` - Added fields:
  - `check_in_image` - Binary field untuk check-in photo
  - `check_in_image_small` - Thumbnail (150x150)
  - `check_out_image` - Binary field untuk check-out photo
  - `check_out_image_small` - Thumbnail (150x150)

### Uses Odoo Built-in GPS Fields:
- `in_latitude` - Check-in latitude (dari Odoo 17)
- `in_longitude` - Check-in longitude (dari Odoo 17)
- `out_latitude` - Check-out latitude (dari Odoo 17)
- `out_longitude` - Check-out longitude (dari Odoo 17)

### Frontend Technology:
- **OWL Components** (Odoo Web Library)
- **MediaDevices API** untuk camera access
- **Geolocation API** untuk GPS (Odoo built-in)
- Responsive CSS untuk mobile & desktop

### Storage:
- Photos disimpan sebagai **binary attachments**
- Efficient storage dengan `attachment=True`
- Auto-generate thumbnails untuk list view

---

## Requirements

### Browser Support:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (iOS 11+)
- ✅ Mobile browsers (Android Chrome, iOS Safari)

### Permissions Required:
- 📷 **Camera permission** - user harus allow di browser
- 📍 **Location permission** - untuk GPS (Odoo built-in)

### Server Requirements:
- 🔒 **HTTPS** (atau localhost untuk development)
- 📦 **Pillow** (Python imaging library) - untuk thumbnail generation

Install Pillow:
```bash
pip install Pillow
```

---

## Troubleshooting

### Camera Not Working?

**Problem**: "Failed to access camera"

**Solutions**:
1. Check browser camera permission
2. Pastikan HTTPS (atau localhost)
3. Camera tidak digunakan aplikasi lain
4. Try refresh page

### GPS Not Detected?

**Problem**: GPS shows "Detecting location..."

**Solutions**:
1. Check browser location permission
2. Pastikan GPS enabled (mobile)
3. Wait 5-10 detik (first GPS lock bisa lama)
4. Indoor bisa lambat, coba outdoor

### Photo Too Large?

**Problem**: Upload gagal karena file terlalu besar

**Solutions**:
1. Settings → Reduce photo quality ke "Medium" atau "Low"
2. Adjust max file size setting

---

## Security & Privacy

### Data Protection:
- ✅ Photos hanya accessible oleh authorized users
- ✅ Configurable access rights (employee vs manager)
- ✅ GPS data menggunakan Odoo built-in (compliant)

### Access Control:
- **Employees**: Bisa lihat photo sendiri saja (default)
- **Managers**: Bisa lihat semua photo (configurable)

---

## Roadmap / Future Features

Phase 2 (optional):
- [ ] Face detection validation
- [ ] Offline mode support (PWA)
- [ ] Dashboard untuk manager (lihat semua photo hari ini)
- [ ] Alert notification (check-in without photo)
- [ ] QR Code check-in (alternative method)
- [ ] Radius validation dari kantor (configurable)

---

## Support

**Developer**: PTP GP Development Team
**Version**: 17.0.1.0.0
**Odoo Version**: 17.0 Community/Enterprise

**Issues/Questions?**
- Check Settings → Attendances → Selfie Attendance Validation
- Review browser permissions (camera + location)
- Contact IT Support

---

## Changelog

### Version 17.0.1.0.0 (2025-11-04)
- ✅ Initial release
- ✅ Check-in/check-out selfie mandatory
- ✅ GPS integration (Odoo built-in)
- ✅ Photo thumbnails in list view
- ✅ Configurable settings page
- ✅ Mobile & desktop support
- ✅ Camera widget with live preview

---

## License

LGPL-3
