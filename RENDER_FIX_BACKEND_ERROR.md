# 🔧 Render.com Xatolik: "cd: backend: No such file or directory"

## ❌ Xatolik

```
bash: line 1: cd: backe No such file or directory
```

## 🔍 Muammo

Build command `cd backend` qilmoqchi, lekin `backend` papkasi topilmayapti.

---

## ✅ Yechimlar

### Variant 1: Root Directory'ni Bo'sh Qoldirish (Tavsiya)

Agar repository root'da `backend` papkasi yo'q bo'lsa:

1. **Settings** → **Root Directory** maydonini **bo'sh qoldiring**
2. **Build Command** ni o'zgartiring:
   ```
   pip install -r backend/requirements.txt && cd backend && alembic upgrade head
   ```
3. **Start Command** ni o'zgartiring:
   ```
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

---

### Variant 2: Root Directory'ni Tekshirish

1. **Settings** → **Root Directory** maydoniga qarang
2. Agar `backend` yozilgan bo'lsa, uni **bo'sh qoldiring**
3. **Build Command** va **Start Command** ni Variant 1 dagidek o'zgartiring

---

### Variant 3: To'g'ri Sozlamalar (Agar backend papkasi bor bo'lsa)

1. **Root Directory**: `backend` (agar papka bor bo'lsa)
2. **Build Command**:
   ```
   pip install -r requirements.txt && alembic upgrade head
   ```
   (Root Directory `backend` bo'lsa, `cd backend` kerak emas!)

3. **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   (Root Directory `backend` bo'lsa, `cd backend` kerak emas!)

---

## 🎯 Eng Oson Yechim

### Agar Root Directory bo'sh bo'lsa:

**Build Command:**
```
pip install -r backend/requirements.txt && cd backend && alembic upgrade head
```

**Start Command:**
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Agar Root Directory `backend` bo'lsa:

**Build Command:**
```
pip install -r requirements.txt && alembic upgrade head
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 📝 Qadam-baqadam

1. **Settings** ga kiring
2. **Root Directory** ni tekshiring:
   - Agar `backend` yozilgan bo'lsa → **bo'sh qoldiring** yoki **`backend` qoldiring**
3. **Build Command** ni yuqoridagidek o'zgartiring
4. **Start Command** ni yuqoridagidek o'zgartiring
5. **Save Changes** bosing
6. **Manual Deploy** → **Deploy latest commit** bosing

---

## 🔍 Tekshirish

Repository'da `backend` papkasi borligini tekshiring:

```bash
# GitHub'da:
https://github.com/Bilolbee/smartcarier/tree/main/backend
```

Agar papka bor bo'lsa → Variant 3
Agar papka yo'q bo'lsa → Variant 1

---

## ✅ Xulosa

**Eng oson yechim:**

1. **Root Directory**: Bo'sh qoldiring
2. **Build Command**: 
   ```
   pip install -r backend/requirements.txt && cd backend && alembic upgrade head
   ```
3. **Start Command**:
   ```
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

Yoki:

1. **Root Directory**: `backend`
2. **Build Command**:
   ```
   pip install -r requirements.txt && alembic upgrade head
   ```
3. **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

**Save va Deploy qiling!**

