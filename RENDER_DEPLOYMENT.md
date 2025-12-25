# 🚀 Render.com Deployment Guide - SmartCareer AI

## 📋 Tarkib

1. [Oldindan Talablar](#oldindan-talablar)
2. [Database Setup (PostgreSQL)](#database-setup-postgresql)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Environment Variables](#environment-variables)
6. [Redis Setup (Ixtiyoriy)](#redis-setup-ixtiyoriy)
7. [Post-Deployment](#post-deployment)

---

## ✅ Oldindan Talablar

1. **Render.com Account**: https://render.com (Free tier mavjud)
2. **GitHub Repository**: Loyiha GitHub'da bo'lishi kerak
3. **Google OAuth Credentials**: Production URL'lar bilan
4. **Stripe Account** (agar payment kerak bo'lsa)

---

## 🗄️ Database Setup (PostgreSQL)

### Qadam 1: PostgreSQL Database Yaratish

1. Render Dashboard: https://dashboard.render.com
2. **"New +"** → **"PostgreSQL"**
3. Sozlamalar:
   - **Name**: `smartcareer-db`
   - **Database**: `smartcareer`
   - **User**: `smartcareer_user`
   - **Region**: Eng yaqin region (yevropa, amerika, hk)
   - **PostgreSQL Version**: `16` (yoki eng yangi)
   - **Plan**: **Free** (test uchun) yoki **Starter** ($7/oy)
4. **"Create Database"** bosing

### Qadam 2: Database Ma'lumotlarini Saqlash

Database yaratilgandan keyin:
- **Internal Database URL**: `postgresql://user:password@host:5432/database`
- **External Database URL**: `postgresql://user:password@host:5432/database`
- **Hostname**, **Port**, **Database**, **Username**, **Password** - bularni saqlang!

---

## 🔧 Backend Deployment

### Qadam 1: Backend Service Yaratish

1. Render Dashboard: **"New +"** → **"Web Service"**
2. GitHub repository'ni ulang
3. Sozlamalar:

#### Basic Settings:
- **Name**: `smartcareer-backend`
- **Region**: Database bilan bir xil region
- **Branch**: `main` (yoki `master`)
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

#### Advanced Settings:
- **Instance Type**: **Free** (test) yoki **Starter** ($7/oy)
- **Auto-Deploy**: `Yes` (GitHub push'dan keyin avtomatik deploy)

### Qadam 2: Environment Variables (Backend)

**"Environment"** bo'limida quyidagilarni qo'shing:

```env
# Application
APP_NAME=SmartCareer AI
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this-generate-random-32-chars

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database
# Yoki Render'dan Internal Database URL ni copy qiling

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
# Yoki OpenAI:
# OPENAI_API_KEY=sk-your-openai-key
# OPENAI_MODEL=gpt-4-turbo-preview

# OAuth2 (Google)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/v1/auth/callback/google
OAUTH_ENABLED=true

# OAuth2 (LinkedIn - ixtiyoriy)
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-secret
LINKEDIN_REDIRECT_URI=https://your-backend.onrender.com/api/v1/auth/callback/linkedin

# Frontend URL
FRONTEND_URL=https://your-frontend.onrender.com

# CORS
CORS_ORIGINS=https://your-frontend.onrender.com,https://www.your-domain.com

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@smartcareer.uz
SMTP_FROM_NAME=SmartCareer AI
SMTP_USE_TLS=true

# SendGrid (Production uchun tavsiya)
# SENDGRID_API_KEY=your-sendgrid-key

# Payments (Stripe)
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
PAYMENTS_REQUIRE_WEBHOOK_SECRET=true

# Redis (Agar Redis addon qo'shgan bo'lsangiz)
REDIS_ENABLED=true
REDIS_URL=redis://user:password@host:6379/0
RATE_LIMIT_USE_REDIS=true
TOKEN_BLACKLIST_USE_REDIS=true
```

### Qadam 3: Build va Deploy

1. **"Create Web Service"** bosing
2. Render avtomatik build va deploy qiladi
3. Logs'ni kuzatib turing

---

## 🎨 Frontend Deployment

### Qadam 1: Frontend Service Yaratish

1. Render Dashboard: **"New +"** → **"Static Site"** (yoki **"Web Service"**)
2. GitHub repository'ni ulang
3. Sozlamalar:

#### Static Site (Tavsiya etiladi):
- **Name**: `smartcareer-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`
- **Build Command**:
  ```bash
  npm install && npm run build
  ```
- **Publish Directory**: `.next`

#### Yoki Web Service (SSR uchun):
- **Name**: `smartcareer-frontend`
- **Root Directory**: `frontend`
- **Build Command**:
  ```bash
  npm install && npm run build
  ```
- **Start Command**:
  ```bash
  npm start
  ```

### Qadam 2: Environment Variables (Frontend)

**"Environment"** bo'limida:

```env
# API URL
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1

# Frontend URL
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.onrender.com

# OAuth (agar kerak bo'lsa)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### Qadam 3: Build va Deploy

1. **"Create Static Site"** bosing
2. Render avtomatik build va deploy qiladi

---

## 🔐 Environment Variables - To'liq Ro'yxat

### Backend (.env)

```bash
# =============================================================================
# APPLICATION
# =============================================================================
APP_NAME=SmartCareer AI
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=generate-with-openssl-rand-hex-32

# =============================================================================
# DATABASE
# =============================================================================
DATABASE_URL=postgresql://user:password@host:5432/database

# =============================================================================
# JWT
# =============================================================================
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# AI PROVIDER
# =============================================================================
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-1.5-flash

# =============================================================================
# OAUTH2
# =============================================================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/v1/auth/callback/google
OAUTH_ENABLED=true

# =============================================================================
# FRONTEND & CORS
# =============================================================================
FRONTEND_URL=https://your-frontend.onrender.com
CORS_ORIGINS=https://your-frontend.onrender.com

# =============================================================================
# EMAIL
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@smartcareer.uz

# =============================================================================
# PAYMENTS
# =============================================================================
STRIPE_SECRET_KEY=sk_live_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret
PAYMENTS_REQUIRE_WEBHOOK_SECRET=true

# =============================================================================
# REDIS (Optional)
# =============================================================================
REDIS_ENABLED=false
REDIS_URL=
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.onrender.com
```

---

## 🔴 Redis Setup (Ixtiyoriy)

Agar Redis kerak bo'lsa (rate limiting, token blacklist):

1. Render Dashboard: **"New +"** → **"Redis"**
2. Sozlamalar:
   - **Name**: `smartcareer-redis`
   - **Plan**: **Free** (test) yoki **Starter** ($10/oy)
3. **"Create Redis"** bosing
4. **Internal Redis URL** ni copy qiling
5. Backend Environment Variables'ga qo'shing:
   ```env
   REDIS_ENABLED=true
   REDIS_URL=redis://user:password@host:6379/0
   ```

---

## 📝 Post-Deployment

### 1. Database Migrations

Backend deploy bo'lgandan keyin, migrations avtomatik ishlaydi (build command'da).

Agar manual ishlatmoqchi bo'lsangiz:
```bash
# Render Shell orqali:
cd backend
alembic upgrade head
```

### 2. Google OAuth Redirect URI Yangilash

1. Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. OAuth Client ID'ni oching
3. **Authorized redirect URIs** ga qo'shing:
   ```
   https://your-backend.onrender.com/api/v1/auth/callback/google
   ```

### 3. Stripe Webhook Sozlash

1. Stripe Dashboard: https://dashboard.stripe.com/webhooks
2. **"Add endpoint"**
3. Endpoint URL:
   ```
   https://your-backend.onrender.com/api/v1/payments/webhook/stripe
   ```
4. Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
5. **Webhook signing secret** ni copy qiling
6. Backend Environment Variables'ga qo'shing:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### 4. Health Check

Backend health check endpoint:
```
https://your-backend.onrender.com/health
```

Frontend:
```
https://your-frontend.onrender.com
```

---

## 🐛 Xatoliklar va Yechimlar

### Backend Build Xatosi

**Muammo**: `psycopg2-binary` install bo'lmaydi
**Yechim**: `requirements.txt` da Python version check qo'shing:
```txt
psycopg2-binary==2.9.9; python_version < "3.13"
psycopg[binary]==3.2.3; python_version >= "3.13"
```

### Database Connection Xatosi

**Muammo**: Database ga ulanmaydi
**Yechim**: 
- `DATABASE_URL` ni tekshiring
- Internal Database URL ishlatishni tavsiya qilaman
- SSL mode: `?sslmode=require`

### Frontend Build Xatosi

**Muammo**: `NEXT_PUBLIC_API_URL` noto'g'ri
**Yechim**: Environment Variables'da `NEXT_PUBLIC_` prefix'i bo'lishi kerak

### CORS Xatosi

**Muammo**: Frontend'dan API'ga so'rov yuborishda CORS xatosi
**Yechim**: Backend'da `CORS_ORIGINS` ga frontend URL'ni qo'shing

---

## 📊 Monitoring

### Render Logs

1. Render Dashboard → Service → **"Logs"**
2. Real-time logs ko'rish
3. Error'larni filter qilish

### Health Checks

Backend:
```bash
curl https://your-backend.onrender.com/health
```

Frontend:
```bash
curl https://your-frontend.onrender.com
```

---

## 💰 Xarajatlar (Taxminiy)

### Free Tier:
- ✅ PostgreSQL: 90 kun (keyin $7/oy)
- ✅ Web Service: 750 soat/oy (Free tier)
- ✅ Static Site: Cheksiz
- ✅ Redis: 25MB (Free tier)

### Starter Plan:
- PostgreSQL: $7/oy
- Web Service: $7/oy
- Redis: $10/oy
- **Jami**: ~$24/oy

---

## 🚀 Tezkor Deploy Checklist

- [ ] GitHub repository tayyor
- [ ] Render.com account yaratildi
- [ ] PostgreSQL database yaratildi
- [ ] Backend service yaratildi va deploy qilindi
- [ ] Frontend service yaratildi va deploy qilindi
- [ ] Environment Variables to'ldirildi
- [ ] Google OAuth redirect URI yangilandi
- [ ] Stripe webhook sozlandi (agar kerak bo'lsa)
- [ ] Health check test qilindi
- [ ] Frontend va Backend o'rtasida connection test qilindi

---

## 📚 Qo'shimcha Ma'lumot

- **Render Docs**: https://render.com/docs
- **PostgreSQL on Render**: https://render.com/docs/databases
- **Environment Variables**: https://render.com/docs/environment-variables

---

## ✅ Xulosa

1. ✅ PostgreSQL database yarating
2. ✅ Backend service yarating va deploy qiling
3. ✅ Frontend service yarating va deploy qiling
4. ✅ Environment Variables'ni to'ldiring
5. ✅ OAuth va Webhook'larni sozlang
6. ✅ Test qiling!

**Tayyor!** 🎉

