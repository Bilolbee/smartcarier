# ⚡ Render.com - Tezkor Boshlash (10 daqiqada)

## 📋 Qadam-baqadam Ko'rsatma

### 1️⃣ GitHub Repository Tayyorlash

1. Loyihani GitHub'ga push qiling:
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

---

### 2️⃣ Render.com Account Yaratish

1. https://render.com ga kiring
2. **"Get Started for Free"** bosing
3. GitHub account bilan login qiling
4. Repository'ni ulang

---

### 3️⃣ PostgreSQL Database Yaratish

1. Render Dashboard → **"New +"** → **"PostgreSQL"**
2. Sozlamalar:
   - **Name**: `smartcareer-db`
   - **Database**: `smartcareer`
   - **User**: `smartcareer_user`
   - **Region**: `Frankfurt` (yoki yaqin)
   - **Plan**: `Free` (test uchun)
3. **"Create Database"** bosing
4. **Internal Database URL** ni saqlang!

---

### 4️⃣ Backend Service Yaratish

1. **"New +"** → **"Web Service"**
2. GitHub repository'ni tanlang
3. Sozlamalar:

#### Basic:
- **Name**: `smartcareer-backend`
- **Region**: Database bilan bir xil
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt && alembic upgrade head
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### Environment Variables:
Quyidagilarni qo'shing (batafsil: `RENDER_DEPLOYMENT.md`):

```env
# Database (PostgreSQL'dan Internal Database URL)
DATABASE_URL=postgresql://user:password@host:5432/database

# Application
SECRET_KEY=generate-random-32-chars-here
DEBUG=false

# AI Provider
GEMINI_API_KEY=your-gemini-key
AI_PROVIDER=gemini

# OAuth (Google)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=https://smartcareer-backend.onrender.com/api/v1/auth/callback/google
OAUTH_ENABLED=true

# Frontend URL (keyinroq to'ldirasiz)
FRONTEND_URL=https://smartcareer-frontend.onrender.com
CORS_ORIGINS=https://smartcareer-frontend.onrender.com

# Email (SMTP)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

4. **"Create Web Service"** bosing
5. Deploy kuting (5-10 daqiqa)

---

### 5️⃣ Frontend Service Yaratish

1. **"New +"** → **"Static Site"** (yoki **"Web Service"**)
2. GitHub repository'ni tanlang
3. Sozlamalar:

#### Static Site:
- **Name**: `smartcareer-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`
- **Build Command**:
  ```bash
  npm install && npm run build
  ```
- **Publish Directory**: `.next`

#### Environment Variables:
```env
NEXT_PUBLIC_API_URL=https://smartcareer-backend.onrender.com/api/v1
NEXT_PUBLIC_FRONTEND_URL=https://smartcareer-frontend.onrender.com
```

4. **"Create Static Site"** bosing
5. Deploy kuting (3-5 daqiqa)

---

### 6️⃣ Environment Variables Yangilash

#### Backend'da:
1. Backend service → **"Environment"**
2. `FRONTEND_URL` va `CORS_ORIGINS` ni frontend URL bilan yangilang
3. `GOOGLE_REDIRECT_URI` ni backend URL bilan yangilang

#### Frontend'da:
1. Frontend service → **"Environment"**
2. `NEXT_PUBLIC_API_URL` ni backend URL bilan yangilang

---

### 7️⃣ Google OAuth Redirect URI Yangilash

1. Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. OAuth Client ID'ni oching
3. **Authorized redirect URIs** ga qo'shing:
   ```
   https://smartcareer-backend.onrender.com/api/v1/auth/callback/google
   ```

---

### 8️⃣ Test Qilish

1. **Backend Health Check**:
   ```
   https://smartcareer-backend.onrender.com/health
   ```

2. **Frontend**:
   ```
   https://smartcareer-frontend.onrender.com
   ```

3. **Login Test**:
   - Frontend'ga kiring
   - Login/Register qiling
   - Google OAuth'ni test qiling

---

## 🚨 Xatoliklar

### Database Connection Xatosi
- `DATABASE_URL` ni tekshiring
- Internal Database URL ishlatishni tavsiya qilaman
- SSL mode: `?sslmode=require` qo'shing

### Build Xatosi
- Logs'ni tekshiring: Service → **"Logs"**
- `requirements.txt` da barcha dependencies borligini tekshiring

### CORS Xatosi
- Backend'da `CORS_ORIGINS` ga frontend URL'ni qo'shing
- Frontend va Backend URL'lar to'g'ri ekanligini tekshiring

---

## 📊 Monitoring

### Logs Ko'rish
1. Service → **"Logs"**
2. Real-time logs
3. Error filter

### Health Check
```bash
curl https://smartcareer-backend.onrender.com/health
```

---

## ✅ Checklist

- [ ] GitHub repository tayyor
- [ ] Render.com account yaratildi
- [ ] PostgreSQL database yaratildi
- [ ] Backend service yaratildi va deploy qilindi
- [ ] Frontend service yaratildi va deploy qilindi
- [ ] Environment Variables to'ldirildi
- [ ] Google OAuth redirect URI yangilandi
- [ ] Health check test qilindi
- [ ] Login/Register test qilindi

---

## 🎯 Xulosa

1. ✅ Database yarating
2. ✅ Backend deploy qiling
3. ✅ Frontend deploy qiling
4. ✅ Environment Variables'ni to'ldiring
5. ✅ OAuth sozlang
6. ✅ Test qiling!

**Tayyor!** 🚀

**Batafsil ma'lumot:** `RENDER_DEPLOYMENT.md`

