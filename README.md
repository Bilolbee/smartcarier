# 🚀 SmartCareer AI

Professional karyera platformasi - AI-powered rezyume yaratish, ish qidirish va HR boshqaruvi.

## 📋 Xususiyatlar

### 👨‍🎓 Student uchun
- ✨ AI bilan professional rezyume yaratish
- 🔍 Mos ishlarni qidirish
- 📝 Bir marta bosish bilan ariza berish
- 📊 Arizalar holatini kuzatish
- 🎯 ATS score va feedback

### 🏢 Kompaniya uchun
- 📢 Vakansiya e'lon qilish
- 🤖 AI yordamida nomzodlarni saralash
- 📋 Arizalarni boshqarish
- 📅 Suhbatlarni rejalashtirish
- 📊 HR analytics

### 👮 Admin uchun
- 👥 Foydalanuvchilarni boshqarish
- 🔍 Error dashboard
- 📊 Tizim statistikasi
- 🏥 Health monitoring

## 🛠️ Texnologiyalar

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy
- **Auth**: JWT (python-jose)
- **AI**: Google Gemini / OpenAI GPT-4
- **Email**: SMTP / SendGrid
- **Cache**: Redis
- **Migration**: Alembic

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Forms**: React Hook Form + Zod
- **Animations**: Framer Motion
- **Charts**: Recharts
- **i18n**: Uzbek, Russian

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite by default)
- Redis (optional, for production)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/smartcareer-ai.git
cd smartcareer-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup_env.py
# Keyin .env faylini to'ldiring (GEMINI_API_KEY majburiy!)

# Run migrations
alembic upgrade head

# Seed test data
python seed_data.py

# Start server
uvicorn app.main:app --reload
```

Backend ishga tushdi: http://localhost:8000

API Docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
node setup_env.js
# Default: http://localhost:8000

# Start development server
npm run dev
```

Frontend ishga tushdi: http://localhost:3000

## 🐳 Docker Setup

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset everything
docker-compose down -v
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 🔑 Test Accounts

```
Admin:
  Email: admin@smartcareer.uz
  Password: Admin123!

Company:
  Email: hr@epam.com
  Password: Company123!

Students:
  Email: john@example.com
  Password: Student123!
  
  Email: jane@example.com
  Password: Student123!
```

## 🌟 AI Configuration

### Google Gemini (FREE! Tavsiya etiladi)
1. https://ai.google.dev/ ga boring
2. "Get API key" bosing
3. API key ni `.env` fayliga qo'shing:
```env
GEMINI_API_KEY=your-key-here
AI_PROVIDER=gemini
```

### OpenAI (Pullik)
1. https://platform.openai.com ga boring
2. API key yarating
3. `.env` fayliga qo'shing:
```env
OPENAI_API_KEY=sk-your-key-here
AI_PROVIDER=openai
```

## 📧 Email Configuration

### Gmail SMTP
1. Google Account > Security
2. 2-Step Verification ON
3. App passwords > Generate
4. `.env` fayliga qo'shing:
```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### SendGrid (Production)
1. https://sendgrid.com da ro'yxatdan o'ting
2. API key yarating
3. `.env` fayliga qo'shing:
```env
SENDGRID_API_KEY=your-key-here
```

## 📂 Project Structure

```
smartcareer-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/
│   │   │       └── routes/ # Auth, Users, Jobs, etc.
│   │   ├── core/           # Security, dependencies
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   │   ├── ai_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── email_service.py
│   │   │   └── error_logging_service.py
│   │   ├── config.py       # Settings
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   ├── setup_env.py
│   └── seed_data.py
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router
│   │   │   ├── (auth)/    # Auth pages
│   │   │   ├── (dashboard)/ # Dashboard pages
│   │   │   └── (landing)/ # Landing page
│   │   ├── components/    # Reusable components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities
│   │   │   └── i18n/      # Translations (uz, ru)
│   │   └── contexts/      # React contexts
│   ├── package.json
│   └── setup_env.js
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🚀 Deployment

### Backend (Production)

```bash
# Set environment variables
export DEBUG=false
export DATABASE_URL=postgresql://user:pass@host:5432/db
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend (Production)

```bash
# Build
npm run build

# Start
npm start
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Ro'yxatdan o'tish
- `POST /api/v1/auth/login` - Kirish
- `POST /api/v1/auth/refresh` - Token yangilash
- `POST /api/v1/auth/forgot-password` - Parolni tiklash

### Users
- `GET /api/v1/users/me` - Profil
- `PATCH /api/v1/users/me` - Profil yangilash

### Jobs
- `GET /api/v1/jobs` - Ish ro'yxati
- `POST /api/v1/jobs` - Yangi ish (company)
- `GET /api/v1/jobs/{id}` - Ish tafsilotlari

### Applications
- `POST /api/v1/applications` - Ariza berish
- `GET /api/v1/applications` - Mening arizalarim
- `PATCH /api/v1/applications/{id}` - Status yangilash (company)

### AI Features
- `POST /api/v1/ai/generate-resume` - AI rezyume yaratish
- `POST /api/v1/ai/analyze-job-match` - Ish bilan moslik tahlili

### Admin
- `GET /api/v1/admin/dashboard` - Dashboard
- `GET /api/v1/admin/errors` - Error ro'yxati
- `GET /api/v1/admin/system/health` - Tizim holati

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Error Logs (Admin)
```bash
curl http://localhost:8000/api/v1/admin/errors \
  -H "Authorization: Bearer <admin-token>"
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file

## 👥 Team

SmartCareer AI Development Team

## 📞 Support

- Email: support@smartcareer.uz
- Telegram: @smartcareer_support
- Website: https://smartcareer.uz

---

**Made with ❤️ in Uzbekistan 🇺🇿**









