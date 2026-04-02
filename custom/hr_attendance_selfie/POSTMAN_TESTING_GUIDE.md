# 🧪 Postman Testing Guide

Panduan lengkap testing API dengan Postman.

---

## 📦 **Setup Postman**

### **Step 1: Import Collection**

1. **Buka Postman**
2. Click **Import** button (kiri atas)
3. Pilih file: `Odoo_Mobile_API.postman_collection.json`
4. Click **Import**

### **Step 2: Import Environment**

1. Click **Environments** (sidebar kiri)
2. Click **Import**
3. Pilih file: `Odoo_API.postman_environment.json`
4. Click **Import**

### **Step 3: Activate Environment**

1. Di kanan atas Postman, pilih dropdown environment
2. Select: **Odoo API - Localhost**
3. Environment sekarang active ✅

---

## 🔧 **Configure Base URL**

Environment sudah pre-configured dengan:
- `base_url`: `http://localhost:8069/api/v1`

**Untuk production**, update base_url:
1. Environments → Odoo API - Localhost
2. Edit `base_url` → `https://your-domain.com/api/v1`
3. Save

---

## 🧪 **Testing Flow**

### **Test 1: Login (Authentication)**

**Folder:** 1. Authentication → Login

**Request:**
```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "username": "admin",
    "name": "Administrator",
    "email": "admin",
    "employee_id": 1,
    "employee_name": "Administrator",
    "employee_code": "",
    "department": null,
    "job_title": null,
    "api_key": "xYz123AbC456...",
    "session_id": "session_token"
  },
  "error": null
}
```

**✅ Important:**
- **API Key** akan auto-save ke environment variable `{{api_key}}`
- **Employee ID** akan auto-save ke `{{employee_id}}`
- Check di: Environments → Odoo API - Localhost → api_key should have value

**⚠️ Troubleshooting:**
- **401 Unauthorized**: Username/password salah
- **404 Not Found**: Endpoint salah, pastikan module sudah di-upgrade
- **500 Error**: Check Odoo logs: `docker-compose logs -f web`

---

### **Test 2: Get Profile**

**Folder:** 1. Authentication → Get Profile (Me)

**Request:**
```http
GET {{base_url}}/auth/me
X-API-Key: {{api_key}}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "employee_id": 1,
    "name": "Administrator",
    "email": "admin",
    "phone": "",
    "department": null,
    "job_title": null,
    "manager": null,
    "work_email": "",
    "work_phone": "",
    "employee_code": "",
    "company": "My Company"
  },
  "error": null
}
```

**✅ Verify:**
- employee_id populated
- name correct
- department/job_title (if set)

---

### **Test 3: Get Attendance Status**

**Folder:** 2. Attendance → Get Attendance Status

**Request:**
```http
GET {{base_url}}/attendance/status
X-API-Key: {{api_key}}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 1,
    "employee_name": "Administrator",
    "status": "checked_out",
    "last_attendance": null
  },
  "error": null
}
```

**Status values:**
- `"checked_out"` - Can check-in
- `"checked_in"` - Can check-out

---

### **Test 4: Check-In**

**Folder:** 2. Attendance → Check-In

**Request:**
```http
POST {{base_url}}/attendance/check-in
Content-Type: application/json
X-API-Key: {{api_key}}

{
  "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "latitude": -6.028448,
  "longitude": 106.047287
}
```

**Note:** Photo di atas adalah 1x1 pixel dummy base64 (valid untuk testing).

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "attendance_id": 123,
    "check_in": "2025-11-30 10:30:00",
    "employee_name": "Administrator",
    "employee_id": 1,
    "gps_location": {
      "latitude": -6.028448,
      "longitude": 106.047287
    }
  },
  "error": null
}
```

**✅ Verify:**
- attendance_id auto-saved ke `{{attendance_id}}`
- check_in timestamp correct
- gps_location matches request

**⚠️ Errors:**
- `"Already checked in"` - Call check-out first
- `"Photo is required"` - Photo field missing
- `"No employee record found"` - User tidak linked ke employee

---

### **Test 5: Check-Out**

**Folder:** 2. Attendance → Check-Out

**Pre-requisite:** Must be checked in (run Test 4 first)

**Request:**
```http
POST {{base_url}}/attendance/check-out
Content-Type: application/json
X-API-Key: {{api_key}}

{
  "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "latitude": -6.028450,
  "longitude": 106.047290
}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "attendance_id": 123,
    "check_in": "2025-11-30 10:30:00",
    "check_out": "2025-11-30 18:30:00",
    "hours_worked": 8.0,
    "employee_name": "Administrator",
    "employee_id": 1
  },
  "error": null
}
```

**✅ Verify:**
- hours_worked calculated correctly
- check_out timestamp > check_in

---

### **Test 6: Get Attendance History**

**Folder:** 2. Attendance → Get Attendance History

**Request:**
```http
GET {{base_url}}/attendance/history?limit=30
X-API-Key: {{api_key}}
```

**Query Parameters (optional):**
- `limit`: Default 30
- `date_from`: YYYY-MM-DD
- `date_to`: YYYY-MM-DD

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 1,
    "employee_name": "Administrator",
    "count": 5,
    "attendances": [
      {
        "id": 123,
        "check_in": "2025-11-30 10:30:00",
        "check_out": "2025-11-30 18:30:00",
        "hours_worked": 8.0,
        "gps_check_in": {
          "latitude": -6.028448,
          "longitude": 106.047287
        },
        "gps_check_out": {
          "latitude": -6.028450,
          "longitude": 106.047290
        },
        "has_check_in_photo": true,
        "has_check_out_photo": true
      }
    ]
  },
  "error": null
}
```

---

### **Test 7: Get Attendance Photo**

**Folder:** 2. Attendance → Get Attendance Photo

**Pre-requisite:** attendance_id dari Test 4/5

**Request:**
```http
GET {{base_url}}/attendance/photo/{{attendance_id}}/check_in
X-API-Key: {{api_key}}
```

**Expected Response:** JPEG image (binary)

**In Postman:**
- Response akan show image preview
- Or "Save Response" → Download JPEG file

**Photo Types:**
- `check_in` - Check-in photo
- `check_out` - Check-out photo

---

### **Test 8: Get Payslip List**

**Folder:** 3. Payslip → Get Payslip List

**Pre-requisite:** Module `hr_payroll` installed & ada payslip data

**Request:**
```http
GET {{base_url}}/payslip/list?year=2025&limit=12
X-API-Key: {{api_key}}
```

**Query Parameters:**
- `year`: 2025
- `month`: 1-12 (optional)
- `limit`: Default 12

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "count": 12,
    "payslips": [
      {
        "id": 999,
        "name": "Salary Slip - November 2025",
        "number": "SLIP/2025/11/001",
        "date_from": "2025-11-01",
        "date_to": "2025-11-30",
        "state": "done",
        "state_display": "Done",
        "basic_wage": 8000000.0,
        "net_wage": 10000000.0,
        "company_id": 1,
        "company_name": "My Company",
        "struct_id": "Regular Pay"
      }
    ]
  },
  "error": null
}
```

**✅ Verify:**
- payslip_id auto-saved ke `{{payslip_id}}`

**⚠️ If empty:**
- Create payslip di Odoo: Payroll → Payslips → Create

---

### **Test 9: Get Payslip Detail**

**Folder:** 3. Payslip → Get Payslip Detail

**Request:**
```http
GET {{base_url}}/payslip/{{payslip_id}}
X-API-Key: {{api_key}}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 999,
    "name": "Salary Slip - November 2025",
    "number": "SLIP/2025/11/001",
    "date_from": "2025-11-01",
    "date_to": "2025-11-30",
    "basic_wage": 8000000.0,
    "net_wage": 10000000.0,
    "lines": [
      {
        "name": "Basic Salary",
        "code": "BASIC",
        "category": "Allowance",
        "amount": 8000000.0
      }
    ]
  },
  "error": null
}
```

---

### **Test 10: Download Payslip PDF**

**Folder:** 3. Payslip → Download Payslip PDF

**Request:**
```http
GET {{base_url}}/payslip/{{payslip_id}}/download
X-API-Key: {{api_key}}
```

**Expected Response:** PDF file (binary)

**In Postman:**
- Click "Send and Download"
- PDF will be saved to Downloads folder

---

### **Test 11: Get Leave Balance**

**Folder:** 4. Leave / Time Off → Get Leave Balance

**Pre-requisite:** Leave types configured & allocated

**Request:**
```http
GET {{base_url}}/leave/balance
X-API-Key: {{api_key}}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 1,
    "employee_name": "Administrator",
    "balances": [
      {
        "leave_type_id": 1,
        "leave_type": "Annual Leave",
        "remaining": 12.0,
        "virtual_remaining": 12.0,
        "max_leaves": 15.0,
        "leaves_taken": 3.0
      }
    ]
  },
  "error": null
}
```

---

### **Test 12: Get Leave List**

**Folder:** 4. Leave / Time Off → Get Leave List

**Request:**
```http
GET {{base_url}}/leave/list?limit=50
X-API-Key: {{api_key}}
```

**Query Parameters:**
- `state`: draft, confirm, validate, refuse
- `limit`: Default 50

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "count": 5,
    "leaves": [
      {
        "id": 111,
        "name": "Annual Leave",
        "leave_type": "Annual Leave",
        "date_from": "2025-12-01",
        "date_to": "2025-12-05",
        "number_of_days": 5.0,
        "state": "validate",
        "state_display": "Approved"
      }
    ]
  },
  "error": null
}
```

---

### **Test 13: Request Leave**

**Folder:** 4. Leave / Time Off → Request Leave

**Request:**
```http
POST {{base_url}}/leave/request
Content-Type: application/json
X-API-Key: {{api_key}}

{
  "leave_type_id": 1,
  "date_from": "2025-12-01",
  "date_to": "2025-12-05",
  "description": "Annual leave - Family vacation"
}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "leave_id": 111,
    "message": "Leave request submitted successfully",
    "state": "confirm",
    "number_of_days": 5.0
  },
  "error": null
}
```

**✅ Verify:**
- leave_id auto-saved ke `{{leave_id}}`

---

### **Test 14: Cancel Leave**

**Folder:** 4. Leave / Time Off → Cancel Leave

**Request:**
```http
POST {{base_url}}/leave/{{leave_id}}/cancel
X-API-Key: {{api_key}}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "message": "Leave cancelled successfully"
  },
  "error": null
}
```

---

## 🔄 **Complete Testing Workflow**

### **Scenario 1: Daily Attendance**

1. **Login** → Get API key
2. **Get Attendance Status** → Check if checked out
3. **Check-In** → Morning arrival (with photo + GPS)
4. Wait beberapa jam...
5. **Check-Out** → Evening departure (with photo + GPS)
6. **Get Attendance History** → Verify today's attendance

### **Scenario 2: View Payslip**

1. **Login** → Get API key
2. **Get Payslip List** → November 2025
3. **Get Payslip Detail** → View breakdown
4. **Download Payslip PDF** → Save to file

### **Scenario 3: Request Leave**

1. **Login** → Get API key
2. **Get Leave Balance** → Check remaining leaves
3. **Request Leave** → Submit cuti 5 hari
4. **Get Leave List** → Verify submission
5. (Optional) **Cancel Leave** → If needed

---

## 📊 **Runner / Automated Testing**

### **Run All Tests Automatically**

1. Click **Collections** → Odoo Mobile API - Complete
2. Click **Run** button (kanan atas collection)
3. **Runner** window opens
4. Select all requests
5. Click **Run Odoo Mobile API**
6. Wait for all tests to complete

**Results:**
- Green ✅ = Success
- Red ❌ = Failed

**View Details:**
- Click each request to see response
- Check "Test Results" tab

---

## 🐛 **Common Errors & Solutions**

### **1. "Authentication required" (401)**

**Problem:** API key tidak valid atau expired

**Solution:**
1. Run **Login** request lagi
2. Verify `{{api_key}}` populated di environment
3. Check Postman environment dropdown is active

### **2. "No employee record found" (404)**

**Problem:** User tidak di-link ke employee

**Solution:**
1. Buka Odoo → Employees
2. Create/edit employee
3. Link ke user (Related User field)

### **3. "Already checked in" (400)**

**Problem:** Employee sudah checked in, tidak bisa check-in lagi

**Solution:**
1. Call **Check-Out** dulu
2. Or cancel attendance di Odoo backend

### **4. Endpoint "Not found" (404)**

**Problem:** Module belum di-upgrade atau URL salah

**Solution:**
```bash
# Upgrade module
docker-compose restart web
# Then: Apps → hr_attendance_selfie → Upgrade
```

### **5. Empty payslip/leave list**

**Problem:** No data in database

**Solution:**
- Create sample data di Odoo:
  - Payslips: Payroll → Payslips → Create
  - Leaves: Time Off → Allocations → Create

---

## 💡 **Tips & Best Practices**

### **1. Use Environment Variables**

Already configured:
- `{{base_url}}` - API base URL
- `{{api_key}}` - Auto-populated after login
- `{{attendance_id}}` - Auto-populated after check-in
- `{{payslip_id}}` - Auto-populated from list
- `{{leave_id}}` - Auto-populated after request

### **2. Save Responses**

- Click **Save Response** → Save as Example
- Useful for documentation & reference

### **3. Test Scripts**

Collection sudah include auto-save scripts:
- Login → Save api_key
- Check-In → Save attendance_id
- Get Payslip List → Save first payslip_id

### **4. Organize Tests**

Create separate environments for:
- **Localhost** (development)
- **Staging** (testing)
- **Production** (live)

---

## 📄 **Files Created**

1. **Odoo_Mobile_API.postman_collection.json** - Postman collection (16 requests)
2. **Odoo_API.postman_environment.json** - Environment variables
3. **POSTMAN_TESTING_GUIDE.md** - This guide

---

## ✅ **Testing Checklist**

- [ ] Import collection to Postman
- [ ] Import environment to Postman
- [ ] Activate environment
- [ ] Upgrade module di Odoo
- [ ] Test Login → API key saved
- [ ] Test Get Profile → Employee info correct
- [ ] Test Check-In → Attendance created
- [ ] Test Check-Out → Hours calculated
- [ ] Test Attendance History → List populated
- [ ] Test Get Photo → Image downloaded
- [ ] Test Payslip List → (if hr_payroll installed)
- [ ] Test Payslip Detail → Breakdown shown
- [ ] Test Leave Balance → Balances shown
- [ ] Test Request Leave → Leave created
- [ ] Run all tests via Runner → All green ✅

---

**Happy Testing!** 🧪✨
