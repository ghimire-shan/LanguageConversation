# Google OAuth Setup Guide

## Step-by-Step Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Console

1. **Go to Google Cloud Console**

   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project** (or select existing)

   - Click "Select a project" → "New Project"
   - Give it a name (e.g., "Language Conversation")
   - Click "Create"

3. **Enable Google+ API**

   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" or "People API"
   - Click on it and press "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen first:
     - Choose "External" (unless you have a Google Workspace)
     - Fill in app name, user support email, developer email
     - Add scopes: `email`, `profile`, `openid`
     - Add test users if in testing mode
     - Save and continue
5. **Configure OAuth Client**
   - Application type: "Web application"
   - Name: "Language Conversation Backend"
   - **Authorized redirect URIs**: Add these:
     - `http://localhost:8000/auth/callback`
     - `http://127.0.0.1:8000/auth/callback` (if you use 127.0.0.1)
   - Click "Create"
   - **Copy the Client ID and Client Secret** (you'll need these!)

### 3. Create Environment File

Create a `.env` file in the `backend` directory:

```bash
# In backend directory
touch .env  # On Windows: type nul > .env
```

Add the following content to `.env`:

```env
# Google OAuth Credentials (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Redirect URI (must match what you set in Google Cloud Console)
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT Secret Key (generate a random string)
SECRET_KEY=your-random-secret-key-change-this-in-production

# Server URL
SERVER_URL=http://localhost:8000
```

**Important**: Replace the placeholder values with your actual credentials!

### 4. Generate a Secret Key

You can generate a random secret key using Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use an online generator. This should be a long, random string.

### 5. Run the Server

```bash
cd backend
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### 6. Test the OAuth Flow

1. **Visit the login endpoint:**

   ```
   http://localhost:8000/auth/login
   ```

2. **You'll be redirected to Google** to sign in

3. **After signing in**, you'll be redirected back to `/auth/callback`

4. **You'll receive a JSON response** with:
   - `access_token`: JWT token for authenticated requests
   - `token_type`: "bearer"
   - `user`: Your user information

### 7. Test Protected Endpoints

Use the access token to access protected endpoints:

```bash
# Get your user info
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/auth/me
```

Or use the interactive docs at: `http://localhost:8000/docs`

## Troubleshooting

### Error: "Google OAuth not configured"

- Make sure your `.env` file exists in the `backend` directory
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly
- Restart the server after creating/modifying `.env`

### Error: "redirect_uri_mismatch"

- The redirect URI in your `.env` must **exactly match** what you set in Google Cloud Console
- Check for trailing slashes, http vs https, localhost vs 127.0.0.1
- Make sure you added the redirect URI in Google Cloud Console

### Error: "invalid_client"

- Double-check your Client ID and Client Secret
- Make sure there are no extra spaces or quotes in your `.env` file

### Database Issues

- The database (`app.db`) will be created automatically on first run
- If you see database errors, delete `app.db` and restart the server

## Next Steps

- The callback currently returns JSON. You may want to redirect to your frontend with the token
- Consider adding token refresh functionality
- Add proper error handling for production
- Set up HTTPS for production (Google requires HTTPS for OAuth in production)
