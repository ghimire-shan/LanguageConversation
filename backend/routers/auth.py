from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from database import get_db
from models.user import User
from schemas.user import UserResponse, Token
from auth import create_access_token, get_current_user
from config import settings
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configure OAuth
config = Config()
oauth = OAuth(config)

# Google OAuth client - will be registered lazily
google = None

def get_google_oauth():
    """Get or register Google OAuth client"""
    global google
    if google is None:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )
        google = oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
    return google

@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    google_oauth = get_google_oauth()
    
    # Use the configured redirect URI or construct from request
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not redirect_uri or redirect_uri == "http://localhost:8000/auth/callback":
        # Construct from request if using default
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/auth/callback"
    
    return await google_oauth.authorize_redirect(request, redirect_uri)

@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    google_oauth = get_google_oauth()
    
    try:
        token = await google_oauth.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OAuth error: {str(e)}"
        )
    
    # Get user info from Google
    user_info = token.get('userinfo')
    if not user_info:
        # Fetch user info if not included in token
        resp = await google_oauth.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
    
    email = user_info.get('email')
    google_id = user_info.get('sub')
    name = user_info.get('name')
    picture = user_info.get('picture')
    
    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user information from Google"
        )
    
    # Check if user exists
    user = db.query(User).filter(
        (User.email == email) | (User.google_id == google_id)
    ).first()
    
    if user:
        # Update user info if needed
        user.email = email
        user.google_id = google_id
        if name:
            user.name = name
        if picture:
            user.picture = picture
    else:
        # Create new user
        user = User(
            email=email,
            google_id=google_id,
            name=name,
            picture=picture
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Return token (in production, you might want to redirect to frontend with token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.get("/status")
async def auth_status():
    """Check OAuth configuration status"""
    return {
        "configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
        "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "message": "OAuth is configured" if (settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET) else "OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file"
    }

