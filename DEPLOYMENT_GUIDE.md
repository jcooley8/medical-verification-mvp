# Medical Verification MVP - Deployment Guide

## Prerequisites
- GitHub account
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Git and CLI tools installed (`gh`, `railway`, `vercel`)

## Repository Setup ✅ COMPLETE

The code has been pushed to: **https://github.com/jcooley8/medical-verification-mvp**

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `jcooley8/medical-verification-mvp`
4. Railway will detect the Dockerfile automatically

### 1.2 Add PostgreSQL Database

1. In your Railway project, click "+ New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance and set `DATABASE_URL`

### 1.3 Add Redis

1. Click "+ New Service" again
2. Select "Database" → "Redis"
3. Railway will automatically create Redis and set `REDIS_URL`

### 1.4 Configure Environment Variables

In the Railway project settings, add these environment variables:

**Backend Service:**
```
DATABASE_URL=(auto-set by Railway)
REDIS_URL=(auto-set by Railway)
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
ENVIRONMENT=staging
DEBUG=false
ALLOWED_ORIGINS=*
PORT=8000
```

**Optional (for advanced LLM features):**
```
OPENAI_API_KEY=sk-...
```

### 1.5 Deploy Backend

1. In Railway, go to your backend service
2. Click "Deploy" or push to GitHub (auto-deploy enabled)
3. Wait for build to complete (~2-3 minutes)
4. Note your backend URL: `https://[your-app].up.railway.app`

### 1.6 Add Celery Worker (Optional for Background Processing)

If you need async document processing:

1. Click "+ New Service"
2. Select "GitHub Repo" → same repo
3. Set Root Directory: `backend`
4. Set Start Command: `celery -A app.celery_app worker --loglevel=info`
5. Add same environment variables as backend

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project

Option A - CLI (if logged in):
```bash
cd medical-verification-mvp/frontend
vercel
```

Option B - Web UI:
1. Go to https://vercel.com/new
2. Import `jcooley8/medical-verification-mvp`
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

### 2.2 Configure Environment Variables

In Vercel project settings → Environment Variables:

```
VITE_API_URL=https://[your-railway-app].up.railway.app
```

**Important:** Replace `[your-railway-app]` with your actual Railway backend URL from Step 1.5

### 2.3 Deploy Frontend

1. Vercel will auto-deploy from `master` branch
2. Wait for build (~1-2 minutes)
3. Note your frontend URL: `https://[your-app].vercel.app`

## Step 3: Update CORS Settings

Once both are deployed, update the backend CORS settings:

1. In Railway, update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://[your-vercel-app].vercel.app,http://localhost:5173
   ```
2. Redeploy the backend service

## Step 4: Run Database Migrations

### 4.1 Connect to Railway PostgreSQL

```bash
# Install Railway CLI if not already
railway login

# Link to your project
cd medical-verification-mvp/backend
railway link

# Run migrations (if using Alembic)
railway run alembic upgrade head

# OR create tables directly (if not using migrations)
railway run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4.2 Verify Database

```bash
# Connect to PostgreSQL
railway connect postgres

# In psql:
\dt  # List tables (should see 'documents' table)
\q   # Quit
```

## Step 5: Smoke Tests

### 5.1 Test Backend API

Visit: `https://[your-railway-app].up.railway.app/docs`

You should see the FastAPI Swagger documentation.

### 5.2 Test Health Endpoint

```bash
curl https://[your-railway-app].up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "connected"
}
```

### 5.3 Test Frontend

1. Visit: `https://[your-vercel-app].vercel.app`
2. Upload a test PDF (from `../test_data/`)
3. Verify the document processes correctly
4. Check that Click-to-Verify highlighting works

### 5.4 Test Full E2E Flow

```bash
# Test document upload
curl -X POST "https://[your-railway-app].up.railway.app/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_data/sample_medical_bill.pdf"

# Note the document_id from response
# Then check status:
curl "https://[your-railway-app].up.railway.app/documents/{document_id}"
```

## Step 6: Monitoring Setup (Optional)

### 6.1 Railway Observability

Railway includes built-in metrics:
- Go to your service → "Metrics" tab
- Monitor CPU, memory, and request volume

### 6.2 Vercel Analytics

Vercel includes basic analytics:
- Go to your project → "Analytics" tab
- View page views and performance

### 6.3 Sentry (Recommended for Production)

1. Create Sentry account: https://sentry.io
2. Create new project (Python + JavaScript)
3. Add to Railway environment variables:
   ```
   SENTRY_DSN=https://...@sentry.io/...
   ```
4. Add to Vercel environment variables:
   ```
   VITE_SENTRY_DSN=https://...@sentry.io/...
   ```

## Troubleshooting

### Backend won't start
- Check Railway logs: Service → "Deployments" → Latest → "View Logs"
- Common issues:
  - Missing DATABASE_URL (add PostgreSQL service)
  - Missing REDIS_URL (add Redis service)
  - Port binding (Railway sets $PORT automatically)

### Frontend shows API errors
- Check VITE_API_URL is correct
- Verify CORS is configured correctly on backend
- Check Network tab in browser DevTools

### Database connection errors
- Verify PostgreSQL service is running in Railway
- Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Ensure migrations have run

### PDF upload fails
- Check file size (Railway default: 100MB limit)
- Verify multipart form data is configured
- Check backend logs for OCR errors

## Rollback Procedure

### Backend Rollback (Railway)
1. Go to Service → "Deployments"
2. Find previous stable deployment
3. Click "⋯" → "Rollback to this version"

### Frontend Rollback (Vercel)
1. Go to Project → "Deployments"
2. Find previous stable deployment
3. Click "⋯" → "Promote to Production"

## Post-Deployment Checklist

- [ ] Backend health endpoint returns 200
- [ ] Frontend loads without console errors
- [ ] PostgreSQL connection successful
- [ ] Redis connection successful
- [ ] PDF upload works end-to-end
- [ ] Extraction results appear correctly
- [ ] Click-to-Verify highlights work
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Domain/URL documented
- [ ] Monitoring enabled (optional)

## Live URLs

**Frontend:** https://[to-be-filled].vercel.app  
**Backend API:** https://[to-be-filled].up.railway.app  
**API Docs:** https://[to-be-filled].up.railway.app/docs

## Next Steps

1. ✅ Complete manual deployment via Railway + Vercel web UIs
2. ✅ Run smoke tests
3. ✅ Document live URLs in DEPLOYMENT_SUMMARY.md
4. ✅ Update TASK_BUILDER.md with completion status
5. 🔄 Set up GitHub Actions for CI/CD (future enhancement)
6. 🔄 Configure custom domain (future enhancement)
7. 🔄 Enable production monitoring (future enhancement)

## Cost Estimate (Staging)

- **Railway:** $5-10/month (Hobby plan with PostgreSQL + Redis)
- **Vercel:** $0 (Free tier, hobby projects)
- **Total:** ~$5-10/month

## Support

For deployment issues:
- Railway: https://railway.app/help
- Vercel: https://vercel.com/help
- GitHub: https://github.com/jcooley8/medical-verification-mvp/issues
