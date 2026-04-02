# 📋 API Endpoint List - Quick Reference

**Base URL:** `http://localhost:8069/api/v1` (Development)
**Base URL:** `https://your-domain.com/api/v1` (Production)

---

## 🔐 **1. AUTHENTICATION (3 endpoints)**

### **1.1 Login**
```
POST /api/v1/auth/login
```
**Auth:** None (public)
**Body:**
```json
{
  "username": "employee@company.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "api_key": "xYz123AbC456...",
    "employee_id": 456,
    "employee_name": "John Doe",
    ...
  }
}
```
**Note:** Save `api_key` for subsequent requests!

---

### **1.2 Get Profile**
```
GET /api/v1/auth/me
```
**Auth:** Required (X-API-Key header)
**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 456,
    "name": "John Doe",
    "email": "john@company.com",
    "department": "IT Department",
    "job_title": "Software Engineer",
    ...
  }
}
```

---

### **1.3 Logout**
```
POST /api/v1/auth/logout
```
**Auth:** Required
**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 👤 **2. ATTENDANCE (5 endpoints)**

### **2.1 Get Status**
```
GET /api/v1/attendance/status
```
**Auth:** Required
**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 456,
    "status": "checked_out",  // or "checked_in"
    "last_attendance": {...}
  }
}
```

---

### **2.2 Check-In**
```
POST /api/v1/attendance/check-in
```
**Auth:** Required
**Body:**
```json
{
  "photo": "base64_encoded_jpeg_without_prefix",
  "latitude": -6.028448,
  "longitude": 106.047287
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "attendance_id": 789,
    "check_in": "2025-11-30 10:30:00",
    "gps_location": {...}
  }
}
```

---

### **2.3 Check-Out**
```
POST /api/v1/attendance/check-out
```
**Auth:** Required
**Body:**
```json
{
  "photo": "base64_encoded_jpeg",
  "latitude": -6.028450,
  "longitude": 106.047290
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "attendance_id": 789,
    "check_in": "2025-11-30 10:30:00",
    "check_out": "2025-11-30 18:30:00",
    "hours_worked": 8.0
  }
}
```

---

### **2.4 Get History**
```
GET /api/v1/attendance/history?limit=30&date_from=2025-11-01&date_to=2025-11-30
```
**Auth:** Required
**Query Params:**
- `limit` (optional, default: 30)
- `date_from` (optional): YYYY-MM-DD
- `date_to` (optional): YYYY-MM-DD

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 10,
    "attendances": [
      {
        "id": 789,
        "check_in": "2025-11-30 10:30:00",
        "check_out": "2025-11-30 18:30:00",
        "hours_worked": 8.0,
        "gps_check_in": {...},
        "gps_check_out": {...}
      }
    ]
  }
}
```

---

### **2.5 Get Photo**
```
GET /api/v1/attendance/photo/{attendance_id}/{photo_type}?api_key=xxx
```
**Auth:** Required (via query param or header)
**Path Params:**
- `{attendance_id}` - Attendance record ID
- `{photo_type}` - Either `check_in` or `check_out`

**Response:** JPEG image (binary)

**Example:**
```
GET /api/v1/attendance/photo/789/check_in?api_key=xyz123
```

---

## 💰 **3. PAYSLIP / SLIP GAJI (3 endpoints)**

### **3.1 Get Payslip List**
```
GET /api/v1/payslip/list?year=2025&month=11&limit=12
```
**Auth:** Required
**Query Params:**
- `year` (optional): 2025
- `month` (optional): 1-12
- `state` (optional): draft, done, paid
- `limit` (optional, default: 12)

**Response:**
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
        "basic_wage": 8000000.0,
        "net_wage": 10000000.0
      }
    ]
  }
}
```

---

### **3.2 Get Payslip Detail**
```
GET /api/v1/payslip/{payslip_id}
```
**Auth:** Required
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 999,
    "number": "SLIP/2025/11/001",
    "basic_wage": 8000000.0,
    "net_wage": 10000000.0,
    "lines": [
      {
        "name": "Basic Salary",
        "code": "BASIC",
        "amount": 8000000.0
      },
      {
        "name": "Transport Allowance",
        "code": "TRANS",
        "amount": 500000.0
      },
      {
        "name": "Tax (PPh 21)",
        "code": "TAX",
        "amount": -300000.0
      }
    ]
  }
}
```

---

### **3.3 Download Payslip PDF**
```
GET /api/v1/payslip/{payslip_id}/download
```
**Auth:** Required
**Response:** PDF file (binary)

**Example:**
```
GET /api/v1/payslip/999/download
Header: X-API-Key: xyz123
```

---

## 🏖️ **4. LEAVE / TIME OFF / CUTI (5 endpoints)**

### **4.1 Get Leave Balance**
```
GET /api/v1/leave/balance
```
**Auth:** Required
**Response:**
```json
{
  "success": true,
  "data": {
    "balances": [
      {
        "leave_type_id": 1,
        "leave_type": "Annual Leave",
        "remaining": 12.0,
        "max_leaves": 15.0,
        "leaves_taken": 3.0
      },
      {
        "leave_type_id": 2,
        "leave_type": "Sick Leave",
        "remaining": 10.0,
        "max_leaves": 12.0,
        "leaves_taken": 2.0
      }
    ]
  }
}
```

---

### **4.2 Get Leave List**
```
GET /api/v1/leave/list?state=validate&limit=50
```
**Auth:** Required
**Query Params:**
- `state` (optional): draft, confirm, validate, refuse
- `date_from` (optional): YYYY-MM-DD
- `date_to` (optional): YYYY-MM-DD
- `limit` (optional, default: 50)

**Response:**
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
  }
}
```

---

### **4.3 Request Leave**
```
POST /api/v1/leave/request
```
**Auth:** Required
**Body:**
```json
{
  "leave_type_id": 1,
  "date_from": "2025-12-01",
  "date_to": "2025-12-05",
  "description": "Family vacation"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "leave_id": 111,
    "message": "Leave request submitted successfully",
    "state": "confirm",
    "number_of_days": 5.0
  }
}
```

---

### **4.4 Cancel Leave**
```
POST /api/v1/leave/{leave_id}/cancel
```
**Auth:** Required
**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Leave cancelled successfully"
  }
}
```

---

## 📊 **Quick Summary**

| Category | Endpoints | Methods |
|----------|-----------|---------|
| **Authentication** | 3 | POST, GET |
| **Attendance** | 5 | GET, POST |
| **Payslip** | 3 | GET |
| **Leave** | 5 | GET, POST |
| **TOTAL** | **16** | - |

---

## 🔑 **Authentication Header**

All endpoints (except Login) require authentication header:

```
X-API-Key: your_api_key_from_login
```

**Example:**
```bash
curl http://localhost:8069/api/v1/auth/me \
  -H "X-API-Key: xYz123AbC456..."
```

---

## ✅ **Response Format**

All endpoints return JSON with consistent format:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**Error:**
```json
{
  "success": false,
  "data": null,
  "error": "Error message here"
}
```

---

## 🌍 **CORS Support**

API supports CORS for web/mobile apps:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key`

---

## 🔒 **Security Notes**

1. **HTTPS Required** in production
2. **API Key** should be stored securely (not hardcoded)
3. **Photo** must be base64 **without** `data:image/jpeg;base64,` prefix
4. **GPS coordinates** are optional but recommended
5. **Rate limiting** recommended for production

---

## 📱 **Quick Test (cURL)**

```bash
# 1. Login
curl -X POST http://localhost:8069/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 2. Get Profile (replace YOUR_API_KEY)
curl http://localhost:8069/api/v1/auth/me \
  -H "X-API-Key: YOUR_API_KEY"

# 3. Get Attendance Status
curl http://localhost:8069/api/v1/attendance/status \
  -H "X-API-Key: YOUR_API_KEY"

# 4. Check-In
curl -X POST http://localhost:8069/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "latitude": -6.028448,
    "longitude": 106.047287
  }'
```

---

**Complete Documentation:** See [COMPLETE_API_DOCUMENTATION.md](COMPLETE_API_DOCUMENTATION.md)
