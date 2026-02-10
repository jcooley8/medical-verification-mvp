#!/bin/bash
set -e

echo "🚀 Medical Verification MVP - Staging Deployment Script"
echo "========================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if logged in to Railway
echo "📋 Checking Railway authentication..."
if railway whoami > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Railway authenticated${NC}"
else
    echo -e "${YELLOW}⚠ Not logged in to Railway${NC}"
    echo "Please run: railway login"
    echo "Then run this script again."
    exit 1
fi

# Check if logged in to Vercel
echo "📋 Checking Vercel authentication..."
if vercel whoami > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Vercel authenticated${NC}"
else
    echo -e "${YELLOW}⚠ Not logged in to Vercel${NC}"
    echo "Please run: vercel login"
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "=============================="
echo "Step 1: Deploy Backend to Railway"
echo "=============================="
echo ""

cd backend

# Check if Railway project is linked
if [ ! -f "railway.json" ] && [ ! -f ".railway" ]; then
    echo "Creating new Railway project..."
    railway init
fi

echo "Deploying backend to Railway..."
railway up

echo ""
echo "Please complete the following manual steps in Railway dashboard:"
echo "1. Add PostgreSQL service: railway add --database postgres"
echo "2. Add Redis service: railway add --database redis"
echo "3. Set environment variables:"
echo "   - ENVIRONMENT=staging"
echo "   - DEBUG=false"
echo "   - ALLOWED_ORIGINS=*"
echo ""
read -p "Press Enter when Railway services are configured..."

# Get the Railway URL
RAILWAY_URL=$(railway variables get RAILWAY_PUBLIC_DOMAIN 2>/dev/null || echo "")
if [ -z "$RAILWAY_URL" ]; then
    echo "Please enter your Railway backend URL (e.g., app-name.up.railway.app):"
    read RAILWAY_URL
fi

echo -e "${GREEN}✓ Backend deployed to: https://$RAILWAY_URL${NC}"

cd ..

echo ""
echo "=============================="
echo "Step 2: Deploy Frontend to Vercel"
echo "=============================="
echo ""

cd frontend

echo "Deploying frontend to Vercel..."
vercel --prod

# Get the Vercel URL
VERCEL_URL=$(vercel inspect --token="$(vercel whoami --token)" | grep "url" | head -1 | awk '{print $2}' 2>/dev/null || echo "")
if [ -z "$VERCEL_URL" ]; then
    echo "Please enter your Vercel frontend URL (e.g., app-name.vercel.app):"
    read VERCEL_URL
fi

echo ""
echo "Setting frontend environment variable..."
vercel env add VITE_API_URL production <<< "https://$RAILWAY_URL"

echo -e "${GREEN}✓ Frontend deployed to: https://$VERCEL_URL${NC}"

cd ..

echo ""
echo "=============================="
echo "Step 3: Update CORS Settings"
echo "=============================="
echo ""

echo "Updating backend CORS to allow frontend..."
cd backend
railway variables set ALLOWED_ORIGINS="https://$VERCEL_URL,http://localhost:5173"
railway up
cd ..

echo ""
echo "=============================="
echo "Step 4: Run Database Migrations"
echo "=============================="
echo ""

cd backend
echo "Creating database tables..."
railway run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
cd ..

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo -e "${GREEN}Frontend URL:${NC} https://$VERCEL_URL"
echo -e "${GREEN}Backend API:${NC} https://$RAILWAY_URL"
echo -e "${GREEN}API Docs:${NC} https://$RAILWAY_URL/docs"
echo ""
echo "Next steps:"
echo "1. Test health endpoint: curl https://$RAILWAY_URL/health"
echo "2. Visit frontend: https://$VERCEL_URL"
echo "3. Run smoke tests (see DEPLOYMENT_GUIDE.md)"
echo "4. Update DEPLOYMENT_SUMMARY.md with URLs"
echo ""

# Save URLs to file
cat > DEPLOYMENT_URLS.txt <<EOF
FRONTEND_URL=https://$VERCEL_URL
BACKEND_URL=https://$RAILWAY_URL
API_DOCS_URL=https://$RAILWAY_URL/docs
DEPLOYED_AT=$(date)
EOF

echo "URLs saved to DEPLOYMENT_URLS.txt"
