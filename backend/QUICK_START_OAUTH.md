# 🚀 Google OAuth - Tezkor Boshlash (5 daqiqada)

## 📍 Hozirgi Holat
Siz Google Cloud Console'da **Credentials** sahifasidasiz.

---

## ✅ Qadam 1: Project Yaratish yoki Tanlash

### Variant A: Yangi Project Yaratish (Agar project yo'q bo'lsa)

1. **"Create project"** tugmasini bosing (o'ng tomonda)
2. Project name: `SmartCareer AI` (yoki istalgan nom)
3. **"Create"** bosing
4. Bir necha soniya kuting (project yaratiladi)

### Variant B: Mavjud Project Tanlash

1. Yuqoridagi **"Select a project"** tugmasini bosing
2. Mavjud project'ni tanlang yoki yangi yarating

---

## ✅ Qadam 2: OAuth Consent Screen Sozlash

Project tanlagandan keyin:

1. Chap menudan **"OAuth consent screen"** ga boring
2. **User type**: **External** ni tanlang → **Create**
3. **App information**:
   - **App name**: `SmartCareer AI`
   - **User support email**: O'zingizning emailingiz
   - **Developer contact**: O'zingizning emailingiz
4. **Save and Continue**
5. **Scopes**: **Save and Continue** (default scopes yetarli)
6. **Test users**: O'zingizni qo'shing (agar test rejimida bo'lsa)
7. **Save and Continue** → **Back to Dashboard**

---

## ✅ Qadam 3: OAuth Client ID Yaratish

1. Chap menudan **"Credentials"** ga boring (yoki yuqoridagi tab)
2. Yuqorida **"+ CREATE CREDENTIALS"** tugmasini bosing
3. **"OAuth client ID"** ni tanlang

### Sozlamalar:

4. **Application type**: **Web application** ✅
5. **Name**: `SmartCareer AI Web`
6. **Authorized JavaScript origins**:
   ```
   http://localhost:3000
   http://localhost:8000
   ```
7. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/callback/google
   ```
8. **Create** bosing

---

## ✅ Qadam 4: Credentials Nusxalash

Yangi oyna ochiladi:

- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

**⚠️ MUHIM:** Client Secret faqat bir marta ko'rsatiladi! Nusxalab oling!

---

## ✅ Qadam 5: Backend .env Fayliga Qo'shish

`backend/.env` faylini oching va quyidagilarni to'ldiring:

```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
OAUTH_ENABLED=true
```

---

## ✅ Qadam 6: Backend Restart

```powershell
# Backend processni to'xtating (Ctrl+C)
# Keyin qayta ishga tushiring:
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Qadam 7: Test Qilish

1. Browser: http://localhost:3000/login
2. **"Google"** tugmasini bosing
3. Google hisobingiz bilan kiring
4. Ruxsat bering
5. Avtomatik dashboard ga kirasiz! ✅

---

## 🚨 Xatoliklar

### "redirect_uri_mismatch"
- Google Cloud Console'da **Authorized redirect URIs** ga quyidagini qo'shing:
  ```
  http://localhost:8000/api/v1/auth/callback/google
  ```

### "access_denied"
- OAuth Consent Screen'da test user sifatida o'zingizni qo'shing

### "invalid_client"
- Client ID yoki Client Secret noto'g'ri
- `.env` faylini tekshiring

---

## 📝 Xulosa

1. ✅ **"Create project"** yoki **"Select a project"** tugmasini bosing
2. ✅ OAuth Consent Screen sozlang
3. ✅ OAuth Client ID yarating
4. ✅ Credentials'ni `.env` ga qo'shing
5. ✅ Backend restart qiling
6. ✅ Test qiling!

**5 daqiqada tayyor!** 🚀

