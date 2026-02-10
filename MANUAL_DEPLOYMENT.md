# Manual Deployment Guide - Web UI Method

Since automated CLI deployment requires interactive login, follow these steps to deploy via web interfaces:

## ✅ Pre-Deployment Checklist

- [x] Code committed to GitHub: https://github.com/jcooley8/medical-verification-mvp
- [x] Deployment configurations added (railway.json, vercel.json, Procfile)
- [x] CORS support added to backend
- [x] Health check endpoint implemented
- [ ] Railway account created
- [ ] Vercel account created

## 🚂 Part 1: Deploy Backend to Railway (15 minutes)

### Step 1.1: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub account
4. Select repository: **jcooley8/medical-verification-mvp**
5. Railway will auto-detect the project

### Step 1.2: Configure Backend Service

1. After project creation, click on the service (it should be auto-created)
2. Go to **Settings** tab
3. Set the following:
   - **Service Name:** `medical-verification-backend`
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click **Deploy**

### Step 1.3: Add PostgreSQL Database

1. In your Railway project dashboard, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway will:
   - Create a PostgreSQL instance
   - Automatically set `DATABASE_URL` environment variable
   - Link it to your backend service

### Step 1.4: Add Redis

1. Click **+ New** again
2. Select **Database** → **Redis**
3. Railway will:
   - Create a Redis instance
   - Automatically set `REDIS_URL` environment variable

### Step 1.5: Set Environment Variables

1. Go to your backend service
2. Click **Variables** tab
3. Add these variables:

```bash
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
ENVIRONMENT=staging
DEBUG=false
ALLOWED_ORIGINS=*
```

4. Click **Save**

### Step 1.6: Generate Public URL

1. Go to **Settings** tab
2. Scroll to **Networking**
3. Click **Generate Domain**
4. Copy your Railway URL (e.g., `medical-verification-backend.up.railway.app`)
5. **Save this URL** - you'll need it for frontend configuration

### Step 1.7: Initialize Database

1. In Railway, go to your backend service
2. Click **Deploy Logs** to monitor
3. Open **Shell** tab (or use `railway run` locally):

```bash
# If using Railway shell:
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Or locally with Railway CLI:
cd backend
railway run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Step 1.8: Verify Deployment

Visit: `https://[your-railway-url]/health`

Expected response:
```json
{
  "status": "ok",
  "database": "connected",
  "service": "medical-verification-mvp"
}
```

Visit API docs: `https://[your-railway-url]/docs`

✅ **Backend deployment complete!**

---

## ▲ Part 2: Deploy Frontend to Vercel (10 minutes)

### Step 2.1: Create Vercel Project

1. Go to https://vercel.com/new
2. Click **Import Git Repository**
3. Select repository: **jcooley8/medical-verification-mvp**
4. Vercel will show import configuration

### Step 2.2: Configure Build Settings

In the project configuration screen, set:

- **Framework Preset:** Vite
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### Step 2.3: Set Environment Variables

Before deploying, add environment variable:

1. Scroll to **Environment Variables** section
2. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://[your-railway-url]` (from Part 1, Step 1.6)
   - **Environment:** Production

### Step 2.4: Deploy

1. Click **Deploy**
2. Wait for build to complete (~2-3 minutes)
3. Copy your Vercel URL (e.g., `medical-verification-mvp.vercel.app`)

### Step 2.5: Verify Deployment

Visit: `https://[your-vercel-url]`

You should see the Medical Verification MVP interface with:
- Header showing "Medical Verification MVP - Click-to-Verify"
- PDF viewer on left
- Medical Chronology / Billing tabs on right

✅ **Frontend deployment complete!**

---

## 🔄 Part 3: Update CORS Configuration

Now that both services are deployed, update the backend CORS to accept requests from the frontend:

### Step 3.1: Update Railway Environment Variable

1. Go to Railway project
2. Select backend service
3. Go to **Variables** tab
4. Update `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=https://[your-vercel-url],http://localhost:5173
```

5. Click **Save**
6. Railway will auto-redeploy

### Step 3.2: Verify CORS

Test that frontend can communicate with backend:

```bash
curl -X OPTIONS https://[your-railway-url]/health \
  -H "Origin: https://[your-vercel-url]" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

Look for `Access-Control-Allow-Origin` header in response.

---

## 🧪 Part 4: Smoke Tests

### Test 1: Backend Health Check

```bash
curl https://[your-railway-url]/health
```

Expected: `{"status":"ok","database":"connected",...}`

### Test 2: API Documentation

Visit: `https://[your-railway-url]/docs`

Expected: Interactive Swagger UI

### Test 3: Frontend Loads

Visit: `https://[your-vercel-url]`

Expected: App loads with mock data visible

### Test 4: Document Upload (Backend Direct)

```bash
# Upload a test PDF
curl -X POST "https://[your-railway-url]/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@../test_data/sample_medical_bill.pdf"
```

Expected: JSON response with document_id and status "QUEUED"

### Test 5: Check Document Status

```bash
# Use document_id from Test 4
curl "https://[your-railway-url]/api/v1/documents/{document_id}"
```

Expected: Document details with status (may be PROCESSING or COMPLETED)

---

## 📋 Part 5: Document URLs

Once deployment is complete, document your URLs:

1. Create/update `DEPLOYMENT_SUMMARY.md`:

```bash
cd medical-verification-mvp

cat > DEPLOYMENT_SUMMARY.md <<EOF
# Deployment Summary - Staging Environment

## Deployment Information

**Deployed:** $(date)
**Environment:** Staging
**Git Commit:** $(git rev-parse HEAD)

## Live URLs

- **Frontend:** https://[your-vercel-url]
- **Backend API:** https://[your-railway-url]
- **API Documentation:** https://[your-railway-url]/docs
- **GitHub Repository:** https://github.com/jcooley8/medical-verification-mvp

## Services

### Railway (Backend)
- **Service:** medical-verification-backend
- **Database:** PostgreSQL (managed by Railway)
- **Cache:** Redis (managed by Railway)
- **Region:** us-west1 (or your selected region)

### Vercel (Frontend)
- **Project:** medical-verification-mvp
- **Framework:** Vite + React
- **Build Time:** ~2 minutes

## Environment Variables

### Backend (Railway)
\`\`\`
DATABASE_URL=(auto-set)
REDIS_URL=(auto-set)
CELERY_BROKER_URL=\${REDIS_URL}
CELERY_RESULT_BACKEND=\${REDIS_URL}
ENVIRONMENT=staging
DEBUG=false
ALLOWED_ORIGINS=https://[your-vercel-url],http://localhost:5173
\`\`\`

### Frontend (Vercel)
\`\`\`
VITE_API_URL=https://[your-railway-url]
\`\`\`

## Smoke Test Results

- [x] Backend health check passes
- [x] Database connection successful
- [x] API documentation accessible
- [x] Frontend loads correctly
- [x] CORS configured properly
- [ ] PDF upload tested (manual test pending)
- [ ] Extraction pipeline tested (pending Celery worker setup)

## Known Issues / Limitations

1. **Celery Worker Not Configured:** Document processing will queue but not execute until worker service is added
2. **Using Mock Data:** Frontend currently displays mock data (backend integration pending)
3. **No Authentication:** Staging environment is publicly accessible (add auth before production)

## Rollback Procedure

### Backend Rollback
1. Go to Railway → Backend Service → Deployments
2. Select previous deployment
3. Click "Redeploy"

### Frontend Rollback
1. Go to Vercel → Project → Deployments
2. Select previous deployment
3. Click "Promote to Production"

## Next Steps

- [ ] Add Celery worker service to Railway
- [ ] Connect frontend to real backend API
- [ ] Add file upload component to frontend
- [ ] Test end-to-end extraction pipeline
- [ ] Set up monitoring (Sentry)
- [ ] Configure custom domain (optional)

## Cost Estimate

- Railway: \$5-10/month (Hobby plan)
- Vercel: \$0 (Free tier)
- **Total:** \$5-10/month

## Support Contacts

- **Developer:** [Your Name]
- **Repository:** https://github.com/jcooley8/medical-verification-mvp/issues
- **Documentation:** See DEPLOYMENT_GUIDE.md
EOF

echo "DEPLOYMENT_SUMMARY.md created!"
```

---

## 🎯 Part 6: Update Task Status

Update `TASK_BUILDER.md` to mark deployment as complete:

```bash
# Update TASK_BUILDER.md with deployment status
cat >> ../TASK_BUILDER.md <<EOF

## ✅ DEPLOYMENT STATUS: COMPLETE

**Deployed:** $(date)
**Environment:** Staging

### Live URLs
- Frontend: https://[your-vercel-url]
- Backend: https://[your-railway-url]
- API Docs: https://[your-railway-url]/docs

### Services Deployed
- [x] Frontend (Vercel)
- [x] Backend API (Railway)
- [x] PostgreSQL Database (Railway)
- [x] Redis Cache (Railway)
- [ ] Celery Worker (pending - see notes)

### Smoke Tests
- [x] Backend health check
- [x] Database connectivity
- [x] Frontend loads
- [x] CORS configured
- [ ] E2E extraction test (pending worker)

See DEPLOYMENT_SUMMARY.md for full details.
EOF
```

---

## 🚨 Troubleshooting

### Issue: Build fails on Railway
**Solution:** Check build logs. Common issues:
- Missing dependencies in requirements.txt
- Dockerfile syntax errors
- Port configuration (Railway sets $PORT automatically)

### Issue: Frontend shows CORS errors
**Solution:**
1. Verify ALLOWED_ORIGINS includes your Vercel URL
2. Check Railway environment variables
3. Redeploy backend after changing variables

### Issue: Database connection fails
**Solution:**
1. Verify PostgreSQL service is running in Railway
2. Check DATABASE_URL is set correctly
3. Review backend logs for connection errors

### Issue: 502 Bad Gateway on Railway
**Solution:**
1. Check if app is binding to correct port ($PORT)
2. Verify health check endpoint is responding
3. Review deploy logs for startup errors

---

## 📞 Need Help?

- Railway Documentation: https://docs.railway.app
- Vercel Documentation: https://vercel.com/docs
- Project Issues: https://github.com/jcooley8/medical-verification-mvp/issues

---

**Estimated Total Time:** 25-30 minutes

Good luck with your deployment! 🚀
