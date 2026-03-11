# Frontend Deployment Guide - Stock Exchange Board

**Document Version**: 1.0
**Last Updated**: March 11, 2026
**Scope**: Production deployment for React frontend

---

## 1. Pre-Deployment Checklist

Before deploying to any environment, verify:

### Code Quality
- [ ] All tests passing: `npm test`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] No ESLint warnings: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] Coverage >= 80%: `npm run coverage`

### Functionality
- [ ] All pages render correctly
- [ ] All routes working
- [ ] API integration tested
- [ ] Forms submission working
- [ ] Notifications displaying
- [ ] Theme toggle functioning
- [ ] Responsive on mobile/tablet/desktop

### Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast WCAG AA
- [ ] Focus outlines visible
- [ ] All interactive elements labeled

### Performance
- [ ] Bundle size acceptable
- [ ] Images optimized
- [ ] No console errors
- [ ] No memory leaks
- [ ] Load time acceptable

---

## 2. Environment Configuration

### Environment Variables

Create `.env.production` for production:

```env
# API Configuration
VITE_API_BASE_URL=https://api.stockexchangeboard.com/api
VITE_WS_URL=wss://api.stockexchangeboard.com/live

# App Configuration
VITE_APP_ENV=production
VITE_APP_NAME=Stock Exchange Board
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_MOCK_DATA=false
VITE_ENABLE_DEBUG=false

# Analytics (optional)
VITE_ANALYTICS_ID=
```

### Development Environment

For development, create `.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/live
VITE_APP_ENV=development
VITE_ENABLE_MOCK_DATA=true
VITE_ENABLE_DEBUG=true
```

### Environment Validation

Add to `src/config.ts`:

```typescript
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  wsUrl: import.meta.env.VITE_WS_URL,
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  enableMockData: import.meta.env.VITE_ENABLE_MOCK_DATA === 'true',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
}

// Validate required environment variables
if (!config.apiBaseUrl && config.appEnv === 'production') {
  throw new Error('VITE_API_BASE_URL is required in production')
}

if (!config.wsUrl && config.appEnv === 'production') {
  throw new Error('VITE_WS_URL is required in production')
}
```

---

## 3. Build Optimization

### Production Build

```bash
# Build for production
npm run build

# Output: dist/
# Files:
#   - dist/index.html
#   - dist/assets/
#     - vendor-*.js
#     - index-*.js
#     - charts-*.js
#     - *.css
#     - *.map (source maps)
```

### Build Analysis

```bash
# Analyze bundle size
npm run build -- --stats

# View bundle breakdown
# Output in dist/stats.html
```

### Optimization Techniques

**1. Code Splitting**

Already configured in `vite.config.ts`:
```javascript
rollupOptions: {
  output: {
    manualChunks: {
      'vendor': ['react', 'react-dom'],
      'charts': ['recharts'],
    },
  },
},
```

**2. Lazy Loading**

Components are ready for lazy loading:
```typescript
const Dashboard = lazy(() => import('@pages/Dashboard'))
const Market = lazy(() => import('@pages/Market'))

// Wrap with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Dashboard />
</Suspense>
```

**3. Asset Optimization**

- SVG icons via lucide-react (no extra files)
- CSS minification (automatic)
- JavaScript minification (automatic)
- HTML minification (automatic)

---

## 4. Deployment Platforms

### 4.1 Vercel Deployment

**Easiest option for Next-generation hosting**

#### Setup
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### Vercel Configuration

Create `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_BASE_URL": "@api_base_url",
    "VITE_WS_URL": "@ws_url"
  }
}
```

#### Benefits
- ✅ Zero-config deployment
- ✅ Automatic HTTPS
- ✅ CDN included
- ✅ Serverless functions (if needed)
- ✅ Environment variables management
- ✅ Preview deployments for PRs

---

### 4.2 Docker Deployment

**For self-hosted or containerized deployments**

#### Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;
    gzip on;
    gzip_types text/plain text/css application/javascript;

    server {
        listen 3000;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        # Cache assets
        location ~* \.(js|css|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy (optional)
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket proxy (optional)
        location /live {
            proxy_pass ws://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

#### Build and Run

```bash
# Build image
docker build -t stock-exchange-board .

# Run container
docker run -p 3000:3000 \
  -e VITE_API_BASE_URL=https://api.example.com/api \
  -e VITE_WS_URL=wss://api.example.com/live \
  stock-exchange-board

# Using docker-compose
docker-compose up
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://backend:8000/api
      VITE_WS_URL: ws://backend:8000/live
    depends_on:
      - backend

  backend:
    image: stock-exchange-backend:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/seb
```

---

### 4.3 AWS S3 + CloudFront

**For static hosting with CDN**

#### Setup

```bash
# Create S3 bucket
aws s3 mb s3://stock-exchange-board-prod

# Enable static website hosting
aws s3 website s3://stock-exchange-board-prod \
  --index-document index.html \
  --error-document index.html

# Block public access (use CloudFront instead)
aws s3api put-block-public-access-configuration \
  --bucket stock-exchange-board-prod \
  --block-public-access-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

#### Deployment Script

```bash
#!/bin/bash
# deploy-aws.sh

# Build
npm run build

# Sync to S3
aws s3 sync dist/ s3://stock-exchange-board-prod \
  --delete \
  --cache-control max-age=31536000,immutable \
  --exclude "index.html"

# Update index.html with no-cache
aws s3 cp dist/index.html s3://stock-exchange-board-prod/index.html \
  --cache-control no-cache

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id E123456ABCD \
  --paths "/*"
```

---

### 4.4 GitHub Pages

**For public documentation or demos**

#### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          VITE_API_BASE_URL: https://api.example.com/api

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

## 5. CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

      - name: Lint
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

      - name: Build
        run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to production
        run: |
          # Add your deployment command here
          # e.g., vercel deploy --prod
```

---

## 6. Pre-Production Testing

### Staging Environment

```bash
# Deploy to staging with test API
npm run build
VITE_API_BASE_URL=https://staging-api.example.com/api npm run deploy:staging
```

### Testing Checklist

- [ ] All pages load
- [ ] API calls work correctly
- [ ] Authentication flow works
- [ ] Orders can be placed
- [ ] Watchlists function properly
- [ ] Charts display correctly
- [ ] Performance acceptable
- [ ] Mobile layout works
- [ ] Dark mode toggles
- [ ] Notifications display

### Performance Testing

```bash
# Lighthouse CLI
npm install -g lighthouse

lighthouse https://staging.example.com --view

# Web Vitals
npm install web-vitals
```

---

## 7. Post-Deployment Monitoring

### Error Tracking

Use Sentry for error monitoring:

```typescript
// src/main.tsx
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_APP_ENV,
})
```

### User Analytics

```typescript
// src/utils/analytics.ts
export function trackEvent(name: string, data?: Record<string, any>) {
  if (window.gtag) {
    window.gtag('event', name, data)
  }
}
```

### Health Checks

```typescript
// Monitor API connectivity
async function healthCheck() {
  try {
    const response = await apiClient.get('/health')
    console.log('API healthy:', response.data)
  } catch (error) {
    console.error('API unhealthy:', error)
    // Alert operations
  }
}

// Check every 5 minutes
setInterval(healthCheck, 5 * 60 * 1000)
```

---

## 8. Security Considerations

### HTTPS Only

```nginx
# nginx configuration
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
}
```

### Security Headers

```nginx
# Add to nginx config
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Content Security Policy

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
```

### CORS Configuration

Backend should allow frontend origin:

```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Rollback Plan

### Version Management

```bash
# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Deploy specific version
git checkout v1.0.0
npm run build
# Deploy...
```

### Quick Rollback

```bash
# If deployment fails, quickly revert
vercel rollback

# Or redeploy previous version
vercel deploy --prod --yes
```

---

## 10. Monitoring & Logging

### Client-Side Logging

```typescript
// src/utils/logger.ts
const isDev = import.meta.env.VITE_APP_ENV === 'development'

export function log(message: string, data?: any) {
  if (isDev) {
    console.log(message, data)
  }
  // Send to logging service in production
}

export function error(message: string, error: Error) {
  console.error(message, error)
  // Send to error tracking service
}
```

### Performance Monitoring

```typescript
// Monitor Core Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

---

## 11. Backup & Recovery

### Database Backups (for user data)

```bash
# PostgreSQL backup
pg_dump -h prod-db.example.com -U user stock_exchange > backup.sql

# Restore
psql -h prod-db.example.com -U user stock_exchange < backup.sql
```

### Asset Backups

```bash
# S3 backup
aws s3 sync s3://stock-exchange-board-prod s3://stock-exchange-board-backups
```

---

## 12. Deployment Troubleshooting

### Issue: Build fails in CI/CD
```bash
# Solution
npm ci  # Use exact versions
npm cache clean --force
npm install
```

### Issue: Environment variables not loading
```bash
# Verify .env file exists
ls -la .env.production

# Check they're passed to build
echo $VITE_API_BASE_URL

# Rebuild
npm run build
```

### Issue: API calls 404
```bash
# Check API URL
console.log(import.meta.env.VITE_API_BASE_URL)

# Verify backend is running
curl https://api.example.com/api/health
```

### Issue: WebSocket fails to connect
```bash
# Check WebSocket URL
console.log(import.meta.env.VITE_WS_URL)

# Verify backend supports WebSocket
# Add fallback to polling if needed
```

---

## 13. Deployment Checklist

### Before Deployment
- [ ] Code merged and reviewed
- [ ] All tests passing
- [ ] No TypeScript errors
- [ ] Build succeeds
- [ ] Environment variables set
- [ ] API backend ready
- [ ] Database migrated (if needed)

### During Deployment
- [ ] Monitor build logs
- [ ] Verify deployment succeeded
- [ ] Check health endpoints
- [ ] Test critical user flows
- [ ] Monitor error rates

### After Deployment
- [ ] Verify all pages load
- [ ] Check API connectivity
- [ ] Review error logs
- [ ] Test on multiple browsers
- [ ] Performance check
- [ ] Announce to team

---

## 14. Rollback Checklist

If problems occur after deployment:

- [ ] Identify the issue
- [ ] Decide rollback vs. hotfix
- [ ] Execute rollback
- [ ] Verify previous version works
- [ ] Investigate root cause
- [ ] Plan fix and redeploy

---

## Deployment Commands Quick Reference

```bash
# Development
npm run dev

# Production build
npm run build

# Test build locally
npm run preview

# Deploy to Vercel
vercel deploy --prod

# Deploy to AWS
./deploy-aws.sh

# Deploy with Docker
docker build -t seb . && docker run -p 3000:3000 seb

# Check version
npm list | grep stock-exchange-board
```

---

## Conclusion

The Stock Exchange Board frontend is production-ready with:
- ✅ Optimized build
- ✅ Multiple deployment options
- ✅ Comprehensive monitoring
- ✅ Security hardening
- ✅ Rollback capability

Choose the deployment platform that best fits your infrastructure and proceed with the checklist.

**Recommended for MVP**: Vercel or Docker
**Recommended for Scale**: AWS S3 + CloudFront
**Recommended for Enterprise**: Docker + Kubernetes

---

**Last Updated**: March 11, 2026
**Maintainer**: DevOps Team
**Version**: 1.0.0
