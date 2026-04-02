# 📡 Complete Mobile App API Documentation

RESTful API untuk Mobile App - Complete Employee Self-Service

**Version:** 1.0.0
**Base URL:** `https://your-domain.com/api/v1`

---

## 📋 **Table of Contents**

1. [Authentication](#1-authentication)
2. [Attendance](#2-attendance)
3. [Payslip / Slip Gaji](#3-payslip--slip-gaji)
4. [Leave / Time Off / Cuti](#4-leave--time-off--cuti)
5. [Testing](#testing)
6. [Error Codes](#error-codes)

---

## 1. Authentication

### **1.1 Login**

**Endpoint:**
```
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "employee@company.com",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "username": "employee@company.com",
    "name": "John Doe",
    "email": "employee@company.com",
    "employee_id": 456,
    "employee_name": "John Doe",
    "employee_code": "EMP001",
    "department": "IT Department",
    "job_title": "Software Engineer",
    "api_key": "xYz123AbC456...",
    "session_id": "session_token_here"
  },
  "error": null
}
```

**Store** `api_key` untuk subsequent requests!

---

### **1.2 Logout**

**Endpoint:**
```
POST /api/v1/auth/logout
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  },
  "error": null
}
```

---

### **1.3 Get Profile**

**Endpoint:**
```
GET /api/v1/auth/me
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "employee_id": 456,
    "name": "John Doe",
    "email": "john@company.com",
    "phone": "+62812345678",
    "department": "IT Department",
    "job_title": "Software Engineer",
    "manager": "Jane Smith",
    "work_email": "john@company.com",
    "work_phone": "+62812345678",
    "employee_code": "EMP001",
    "company": "PT ABC Indonesia"
  },
  "error": null
}
```

---

## 2. Attendance

### **2.1 Get Attendance Status**

**Endpoint:**
```
GET /api/v1/attendance/status
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 456,
    "employee_name": "John Doe",
    "status": "checked_in",
    "last_attendance": {
      "id": 789,
      "check_in": "2025-11-30 10:30:00",
      "check_out": null,
      "hours_worked": 0,
      "has_check_in_photo": true,
      "has_check_out_photo": false
    }
  },
  "error": null
}
```

**Status values:**
- `"checked_in"` - Currently checked in
- `"checked_out"` - Currently checked out

---

### **2.2 Check-In**

**Endpoint:**
```
POST /api/v1/attendance/check-in
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "photo": "base64_encoded_jpeg_without_prefix",
  "latitude": -6.028448,
  "longitude": 106.047287
}
```

**Important:** Photo harus base64 **TANPA prefix** `data:image/jpeg;base64,`

**Response:**
```json
{
  "success": true,
  "data": {
    "attendance_id": 789,
    "check_in": "2025-11-30 10:30:00",
    "employee_name": "John Doe",
    "employee_id": 456,
    "gps_location": {
      "latitude": -6.028448,
      "longitude": 106.047287
    }
  },
  "error": null
}
```

---

### **2.3 Check-Out**

**Endpoint:**
```
POST /api/v1/attendance/check-out
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "photo": "base64_encoded_jpeg",
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
    "check_out": "2025-11-30 18:30:00",
    "hours_worked": 8.0,
    "employee_name": "John Doe",
    "employee_id": 456
  },
  "error": null
}
```

---

### **2.4 Get Attendance History**

**Endpoint:**
```
GET /api/v1/attendance/history
```

**Headers:**
```
X-API-Key: your_api_key
```

**Query Parameters:**
- `limit` (optional, default: 30)
- `date_from` (optional): YYYY-MM-DD
- `date_to` (optional): YYYY-MM-DD

**Example:**
```
GET /api/v1/attendance/history?limit=10&date_from=2025-11-01&date_to=2025-11-30
```

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 456,
    "employee_name": "John Doe",
    "count": 10,
    "attendances": [
      {
        "id": 789,
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

### **2.5 Get Attendance Photo**

**Endpoint:**
```
GET /api/v1/attendance/photo/{attendance_id}/{photo_type}
```

**Parameters:**
- `{attendance_id}` - Attendance record ID
- `{photo_type}` - Either `check_in` or `check_out`

**Query Parameters:**
- `api_key` - Your API key

**Example:**
```
GET /api/v1/attendance/photo/789/check_in?api_key=your_api_key
```

**Response:** JPEG image (binary)

**Usage in HTML:**
```html
<img src="https://domain.com/api/v1/attendance/photo/789/check_in?api_key=xxx" />
```

---

## 3. Payslip / Slip Gaji

### **3.1 Get Payslip List**

**Endpoint:**
```
GET /api/v1/payslip/list
```

**Headers:**
```
X-API-Key: your_api_key
```

**Query Parameters:**
- `year` (optional): 2025
- `month` (optional): 1-12
- `state` (optional): draft, done, paid
- `limit` (optional, default: 12)

**Example:**
```
GET /api/v1/payslip/list?year=2025&month=11
```

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
        "state_display": "Done",
        "basic_wage": 8000000.0,
        "net_wage": 10000000.0,
        "company_id": 1,
        "company_name": "PT ABC Indonesia",
        "struct_id": "Regular Pay"
      }
    ]
  },
  "error": null
}
```

---

### **3.2 Get Payslip Detail**

**Endpoint:**
```
GET /api/v1/payslip/{payslip_id}
```

**Headers:**
```
X-API-Key: your_api_key
```

**Example:**
```
GET /api/v1/payslip/999
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 999,
    "name": "Salary Slip - November 2025",
    "number": "SLIP/2025/11/001",
    "date_from": "2025-11-01",
    "date_to": "2025-11-30",
    "date_payment": "2025-12-01",
    "state": "done",
    "state_display": "Done",
    "employee_id": 456,
    "employee_name": "John Doe",
    "employee_code": "EMP001",
    "contract": "Contract for John Doe",
    "struct": "Regular Pay",
    "basic_wage": 8000000.0,
    "net_wage": 10000000.0,
    "company": "PT ABC Indonesia",
    "lines": [
      {
        "id": 1,
        "name": "Basic Salary",
        "code": "BASIC",
        "category": "Allowance",
        "sequence": 1,
        "quantity": 1.0,
        "rate": 100.0,
        "amount": 8000000.0,
        "total": 8000000.0
      },
      {
        "id": 2,
        "name": "Transport Allowance",
        "code": "TRANS",
        "category": "Allowance",
        "sequence": 2,
        "quantity": 1.0,
        "rate": 100.0,
        "amount": 500000.0,
        "total": 500000.0
      },
      {
        "id": 3,
        "name": "Tax (PPh 21)",
        "code": "TAX",
        "category": "Deduction",
        "sequence": 10,
        "quantity": 1.0,
        "rate": 100.0,
        "amount": -300000.0,
        "total": -300000.0
      }
    ],
    "note": ""
  },
  "error": null
}
```

---

### **3.3 Download Payslip PDF**

**Endpoint:**
```
GET /api/v1/payslip/{payslip_id}/download
```

**Headers:**
```
X-API-Key: your_api_key
```

**Example:**
```
GET /api/v1/payslip/999/download
```

**Response:** PDF file (binary)

**Usage:**
```javascript
// Download PDF
fetch('https://domain.com/api/v1/payslip/999/download', {
  headers: { 'X-API-Key': 'your_key' }
})
.then(response => response.blob())
.then(blob => {
  // Save or display PDF
  const url = window.URL.createObjectURL(blob);
  window.open(url);
});
```

---

## 4. Leave / Time Off / Cuti

### **4.1 Get Leave Balance**

**Endpoint:**
```
GET /api/v1/leave/balance
```

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 456,
    "employee_name": "John Doe",
    "balances": [
      {
        "leave_type_id": 1,
        "leave_type": "Annual Leave",
        "remaining": 12.0,
        "virtual_remaining": 12.0,
        "max_leaves": 15.0,
        "leaves_taken": 3.0
      },
      {
        "leave_type_id": 2,
        "leave_type": "Sick Leave",
        "remaining": 10.0,
        "virtual_remaining": 10.0,
        "max_leaves": 12.0,
        "leaves_taken": 2.0
      }
    ]
  },
  "error": null
}
```

---

### **4.2 Get Leave List**

**Endpoint:**
```
GET /api/v1/leave/list
```

**Headers:**
```
X-API-Key: your_api_key
```

**Query Parameters:**
- `state` (optional): draft, confirm, validate, refuse
- `date_from` (optional): YYYY-MM-DD
- `date_to` (optional): YYYY-MM-DD
- `limit` (optional, default: 50)

**Example:**
```
GET /api/v1/leave/list?state=validate&limit=20
```

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
        "leave_type_id": 1,
        "date_from": "2025-12-01",
        "date_to": "2025-12-05",
        "number_of_days": 5.0,
        "state": "validate",
        "state_display": "Approved",
        "request_date": "2025-11-20 10:00:00"
      }
    ]
  },
  "error": null
}
```

**State values:**
- `draft` - Draft
- `confirm` - To Approve
- `refuse` - Refused
- `validate` - Approved

---

### **4.3 Request Leave**

**Endpoint:**
```
POST /api/v1/leave/request
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
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
  },
  "error": null
}
```

---

### **4.4 Cancel Leave**

**Endpoint:**
```
POST /api/v1/leave/{leave_id}/cancel
```

**Headers:**
```
X-API-Key: your_api_key
```

**Example:**
```
POST /api/v1/leave/111/cancel
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Leave cancelled successfully"
  },
  "error": null
}
```

**Note:** Hanya bisa cancel leave dengan state `draft` atau `confirm`

---

## Testing

### **Complete Flow Test (cURL)**

#### **1. Login:**
```bash
curl -X POST http://localhost:8069/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "employee@company.com",
    "password": "password123"
  }'
```

**Copy `api_key` dari response!**

#### **2. Get Profile:**
```bash
curl http://localhost:8069/api/v1/auth/me \
  -H "X-API-Key: YOUR_API_KEY"
```

#### **3. Check Attendance Status:**
```bash
curl http://localhost:8069/api/v1/attendance/status \
  -H "X-API-Key: YOUR_API_KEY"
```

#### **4. Check-In:**
```bash
curl -X POST http://localhost:8069/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "photo": "BASE64_PHOTO_HERE",
    "latitude": -6.028448,
    "longitude": 106.047287
  }'
```

#### **5. Get Payslip List:**
```bash
curl http://localhost:8069/api/v1/payslip/list?year=2025 \
  -H "X-API-Key: YOUR_API_KEY"
```

#### **6. Get Leave Balance:**
```bash
curl http://localhost:8069/api/v1/leave/balance \
  -H "X-API-Key: YOUR_API_KEY"
```

#### **7. Request Leave:**
```bash
curl -X POST http://localhost:8069/api/v1/leave/request \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "leave_type_id": 1,
    "date_from": "2025-12-01",
    "date_to": "2025-12-05",
    "description": "Annual leave"
  }'
```

---

## Error Codes

| HTTP | Error | Description |
|------|-------|-------------|
| 200 | - | Success |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid credentials or API key |
| 403 | Forbidden | Access denied (not your data) |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

**Error Response Format:**
```json
{
  "success": false,
  "data": null,
  "error": "Error message here"
}
```

---

## 📱 Mobile App Integration Example

### **React Native / JavaScript:**

```javascript
const API_BASE = 'https://your-domain.com/api/v1';
let API_KEY = null;

// 1. Login
async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const result = await response.json();

  if (result.success) {
    API_KEY = result.data.api_key;
    // Store API_KEY securely (AsyncStorage, SecureStore, etc.)
    return result.data;
  } else {
    throw new Error(result.error);
  }
}

// 2. Get Profile
async function getProfile() {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return await response.json();
}

// 3. Check-In
async function checkIn(photoBase64, latitude, longitude) {
  const response = await fetch(`${API_BASE}/attendance/check-in`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      photo: photoBase64,
      latitude,
      longitude
    })
  });
  return await response.json();
}

// 4. Get Payslips
async function getPayslips(year, month) {
  const url = `${API_BASE}/payslip/list?year=${year}&month=${month}`;
  const response = await fetch(url, {
    headers: { 'X-API-Key': API_KEY }
  });
  return await response.json();
}

// 5. Get Leave Balance
async function getLeaveBalance() {
  const response = await fetch(`${API_BASE}/leave/balance`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return await response.json();
}

// 6. Request Leave
async function requestLeave(leaveTypeId, dateFrom, dateTo, description) {
  const response = await fetch(`${API_BASE}/leave/request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      leave_type_id: leaveTypeId,
      date_from: dateFrom,
      date_to: dateTo,
      description
    })
  });
  return await response.json();
}
```

---

## 🔐 Production Security Checklist

- [ ] Use **HTTPS** only (mandatory)
- [ ] Implement proper **API key authentication**
- [ ] Add **rate limiting** (max requests per minute)
- [ ] Enable **audit logging** for all API calls
- [ ] Validate **photo size** (max 1MB)
- [ ] Validate **GPS coordinates** range
- [ ] Implement **API key rotation** policy
- [ ] Use **secure storage** for API keys in mobile app
- [ ] Add **request/response encryption** if needed
- [ ] Monitor **failed authentication attempts**
- [ ] Set up **CORS** whitelist for allowed domains
- [ ] Add **API version** for backward compatibility

---

## 📊 API Endpoint Summary

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Auth** | `/api/v1/auth/login` | POST | Login |
| | `/api/v1/auth/logout` | POST | Logout |
| | `/api/v1/auth/me` | GET | Get profile |
| **Attendance** | `/api/v1/attendance/status` | GET | Get status |
| | `/api/v1/attendance/check-in` | POST | Check-in |
| | `/api/v1/attendance/check-out` | POST | Check-out |
| | `/api/v1/attendance/history` | GET | Get history |
| | `/api/v1/attendance/photo/{id}/{type}` | GET | Get photo |
| **Payslip** | `/api/v1/payslip/list` | GET | List payslips |
| | `/api/v1/payslip/{id}` | GET | Get detail |
| | `/api/v1/payslip/{id}/download` | GET | Download PDF |
| **Leave** | `/api/v1/leave/balance` | GET | Get balance |
| | `/api/v1/leave/list` | GET | List leaves |
| | `/api/v1/leave/request` | POST | Request leave |
| | `/api/v1/leave/{id}/cancel` | POST | Cancel leave |

**Total: 16 endpoints**

---

**API Complete & Ready for Mobile App!** 📱✨
