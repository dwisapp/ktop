# 📡 Attendance API Documentation

RESTful API untuk mobile app / external system integration.

---

## 🔑 **Authentication**

### **Method 1: API Key (Recommended for Mobile App)**

**Header:**
```
X-API-Key: your_api_key_here
```

### **Method 2: Session-based (Web Portal)**

Login via `/web/login` dulu, session cookie otomatis digunakan.

---

## 📋 **API Endpoints**

### **Base URL:**
```
http://localhost:8069/api/v1/attendance
```

Production:
```
https://your-domain.com/api/v1/attendance
```

---

## 1️⃣ **Check-In**

### **Endpoint:**
```
POST /api/v1/attendance/check-in
```

### **Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

### **Request Body:**
```json
{
  "photo": "base64_encoded_jpeg_without_prefix",
  "latitude": -6.028448,
  "longitude": 106.047287,
  "employee_id": 123  // optional if API key linked to employee
}
```

### **Response (Success):**
```json
{
  "success": true,
  "data": {
    "attendance_id": 456,
    "check_in": "2025-11-30 10:30:00",
    "employee_name": "John Doe",
    "employee_id": 123,
    "gps_location": {
      "latitude": -6.028448,
      "longitude": 106.047287
    }
  },
  "error": null
}
```

### **Response (Error):**
```json
{
  "success": false,
  "data": null,
  "error": "Already checked in"
}
```

### **HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (missing photo, already checked in, etc.)
- `401` - Unauthorized (invalid API key)
- `404` - Employee not found
- `500` - Server error

---

## 2️⃣ **Check-Out**

### **Endpoint:**
```
POST /api/v1/attendance/check-out
```

### **Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

### **Request Body:**
```json
{
  "photo": "base64_encoded_jpeg_without_prefix",
  "latitude": -6.028448,
  "longitude": 106.047287,
  "employee_id": 123  // optional
}
```

### **Response (Success):**
```json
{
  "success": true,
  "data": {
    "attendance_id": 456,
    "check_in": "2025-11-30 10:30:00",
    "check_out": "2025-11-30 18:30:00",
    "hours_worked": 8.0,
    "employee_name": "John Doe",
    "employee_id": 123
  },
  "error": null
}
```

### **HTTP Status Codes:**
- `200` - Success
- `400` - Already checked out, photo missing
- `401` - Unauthorized
- `404` - No open attendance found
- `500` - Server error

---

## 3️⃣ **Get Attendance Status**

### **Endpoint:**
```
GET /api/v1/attendance/status
```

### **Headers:**
```
X-API-Key: your_api_key
```

### **Query Parameters:**
- `employee_id` (optional) - Employee ID

### **Example:**
```
GET /api/v1/attendance/status?employee_id=123
```

### **Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 123,
    "employee_name": "John Doe",
    "status": "checked_in",
    "last_attendance": {
      "id": 456,
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

## 4️⃣ **Get Attendance History**

### **Endpoint:**
```
GET /api/v1/attendance/history
```

### **Headers:**
```
X-API-Key: your_api_key
```

### **Query Parameters:**
- `employee_id` (optional) - Employee ID
- `limit` (optional, default: 30) - Number of records
- `date_from` (optional) - Start date (YYYY-MM-DD)
- `date_to` (optional) - End date (YYYY-MM-DD)

### **Example:**
```
GET /api/v1/attendance/history?employee_id=123&limit=10&date_from=2025-11-01&date_to=2025-11-30
```

### **Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 123,
    "employee_name": "John Doe",
    "count": 10,
    "attendances": [
      {
        "id": 456,
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

## 5️⃣ **Get Photo Image**

### **Endpoint:**
```
GET /api/v1/attendance/photo/{attendance_id}/{photo_type}
```

### **Parameters:**
- `attendance_id` - Attendance record ID
- `photo_type` - Either `"check_in"` or `"check_out"`

### **Query Parameters (for API key):**
- `api_key` - Your API key (alternative to header)

### **Example:**
```
GET /api/v1/attendance/photo/456/check_in?api_key=your_api_key
```

**Or with header:**
```
GET /api/v1/attendance/photo/456/check_in
Header: X-API-Key: your_api_key
```

### **Response:**
- **Content-Type:** `image/jpeg`
- **Body:** Binary JPEG image data

**Usage in HTML:**
```html
<img src="http://localhost:8069/api/v1/attendance/photo/456/check_in?api_key=xxx" />
```

---

## 🔐 **API Key Setup**

### **Option 1: Simple Token (Development)**

**Via Odoo Settings:**
1. **Settings** → **Technical** → **System Parameters**
2. Create key: `attendance.api.key`
3. Value: `your_secret_token_123`

**Hardcode check in controller:**
```python
def _authenticate_api_key(self, api_key):
    valid_key = request.env['ir.config_parameter'].sudo().get_param('attendance.api.key')
    return api_key == valid_key
```

### **Option 2: Per-User API Key (Recommended)**

**Add field to res.users:**
```python
# models/res_users.py
class ResUsers(models.Model):
    _inherit = 'res.users'

    api_key = fields.Char(string='API Key', copy=False)

    def generate_api_key(self):
        import secrets
        self.api_key = secrets.token_urlsafe(32)
```

**Generate API key:**
```python
user.generate_api_key()
# Returns: "xYz123AbC456..."
```

### **Option 3: OAuth2 / JWT (Production)**

For production, implement OAuth2 or JWT authentication.

---

## 📱 **Mobile App Integration Example**

### **React Native / Flutter / Kotlin**

```javascript
// JavaScript/React Native example

const API_BASE_URL = 'https://your-domain.com/api/v1/attendance';
const API_KEY = 'your_api_key_here';

// Check-In function
async function checkIn(photoBase64, latitude, longitude) {
  try {
    const response = await fetch(`${API_BASE_URL}/check-in`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        photo: photoBase64,  // WITHOUT "data:image/jpeg;base64," prefix
        latitude: latitude,
        longitude: longitude
      })
    });

    const result = await response.json();

    if (result.success) {
      console.log('Check-in successful:', result.data);
      return result.data;
    } else {
      console.error('Check-in failed:', result.error);
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Network error:', error);
    throw error;
  }
}

// Check-Out function
async function checkOut(photoBase64, latitude, longitude) {
  const response = await fetch(`${API_BASE_URL}/check-out`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      photo: photoBase64,
      latitude: latitude,
      longitude: longitude
    })
  });

  const result = await response.json();
  return result;
}

// Get Status
async function getStatus() {
  const response = await fetch(`${API_BASE_URL}/status`, {
    method: 'GET',
    headers: {
      'X-API-Key': API_KEY
    }
  });

  const result = await response.json();
  return result.data;
}

// Get History
async function getHistory(limit = 30) {
  const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`, {
    method: 'GET',
    headers: {
      'X-API-Key': API_KEY
    }
  });

  const result = await response.json();
  return result.data.attendances;
}

// Usage:
// const photoBase64 = await capturePhotoAndConvertToBase64();
// const { latitude, longitude } = await getCurrentLocation();
// await checkIn(photoBase64, latitude, longitude);
```

### **Python example:**

```python
import requests
import base64

API_BASE_URL = 'https://your-domain.com/api/v1/attendance'
API_KEY = 'your_api_key_here'

def check_in(photo_path, latitude, longitude):
    # Read and encode photo
    with open(photo_path, 'rb') as f:
        photo_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Make request
    response = requests.post(
        f'{API_BASE_URL}/check-in',
        json={
            'photo': photo_base64,
            'latitude': latitude,
            'longitude': longitude
        },
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
    )

    result = response.json()

    if result['success']:
        print(f"Check-in successful: {result['data']}")
        return result['data']
    else:
        print(f"Error: {result['error']}")
        return None

# Usage:
# check_in('selfie.jpg', -6.028448, 106.047287)
```

---

## 🧪 **Testing API with cURL**

### **Check-In:**
```bash
curl -X POST http://localhost:8069/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "photo": "BASE64_IMAGE_HERE",
    "latitude": -6.028448,
    "longitude": 106.047287,
    "employee_id": 123
  }'
```

### **Get Status:**
```bash
curl -X GET http://localhost:8069/api/v1/attendance/status \
  -H "X-API-Key: your_api_key"
```

### **Get History:**
```bash
curl -X GET "http://localhost:8069/api/v1/attendance/history?limit=10" \
  -H "X-API-Key: your_api_key"
```

### **Get Photo:**
```bash
curl -X GET "http://localhost:8069/api/v1/attendance/photo/456/check_in?api_key=your_api_key" \
  --output photo.jpg
```

---

## 🧪 **Testing with Postman**

### **Import Collection:**

Create new collection with these requests:

**1. Check-In:**
- Method: `POST`
- URL: `{{base_url}}/check-in`
- Headers:
  - `Content-Type`: `application/json`
  - `X-API-Key`: `{{api_key}}`
- Body (JSON):
```json
{
  "photo": "{{test_photo_base64}}",
  "latitude": -6.028448,
  "longitude": 106.047287
}
```

**2. Check-Out:**
- Method: `POST`
- URL: `{{base_url}}/check-out`
- Body: Same as check-in

**3. Get Status:**
- Method: `GET`
- URL: `{{base_url}}/status`

**4. Get History:**
- Method: `GET`
- URL: `{{base_url}}/history?limit=10`

**Environment Variables:**
- `base_url`: `http://localhost:8069/api/v1/attendance`
- `api_key`: `your_api_key_here`

---

## ⚠️ **Error Codes & Messages**

| Code | Message | Description |
|------|---------|-------------|
| 400 | Photo is required | Missing photo in request |
| 400 | Already checked in | Employee already has open attendance |
| 400 | Already checked out | No open attendance to check-out |
| 401 | Invalid API key | API key not valid |
| 401 | Authentication required | No API key or session |
| 404 | No employee record found | User not linked to employee |
| 404 | No open attendance found | No check-in to check-out |
| 404 | Photo not found | Attendance has no photo |
| 500 | Server error | Internal server error |

---

## 🔒 **Security Best Practices**

### **For Production:**

1. **Use HTTPS** (mandatory)
   ```
   https://your-domain.com/api/v1/...
   ```

2. **Secure API Key Storage**
   - Don't hardcode in app
   - Store in secure keychain/keystore
   - Rotate keys regularly

3. **Rate Limiting**
   - Implement rate limiting per API key
   - Max 100 requests/minute recommended

4. **CORS Configuration**
   ```python
   # In controller, restrict CORS:
   'Access-Control-Allow-Origin': 'https://your-app-domain.com'
   ```

5. **Photo Size Validation**
   - Max 1MB per photo
   - Validate image format (JPEG only)

6. **GPS Validation**
   - Validate latitude (-90 to 90)
   - Validate longitude (-180 to 180)

7. **Audit Logging**
   - Log all API requests
   - Track failed authentication attempts

---

## 📊 **Performance Notes**

- **Photo upload:** ~100-200 KB per photo (JPEG quality 0.85)
- **Request time:** ~500ms - 2s (depends on photo size)
- **Max concurrent requests:** 100 (default Odoo)
- **Database:** Photos stored as attachments (efficient)

---

## 🚀 **Next Steps**

After upgrading module:

1. ✅ Test APIs with cURL or Postman
2. ✅ Setup API key authentication
3. ✅ Document API key to mobile team
4. ✅ Test check-in/check-out flow
5. ✅ Verify photos saved correctly
6. ✅ Test error handling
7. ✅ Deploy to production with HTTPS

---

**API is ready for mobile app integration!** 📱✨
