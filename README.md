# Medical Verification MVP

**Status:** ✅ **Ready for Staging Deployment**  
**Repository:** https://github.com/jcooley8/medical-verification-mvp  
**Documentation:** Comprehensive deployment guides included

---

## Quick Start

### To Deploy to Staging (30 minutes):

```bash
# Read the quick deploy guide:
cat QUICK_DEPLOY.md

# Or for detailed step-by-step:
cat MANUAL_DEPLOYMENT.md
```

**What you need:**
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- 30 minutes of time

**Cost:** ~$5-10/month for staging

---

## 📚 Documentation Index

### Deployment Guides

| Document | Size | Purpose | When to Use |
|----------|------|---------|-------------|
| **QUICK_DEPLOY.md** | 2.6K | 3-step deployment guide | Start here! ⭐⭐⭐ |
| **MANUAL_DEPLOYMENT.md** | 10K | Step-by-step web UI guide | Need detailed instructions ⭐⭐⭐ |
| **DEPLOYMENT_GUIDE.md** | 7.4K | Complete reference | Troubleshooting, advanced config ⭐⭐ |
| **DEPLOYMENT_SUMMARY.md** | 7.6K | Status tracker template | Track deployment progress ⭐ |
| **deploy-staging.sh** | 4KB | Automated CLI script | If Railway/Vercel CLIs are logged in ⭐ |

### Implementation Documentation

| Document | Size | Purpose |
|----------|------|---------|
| **IMPLEMENTATION_COMPLETE.md** | 10K | Feature completion summary |
| **LLM_PIPELINE_SUMMARY.md** | 9.1K | LLM extraction pipeline details |
| **backend/README.md** | 3.6K | Backend API documentation |
| **frontend/README.md** | 2.5K | Frontend development guide |

---

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework:** FastAPI with async support
- **Database:** PostgreSQL (managed by Railway)
- **Cache:** Redis (managed by Railway)
- **Task Queue:** Celery (for background processing)
- **Health Check:** `/health` endpoint
- **API Docs:** `/docs` (Swagger UI)

### Frontend (React + Vite)
- **Framework:** React 19 + Vite
- **UI:** Tailwind CSS + Framer Motion
- **PDF Rendering:** react-pdf + pdf.js
- **State Management:** React Query
- **Features:** Click-to-Verify highlighting

### Infrastructure
- **Backend Hosting:** Railway (https://railway.app)
- **Frontend Hosting:** Vercel (https://vercel.com)
- **Database:** PostgreSQL (Railway managed)
- **Cache:** Redis (Railway managed)

---

## 📦 Project Structure

```
medical-verification-mvp/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── main.py              # API endpoints with CORS
│   │   ├── models.py            # Database models
│   │   ├── tasks.py             # Celery tasks
│   │   ├── verification_service.py  # Core verification logic
│   │   ├── llm_service.py       # LLM extraction
│   │   └── ocr_service.py       # OCR processing
│   ├── Dockerfile               # Container configuration
│   ├── railway.toml             # Railway service config
│   ├── Procfile                 # Process definitions
│   └── requirements.txt         # Python dependencies
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/          # UI components
│   │   │   ├── PDFViewer/      # PDF rendering + highlighting
│   │   │   └── DataPanel/      # Data display components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript definitions
│   │   └── App.tsx             # Main application
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Build configuration
│
├── QUICK_DEPLOY.md             # ⭐ Start here for deployment
├── MANUAL_DEPLOYMENT.md        # Detailed deployment guide
├── DEPLOYMENT_GUIDE.md         # Complete reference
├── DEPLOYMENT_SUMMARY.md       # Status tracker
├── railway.json                # Railway project config
├── vercel.json                 # Vercel project config
├── .env.example                # Environment variables template
└── deploy-staging.sh           # Automated deployment script
```

---

## 🚀 Deployment Options

### Option 1: Quick Deploy (Web UI)
**Time:** 30 minutes  
**Difficulty:** Easy  
**Guide:** `QUICK_DEPLOY.md`

1. Deploy backend to Railway
2. Deploy frontend to Vercel
3. Update CORS configuration

### Option 2: Detailed Manual Deploy
**Time:** 30 minutes  
**Difficulty:** Easy (with hand-holding)  
**Guide:** `MANUAL_DEPLOYMENT.md`

Complete step-by-step instructions with troubleshooting.

### Option 3: Automated CLI
**Time:** 10 minutes  
**Difficulty:** Requires Railway/Vercel CLI login  
**Script:** `./deploy-staging.sh`

Fully automated if CLIs are authenticated.

---

## 🧪 Testing

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Smoke Tests (After Deployment)

**Backend Health:**
```bash
curl https://[railway-url]/health
```

**Frontend:**
Visit `https://[vercel-url]`

**API Docs:**
Visit `https://[railway-url]/docs`

---

## 🔧 Configuration

### Environment Variables

**Backend (Railway):**
```bash
DATABASE_URL=(auto-set by Railway)
REDIS_URL=(auto-set by Railway)
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
ENVIRONMENT=staging
DEBUG=false
ALLOWED_ORIGINS=https://[vercel-url],http://localhost:5173
```

**Frontend (Vercel):**
```bash
VITE_API_URL=https://[railway-url]
```

See `.env.example` for complete template.

---

## 💰 Cost Estimate

**Staging Environment:**
- Railway (Hobby): $5-10/month
- Vercel (Free): $0/month
- **Total: ~$5-10/month**

**Includes:**
- PostgreSQL database
- Redis cache
- Backend hosting
- Frontend CDN
- SSL certificates
- Basic monitoring

---

## 🔒 Security

- ✅ CORS configured with explicit origins
- ✅ Environment-based configuration
- ✅ Health check endpoints
- ✅ Database connection validation
- ✅ Secure file uploads (PDF only)
- ✅ Input validation (FastAPI + Pydantic)

**Future Enhancements:**
- API key authentication
- Rate limiting
- Request logging
- Sentry error tracking

---

## 🔄 Rollback Procedure

### Backend (Railway)
1. Navigate to Service → Deployments
2. Select previous deployment
3. Click "Redeploy"

### Frontend (Vercel)
1. Navigate to Deployments
2. Select previous deployment
3. Click "Promote to Production"

**Recovery Time:** < 5 minutes

---

## 📊 Features

### Current (MVP)
- ✅ PDF upload and storage
- ✅ OCR text extraction
- ✅ Document classification (Chronology vs Bill)
- ✅ LLM-powered structured extraction
- ✅ Click-to-Verify highlighting
- ✅ Bounding box coordinate mapping
- ✅ Health checks and monitoring
- ✅ API documentation

### Planned (Post-MVP)
- ⏳ Real-time frontend integration
- ⏳ File upload component
- ⏳ Celery worker service
- ⏳ User authentication
- ⏳ Rate limiting
- ⏳ Error monitoring (Sentry)
- ⏳ Custom domain

---

## 🐛 Known Limitations

1. **Celery Worker:** Background processing requires separate Railway service
2. **Mock Data:** Frontend currently uses mock data (API integration pending)
3. **No Auth:** Public access (acceptable for staging)
4. **Ephemeral Storage:** Railway storage is temporary (use S3 for production)
5. **No Monitoring:** Sentry integration pending

---

## 📞 Support

**Documentation:**
- Quick Start: `QUICK_DEPLOY.md`
- Detailed Guide: `MANUAL_DEPLOYMENT.md`
- Full Reference: `DEPLOYMENT_GUIDE.md`

**External Resources:**
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev

**Issues:**
https://github.com/jcooley8/medical-verification-mvp/issues

---

## 🎯 Quick Links

| Resource | URL |
|----------|-----|
| GitHub Repository | https://github.com/jcooley8/medical-verification-mvp |
| Railway Dashboard | https://railway.app |
| Vercel Dashboard | https://vercel.com |
| Deploy Backend | https://railway.app/new |
| Deploy Frontend | https://vercel.com/new |

---

## ✅ Deployment Checklist

**Pre-Deployment**
- [x] Code committed to GitHub
- [x] Deployment configurations created
- [x] CORS middleware implemented
- [x] Health check endpoint added
- [x] Documentation written

**Deployment**
- [ ] Railway account created
- [ ] Backend deployed
- [ ] PostgreSQL service added
- [ ] Redis service added
- [ ] Vercel account created
- [ ] Frontend deployed
- [ ] Environment variables configured

**Post-Deployment**
- [ ] Health check passes
- [ ] Frontend loads
- [ ] API docs accessible
- [ ] CORS working
- [ ] URLs documented

---

## 🎉 Ready to Deploy!

Everything is ready for staging deployment. Start with:

```bash
cat QUICK_DEPLOY.md
```

Or jump right in:
1. Visit https://railway.app/new
2. Deploy from this GitHub repo
3. Follow the guide!

Good luck! 🚀

---

**Last Updated:** $(date)  
**Status:** Ready for staging deployment  
**Deployment Infrastructure:** 100% complete
