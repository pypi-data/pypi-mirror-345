# keylin

[![Python Versions](https://img.shields.io/pypi/pyversions/keylin)](https://pypi.org/project/keylin)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://github.com/beanone/keylin/actions/workflows/tests.yml/badge.svg)](https://github.com/beanone/keylin/actions?query=workflow%3Atests)
[![Coverage](https://codecov.io/gh/beanone/keylin/branch/main/graph/badge.svg)](https://codecov.io/gh/beanone/keylin)
[![Code Quality](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![PyPI version](https://img.shields.io/pypi/v/keylin)](https://pypi.org/project/keylin)

## Features

- User model and schema library for authentication services
- Designed for integration with FastAPI and fastapi-users
- Reusable across multiple services

## Installation

```bash
pip install keylin
```

## Usage

```python
from keylin.models import User
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from keylin.db import get_async_session

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        User.__table__.select().where(User.id == user_id)
    )
    user = result.fetchone()
    if user:
        return user
    return {"error": "User not found"}
```

## Architecture & Integration Guide

### Typical Architecture

A recommended architecture for a login/authentication service using `keylin`:

```mermaid
graph TD
    A[Client App / Frontend]
    B[API Gateway / HTTPS Proxy]
    C[FastAPI Login Service - uses keylin]
    D[Database - PostgreSQL, etc.]
    A --> B
    B --> C
    C --> D
```

- **keylin** provides the user model, schemas, and authentication logic.
- The login service is a FastAPI app that imports keylin and wires up routers.
- Other services can import keylin to share the user model and schemas for consistent user data handling.

### Example FastAPI Login Service

```python
from fastapi import FastAPI
from keylin.auth import auth_backend, fastapi_users, get_user_manager
from keylin.schemas import UserRead, UserCreate

app = FastAPI()

# Auth routes
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserRead), prefix="/users", tags=["users"])
```

### Environment Variables (Required for Production)
- `KEYLIN_JWT_SECRET`: Secret key for JWT signing (required)
- `KEYLIN_RESET_PASSWORD_SECRET`: Secret for password reset tokens (optional, defaults to JWT secret)
- `KEYLIN_VERIFICATION_SECRET`: Secret for verification tokens (optional, defaults to JWT secret)
- `KEYLIN_DATABASE_URL`: SQLAlchemy DB URL (e.g., `postgresql+asyncpg://user:pass@host/dbname`)

### Security & Deployment Best Practices
- **CORS:** Configure CORS in your FastAPI app using `CORSMiddleware` to restrict allowed origins.
- **HTTPS:** Always deploy behind a TLS-terminating proxy (e.g., NGINX, Caddy, cloud load balancer).
- **Secret Management:** Never hardcode secrets. Use environment variables or a secrets manager.
- **Rate Limiting:** Add rate limiting at the API gateway or with middleware to prevent brute-force attacks.
- **Email Verification:** Enable and configure email verification in your login service for new users.
- **Audit Logging:** Log authentication events for security monitoring.

### Extending the User Model
- You can add fields to the `User` model and corresponding Pydantic schemas in your own code or by forking/extending keylin.
- All models and schemas use type annotations and are compatible with FastAPI and Pydantic.

### User Model & Database Schema

#### Default User Model Fields

| Field            | Type      | Description                 | Required | Notes                |
|------------------|-----------|-----------------------------|----------|----------------------|
| id               | UUID      | Unique user identifier      | Yes      | Primary key          |
| email            | str       | User email (unique)         | Yes      | Unique, indexed      |
| hashed_password  | str       | Hashed password             | Yes      | Not exposed in API responses |
| full_name        | str/None  | User's full name            | No       | Optional             |
| is_active        | bool      | Is the user active?         | Yes      |                      |
| is_superuser     | bool      | Is the user an admin?       | Yes      |                      |
| is_verified      | bool      | Has the user verified email | Yes      |                      |

> **Note:** The table is named `"user"`, which is a reserved word in some databases (e.g., PostgreSQL). Consider renaming to `"users"` if you encounter issues.

#### Example User Schema

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

#### Extending the User Model
- To add fields, update the `User` SQLAlchemy model and the corresponding Pydantic schemas.
- Run a new Alembic migration to update the database schema.
- Update the UI to handle new fields as needed.
- Keep the UI and backend in sync regarding user data shape.
- **Tip:** If you need roles or permissions, add fields (e.g., `role`, `permissions`) to the model and schemas, and update your business logic accordingly.

### Testing
- 100% code coverage with pytest and pytest-asyncio.
- Pre-commit hooks for linting, formatting, and type checking.
- See `tests/unit/test_keylin.py` for example tests and mocking patterns.

### Setting Up the User Database

Before running your login service, you need to ensure the user table exists in your database.

#### Recommended: Use Alembic for Migrations
For production and team environments, use [Alembic](https://alembic.sqlalchemy.org/) to manage database migrations:

```bash
alembic revision --autogenerate -m "create user table"
alembic upgrade head
```

Make sure your Alembic `env.py` includes the keylin model's metadata:
```python
from keylin.models import Base

target_metadata = Base.metadata
```

#### Quick Local Setup: Create Tables Programmatically
For local development or quick tests, you can create the tables directly using SQLAlchemy:

```python
from keylin.models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./test.db")  # Or your DB URL
Base.metadata.create_all(engine)
```

> **Note:** For production, always use migrations to avoid data loss and ensure schema consistency.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
