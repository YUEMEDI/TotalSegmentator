# �� Google OAuth Quick Setup Reference

## 🚨 **URGENT: Fix the invalid_client Error**

Your current error is because you still have placeholder values in the code. Follow these steps:

### **Step 1: Get Your Google Credentials**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with: **yuemedical@gmail.com**
3. Create/select project: **YueTransfer-Medical**
4. Go to: **APIs & Services** → **Credentials**
5. Create OAuth 2.0 Client ID:
   - **Type**: Web application
   - **Name**: YueTransfer Web Client
   - **Authorized JavaScript origins**:
     ```
     http://localhost:5000
     http://127.0.0.1:5000
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:5000/login/google/authorized
     http://127.0.0.1:5000/login/google/authorized
     ```

### **Step 2: Copy Your Credentials**
After creation, you'll get:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

### **Step 3: Update Your Code**
Open `start_server_step3_google_fixed.py` and replace lines 15-17:

```python
# Replace these placeholder values:
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET_HERE"

# With your actual values:
GOOGLE_CLIENT_ID = "123456789-abcdefghijklmnop.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz"
```

### **Step 4: Test**
1. Save the file
2. Run: `start_google_oauth_fixed.bat`
3. Go to: http://localhost:5000
4. Click "Sign in with Google"

## ✅ **What Should Work After Fix**
- Google login button should redirect to Google
- After Google login, you should return to YueTransfer
- Your Google account should be automatically created in the system

## 🆘 **If Still Getting Errors**
1. Double-check Client ID/Secret are copied exactly
2. Verify redirect URIs in Google Console match exactly
3. Make sure you're using the correct Google account
4. Check that OAuth consent screen has your email as test user 