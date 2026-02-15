# Contributing to Medical Verification MVP

Thank you for your interest in contributing to the Medical Verification MVP! This document provides guidelines and instructions for developers.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker (optional, for containerized development)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical-verification-mvp/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Set up database**
   ```bash
   # FastAPI will auto-create tables on startup
   # Or run migrations manually if needed
   ```

6. **Start services**
   ```bash
   # Terminal 1: Redis
   redis-server
   
   # Terminal 2: Celery worker
   celery -A app.celery_app worker --loglevel=info
   
   # Terminal 3: FastAPI server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd medical-verification-mvp/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
medical-verification-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # Database connection
│   │   ├── tasks.py             # Celery tasks
│   │   ├── ocr_service.py       # OCR processing
│   │   ├── llm_service.py       # LLM classification & extraction
│   │   └── verification_service.py  # Verification linkage algorithm
│   ├── tests/                   # Backend tests
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── types/              # TypeScript types
│   │   ├── utils/              # Utility functions
│   │   └── App.tsx             # Main application component
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite configuration
└── CONTRIBUTING.md             # This file
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, documented code
- Follow the code style guidelines below
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Frontend build test
cd frontend
npm run build

# End-to-end test
cd backend
python test_e2e_pipeline.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use docstrings for all functions and classes
- Format code with `black` (recommended)

Example:
```python
def process_document(document_id: int, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a document through the extraction pipeline.
    
    Args:
        document_id: ID of the document to process
        user_id: Optional user ID for tracking
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        ValueError: If document_id is invalid
        ProcessingError: If processing fails
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

- Follow the existing code style
- Use TypeScript strict mode
- Define interfaces for all data structures
- Use functional components with hooks
- Maximum line length: 100 characters

Example:
```typescript
interface DocumentStatus {
  documentId: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  filename: string;
}

export const useDocumentStatus = (documentId: number): DocumentStatus | null => {
  // Implementation here
};
```

### General Guidelines

- **Naming Conventions**:
  - Python: `snake_case` for variables and functions, `PascalCase` for classes
  - TypeScript: `camelCase` for variables and functions, `PascalCase` for components and interfaces
  
- **Comments**:
  - Explain *why*, not *what* (code should be self-explanatory)
  - Use docstrings for all public functions
  - Add inline comments for complex logic

- **Error Handling**:
  - Always handle errors gracefully
  - Log errors with appropriate context
  - Return user-friendly error messages

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_verification_service.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Type checking
npm run build  # This runs TypeScript compiler
```

### End-to-End Tests

```bash
cd backend
python test_e2e_pipeline.py
```

## Submitting Changes

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all tests pass

3. **Code Review**
   - Address reviewer feedback
   - Update your PR as needed

4. **Merge**
   - Once approved, your PR will be merged
   - Delete your feature branch after merge

## Common Issues & Solutions

### Backend won't start

- **Check database connection**: Verify `DATABASE_URL` in `.env`
- **Check Redis**: Ensure Redis is running (`redis-cli ping` should return `PONG`)
- **Port in use**: Change the port or kill the process using port 8000

### Celery worker not processing tasks

- **Check Redis connection**: Verify `REDIS_URL` in `.env`
- **Check Celery logs**: Look for error messages in the worker terminal
- **Restart worker**: Stop and restart the Celery worker

### Frontend not loading

- **Check backend**: Ensure backend is running on port 8000
- **Check CORS**: Verify `ALLOWED_ORIGINS` includes your frontend URL
- **Clear cache**: Hard refresh your browser (Ctrl+Shift+R)

### Import errors

- **Backend**: Ensure virtual environment is activated and dependencies installed
- **Frontend**: Run `npm install` to ensure all packages are installed

## Getting Help

- **Documentation**: Check the README files in backend and frontend directories
- **Issues**: Search existing issues or create a new one
- **Questions**: Reach out to the team via [contact method]

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Medical Verification MVP! 🎉
