# 🚀 Production Deployment Guide

## Pre-Deployment Checklist

### 1. Security
- [ ] Change all default passwords and secrets
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set `DEBUG=false`

### 2. Database
- [ ] Set up PostgreSQL production instance
- [ ] Configure database backups
- [ ] Run all migrations
- [ ] Set up connection pooling
- [ ] Configure read replicas (optional)

### 3. Environment Variables
- [ ] Set all required `.env` variables
- [ ] Configure AI API keys (Gemini/OpenAI)
- [ ] Set up email service (SMTP/SendGrid)
- [ ] Configure payment provider (Stripe)
- [ ] Set proper `FRONTEND_URL` and `CORS_ORIGINS`

### 4. Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging (ELK/CloudWatch)
- [ ] Set up uptime monitoring
- [ ] Configure alerts
- [ ] Set up analytics

---

## Deployment Options

### Option 1: Docker Compose (Simple)

**Best for:** Small to medium deployments, VPS hosting

#### Step 1: Prepare Server
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Configure Environment
```bash
# Clone repository
git clone https://github.com/yourusername/smartcareer-ai.git
cd smartcareer-ai

# Set up backend environment
cd backend
python setup_env.py
# Edit .env with production values
nano .env

# Set up frontend environment
cd ../frontend
node setup_env.js
# Edit .env.local with production values
nano .env.local
```

#### Step 3: Update docker-compose.yml
```yaml
# Change these in docker-compose.yml:
- DEBUG=false
- DATABASE_URL=postgresql://...  # Production DB
- Use proper secrets
- Configure volumes for persistence
```

#### Step 4: Deploy
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### Step 5: Set up Nginx (Reverse Proxy)
```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/smartcareer
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (use certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smartcareer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### Option 2: AWS (Scalable)

**Best for:** Production, scalable deployments

#### Architecture
- **Frontend**: AWS Amplify or S3 + CloudFront
- **Backend**: ECS (Fargate) or EC2 + Auto Scaling
- **Database**: RDS (PostgreSQL)
- **Cache**: ElastiCache (Redis)
- **Storage**: S3
- **CDN**: CloudFront
- **Load Balancer**: ALB

#### Step 1: Set up RDS (PostgreSQL)
```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier smartcareer-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.3 \
    --master-username admin \
    --master-user-password <strong-password> \
    --allocated-storage 20 \
    --backup-retention-period 7 \
    --vpc-security-group-ids <sg-id>
```

#### Step 2: Deploy Backend to ECS
```bash
# Build and push Docker image
docker build -t smartcareer-backend ./backend
docker tag smartcareer-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/smartcareer-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/smartcareer-backend:latest

# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS service
aws ecs create-service \
    --cluster smartcareer-cluster \
    --service-name smartcareer-backend \
    --task-definition smartcareer-backend:1 \
    --desired-count 2 \
    --launch-type FARGATE
```

#### Step 3: Deploy Frontend to Amplify
```bash
# Connect GitHub repository to Amplify
# Configure build settings in amplify.yml

# Or use S3 + CloudFront:
cd frontend
npm run build
aws s3 sync .next/out s3://smartcareer-frontend
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

---

### Option 3: Vercel + Railway (Easiest)

**Best for:** Quick deployment, startups

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Backend (Railway)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
cd backend
railway login
railway init
railway up
```

---

## Post-Deployment Tasks

### 1. Database Setup
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data (optional)
docker-compose exec backend python seed_data.py
```

### 2. Create Admin User
```bash
# SSH into backend container
docker-compose exec backend python

# In Python shell:
from app.models import User, UserRole
from app.core.dependencies import get_db

db = next(get_db())
admin = User(
    email="admin@yourdomain.com",
    full_name="Admin User",
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
admin.set_password("SuperSecurePassword123!")
db.add(admin)
db.commit()
```

### 3. Configure Monitoring

#### Sentry (Error Tracking)
```bash
# Backend
pip install sentry-sdk[fastapi]

# Add to main.py:
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
)
```

```typescript
// Frontend - next.config.js
const { withSentryConfig } = require('@sentry/nextjs');

module.exports = withSentryConfig({
  // ... your config
}, {
  dsn: 'your-sentry-dsn',
});
```

#### Uptime Monitoring
- Use UptimeRobot, Pingdom, or AWS CloudWatch
- Monitor: `/health`, `/api/v1/health`
- Alert on downtime

### 4. Backups

#### Database Backups
```bash
# Automated daily backups
0 2 * * * docker-compose exec -T postgres pg_dump -U smartcareer smartcareer > /backups/smartcareer_$(date +\%Y\%m\%d).sql
```

#### Application Backups
```bash
# Backup uploads directory
0 3 * * * tar -czf /backups/uploads_$(date +\%Y\%m\%d).tar.gz /path/to/uploads
```

### 5. SSL Certificate Auto-Renewal
```bash
# Certbot auto-renewal (runs automatically)
sudo certbot renew --dry-run
```

---

## Scaling Guidelines

### Vertical Scaling (Single Server)
- Increase CPU/RAM
- Optimize database queries
- Add Redis caching
- Use CDN for static assets

### Horizontal Scaling (Multiple Servers)
- Load balancer (Nginx, HAProxy, ALB)
- Multiple backend containers
- Database read replicas
- Redis cluster
- S3 for file storage

### Performance Optimization
- Enable Gzip compression
- Use CDN (CloudFlare, CloudFront)
- Optimize images (WebP, lazy loading)
- Database indexing
- API response caching
- Connection pooling

---

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://your-domain.com/health

# API health
curl https://your-domain.com/api/v1/health

# Database connection
curl https://your-domain.com/api/v1/health/db
```

### Logs
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Export logs
docker-compose logs backend > backend.log
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run new migrations
docker-compose exec backend alembic upgrade head
```

---

## Troubleshooting

### Backend won't start
- Check `.env` file exists and has all required variables
- Verify database connection
- Check logs: `docker-compose logs backend`
- Ensure migrations are run: `alembic upgrade head`

### Frontend won't build
- Check `NEXT_PUBLIC_API_URL` is set
- Verify Node.js version (18+)
- Clear cache: `rm -rf .next && npm run build`

### Database connection issues
- Verify `DATABASE_URL` format
- Check firewall rules
- Ensure PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### API errors
- Check API logs: `docker-compose logs backend`
- Verify CORS settings
- Test endpoint: `curl -X GET https://api.your-domain.com/health`

---

## Security Hardening

### 1. Environment Variables
Never commit `.env` files! Use secrets management:
- AWS Secrets Manager
- HashiCorp Vault
- Docker secrets

### 2. Database Security
- Use strong passwords
- Enable SSL connections
- Restrict IP access
- Regular backups
- Encrypt at rest

### 3. API Security
- Rate limiting (already implemented)
- JWT expiration
- HTTPS only
- Security headers (HSTS, CSP)
- Input validation

### 4. Regular Updates
```bash
# Update dependencies
pip list --outdated
npm outdated

# Apply security patches
pip install --upgrade <package>
npm update
```

---

## Support & Maintenance

### Regular Tasks
- [ ] Weekly: Review error logs
- [ ] Weekly: Check disk space
- [ ] Weekly: Review API usage
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review backups
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

### Emergency Contacts
- DevOps: your-email@domain.com
- Database: dba@domain.com
- Security: security@domain.com

---

**🎉 Your SmartCareer AI platform is now live!**

For issues or questions, open an issue on GitHub or contact support@smartcareer.uz









