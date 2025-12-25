# 🔐 Render.com Environment Variables - To'liq Ro'yxat

## 📋 Qaysi Environment Variables Qo'shish Kerak

### ✅ Majburiy (Kerak)

#### 1. **DATABASE_URL**
```
NAME: DATABASE_URL
VALUE: postgresql://user:password@host:5432/database
```
**Qayerdan olish:** PostgreSQL Database → **"Internal Database URL"** ni copy qiling

---

#### 2. **SECRET_KEY**
```
NAME: SECRET_KEY
VALUE: [Generate tugmasini bosing yoki random 32 char yozing]
```
**Yoki Generate tugmasini bosing** - Render avtomatik yaratadi

---

#### 3. **GEMINI_API_KEY** (yoki OPENAI_API_KEY)
```
NAME: GEMINI_API_KEY
VALUE: your-gemini-api-key-here
```
**Qayerdan olish:** https://ai.google.dev/

---

#### 4. **AI_PROVIDER**
```
NAME: AI_PROVIDER
VALUE: gemini
```
(Yoki `openai` agar OpenAI ishlatmoqchi bo'lsangiz)

---

### ✅ OAuth (Google) - Agar kerak bo'lsa

#### 5. **GOOGLE_CLIENT_ID**
```
NAME: GOOGLE_CLIENT_ID
VALUE: your-client-id.apps.googleusercontent.com
```

#### 6. **GOOGLE_CLIENT_SECRET**
```
NAME: GOOGLE_CLIENT_SECRET
VALUE: your-client-secret
```

#### 7. **GOOGLE_REDIRECT_URI**
```
NAME: GOOGLE_REDIRECT_URI
VALUE: https://smartcarier-2.onrender.com/api/v1/auth/callback/google
```
**⚠️ Service URL'ni o'zgartiring!**

#### 8. **OAUTH_ENABLED**
```
NAME: OAUTH_ENABLED
VALUE: true
```

---

### ✅ Frontend URL (Keyinroq to'ldirish)

#### 9. **FRONTEND_URL**
```
NAME: FRONTEND_URL
VALUE: https://your-frontend.onrender.com
```
**⚠️ Frontend deploy qilingandan keyin to'ldiring!**

#### 10. **CORS_ORIGINS**
```
NAME: CORS_ORIGINS
VALUE: https://your-frontend.onrender.com
```
**⚠️ Frontend deploy qilingandan keyin to'ldiring!**

---

### ✅ Application Settings

#### 11. **APP_NAME**
```
NAME: APP_NAME
VALUE: SmartCareer AI
```

#### 12. **APP_VERSION**
```
NAME: APP_VERSION
VALUE: 1.0.0
```

#### 13. **DEBUG**
```
NAME: DEBUG
VALUE: false
```

---

### ✅ JWT Settings

#### 14. **ALGORITHM**
```
NAME: ALGORITHM
VALUE: HS256
```

#### 15. **ACCESS_TOKEN_EXPIRE_MINUTES**
```
NAME: ACCESS_TOKEN_EXPIRE_MINUTES
VALUE: 30
```

#### 16. **REFRESH_TOKEN_EXPIRE_DAYS**
```
NAME: REFRESH_TOKEN_EXPIRE_DAYS
VALUE: 7
```

---

### ✅ Email Settings (Ixtiyoriy)

#### 17. **SMTP_HOST**
```
NAME: SMTP_HOST
VALUE: smtp.gmail.com
```

#### 18. **SMTP_PORT**
```
NAME: SMTP_PORT
VALUE: 587
```

#### 19. **SMTP_USER**
```
NAME: SMTP_USER
VALUE: your-email@gmail.com
```

#### 20. **SMTP_PASSWORD**
```
NAME: SMTP_PASSWORD
VALUE: your-app-password
```

#### 21. **SMTP_FROM_EMAIL**
```
NAME: SMTP_FROM_EMAIL
VALUE: noreply@smartcareer.uz
```

#### 22. **SMTP_FROM_NAME**
```
NAME: SMTP_FROM_NAME
VALUE: SmartCareer AI
```

#### 23. **SMTP_USE_TLS**
```
NAME: SMTP_USE_TLS
VALUE: true
```

---

### ✅ Payments (Stripe) - Agar kerak bo'lsa

#### 24. **STRIPE_SECRET_KEY**
```
NAME: STRIPE_SECRET_KEY
VALUE: sk_live_your-stripe-secret-key
```

#### 25. **STRIPE_WEBHOOK_SECRET**
```
NAME: STRIPE_WEBHOOK_SECRET
VALUE: whsec_your-webhook-secret
```

#### 26. **PAYMENTS_REQUIRE_WEBHOOK_SECRET**
```
NAME: PAYMENTS_REQUIRE_WEBHOOK_SECRET
VALUE: true
```

---

## 🎯 Minimal Sozlamalar (Boshlash uchun)

Agar hamma narsani qo'shishni xohlamasangiz, quyidagilar yetarli:

```
1. DATABASE_URL (PostgreSQL'dan)
2. SECRET_KEY (Generate tugmasini bosing)
3. GEMINI_API_KEY (Google Gemini'dan)
4. AI_PROVIDER = gemini
5. DEBUG = false
```

---

## 📝 Qadam-baqadam

1. **"+ Add Environment Variable"** tugmasini bosing
2. **NAME** maydoniga variable nomini yozing (masalan: `DATABASE_URL`)
3. **VALUE** maydoniga qiymatni yozing
4. Yana **"+ Add Environment Variable"** bosing va keyingisini qo'shing
5. Barcha variables qo'shgandan keyin **"Save Changes"** bosing

---

## 🔍 Qayerdan Olish

### DATABASE_URL:
1. Render Dashboard → PostgreSQL Database
2. **"Internal Database URL"** ni copy qiling
3. Environment Variables'ga qo'shing

### SECRET_KEY:
1. **"Generate"** tugmasini bosing (magic wand icon)
2. Yoki random 32 character yozing

### GEMINI_API_KEY:
1. https://ai.google.dev/ ga kiring
2. API key yarating
3. Copy qiling va qo'shing

### GOOGLE_CLIENT_ID va GOOGLE_CLIENT_SECRET:
1. Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. OAuth Client ID yarating
3. Credentials'ni copy qiling

---

## ⚠️ Muhim Eslatmalar

1. **DATABASE_URL** - Bu eng muhim! PostgreSQL'dan olish kerak
2. **SECRET_KEY** - Generate tugmasini ishlatish tavsiya etiladi
3. **FRONTEND_URL** va **CORS_ORIGINS** - Frontend deploy qilingandan keyin to'ldiring
4. **GOOGLE_REDIRECT_URI** - Service URL'ni to'g'ri yozing!

---

## ✅ Xulosa

**Minimal (boshlash uchun):**
- DATABASE_URL
- SECRET_KEY
- GEMINI_API_KEY
- AI_PROVIDER = gemini
- DEBUG = false

**To'liq (production):**
- Yuqoridagi barcha variables

**"+ Add Environment Variable"** tugmasini bosib, har birini qo'shing!

