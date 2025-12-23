# 🚀 SmartCareer AI - Tez Deploy Qilish

## 10 daqiqada online!

---

## 1️⃣ FRONTEND - Vercel (BEPUL)

### Qadamlar:
```bash
1. https://vercel.com ga boring
2. GitHub bilan sign up
3. "New Project" bosing
4. Repository ni import qiling
5. Root directory: frontend
6. Framework: Next.js (avtomatik aniqlanadi)
7. Environment variables qo'shing:
   - NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
8. Deploy bosing!
```

### Natija:
`https://smartcareer-ai.vercel.app`

---

## 2️⃣ BACKEND - Railway ($5/oy)

### Qadamlar:
```bash
1. https://railway.app ga boring
2. GitHub bilan sign up
3. "New Project" → "Deploy from GitHub"
4. Repository ni tanlang
5. Root directory: backend
6. Environment variables qo'shing:
   - DATABASE_URL=postgresql://... (Railway beradi)
   - OPENAI_API_KEY=sk-...
   - JWT_SECRET_KEY=your-secret
   - CORS_ORIGINS=https://smartcareer-ai.vercel.app
7. Deploy!
```

### Natija:
`https://smartcareer-backend.railway.app`

---

## 3️⃣ DATABASE - Supabase (BEPUL)

### Qadamlar:
```bash
1. https://supabase.com ga boring
2. Sign up
3. New Project yarating
4. Database credentials ni oling
5. Railway ga DATABASE_URL qo'shing:
   postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
```

---

## 4️⃣ DOMAIN - smartcareer.uz

### Qadamlar:
```bash
1. webnames.uz yoki ahost.uz dan domain oling (~$15/yil)
2. DNS sozlamalari:
   - A record: @ → Vercel IP
   - CNAME: www → cname.vercel-dns.com
3. Vercel dashboard → Domains → Add domain
```

---

## ⚡ QUICK DEPLOY CHECKLIST

```
Pre-deploy:
[ ] OpenAI API key olindi
[ ] .env fayllar to'ldirildi
[ ] Lokal test qilindi

Frontend (Vercel):
[ ] GitHub ga push qilindi
[ ] Vercel project yaratildi
[ ] Environment variables qo'shildi
[ ] Deploy muvaffaqiyatli

Backend (Railway):
[ ] Railway project yaratildi
[ ] Database ulandi
[ ] Environment variables qo'shildi
[ ] Deploy muvaffaqiyatli

Post-deploy:
[ ] Frontend → Backend API ishlayapti
[ ] Auth flow ishlayapti
[ ] AI generation ishlayapti
[ ] Domain ulandi
```

---

## 🔧 DEBUGGING

### Frontend xatolar:
```bash
# Vercel logs ko'rish
vercel logs --follow

# Lokal build test
npm run build
```

### Backend xatolar:
```bash
# Railway logs ko'rish
railway logs

# Health check
curl https://your-backend.railway.app/health
```

---

## 💰 XARAJATLAR

| Xizmat | Narx | Izoh |
|--------|------|------|
| Vercel | $0 | Hobby plan, 100GB bandwidth |
| Railway | $5/oy | Starter plan |
| Supabase | $0 | 500MB database |
| Domain | $15/yil | .uz domain |
| OpenAI | ~$20/oy | 1000 ta resume uchun |
| **JAMI** | **~$25/oy** | |

---

## 🎯 KEYINGI QADAMLAR

Deploy qilgandan keyin:
1. [ ] Google Analytics qo'shish
2. [ ] Sentry error tracking
3. [ ] Telegram bot xabarnomalar
4. [ ] Click.uz to'lov integratsiya
5. [ ] SSL check

---

## 📞 YORDAM KERAK?

- Vercel docs: https://vercel.com/docs
- Railway docs: https://docs.railway.app
- Supabase docs: https://supabase.com/docs

