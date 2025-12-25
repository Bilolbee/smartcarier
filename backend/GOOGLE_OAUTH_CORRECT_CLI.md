# 🔐 Google OAuth - To'g'ri CLI Buyruqlari

## ⚠️ Muhim Eslatma

Siz ko'rsatgan `gcloud iam oauth-clients` buyruqlari **IAM OAuth client'lari** uchun. Bu:
- ❌ **Workforce Identity Pool** uchun
- ❌ **Service-to-service** authentication uchun  
- ❌ **Web application OAuth** uchun emas!

SmartCareer AI uchun **OAuth 2.0 Client ID (Web Application)** kerak.

---

## ✅ To'g'ri Usul: OAuth 2.0 Client ID Yaratish

### Variant 1: Web Console (Tavsiya etiladi - 5 daqiqa)

1. https://console.cloud.google.com/apis/credentials
2. "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Redirect URI: `http://localhost:8000/api/v1/auth/callback/google`

**Batafsil:** `GOOGLE_OAUTH_SETUP.md`

---

### Variant 2: REST API orqali (CLI)

Agar CLI ishlatmoqchi bo'lsangiz:

```bash
# 1. Access token olish
ACCESS_TOKEN=$(gcloud auth print-access-token)

# 2. Project ID ni o'rnating
PROJECT_ID="your-project-id"

# 3. OAuth 2.0 Client ID yaratish (REST API)
curl -X POST \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/oauth2/clients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SmartCareer AI Web",
    "redirectUris": [
      "http://localhost:8000/api/v1/auth/callback/google"
    ],
    "grantTypes": ["authorization_code"],
    "scopes": ["openid", "email", "profile"]
  }'
```

**⚠️ Eslatma:** Bu ham hali experimental. Web Console tavsiya etiladi.

---

### Variant 3: gcloud (Hozircha qo'llab-quvvatlanmaydi)

Hozirgi vaqtda `gcloud` da OAuth 2.0 Client ID yaratish uchun to'g'ridan-to'g'ri buyruq yo'q.

**Yechim:** Web Console yoki REST API (yuqorida).

---

## 🔍 IAM OAuth Client vs OAuth 2.0 Client ID

| Xususiyat | IAM OAuth Client | OAuth 2.0 Client ID |
|-----------|----------------|---------------------|
| **Maqsad** | Workforce Identity Pool | Web Application Login |
| **Buyruq** | `gcloud iam oauth-clients` | Web Console yoki REST API |
| **Foydalanish** | Service-to-service | Browser orqali login |
| **SmartCareer AI** | ❌ Kerak emas | ✅ Kerak |

---

## 📝 Credentials Olish (Agar allaqachon yaratilgan bo'lsa)

Agar siz allaqachon OAuth 2.0 Client ID yaratgan bo'lsangiz:

### Web Console orqali:
1. https://console.cloud.google.com/apis/credentials
2. O'zingizning OAuth client ID'ingizni toping
3. Client ID va Client Secret ni ko'ring

### REST API orqali:
```bash
PROJECT_ID="your-project-id"
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Barcha OAuth client'larni ko'rish
curl -X GET \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/oauth2/clients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

---

## ✅ Tezkor Yechim

**Eng oson va ishonchli:**

1. **Web Console'ga kiring:**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **OAuth client ID yarating:**
   - "Create Credentials" → "OAuth client ID"
   - Application type: **Web application**
   - Redirect URI: `http://localhost:8000/api/v1/auth/callback/google`

3. **Credentials'ni .env ga qo'shing:**
   ```env
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
   OAUTH_ENABLED=true
   ```

4. **Backend restart:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload
   ```

---

## 🎯 Xulosa

- ❌ `gcloud iam oauth-clients` - Bu SmartCareer AI uchun emas
- ✅ **Web Console** - Eng oson va ishonchli usul
- ✅ **REST API** - CLI alternativasi (experimental)

**Tavsiya:** Web Console orqali yarating - 5 daqiqada tayyor! 🚀

