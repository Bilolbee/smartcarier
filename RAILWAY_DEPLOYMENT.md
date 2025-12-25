# 🚂 Railway.com Deployment Guide - SmartCareer AI

## 📋 Tarkib

1. [Backend Deployment](#backend-deployment)
2. [Frontend Deployment](#frontend-deployment)
3. [Database Setup](#database-setup)
4. [Environment Variables](#environment-variables)

---

## 🔧 Backend Deployment

### Qadam 1: Backend Service Yaratish

1. Railway Dashboard: https://railway.app
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Repository'ni tanlang
4. **"Add Service"** → **"GitHub Repo"**

### Qadam 2: Backend Sozlamalari

1. Service nomi: `smartcareer-backend`
2. **Root Directory**: `backend`
3. **Build Command**: 
   ```
   pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
   ```
4. **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Qadam 3: Environment Variables

Quyidagilarni qo'shing (batafsil: [Environment Variables](#environment-variables))

---

## 🎨 Frontend Deployment

### ❌ Xatolik

```
sh: 2: npm: not found
```

### ✅ Yechim: Railway Node.js Service

Railway'da frontend'ni **Node.js service** sifatida deploy qilish kerak (Docker emas).

---

### Qadam 1: Frontend Service Yaratish

1. Railway Dashboard → Project
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang
4. Service nomi: `smartcareer-frontend`

### Qadam 2: Frontend Sozlamalari

1. **Root Directory**: `frontend`
2. Railway avtomatik Node.js ni tanlaydi
3. **Build Command** (avtomatik yoki manual):
   ```
   npm install && npm run build
   ```
4. **Start Command**:
   ```
   npm start
   ```

### Qadam 3: Environment Variables (Frontend)

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app
```

---

## 🗄️ Database Setup

### PostgreSQL Database Yaratish

1. Railway Dashboard → Project
2. **"New"** → **"Database"** → **"PostgreSQL"**
3. Database avtomatik yaratiladi
4. **"Variables"** tab'da `DATABASE_URL` ni ko'ring

---

## 🔐 Environment Variables

### Backend Environment Variables

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

# Payments (Stripe)
STRIPE_SECRET_KEY=sk_live_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret
PAYMENTS_REQUIRE_WEBHOOK_SECRET=true
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app
```

---

## 🚨 Frontend Xatolikni Tuzatish

### Muammo: `npm: not found`

Bu xatolik Docker image'da Node.js yo'qligini ko'rsatadi.

### Yechim 1: Node.js Service (Tavsiya)

1. Frontend service'ni **o'chiring** (agar Docker sifatida yaratilgan bo'lsa)
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang
4. Railway avtomatik Node.js ni tanlaydi
5. **Root Directory**: `frontend`
6. Build va Start command'lar avtomatik sozlanadi

### Yechim 2: Dockerfile Yaratish (Agar Docker ishlatmoqchi bo'lsangiz)

`frontend/Dockerfile` yarating:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production=false

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Lekin **tavsiya etilmaydi** - Node.js service osonroq!

---

## ✅ To'g'ri Sozlamalar

### Backend Service:

```
Service Type: Python
Root Directory: backend
Build Command: pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Service:

```
Service Type: Node.js (Docker emas!)
Root Directory: frontend
Build Command: npm install && npm run build (avtomatik)
Start Command: npm start (avtomatik)
```

---

## 🎯 Qadam-baqadam

### Frontend Deploy:

1. Railway Dashboard → Project
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang
4. Railway avtomatik **Node.js** ni tanlaydi
5. **Root Directory**: `frontend` ni kiriting
6. **Variables** → Environment Variables qo'shing
7. Deploy avtomatik boshlanadi

---

## 📝 Railway vs Render.com

| Xususiyat | Railway | Render.com |
|-----------|---------|------------|
| **Backend** | Python service | Web Service |
| **Frontend** | Node.js service | Static Site |
| **Database** | PostgreSQL (avtomatik) | PostgreSQL (alohida) |
| **Deploy** | GitHub push | GitHub push |

---

## ✅ Xulosa

**Frontend xatolikni tuzatish:**

1. Frontend service'ni **o'chiring** (agar Docker sifatida yaratilgan bo'lsa)
2. **"New"** → **"GitHub Repo"**
3. Railway avtomatik **Node.js** ni tanlaydi
4. **Root Directory**: `frontend`
5. Environment Variables qo'shing
6. Deploy avtomatik boshlanadi

**Tayyor!** 🚀

