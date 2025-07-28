# 🔐 Google OAuth Setup Guide for YueTransfer

## 📋 **Prerequisites**
- Google account (yuemedical@gmail.com)
- Access to Google Cloud Console

## 🚀 **Step-by-Step Setup**

### **Step 1: Access Google Cloud Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account: **yuemedical@gmail.com**
3. If you don't have a project, create one:
   - Click "Select a project" → "New Project"
   - **Project name**: `YueTransfer-Medical`
   - Click "Create"

### **Step 2: Enable Required APIs**
1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. Search for and enable these APIs:
   - **"Google+ API"** (or "Google Identity and Access Management (IAM) API")
   - **"Google Identity"**
   - **"Google OAuth2 API"**

### **Step 3: Configure OAuth Consent Screen**
1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. **User Type**: Select **"External"** (for development)
3. Fill in the required information:
   - **App name**: `YueTransfer Medical Imaging Platform`
   - **User support email**: `yuemedical@gmail.com`
   - **Developer contact information**: `yuemedical@gmail.com`
4. Click **"Save and Continue"**
5. **Scopes**: Add these scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
6. Click **"Save and Continue"**
7. **Test users**: Add these emails:
   - `yuemedical@gmail.com`
   - Any other test emails you want to use
8. Click **"Save and Continue"**

### **Step 4: Create OAuth 2.0 Credentials**
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. **Application type**: Select **"Web application"**
5. **Name**: `YueTransfer Web Client`
6. **Authorized JavaScript origins**:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
7. **Authorized redirect URIs**:
   ```
   http://localhost:5000/login/google/authorized
   http://127.0.0.1:5000/login/google/authorized
   ```
8. Click **"Create"**

### **Step 5: Get Your Credentials**
After creation, you'll see:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

**⚠️ IMPORTANT**: Copy these values - you'll need them for the next step!

### **Step 6: Update YueTransfer Configuration**
1. Open `start_server_step3_google.py`
2. Find these lines (around line 15-17):
   ```python
   GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"
   GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET_HERE"
   ```
3. Replace with your actual credentials:
   ```python
   GOOGLE_CLIENT_ID = "123456789-abcdefghijklmnop.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz"
   ```

### **Step 7: Install Required Dependencies**
```bash
pip install requests
```

### **Step 8: Test the Implementation**
1. Run the server:
   ```bash
   python start_server_step3_google.py
   ```
2. Open browser: http://localhost:5000
3. Click "Sign in with Google"
4. You should be redirected to Google's login page
5. After successful login, you'll be redirected back to YueTransfer

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"redirect_uri_mismatch" error**
   - Make sure the redirect URI in Google Console exactly matches: `http://localhost:5000/login/google/authorized`
   - Check for extra spaces or typos

2. **"invalid_client" error**
   - Verify your Client ID and Client Secret are correct
   - Make sure you copied the entire values

3. **"access_denied" error**
   - Add your email to the test users list in OAuth consent screen
   - Make sure you're using an external user type

4. **"scope" error**
   - Ensure you've added the required scopes: `email` and `profile`

### **Security Notes:**
- Never commit your Client Secret to version control
- Use environment variables in production
- Regularly rotate your credentials
- Monitor your OAuth usage in Google Cloud Console

## 🎯 **Production Deployment**

For production deployment, you'll need to:
1. Change redirect URIs to your production domain
2. Set up proper SSL certificates
3. Use environment variables for credentials
4. Configure proper session management
5. Set up user database persistence

## 📞 **Support**

If you encounter issues:
1. Check Google Cloud Console logs
2. Verify all configuration steps
3. Test with a simple OAuth flow first
4. Contact: yuemedical@gmail.com

---

**🎉 Congratulations!** You now have Google OAuth integrated with YueTransfer! 