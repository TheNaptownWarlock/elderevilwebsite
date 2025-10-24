# Streamlit Cloud Deployment Guide

## Prerequisites
1. Install Git: https://git-scm.com/download/win
2. GitHub account: https://github.com

## Deployment Steps

### 1. Initialize Git Repository
```bash
cd C:\Users\bbusald\elderevilwebsite
git init
git add .
git commit -m "Initial commit - Fantasy Calendar RSVP app"
```

### 2. Create GitHub Repository
- Go to https://github.com/new
- Repository name: `elderevilwebsite`
- Make it PUBLIC (required for free Streamlit Cloud)
- Don't initialize with README (you already have files)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YourUsername/elderevilwebsite.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect GitHub account
4. Select repository: `elderevilwebsite`
5. Main file path: `app.py`
6. Click "Deploy!"

### 5. Set Up Email Configuration
1. In your deployed app, click ⚙️ Settings
2. Go to "Secrets" tab
3. Add the secrets from secrets_template.toml
4. Save and restart app

### 6. Update Website iframe
Update fantasy-calendar.html to use deployed URL:
```html
<iframe src="https://your-app-name.streamlit.app" 
        width="100%" height="800px">
</iframe>
```

## What You Get FREE:
✅ Unlimited public apps
✅ Real-time sharing with all users worldwide
✅ Automatic HTTPS
✅ Custom domain support
✅ 1GB RAM per app
✅ Community support

## Database Options:
- **SQLite**: Works but resets on app restart
- **PostgreSQL**: Persistent, recommended for production
  - Free options: Supabase, Railway, Render
  - Upgrade instructions in cloud_database.py