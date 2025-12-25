# 🔧 Render.com Xatolikni Tuzatish

## ❌ Xatolik

```
error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

## 🔍 Muammo

Render.com service **Docker** rejimida yaratilgan, lekin loyihada Dockerfile yo'q.

## ✅ Yechim

Service'ni **Python Web Service** ga o'zgartirish kerak.

---

## 📝 Qadam-baqadam Tuzatish

### 1️⃣ Service Settings'ga Kirish

1. Render Dashboard → **smartcarier** service
2. **"Settings"** tab'ga boring

### 2️⃣ Service Type O'zgartirish

**"Service Type"** bo'limida:

#### ❌ Hozirgi (Noto'g'ri):
- **Docker** ✅ (bu yerni o'chirish kerak)

#### ✅ To'g'ri:
- **Web Service** ✅
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  cd backend && pip install -r requirements.txt && alembic upgrade head
  ```
- **Start Command**:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### 3️⃣ Root Directory Sozlash

**"Root Directory"** bo'limida:
- **Root Directory**: `backend` ✅

Yoki bo'sh qoldiring (agar service backend/ ichida bo'lsa).

### 4️⃣ Environment Variables Tekshirish

**"Environment"** bo'limida quyidagilar bo'lishi kerak:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
# ... boshqalar
```

### 5️⃣ Save va Deploy

1. **"Save Changes"** bosing
2. **"Manual Deploy"** → **"Deploy latest commit"** bosing
3. Build loglarni kuzatib turing

---

## 🚨 Agar Xatolik Davom Etsa

### Variant 1: Service'ni Qayta Yaratish (Tavsiya)

1. **"Settings"** → **"Delete Service"**
2. **"New +"** → **"Web Service"**
3. GitHub repository'ni tanlang
4. Sozlamalar:

```
Name: smartcarier-backend
Region: Frankfurt (yoki yaqin)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: cd backend && pip install -r requirements.txt && alembic upgrade head
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Environment Variables'ni qo'shing
6. **"Create Web Service"** bosing

### Variant 2: Dockerfile Yaratish (Agar Docker ishlatmoqchi bo'lsangiz)

Agar Docker ishlatmoqchi bo'lsangiz, `backend/Dockerfile` yarating:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

Lekin **tavsiya etilmaydi** - oddiy Python Web Service osonroq!

---

## ✅ To'g'ri Sozlamalar

### Backend Service:

```
Service Type: Web Service (Docker emas!)
Runtime: Python 3
Root Directory: backend
Build Command: cd backend && pip install -r requirements.txt && alembic upgrade head
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Service:

```
Service Type: Static Site (yoki Web Service)
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: .next (agar Static Site bo'lsa)
Start Command: npm start (agar Web Service bo'lsa)
```

---

## 🎯 Xulosa

**Muammo:** Service Docker rejimida, lekin Dockerfile yo'q.

**Yechim:** 
1. Service Settings → Service Type → **Web Service** ga o'zgartiring
2. Build Command va Start Command'ni to'g'ri sozlang
3. Root Directory'ni `backend` qiling
4. Save va Deploy qiling

**Yoki:** Service'ni qayta yarating - **Web Service** sifatida (Docker emas).

---

## 📞 Yordam

Agar muammo davom etsa:
1. Logs'ni tekshiring: Service → **"Logs"**
2. Settings'ni tekshiring: Service → **"Settings"**
3. `RENDER_QUICK_START.md` dagi ko'rsatmalarni qayta bajaring

