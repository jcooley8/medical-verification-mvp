# 🚀 Quick Deploy Guide

## TL;DR - Deploy in 3 Steps

### Step 1: Deploy Backend (Railway)
1. Visit: https://railway.app/new
2. Choose: "Deploy from GitHub repo" → `jcooley8/medical-verification-mvp`
3. Add databases: PostgreSQL + Redis
4. Configure: Set environment variables (see below)
5. Deploy: Railway will auto-build and deploy

**Required Environment Variables:**
```
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
ENVIRONMENT=staging
DEBUG=false
ALLOWED_ORIGINS=*
```

**Time:** ~15 minutes  
**Copy your Railway URL:** `https://[app-name].up.railway.app`

---

### Step 2: Deploy Frontend (Vercel)
1. Visit: https://vercel.com/new
2. Import: `jcooley8/medical-verification-mvp`
3. Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set environment variable:
   ```
   VITE_API_URL=https://[your-railway-url-from-step-1]
   ```
5. Deploy: Vercel will build and deploy

**Time:** ~10 minutes  
**Copy your Vercel URL:** `https://[app-name].vercel.app`

---

### Step 3: Update CORS
1. Go back to Railway → Backend service → Variables
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://[your-vercel-url-from-step-2],http://localhost:5173
   ```
3. Railway will auto-redeploy

**Time:** ~2 minutes

---

## ✅ Verify Deployment

**Backend Health Check:**
```bash
curl https://[your-railway-url]/health
```
Expected: `{"status":"ok","database":"connected"}`

**Frontend:**
Visit: `https://[your-vercel-url]`  
Expected: Medical Verification MVP interface loads

**API Docs:**
Visit: `https://[your-railway-url]/docs`  
Expected: Swagger UI with API endpoints

---

## 📄 Need More Details?

- **Complete Guide:** See `MANUAL_DEPLOYMENT.md` for step-by-step screenshots and troubleshooting
- **Reference Docs:** See `DEPLOYMENT_GUIDE.md` for comprehensive documentation
- **Status Tracking:** See `DEPLOYMENT_SUMMARY.md` for deployment status

---

## 🆘 Troubleshooting

**Backend won't start?**  
→ Check Railway logs for errors  
→ Verify DATABASE_URL and REDIS_URL are set

**Frontend shows errors?**  
→ Check VITE_API_URL matches your Railway URL  
→ Verify CORS is configured with your Vercel URL

**Database connection fails?**  
→ Ensure PostgreSQL service is running in Railway  
→ Check backend logs for connection errors

---

## 📞 Support

- **GitHub Issues:** https://github.com/jcooley8/medical-verification-mvp/issues
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs

---

**Total Time to Deploy:** ~25-30 minutes  
**Cost:** ~$5/month (Railway Hobby plan)

Ready? Start with Step 1! 🚀
