# 📡 API Quick Reference

---

## 🔑 **Authentication**
```
Header: X-API-Key: your_api_key_here
```

---

## 📋 **Endpoints Summary**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/attendance/check-in` | Check-in with photo + GPS |
| POST | `/api/v1/attendance/check-out` | Check-out with photo + GPS |
| GET | `/api/v1/attendance/status` | Get current status |
| GET | `/api/v1/attendance/history` | Get attendance history |
| GET | `/api/v1/attendance/photo/{id}/{type}` | Get photo image |

---

## ⚡ **Quick Examples**

### **Check-In:**
```bash
curl -X POST http://localhost:8069/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"photo": "BASE64", "latitude": -6.028, "longitude": 106.047}'
```

### **Check-Out:**
```bash
curl -X POST http://localhost:8069/api/v1/attendance/check-out \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"photo": "BASE64", "latitude": -6.028, "longitude": 106.047}'
```

### **Get Status:**
```bash
curl http://localhost:8069/api/v1/attendance/status \
  -H "X-API-Key: YOUR_KEY"
```

### **Get History:**
```bash
curl "http://localhost:8069/api/v1/attendance/history?limit=30" \
  -H "X-API-Key: YOUR_KEY"
```

### **Get Photo:**
```bash
curl "http://localhost:8069/api/v1/attendance/photo/456/check_in?api_key=YOUR_KEY" \
  --output photo.jpg
```

---

## 📱 **Mobile App Code (JavaScript)**

```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://your-domain.com/api/v1/attendance';

async function checkIn(photoBase64, lat, lng) {
  const res = await fetch(`${BASE_URL}/check-in`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      photo: photoBase64,
      latitude: lat,
      longitude: lng
    })
  });
  return await res.json();
}

async function getStatus() {
  const res = await fetch(`${BASE_URL}/status`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return await res.json();
}
```

---

## 📄 **Response Format**

### **Success:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### **Error:**
```json
{
  "success": false,
  "data": null,
  "error": "Error message here"
}
```

---

## ⚠️ **Common Errors**

| Code | Error | Solution |
|------|-------|----------|
| 401 | Invalid API key | Check API key |
| 400 | Photo is required | Include base64 photo |
| 400 | Already checked in | Check-out first |
| 404 | No employee found | Link user to employee |

---

**Full Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
