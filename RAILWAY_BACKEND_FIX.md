# 🔧 Railway Backend Xatolikni Tuzatish

## ❌ Xatolik

```
sh: 2: pip: not found
ERROR: failed to build: failed to solve: process "sh -c cd backend && pip install -r requirements.txt && alembic upgrade head" did not complete successfully: exit code: 127
```

## 🔍 Muammo

Railway backend'ni **Docker** sifatida deploy qilmoqchi, lekin Docker image'da Python/pip yo'q.

---

## ✅ Yechim: Python Service (Tavsiya)

### Qadam 1: Eski Service'ni O'chirish

1. Railway Dashboard → Backend service
2. **"Settings"** → **"Delete Service"**
3. Tasdiqlang

### Qadam 2: Yangi Python Service Yaratish

1. Railway Dashboard → Project
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang: `Bilolbee/smartcarier`
4. Railway avtomatik **Python** ni tanlaydi ✅

### Qadam 3: Sozlamalar

1. **Service Name**: `smartcareer-backend`
2. **Root Directory**: `backend`
3. **Build Command**: (avtomatik yoki manual)
   ```
   pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
   ```
4. **Start Command**: (avtomatik yoki manual)
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Qadam 4: Environment Variables

**"Variables"** tab'ga boring va qo'shing (batafsil: `RAILWAY_DEPLOYMENT.md`):

```env
# Database (PostgreSQL'dan avtomatik)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Application
SECRET_KEY=your-secret-key-here
DEBUG=false
APP_NAME=SmartCareer AI
APP_VERSION=1.0.0

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-1.5-flash

# OAuth (Google)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=https://your-backend.railway.app/api/v1/auth/callback/google
OAUTH_ENABLED=true

# Frontend URL
FRONTEND_URL=https://your-frontend.railway.app
CORS_ORIGINS=https://your-frontend.railway.app

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@smartcareer.uz
SMTP_FROM_NAME=SmartCareer AI
SMTP_USE_TLS=true
```

### Qadam 5: Deploy

Railway avtomatik deploy qiladi!

---

## 🔄 Alternativ: Dockerfile Ishlatish

Agar Docker ishlatmoqchi bo'lsangiz:

### 1. Dockerfile Yaratish

`backend/Dockerfile` allaqachon mavjud. Lekin Railway'da Python service osonroq!

### 2. Railway'da Docker Service

1. **"New"** → **"GitHub Repo"**
2. Repository'ni tanlang
3. Railway Dockerfile'ni topadi
4. **Root Directory**: `backend`
5. Deploy qiling

**Lekin tavsiya etilmaydi** - Python service osonroq va tezroq!

---

## ✅ To'g'ri Sozlamalar

### Python Service (Tavsiya):

```
Service Type: Python (avtomatik)
Root Directory: backend
Build Command: pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Docker Service (Alternativ):

```
Service Type: Docker
Root Directory: backend
Dockerfile: backend/Dockerfile (avtomatik topiladi)
```

---

## 🎯 Qadam-baqadam (Tezkor)

1. **Backend service'ni o'chiring** (agar Docker sifatida yaratilgan bo'lsa)
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang
4. Railway avtomatik **Python** ni tanlaydi ✅
5. **Root Directory**: `backend` ni kiriting
6. **Build Command** ni quyidagiga o'zgartiring:
   ```
   pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
   ```
7. **Start Command** ni quyidagiga o'zgartiring:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
8. **Variables** → Environment Variables qo'shing
9. Deploy avtomatik boshlanadi!

---

## 📝 Muhim Eslatmalar

1. **Python Service** - Eng oson va tavsiya etiladi
2. **Docker Service** - Murakkab, lekin ishlaydi
3. **Root Directory** - `backend` bo'lishi kerak
4. **Build Command** - `--no-cache-dir` flag'i Rust muammosini hal qiladi
5. **Start Command** - `$PORT` Railway avtomatik beradi

---

## ✅ Xulosa

**Eng oson yechim:**

1. Backend service'ni o'chiring
2. Yangi **Python service** yarating
3. **Root Directory**: `backend`
4. **Build Command** va **Start Command** ni yuqoridagidek o'zgartiring
5. Environment Variables qo'shing
6. Deploy avtomatik!

**Tayyor!** 🚀

