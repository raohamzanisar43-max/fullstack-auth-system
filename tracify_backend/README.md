# Tracerfy Backend

Professional Skip Tracing Platform for Real Estate Lead Generation

## Features

- **JWT Authentication**: Secure user authentication with access and refresh tokens
- **API Key Management**: Generate and manage API keys for programmatic access
- **Role-Based Access Control**: Admin, manager, and user roles
- **Password Reset**: Secure password reset via email
- **Email Verification**: Verify user email addresses
- **Rate Limiting**: Configurable rate limiting for API endpoints
- **Database Migrations**: Alembic-based database migrations
- **Comprehensive Logging**: Structured logging with multiple levels
- **Health Checks**: Monitor application and service health
- **CORS Support**: Cross-origin resource sharing configuration

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Rate Limiting**: Redis (optional)
- **Background Tasks**: Celery (optional)
- **Payment**: Stripe (optional)

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional, for rate limiting and caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tracerfy_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb tracerfy_db
   
   # Run migrations
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   # Development
   python -m app.main
   
   # Or with uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile
- `PUT /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/verify-email` - Verify email
- `POST /api/v1/auth/resend-verification` - Resend verification email

### API Keys

- `POST /api/v1/api-keys/` - Create API key
- `GET /api/v1/api-keys/` - List API keys
- `GET /api/v1/api-keys/{id}` - Get API key
- `PUT /api/v1/api-keys/{id}` - Update API key
- `DELETE /api/v1/api-keys/{id}` - Delete API key

### Health & Monitoring

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /metrics` - Application metrics

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tracerfy_db

# Security
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Stripe (optional)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
```

## Database Migrations

### Create new migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Description of changes"

# Manual migration
alembic revision -m "Description of changes"
```

### Apply migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade +1
alembic upgrade <revision_id>
```

### Downgrade migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>
```

## Authentication Flow

1. **Register**: Create a new user account
2. **Login**: Authenticate with email and password to receive tokens
3. **Access Token**: Use access token for authenticated requests (expires in 30 minutes)
4. **Refresh Token**: Use refresh token to get new access token (expires in 7 days)
5. **API Keys**: Generate API keys for programmatic access

## API Usage Examples

### Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Access Protected Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create API Key

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "permissions": ["read", "write"],
    "rate_limit": 1000
  }'
```

## Security Features

- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Rate Limiting**: Prevent abuse with configurable limits
- **CORS Protection**: Control cross-origin requests
- **Input Validation**: Comprehensive validation with Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM protects against SQL injection
- **Security Headers**: Built-in security headers

## Development

### Code Style

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API routes
│   ├── core/            # Core configuration and utilities
│   ├── db/              # Database configuration
│   ├── middleware/      # Custom middleware
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── alembic/             # Database migrations
├── logs/                # Application logs
└── tests/               # Test files
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set secure values for all secrets
2. **Database**: Use PostgreSQL in production
3. **Redis**: Enable Redis for rate limiting and caching
4. **HTTPS**: Use HTTPS in production
5. **CORS**: Configure appropriate CORS origins
6. **Logging**: Enable structured logging
7. **Monitoring**: Set up monitoring and alerting

### Docker Production

```bash
# Build production image
docker build -t tracerfy-backend .

# Run with environment variables
docker run -d \
  --name tracerfy-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-secret-key \
  tracerfy-backend
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, contact:
- Email: support@tracerfy.com
- Website: https://www.tracerfy.com
