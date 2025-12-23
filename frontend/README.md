# SmartCareer AI - Frontend

Production-grade Next.js 14 frontend for the SmartCareer AI platform.

## 🚀 Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** with custom design system
- **shadcn/ui** components
- **Zustand** for state management
- **React Hook Form** + **Zod** for form validation
- **Framer Motion** for animations
- **Responsive design** - Mobile first

## 📁 Project Structure

```
/frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── (auth)/             # Auth pages (login, register, forgot-password)
│   │   ├── (dashboard)/        # Dashboard pages
│   │   │   ├── student/        # Student dashboard
│   │   │   │   ├── resumes/
│   │   │   │   ├── jobs/
│   │   │   │   └── applications/
│   │   │   └── company/        # Company dashboard
│   │   │       ├── jobs/
│   │   │       └── applicants/
│   │   ├── layout.tsx
│   │   └── page.tsx            # Landing page
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── layouts/            # Layout components
│   │   ├── forms/              # Form components
│   │   ├── resume/             # Resume-related components
│   │   └── job/                # Job-related components
│   ├── lib/
│   │   ├── api.ts              # Axios instance
│   │   ├── auth.ts             # Auth helpers
│   │   └── utils.ts            # Utility functions
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useResume.ts
│   │   └── useJobs.ts
│   ├── store/                  # Zustand stores
│   │   ├── authStore.ts
│   │   ├── resumeStore.ts
│   │   ├── jobStore.ts
│   │   └── applicationStore.ts
│   └── types/
│       └── api.ts              # TypeScript types
├── public/
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## 🛠️ Setup

### Prerequisites

- Node.js 18.17+
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Update .env.local with your values
```

### Development

```bash
# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🎨 Design System

### Colors

- **Brand**: Cyan/Teal (`#06b6d4`)
- **Accent**: Amber (`#f59e0b`)
- **Surface**: Slate grays
- **Success**: Green
- **Warning**: Yellow
- **Error**: Red

### Typography

- **Display**: Cal Sans / Outfit
- **Body**: Outfit
- **Mono**: JetBrains Mono

### Components

All UI components are built with shadcn/ui and customized to match our design system:

- Button (multiple variants)
- Input
- Card
- Badge
- Avatar
- Dialog
- Select
- Tabs
- Progress
- Skeleton

## 📱 Pages

### Public

- `/` - Landing page with hero section
- `/login` - User login
- `/register` - User registration
- `/forgot-password` - Password reset

### Student Dashboard

- `/student/resumes` - Resume management
- `/student/jobs` - Job search
- `/student/applications` - Application tracking
- `/student/settings` - Profile settings

### Company Dashboard

- `/company/jobs` - Job postings management
- `/company/applicants` - Applicant management
- `/company/settings` - Company settings

## 🔐 Authentication

Authentication is handled via JWT tokens with automatic refresh:

```typescript
// Token management
import { TokenManager } from "@/lib/api";

TokenManager.getAccessToken();
TokenManager.setTokens(accessToken, refreshToken);
TokenManager.clearTokens();
```

## 📊 State Management

Zustand stores with persistence:

```typescript
// Auth store
import { useAuthStore } from "@/store/authStore";

const { user, login, logout, isAuthenticated } = useAuthStore();
```

## 🔗 API Client

Axios instance with interceptors:

```typescript
import { get, post, put, del } from "@/lib/api";

// GET request
const users = await get<User[]>("/users");

// POST request
const resume = await post<Resume>("/resumes", data);
```

## 📝 Forms

Using React Hook Form with Zod validation:

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const { register, handleSubmit } = useForm({
  resolver: zodResolver(schema),
});
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 📦 Build & Deploy

```bash
# Build
npm run build

# Analyze bundle
npm run analyze
```

### Docker

```bash
docker build -t smartcareer-frontend .
docker run -p 3000:3000 smartcareer-frontend
```

## 📄 License

MIT
















