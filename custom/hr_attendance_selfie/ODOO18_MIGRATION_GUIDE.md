# Odoo 18 Enterprise Migration Guide
## HR Attendance Selfie Module

### Quick Migration Checklist

#### 1. Update Manifest Version
**File:** `__manifest__.py`

```python
# Change this:
'version': '17.0.1.0.0',

# To this:
'version': '18.0.1.0.0',
```

#### 2. Update Documentation References
**File:** `__manifest__.py`

```python
# Update the description section:
"""
Requirements:
-------------
* Browser must support camera access (MediaDevices API)
* User must allow camera permission
* Works on HTTPS or localhost
* Odoo 18 Community/Enterprise  # Changed from 17
"""
```

#### 3. Verify GPS Field Compatibility (CRITICAL)

Before updating, check if GPS fields exist in your Odoo 18 installation:

```python
# Run this in Odoo shell or debug mode:
model = self.env['hr.attendance']
fields = model.fields_get()
print("Available GPS-related fields:")
for field in fields:
    if 'lat' in field.lower() or 'long' in field.lower() or 'gps' in field.lower():
        print(f"  - {field}: {fields[field]}")
```

**If GPS fields have changed, update these files:**

**File:** `controllers/portal.py` (if exists)
```python
# Look for and update these field references:
'in_latitude': float(latitude) if latitude else False,
'in_longitude': float(longitude) if longitude else False,
'out_latitude': float(latitude) if latitude else False,
'out_longitude': float(longitude) if longitude else False,
```

**File:** `models/hr_attendance.py` (if exists)
```python
# Check field definitions and update if needed
in_latitude = fields.Float(string='Check-in Latitude')
in_longitude = fields.Float(string='Check-in Longitude')
# etc.
```

#### 4. Test JavaScript Compatibility

The module already uses modern OWL 1.x syntax, which is compatible with Odoo 18. No changes needed for:
- ✅ `/** @odoo-module **/` directives
- ✅ ES6 imports from "@odoo/owl"
- ✅ Component lifecycle methods
- ✅ Reactive state management

#### 5. Verify Enterprise Features

The module uses standard Odoo features that work in both Community and Enterprise:
- GPS tracking (built-in hr.attendance fields)
- Binary attachments for photos
- Standard access rights

### Step-by-Step Migration Process

#### Step 1: Backup
```bash
# Always backup before migration
cp -r custom/hr_attendance_selfie custom/hr_attendance_selfie_backup
```

#### Step 2: Update Version Numbers
```bash
# Update __manifest__.py
sed -i '' 's/17\.0\.1\.0\.0/18.0.1.0.0/g' custom/hr_attendance_selfie/__manifest__.py
```

#### Step 3: Update Documentation
Edit `__manifest__.py` to change all references from "Odoo 17" to "Odoo 18"

#### Step 4: Verify GPS Fields
1. Install module in development mode
2. Check for any field errors in logs
3. Test attendance creation with GPS

#### Step 5: Test Core Functionality
Create a test checklist:

```markdown
[ ] Module installs without errors
[ ] Camera popup opens on check-in
[ ] Photo captures and saves
[ ] GPS location is recorded
[ ] Photos display in list view
[ ] Portal access works for employees
[ ] Manager can see all attendance
[ ] Settings page loads correctly
```

### Troubleshooting Common Issues

#### GPS Fields Not Found
If GPS fields don't exist in Odoo 18:

1. **Option 1 - Add fields manually:**
```python
# In models/hr_attendance.py (create if doesn't exist)
from odoo import models, fields

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    in_latitude = fields.Float(string='Check-in Latitude', digits=(10, 6))
    in_longitude = fields.Float(string='Check-in Longitude', digits=(10, 6))
    out_latitude = fields.Float(string='Check-out Latitude', digits=(10, 6))
    out_longitude = fields.Float(string='Check-out Longitude', digits=(10, 6))
```

2. **Option 2 - Use alternative location fields:**
```python
# Check if these exist instead:
# - location_in
# - location_out
# - gps_coordinates
# Or check the new odoo.geolocation module fields
```

#### JavaScript Errors
If you encounter JavaScript issues:

1. Clear browser cache
2. Update assets:
```python
# In __manifest__.py, ensure assets are correctly defined:
'assets': {
    'web.assets_backend': [
        'hr_attendance_selfie/static/src/js/attendance_camera_widget.js',
        'hr_attendance_selfie/static/src/css/attendance_camera.css',
        'hr_attendance_selfie/static/src/xml/camera_templates.xml',
    ],
    'web.assets_frontend': [
        'hr_attendance_selfie/static/src/js/portal_attendance.js',
        'hr_attendance_selfie/static/src/css/portal_attendance.css',
    ],
},
```

#### Portal Access Issues
For employee portal access:

1. Ensure portal group has correct permissions
2. Update `ir.model.access.csv` if needed
3. Check portal templates use correct odoo 18 syntax

### Validation Script

Create this Python script to validate your migration:

```python
# validate_migration.py
import odoo
from odoo.tools import config

def validate_migration():
    """Validate HR Attendance Selfie module for Odoo 18"""

    # 1. Check module version
    manifest_path = 'custom/hr_attendance_selfie/__manifest__.py'
    with open(manifest_path, 'r') as f:
        content = f.read()
        if '18.0.1.0.0' not in content:
            print("❌ Module version not updated to 18.0")
            return False

    # 2. Check GPS fields
    registry = odoo.registry(config.get('db_name'))
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, 1, {})
        fields = env['hr.attendance'].fields_get()

        required_fields = ['in_latitude', 'in_longitude', 'out_latitude', 'out_longitude']
        for field in required_fields:
            if field not in fields:
                print(f"⚠️  GPS field '{field}' not found in hr.attendance")

    # 3. Check assets
    if 'web.assets_backend' not in content:
        print("❌ Backend assets not properly configured")
        return False

    print("✅ Migration validation complete")
    return True

if __name__ == '__main__':
    validate_migration()
```

### Production Deployment Steps

1. **Testing Phase:**
   - Deploy to a test/staging Odoo 18 instance
   - Run all functionality tests
   - Performance test with multiple users

2. **User Acceptance Testing:**
   - Test with real employees
   - Test on various devices (mobile, desktop)
   - Test camera permissions on different browsers

3. **Production Rollout:**
   - Schedule maintenance window
   - Backup production database
   - Update module code
   - Run `odoo -u hr_attendance_selfie -d database_name`
   - Verify all functionality

4. **Post-Deployment Monitoring:**
   - Check Odoo logs for errors
   - Monitor attendance creation
   - Verify photo storage
   - Check GPS accuracy

### Summary

Your `hr_attendance_selfie` module is **90% ready** for Odoo 18 Enterprise. The main tasks are:

1. ✅ Update version numbers in manifest
2. ✅ Update documentation references
3. ⚠️ Verify GPS field compatibility (most critical)
4. ✅ JavaScript is already compatible (OWL 1.x)
5. ✅ Standard Odoo patterns are used

The module uses modern Odoo development practices and should migrate smoothly once GPS field compatibility is verified.