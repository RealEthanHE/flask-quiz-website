# 🚀 Render Deployment Guide

## Quick Deploy Steps

### 1. Go to Render Dashboard
- Visit https://render.com
- Sign in and click "New +" → "Web Service"

### 2. Connect Repository
- Connect your GitHub repository
- Select the main branch with your latest commits

### 3. Verify Auto-Configuration
Your `render.yaml` should auto-configure:
```yaml
name: flask-quiz-website
type: web
env: python
buildCommand: pip install -r requirements.txt
startCommand: python main_new.py
```

### 4. Environment Variables (Auto-set)
```
DATABASE_URL: [Links to your PostgreSQL database]
SECRET_KEY: [Auto-generated]
FLASK_DEBUG: false
PORT: 10000
```

### 5. Deploy & Monitor
- Click "Create Web Service"
- Watch build logs for success
- Your app will be live at: `https://your-app-name.onrender.com`

## 🧪 Test After Deployment

Run this command with your live URL:
```bash
python deployment_test.py https://your-app-name.onrender.com
```

## ✅ Expected Build Output
```
==> Installing dependencies
Installing collected packages: psycopg2-binary, Flask, gunicorn...
==> Starting service
* Running on all addresses (0.0.0.0)
* Running on http://0.0.0.0:10000
Your service is live 🎉
```

## 🔧 If Build Fails
1. Check build logs for errors
2. Verify all files are committed to git
3. Ensure PostgreSQL database is running
4. Check that DATABASE_URL is properly set

## 📱 What Happens After Deploy
- Users can register accounts
- Login system works with PostgreSQL
- All 343 quiz questions are available
- Scores are tracked in the database
- App is production-ready!

**Your Flask Quiz App with 343 Questions is Ready to Go Live! 🎉**
