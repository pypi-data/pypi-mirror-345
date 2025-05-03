# FastAuth

A comprehensive authentication library for FastAPI applications with JWT-based authentication and SQLModel integration. Now with a modular architecture for better maintainability and extensibility.

## Features

- **OAuth2 and JWT authentication** built-in
- **Cookie-based authentication** option
- **Token refresh mechanism** for extended sessions
- **SQLModel integration** for easy database operations
- **Ready-to-use authentication routes** with minimal setup
- **Password hashing** with bcrypt
- **Modular architecture** for better code organization and extensibility

## Installation

```bash
pip install fastauth_iq
```

Or install from source:

```bash
git clone https://github.com/hu55ain3laa/fastauth.git
cd fastauth
pip install -e .
```

## Quick Start

### 1. Create a User Model

FastAuth works with SQLModel's user model. You can use the built-in User model or create your own:

```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    disabled: bool = Field(default=False)
```

### 2. Initialize FastAuth in Your Application

```python
from fastapi import FastAPI, Depends
from sqlmodel import create_engine, Session, SQLModel

from fastauth import FastAuth, User

# Create FastAPI app
app = FastAPI()

# Setup database
engine = create_engine("sqlite:///./app.db")

# Session dependency
def get_session():
    with Session(engine) as session:
        yield session

# Initialize FastAuth with your configuration
auth = FastAuth(
    secret_key="your-secure-secret-key",  # Use strong secret in production
    algorithm="HS256",
    user_model=User,
    engine=engine,
    use_cookie=True,  # Enable cookie-based auth (optional)
    token_url="/token",
    access_token_expires_in=30,  # minutes
    refresh_token_expires_in=7   # days
)

# Add all authentication routes automatically
auth_router = auth.get_auth_router(get_session)
app.include_router(auth_router, tags=["authentication"])
```

### 3. Protect Your Routes

```python
@app.get("/protected")
def protected_route(current_user = Depends(auth.get_current_active_user_dependency())):
    return {"message": f"Hello, {current_user.username}!"}
```

## Available Authentication Endpoints

The `get_auth_router()` method automatically adds these endpoints to your application:

- **POST /token** - Get access and refresh tokens with username/password
- **POST /token/refresh** - Get a new access token using a refresh token
- **POST /users** - Register a new user
- **GET /users/me** - Get the current authenticated user's information

## Customization Options

### Cookie-Based Authentication

Enable cookie-based authentication by setting `use_cookie=True`:

```python
auth = FastAuth(
    # ... other parameters
    use_cookie=True
)
```

### Custom Token Expiration

Set custom expiration times for tokens:

```python
auth = FastAuth(
    # ... other parameters
    access_token_expires_in=60,  # 60 minutes
    refresh_token_expires_in=30  # 30 days
)
```

### Advanced Usage: Custom Authentication Routes

You can create your own authentication routes instead of using the built-in router:

```python
@app.post("/custom-login")
async def custom_login(
    username: str, 
    password: str, 
    session: Session = Depends(get_session)
):
    user = auth.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Security Best Practices

1. **Always use HTTPS** in production
2. **Use a strong secret key** and keep it secure
3. **Set appropriate token expiration times**
4. **Enable httpOnly and secure flags** for cookies
5. **Consider implementing rate limiting** for authentication endpoints

## License

MIT

## Modular Architecture

With version 0.2.0, FastAuth has been refactored into a modular architecture to improve maintainability, testability, and extensibility. The code is now organized into specialized modules:

```
fastauth/
├── core/       # Core FastAuth class and OAuth2 implementation
├── security/   # Password management and token handling
├── models/     # User and token data models
├── routers/    # Authentication route handlers
├── dependencies/ # FastAPI dependencies for authentication
└── utils/      # Utility functions and helpers
```

This modular structure makes it easier to:
- Understand and modify specific parts of the library
- Write targeted tests for each component
- Extend functionality with new features
- Reuse components in other projects

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
