from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, practice

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Language Conversation API",
    description="API with Google OAuth authentication",
    version="1.0.0"
)

# CORS configuration
origins = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:5173',
    'http://localhost:5174',
]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth.router)
app.include_router(practice.router)

@app.get("/")
async def root():
    return {
        "message": "Language Conversation API",
        "docs": "/docs",
        "auth": {
            "login": "/auth/login",
            "callback": "/auth/callback",
            "me": "/auth/me"
        }
    }

@app.get("/test")
async def test():
    return {"message": "hello world"}