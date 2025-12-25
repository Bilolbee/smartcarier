# 🔧 Railway Frontend Xatolikni Tuzatish

## ❌ Xatolik

```
sh: 2: npm: not found
ERROR: failed to build: failed to solve: process "sh -c cd frontend && npm install && npm run build" did not complete successfully: exit code: 127
```

## 🔍 Muammo

Railway frontend'ni **Docker** sifatida deploy qilmoqchi, lekin Docker image'da Node.js/npm yo'q.

---

## ✅ Yechim: Node.js Service (Tavsiya)

### Qadam 1: Eski Service'ni O'chirish

1. Railway Dashboard → Frontend service
2. **"Settings"** → **"Delete Service"**
3. Tasdiqlang

### Qadam 2: Yangi Node.js Service Yaratish

1. Railway Dashboard → Project
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang: `Bilolbee/smartcarier`
4. Railway avtomatik **Node.js** ni tanlaydi ✅

### Qadam 3: Sozlamalar

1. **Service Name**: `smartcareer-frontend`
2. **Root Directory**: `frontend`
3. **Build Command**: (avtomatik yoki manual)
   ```
   npm install && npm run build
   ```
4. **Start Command**: (avtomatik yoki manual)
   ```
   npm start
   ```

### Qadam 4: Environment Variables

**"Variables"** tab'ga boring va qo'shing:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend.railway.app
```

### Qadam 5: Deploy

Railway avtomatik deploy qiladi!

---

## 🔄 Alternativ: Dockerfile Ishlatish

Agar Docker ishlatmoqchi bo'lsangiz:

### 1. Dockerfile Yaratish

`frontend/Dockerfile` yarating (allaqachon yaratilgan: `frontend/Dockerfile`)

### 2. Railway'da Docker Service

1. **"New"** → **"GitHub Repo"**
2. Repository'ni tanlang
3. Railway Dockerfile'ni topadi
4. **Root Directory**: `frontend`
5. Deploy qiling

**Lekin tavsiya etilmaydi** - Node.js service osonroq va tezroq!

---

## ✅ To'g'ri Sozlamalar

### Node.js Service (Tavsiya):

```
Service Type: Node.js (avtomatik)
Root Directory: frontend
Build Command: npm install && npm run build
Start Command: npm start
```

### Docker Service (Alternativ):

```
Service Type: Docker
Root Directory: frontend
Dockerfile: frontend/Dockerfile (avtomatik topiladi)
```

---

## 🎯 Qadam-baqadam (Tezkor)

1. **Frontend service'ni o'chiring** (agar Docker sifatida yaratilgan bo'lsa)
2. **"New"** → **"GitHub Repo"**
3. Repository'ni tanlang
4. Railway avtomatik **Node.js** ni tanlaydi ✅
5. **Root Directory**: `frontend` ni kiriting
6. **Variables** → Environment Variables qo'shing
7. Deploy avtomatik boshlanadi!

---

## 📝 Muhim Eslatmalar

1. **Node.js Service** - Eng oson va tavsiya etiladi
2. **Docker Service** - Murakkab, lekin ishlaydi
3. **Root Directory** - `frontend` bo'lishi kerak
4. **Environment Variables** - `NEXT_PUBLIC_` prefix'i kerak

---

## ✅ Xulosa

**Eng oson yechim:**

1. Frontend service'ni o'chiring
2. Yangi **Node.js service** yarating
3. **Root Directory**: `frontend`
4. Environment Variables qo'shing
5. Deploy avtomatik!

**Tayyor!** 🚀

