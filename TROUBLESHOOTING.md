# Troubleshooting Guide

Common issues and solutions for the Medical Verification MVP.

## Table of Contents

- [Backend Issues](#backend-issues)
- [Frontend Issues](#frontend-issues)
- [Database Issues](#database-issues)
- [Celery/Redis Issues](#celeryredis-issues)
- [Deployment Issues](#deployment-issues)
- [Performance Issues](#performance-issues)

---

## Backend Issues

### Backend Server Won't Start

**Symptom**: `uvicorn app.main:app` fails to start

**Possible Causes & Solutions**:

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   
   # Kill the process or use a different port
   uvicorn app.main:app --port 8001
   ```

2. **Database Connection Failed**
   ```bash
   # Check DATABASE_URL in .env
   # Verify PostgreSQL is running
   pg_isready  # Should return "accepting connections"
   
   # Try connecting manually
   psql $DATABASE_URL
   ```

3. **Missing Dependencies**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate  # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   
   # Check PYTHONPATH
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

### Documents Stuck in "QUEUED" Status

**Symptom**: Documents never move from QUEUED to PROCESSING

**Possible Causes**:

1. **Celery Worker Not Running**
   ```bash
   # Check if Celery worker is running
   ps aux | grep celery
   
   # Start Celery worker
   celery -A app.celery_app worker --loglevel=info
   ```

2. **Redis Not Running**
   ```bash
   # Check if Redis is running
   redis-cli ping  # Should return "PONG"
   
   # Start Redis
   redis-server
   ```

3. **Task Queue Error**
   ```bash
   # Check Celery worker logs for errors
   # Look for connection errors or task failures
   
   # Purge queue and retry
   celery -A app.celery_app purge
   ```

### Documents Stuck in "PROCESSING" Status

**Symptom**: Documents stuck in PROCESSING, never complete

**Possible Causes**:

1. **Celery Worker Crashed**
   ```bash
   # Check Celery worker logs
   # Restart the worker
   celery -A app.celery_app worker --loglevel=info
   ```

2. **Task Exception Not Handled**
   ```bash
   # Check Celery logs for exceptions
   # Look for Python tracebacks
   
   # Manually update document status
   # Connect to database and run:
   UPDATE documents SET status = 'FAILED' WHERE id = <document_id>;
   ```

3. **File Not Found**
   ```bash
   # Check if uploaded file exists
   ls -la /code/uploads/
   
   # Verify file_path in database matches actual file location
   ```

### API Returns 500 Errors

**Symptom**: Endpoints return "Internal Server Error"

**Debugging Steps**:

1. **Check Server Logs**
   ```bash
   # Look for detailed error messages in uvicorn output
   # Note the timestamp and endpoint
   ```

2. **Enable Debug Mode**
   ```python
   # In main.py, temporarily enable debug
   app = FastAPI(debug=True)
   ```

3. **Check Database Connection**
   ```bash
   # Test database connectivity
   python -c "from app.database import engine; print(engine.connect())"
   ```

4. **Verify File Permissions**
   ```bash
   # Check upload directory permissions
   ls -la /code/
   chmod 755 /code/uploads/
   ```

---

## Frontend Issues

### Frontend Won't Start

**Symptom**: `npm run dev` fails

**Solutions**:

1. **Install Dependencies**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port Conflict**
   ```bash
   # Vite uses port 5173 by default
   # Change port in vite.config.ts or:
   npm run dev -- --port 3000
   ```

3. **Node Version**
   ```bash
   # Check Node version (needs 18+)
   node --version
   
   # Use nvm to switch versions
   nvm use 18
   ```

### PDF Not Displaying

**Symptom**: PDF viewer shows blank or error

**Possible Causes**:

1. **CORS Issue**
   - Backend must allow frontend origin
   - Check `ALLOWED_ORIGINS` in backend `.env`
   ```bash
   # Add frontend URL to ALLOWED_ORIGINS
   ALLOWED_ORIGINS=http://localhost:5173
   ```

2. **PDF Worker Not Loading**
   ```javascript
   // Check browser console for pdf.worker errors
   // Verify pdfjs-dist is installed
   npm list pdfjs-dist
   ```

3. **Invalid PDF URL**
   ```javascript
   // Check if PDF URL is correct in mockData.ts
   // Verify the PDF file exists and is accessible
   ```

### Highlights Not Appearing

**Symptom**: Click-to-verify doesn't show highlights

**Debugging**:

1. **Check Source References**
   ```javascript
   // Log extraction result in console
   console.log(extractionResult.events[0].source_refs);
   
   // Verify source_refs array exists and has valid bounding boxes
   ```

2. **Check Coordinate Conversion**
   ```javascript
   // In coordinateMapping.ts, add debug logs
   console.log('Page dimensions:', pageWidth, pageHeight);
   console.log('Highlight region:', region);
   ```

3. **Check PDF Page Rendering**
   ```javascript
   // Verify currentPage matches source_ref.page_number
   // Check if page is fully rendered before showing highlight
   ```

### Build Fails

**Symptom**: `npm run build` produces errors

**Solutions**:

1. **TypeScript Errors**
   ```bash
   # Run type checking separately
   npm run build  # Will show TS errors
   
   # Fix type errors in the code
   ```

2. **Memory Issues**
   ```bash
   # Increase Node memory limit
   NODE_OPTIONS="--max-old-space-size=4096" npm run build
   ```

---

## Database Issues

### Database Connection Refused

**Symptom**: "could not connect to server: Connection refused"

**Solutions**:

1. **PostgreSQL Not Running**
   ```bash
   # Start PostgreSQL
   # Mac (Homebrew):
   brew services start postgresql
   
   # Linux (systemd):
   sudo systemctl start postgresql
   
   # Windows:
   # Start PostgreSQL service from Services panel
   ```

2. **Wrong Connection String**
   ```bash
   # Check DATABASE_URL format
   # postgresql://username:password@host:port/database
   
   # Verify credentials
   psql -U username -d database_name
   ```

3. **Firewall Blocking Connection**
   ```bash
   # Check PostgreSQL is listening
   netstat -an | grep 5432
   
   # Allow connections in pg_hba.conf
   ```

### Database Tables Don't Exist

**Symptom**: "relation does not exist"

**Solution**:
```bash
# FastAPI creates tables automatically on startup
# If tables aren't created, try:

python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Database Migration Needed

**Symptom**: Schema changes not reflected

**Solution**:
```bash
# For development, drop and recreate tables
# WARNING: This deletes all data!

python -c "from app.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"

# For production, use Alembic migrations (to be implemented)
```

---

## Celery/Redis Issues

### Redis Connection Failed

**Symptom**: "Error 111 connecting to localhost:6379. Connection refused"

**Solutions**:

1. **Start Redis**
   ```bash
   # Mac (Homebrew):
   brew services start redis
   
   # Linux (systemd):
   sudo systemctl start redis
   
   # Manual:
   redis-server
   ```

2. **Wrong Redis URL**
   ```bash
   # Check REDIS_URL in .env
   # Default: redis://localhost:6379/0
   
   # Test connection
   redis-cli ping
   ```

### Celery Worker Not Processing Tasks

**Symptom**: Tasks queued but not executed

**Debugging**:

1. **Check Worker Logs**
   ```bash
   # Start worker with debug logging
   celery -A app.celery_app worker --loglevel=debug
   
   # Look for task registration and execution logs
   ```

2. **Inspect Queue**
   ```bash
   # List all tasks in queue
   celery -A app.celery_app inspect active
   celery -A app.celery_app inspect scheduled
   
   # Purge queue if needed
   celery -A app.celery_app purge
   ```

3. **Task Import Errors**
   ```bash
   # Make sure Celery can import tasks
   python -c "from app.tasks import process_document; print(process_document)"
   ```

### Task Fails Silently

**Symptom**: Task doesn't complete, no error shown

**Solutions**:

1. **Enable Task Events**
   ```bash
   celery -A app.celery_app worker --loglevel=info --events
   ```

2. **Check Task Result Backend**
   ```python
   # In celery_app.py, configure result backend
   celery_app.conf.result_backend = 'redis://localhost:6379/0'
   ```

3. **Add Error Handling**
   ```python
   @celery_app.task(bind=True, max_retries=3)
   def process_document(self, document_id: int):
       try:
           # Task logic
       except Exception as e:
           logger.error(f"Task failed: {e}")
           raise self.retry(exc=e, countdown=60)
   ```

---

## Deployment Issues

### Railway/Vercel Deployment Fails

**Common Issues**:

1. **Environment Variables Missing**
   - Check all required env vars are set in Railway/Vercel
   - Especially: `DATABASE_URL`, `REDIS_URL`, `ALLOWED_ORIGINS`

2. **Build Command Fails**
   ```bash
   # Check build logs for specific errors
   # Verify requirements.txt/package.json is correct
   ```

3. **Port Binding Issues**
   ```python
   # Railway provides $PORT environment variable
   port = int(os.getenv("PORT", 8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
   ```

4. **File Upload Directory**
   ```python
   # Railway filesystem is ephemeral
   # Consider using cloud storage (S3, etc.) for production
   ```

### CORS Errors in Production

**Symptom**: "Access-Control-Allow-Origin" errors

**Solution**:
```python
# In backend main.py, ensure frontend URL is in ALLOWED_ORIGINS
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-backend.railway.app
```

---

## Performance Issues

### Slow Document Processing

**Symptom**: Documents take a long time to process

**Optimization Tips**:

1. **OCR Service**
   - Use real OCR service (AWS Textract) instead of mock
   - Implement caching for previously processed documents

2. **Database Queries**
   - Add indexes on frequently queried columns
   ```sql
   CREATE INDEX idx_documents_status ON documents(status);
   CREATE INDEX idx_documents_created_at ON documents(created_at);
   ```

3. **Celery Configuration**
   ```python
   # Increase worker concurrency
   celery -A app.celery_app worker --concurrency=4
   ```

### Large Bundle Size (Frontend)

**Symptom**: Frontend loads slowly

**Solutions**:

1. **Code Splitting**
   ```typescript
   // Use dynamic imports
   const PDFViewer = lazy(() => import('./components/PDFViewer'));
   ```

2. **Optimize Dependencies**
   ```bash
   # Analyze bundle size
   npm run build -- --mode analyze
   
   # Consider lighter alternatives to heavy libraries
   ```

3. **Tree Shaking**
   ```typescript
   // Import only what you need
   import { specific } from 'library';  // Good
   import * as entire from 'library';    // Avoid
   ```

### Memory Leaks

**Symptom**: Application memory usage grows over time

**Debugging**:

1. **Frontend Memory Leaks**
   - Use React DevTools Profiler
   - Check for uncleared intervals/timeouts
   - Verify useEffect cleanup functions

2. **Backend Memory Leaks**
   ```bash
   # Monitor process memory
   ps aux | grep uvicorn
   
   # Use memory profiler
   pip install memory-profiler
   python -m memory_profiler app/main.py
   ```

---

## Getting More Help

If these solutions don't resolve your issue:

1. **Check Logs**: Always check server logs and browser console
2. **Search Issues**: Look for similar issues in the repository
3. **Create Issue**: File a detailed bug report with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs
   - Environment details (OS, versions, etc.)

**Emergency Debugging**:
```bash
# Backend: Enable all logging
export LOG_LEVEL=DEBUG

# Frontend: Enable React DevTools
# Install: https://react.dev/learn/react-developer-tools

# Database: Check connections
psql $DATABASE_URL -c "SELECT * FROM documents ORDER BY created_at DESC LIMIT 5;"

# Redis: Monitor commands
redis-cli MONITOR
```

---

**Last Updated**: February 2024  
**Maintainers**: Development Team
