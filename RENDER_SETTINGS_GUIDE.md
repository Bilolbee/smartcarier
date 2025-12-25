# ⚙️ Render.com Service Settings - To'g'ri Sozlash

## 📋 Qaysi Sozlamalarni O'zgartirish Kerak

### ✅ To'g'ri Sozlamalar:

#### 1. **Name**
```
smartcareer-backend
```
(Yoki istalgan nom, lekin "smartcarier-2" emas)

---

#### 2. **Language**
```
Python 3 ✅ (Bu to'g'ri!)
```

---

#### 3. **Branch**
```
main ✅ (Bu to'g'ri!)
```

---

#### 4. **Region**
```
Oregon (US West) ✅ (Yoki Frankfurt, Singapore - yaqin region)
```

---

#### 5. **Root Directory** ⚠️ MUHIM!
```
backend
```
**Eslatma:** Bu Root Directory'ni to'ldirish kerak! `backend` yozing.

---

#### 6. **Build Command** ⚠️ MUHIM! O'ZGARTIRISH KERAK!
```
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements.txt && cd backend && alembic upgrade head
```

**Yoki agar Root Directory = `backend` bo'lsa:**
```
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
```

**Hozirgi (Noto'g'ri):**
```
$ pip install -r requirements.txt
```

**To'g'ri:**
```
cd backend && pip install -r requirements.txt && alembic upgrade head
```

---

#### 7. **Start Command** ⚠️ MUHIM! O'ZGARTIRISH KERAK!
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Hozirgi (Noto'g'ri):**
```
$ gunicorn your_application.wsgi
```

**To'g'ri:**
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## ✅ To'liq Sozlamalar Ro'yxati

```
Name: smartcareer-backend
Project: (Bo'sh qoldirish mumkin)
Environment: (Bo'sh qoldirish mumkin)
Language: Python 3
Branch: main
Region: Oregon (US West) (yoki yaqin region)
Root Directory: backend
Build Command: cd backend && pip install -r requirements.txt && alembic upgrade head
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎯 Qadam-baqadam

1. **Root Directory** maydoniga `backend` yozing
2. **Build Command** ni quyidagiga o'zgartiring:
   ```
   cd backend && pip install -r requirements.txt && alembic upgrade head
   ```
3. **Start Command** ni quyidagiga o'zgartiring:
   ```
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **"Create Web Service"** tugmasini bosing

---

## ⚠️ Muhim Eslatmalar

1. **Root Directory** - Bu muhim! `backend` yozish kerak
2. **Build Command** - `cd backend &&` bilan boshlanishi kerak
3. **Start Command** - `uvicorn` ishlatish kerak (gunicorn emas!)
4. **$PORT** - Render avtomatik beradi, o'zgartirmang

---

## 🔍 Keyin Nima Qilish Kerak?

1. **Environment Variables** qo'shing (keyingi qadam)
2. **"Create Web Service"** bosing
3. Deploy kuting (5-10 daqiqa)
4. Logs'ni tekshiring

---

## 📝 Environment Variables (Keyingi Qadam)

Service yaratilgandan keyin **"Environment"** tab'ga boring va quyidagilarni qo'shing:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-key
AI_PROVIDER=gemini
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
FRONTEND_URL=https://your-frontend.onrender.com
CORS_ORIGINS=https://your-frontend.onrender.com
```

Batafsil: `RENDER_DEPLOYMENT.md`

