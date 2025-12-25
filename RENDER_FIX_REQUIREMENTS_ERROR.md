# 🔧 Render.com Xatolik: "Could not open requirements file"

## ❌ Xatolik

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'backend/requirements.txt'
```

## 🔍 Muammo

Build Command `backend/requirements.txt` ni qidiryapti, lekin:
- Root Directory = `backend` bo'lsa → `backend/requirements.txt` emas, `requirements.txt` bo'lishi kerak
- Root Directory bo'sh bo'lsa → `backend/requirements.txt` to'g'ri, lekin path noto'g'ri bo'lishi mumkin

---

## ✅ Yechimlar

### Variant 1: Root Directory = `backend` (Tavsiya)

Agar **Root Directory** = `backend` bo'lsa:

**Build Command:**
```
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
```

**⚠️ Eslatma:** `cd backend` va `backend/requirements.txt` kerak emas, chunki allaqachon `backend` papkasidasiz!

---

### Variant 2: Root Directory Bo'sh

Agar **Root Directory** bo'sh bo'lsa:

**Build Command:**
```
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements.txt && cd backend && alembic upgrade head
```

---

## 🎯 Qaysi Variant Ishlatish?

### Tekshirish:

1. Render.com Settings → **Root Directory** ni tekshiring
2. Agar `backend` yozilgan bo'lsa → **Variant 1** ishlating
3. Agar bo'sh bo'lsa → **Variant 2** ishlating

---

## 📝 Qadam-baqadam

### Agar Root Directory = `backend` bo'lsa:

1. **Settings** ga kiring
2. **Build Command** ni quyidagiga o'zgartiring:
   ```
   pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
   ```
3. **Start Command** ni quyidagiga o'zgartiring:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   (⚠️ `cd backend` kerak emas!)
4. **Save Changes** bosing
5. **Manual Deploy** → **Deploy latest commit** bosing

---

### Agar Root Directory Bo'sh bo'lsa:

1. **Settings** ga kiring
2. **Build Command** ni quyidagiga o'zgartiring:
   ```
   pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements.txt && cd backend && alembic upgrade head
   ```
3. **Start Command** ni quyidagiga o'zgartiring:
   ```
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Save Changes** bosing
5. **Manual Deploy** → **Deploy latest commit** bosing

---

## ✅ To'g'ri Sozlamalar

### Variant 1 (Root Directory = `backend`):

```
Root Directory: backend
Build Command: pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && alembic upgrade head
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Variant 2 (Root Directory bo'sh):

```
Root Directory: (bo'sh)
Build Command: pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements.txt && cd backend && alembic upgrade head
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🔍 Muhim Eslatma

**Root Directory = `backend` bo'lsa:**
- ❌ `cd backend` kerak emas
- ❌ `backend/requirements.txt` emas
- ✅ `requirements.txt` to'g'ri
- ✅ `uvicorn app.main:app` to'g'ri

**Root Directory bo'sh bo'lsa:**
- ✅ `cd backend` kerak
- ✅ `backend/requirements.txt` to'g'ri
- ✅ `cd backend && uvicorn app.main:app` to'g'ri

---

## ✅ Xulosa

1. **Root Directory** ni tekshiring
2. **Build Command** ni yuqoridagidek o'zgartiring
3. **Start Command** ni yuqoridagidek o'zgartiring
4. **Save va Deploy** qiling

**Eng oson:** Root Directory = `backend` qiling va Variant 1 ishlating!

