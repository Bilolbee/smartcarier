# Frontend Dockerfile (Railway uchun - agar Docker ishlatmoqchi bo'lsangiz)
# Lekin tavsiya etilmaydi - Node.js service osonroq!

FROM node:18-alpine

WORKDIR /app

# Dependencies install
COPY package*.json ./
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Start
CMD ["npm", "start"]
