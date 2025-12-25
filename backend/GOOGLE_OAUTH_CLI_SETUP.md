# 🔐 Google OAuth Setup - gcloud CLI (Command Line)

## ✅ gcloud CLI orqali OAuth Client Yaratish

Agar sizda Google Cloud CLI (`gcloud`) o'rnatilgan bo'lsa, terminal orqali ham OAuth client yaratishingiz mumkin.

---

## 📋 Oldindan Talablar

### 1. gcloud CLI O'rnatish
Agar o'rnatilmagan bo'lsa:
- Windows: https://cloud.google.com/sdk/docs/install
- Yoki: `winget install Google.CloudSDK`

### 2. Authentication
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 🚀 OAuth Client Yaratish (gcloud CLI)

### Variant 1: Web Application uchun (Tavsiya etiladi)

```bash
# Project ID ni o'rnating
PROJECT_ID="your-project-id"
CLIENT_NAME="SmartCareer AI Web"
REDIRECT_URI="http://localhost:8000/api/v1/auth/callback/google"

# OAuth client yaratish
gcloud auth application-default login

# OAuth 2.0 Client ID yaratish (Web application)
gcloud alpha iap oauth-clients create "${CLIENT_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="${CLIENT_NAME}" \
    --allowed-redirect-uris="${REDIRECT_URI}"
```

**⚠️ Eslatma:** `gcloud alpha iap oauth-clients` hali experimental. Web Console tavsiya etiladi.

---

### Variant 2: REST API orqali (Ishonchli)

```bash
# Project ID ni o'rnating
PROJECT_ID="your-project-id"
CLIENT_NAME="SmartCareer AI Web"
REDIRECT_URI="http://localhost:8000/api/v1/auth/callback/google"

# OAuth consent screen sozlash (bir marta)
gcloud auth application-default login

# OAuth 2.0 Client ID yaratish
gcloud projects create-oauth-client \
    --project="${PROJECT_ID}" \
    --display-name="${CLIENT_NAME}" \
    --redirect-uris="${REDIRECT_URI}"
```

---

### Variant 3: REST API to'g'ridan-to'g'ri (Eng ishonchli)

```bash
# 1. Access token olish
ACCESS_TOKEN=$(gcloud auth print-access-token)

# 2. Project ID ni o'rnating
PROJECT_ID="your-project-id"

# 3. OAuth client yaratish
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

---

## ✅ Eng Oson Usul: Web Console (Tavsiya etiladi)

gcloud CLI hali OAuth 2.0 Client ID yaratish uchun to'liq qo'llab-quvvatlanmaydi. 

**Tavsiya:** Web Console orqali yarating:
1. https://console.cloud.google.com/apis/credentials
2. "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Redirect URI: `http://localhost:8000/api/v1/auth/callback/google`

---

## 🔧 Credentials Olish (gcloud CLI)

Agar credentials allaqachon yaratilgan bo'lsa:

```bash
# Barcha OAuth client'larni ko'rish
gcloud auth application-default print-access-token

# Yoki REST API orqali:
PROJECT_ID="your-project-id"
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X GET \
  "https://apigee.googleapis.com/v1/organizations/${PROJECT_ID}/oauth2/clients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

---

## 📝 .env Fayliga Qo'shish

Credentials olingandan keyin `backend/.env` fayliga qo'shing:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
OAUTH_ENABLED=true
```

---

## 🧪 Test Qilish

```bash
# Backend restart
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# Browser'da test qiling
# http://localhost:3000/login → "Google" tugmasi
```

---

## 📚 Qo'shimcha Ma'lumot

- **Web Console:** https://console.cloud.google.com/apis/credentials
- **gcloud CLI Docs:** https://cloud.google.com/sdk/gcloud/reference
- **OAuth 2.0 Guide:** https://developers.google.com/identity/protocols/oauth2

---

## ⚠️ Eslatma

**Hozirgi vaqtda eng oson va ishonchli usul:**
1. Web Console orqali yaratish (GOOGLE_OAUTH_SETUP.md da batafsil)
2. Credentials'ni `.env` ga qo'yish
3. Backend restart

gcloud CLI OAuth client yaratish uchun hali experimental va to'liq qo'llab-quvvatlanmaydi.

