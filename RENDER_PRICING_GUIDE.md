# 💰 Render.com Pricing Guide - SmartCareer AI

## 📊 Instance Type Tanlash

### 🆓 Free Tier (Test/Development uchun)

**Xususiyatlar:**
- **RAM**: 512 MB
- **CPU**: 0.1 CPU
- **Narx**: $0/oy
- **Cheklovlar**: 
  - Inactivity'dan keyin to'xtaydi (spin down)
  - SSH yo'q
  - Scaling yo'q
  - Persistent disks yo'q

**Tavsiya:**
- ✅ **Test uchun yaxshi**
- ✅ **Development**
- ❌ **Production uchun tavsiya etilmaydi**

---

### 💼 Production Plans

#### 1. Starter ($7/oy) - **Kichik loyihalar**

**Xususiyatlar:**
- **RAM**: 512 MB
- **CPU**: 0.5 CPU
- **Narx**: $7/oy

**Tavsiya:**
- ✅ **Kichik loyihalar** (100-500 user)
- ✅ **MVP**
- ✅ **Testing**
- ⚠️ **RAM cheklangan** (512 MB)

**SmartCareer AI uchun:**
- Backend: ⚠️ Minimal (yaxshi ishlaydi, lekin cheklangan)
- Frontend: ✅ Static Site (yaxshi)

---

#### 2. Standard ($25/oy) - **Tavsiya etiladi** ⭐

**Xususiyatlar:**
- **RAM**: 2 GB
- **CPU**: 1 CPU
- **Narx**: $25/oy

**Tavsiya:**
- ✅ **O'rta loyihalar** (500-2000 user)
- ✅ **Production-ready**
- ✅ **Yaxshi performance**
- ✅ **SSH access**
- ✅ **Scaling**

**SmartCareer AI uchun:**
- Backend: ✅ **Ideal** (2 GB RAM yetarli)
- Frontend: ✅ Static Site yoki Web Service

**Jami xarajat (Backend + Frontend + Database):**
- Backend: $25/oy
- Frontend: $7/oy (Starter) yoki Free (Static Site)
- Database: $7/oy (Starter)
- **Jami**: ~$39-42/oy

---

#### 3. Pro ($85/oy) - **Katta loyihalar**

**Xususiyatlar:**
- **RAM**: 4 GB
- **CPU**: 2 CPU
- **Narx**: $85/oy

**Tavsiya:**
- ✅ **Katta loyihalar** (2000+ user)
- ✅ **Yuqori performance**
- ✅ **Heavy traffic**

**SmartCareer AI uchun:**
- Backend: ✅ **Katta loyihalar uchun**
- Frontend: ✅ **SSR yoki Static Site**

---

#### 4. Pro Plus ($175/oy) - **Enterprise**

**Xususiyatlar:**
- **RAM**: 8 GB
- **CPU**: 4 CPU
- **Narx**: $175/oy

**Tavsiya:**
- ✅ **Enterprise loyihalar**
- ✅ **Yuqori load**

---

#### 5. Pro Max ($225/oy) - **Enterprise+**

**Xususiyatlar:**
- **RAM**: 16 GB
- **CPU**: 4 CPU
- **Narx**: $225/oy

---

#### 6. Pro Ultra ($450/oy) - **Maximum**

**Xususiyatlar:**
- **RAM**: 32 GB
- **CPU**: 8 CPU
- **Narx**: $450/oy

---

## 🎯 SmartCareer AI uchun Tavsiyalar

### Variant 1: **MVP/Test** (Eng Arzon)

| Service | Plan | Narx |
|---------|------|------|
| Backend | Free | $0 |
| Frontend | Static Site (Free) | $0 |
| Database | Free (90 kun) | $0 |
| **Jami** | | **$0** (90 kun) |

**Cheklovlar:**
- Backend inactivity'dan keyin to'xtaydi
- Database 90 kundan keyin $7/oy

---

### Variant 2: **Production (Kichik)** ⭐ Tavsiya etiladi

| Service | Plan | Narx |
|---------|------|------|
| Backend | Starter | $7/oy |
| Frontend | Static Site (Free) | $0 |
| Database | Starter | $7/oy |
| **Jami** | | **$14/oy** |

**Xususiyatlar:**
- ✅ Production-ready
- ✅ 24/7 ishlaydi
- ✅ SSH access
- ⚠️ RAM cheklangan (512 MB)

---

### Variant 3: **Production (O'rta)** ⭐⭐ Eng yaxshi

| Service | Plan | Narx |
|---------|------|------|
| Backend | Standard | $25/oy |
| Frontend | Static Site (Free) | $0 |
| Database | Starter | $7/oy |
| **Jami** | | **$32/oy** |

**Xususiyatlar:**
- ✅ **Ideal performance**
- ✅ **2 GB RAM** (yetarli)
- ✅ **1 CPU** (yaxshi)
- ✅ **SSH access**
- ✅ **Scaling**

**Tavsiya:** Bu eng yaxshi variant! 🎯

---

### Variant 4: **Production (Katta)**

| Service | Plan | Narx |
|---------|------|------|
| Backend | Pro | $85/oy |
| Frontend | Static Site (Free) | $0 |
| Database | Starter | $7/oy |
| **Jami** | | **$92/oy** |

**Xususiyatlar:**
- ✅ **Yuqori performance**
- ✅ **4 GB RAM**
- ✅ **2 CPU**
- ✅ **Katta traffic**

---

## 📝 Database Plans

### PostgreSQL:

| Plan | RAM | Storage | Narx |
|------|-----|---------|------|
| Free | - | 1 GB | $0 (90 kun) |
| Starter | - | 1 GB | $7/oy |
| Standard | - | 10 GB | $20/oy |
| Pro | - | 25 GB | $90/oy |

**Tavsiya:**
- Test: Free (90 kun)
- Production: Starter ($7/oy) - 1 GB yetarli

---

## 🎯 Xulosa va Tavsiyalar

### Test/Development:
```
✅ Free tier (90 kun)
✅ Jami: $0
```

### Production (Kichik):
```
✅ Backend: Starter ($7/oy)
✅ Frontend: Static Site (Free)
✅ Database: Starter ($7/oy)
✅ Jami: $14/oy
```

### Production (O'rta) - **Tavsiya etiladi** ⭐:
```
✅ Backend: Standard ($25/oy)
✅ Frontend: Static Site (Free)
✅ Database: Starter ($7/oy)
✅ Jami: $32/oy
```

### Production (Katta):
```
✅ Backend: Pro ($85/oy)
✅ Frontend: Static Site (Free)
✅ Database: Starter ($7/oy)
✅ Jami: $92/oy
```

---

## 💡 Qo'shimcha Maslahatlar

1. **Frontend Static Site** - Har doim Free (eng yaxshi)
2. **Backend** - Standard ($25/oy) eng yaxshi nisbat
3. **Database** - Starter ($7/oy) yetarli
4. **Redis** (ixtiyoriy) - Free tier (25 MB) yoki Starter ($10/oy)

---

## 🚀 Boshlash

1. **Free tier** bilan boshlang (test uchun)
2. **Starter** ga upgrade qiling (production)
3. **Standard** ga upgrade qiling (traffic oshganda)

**Tavsiya:** Standard plan bilan boshlang - $32/oy professional loyiha uchun juda yaxshi narx! 🎯

