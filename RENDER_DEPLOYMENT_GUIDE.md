# 🚀 Render Deployment Guide - StockPredictor

## ✅ Pre-Deployment Checklist

Your project is **ready for deployment**! All required files are in place:
- ✓ `Procfile` - Web server configuration
- ✓ `requirements.txt` - Python dependencies
- ✓ `runtime.txt` - Python version specification
- ✓ `app.py` - Flask application
- ✓ `.gitignore` - Properly configured
- ✓ GitHub repository - https://github.com/rishijajee/StockPredictor.git

---

## 📋 Step-by-Step Deployment Process

### Step 1: Sign Up / Log In to Render

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign In"**
3. Choose one of these options:
   - Sign up with GitHub (recommended - easiest integration)
   - Sign up with GitLab
   - Sign up with Email

**Recommendation:** Use GitHub sign-in for seamless repository access.

---

### Step 2: Create New Web Service

1. Once logged in, click **"New +"** button (top right)
2. Select **"Web Service"**
3. You'll see options to connect a repository

---

### Step 3: Connect Your GitHub Repository

**Option A: If you signed up with GitHub:**
1. Click **"Connect account"** if not already connected
2. Authorize Render to access your GitHub repositories
3. Select **"rishijajee/StockPredictor"** from the list

**Option B: If you signed up with email:**
1. Click **"Connect GitHub"**
2. Authorize Render
3. Select **"rishijajee/StockPredictor"**

**Option C: Use Public Repository URL:**
1. Click **"Public Git repository"**
2. Enter: `https://github.com/rishijajee/StockPredictor.git`
3. Click **"Continue"**

---

### Step 4: Configure Your Web Service

Render will auto-detect most settings. Verify/configure these fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `stockpredictor` | Choose any name (will be part of URL) |
| **Region** | `Oregon (US West)` | Choose closest to your users |
| **Branch** | `main` | Should auto-detect |
| **Runtime** | `Python 3` | Auto-detected from runtime.txt |
| **Build Command** | `pip install -r requirements.txt` | Auto-detected |
| **Start Command** | `gunicorn app:app` | Auto-detected from Procfile |
| **Instance Type** | `Free` or `Starter` | See pricing below |

---

### Step 5: Add Environment Variables

**Critical Step:** Your app needs the Hugging Face API key to work.

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add the following:

| Key | Value |
|-----|-------|
| `HF_API_KEY` | `your_huggingface_api_key_here` |
| `PYTHON_VERSION` | `3.11.5` |
| `FLASK_ENV` | `production` |

**Security Note:** Replace `your_huggingface_api_key_here` with your actual Hugging Face API key from https://huggingface.co/settings/tokens

---

### Step 6: Choose Instance Type

**Free Tier:**
- **Cost:** $0/month
- **RAM:** 512 MB
- **Features:** Spins down after 15 min inactivity, 750 hours/month
- **Best for:** Testing and development
- ⚠️ **Warning:** May run out of memory for large stock analysis

**Starter Tier (Recommended):**
- **Cost:** $7/month
- **RAM:** 512 MB
- **Features:** Always on, no spin down, unlimited hours
- **Best for:** Production use with moderate traffic

**Standard Tier (If needed):**
- **Cost:** $25/month
- **RAM:** 2 GB
- **Features:** Better for ML workloads
- **Best for:** High traffic or heavy processing

**Recommendation:** Start with **Starter** tier for reliable production performance.

---

### Step 7: Deploy!

1. Click **"Create Web Service"** button at the bottom
2. Render will start building your application
3. Watch the deployment logs in real-time

**Build Process (takes 2-5 minutes):**
```
==> Cloning from https://github.com/rishijajee/StockPredictor...
==> Using Python version 3.11.5
==> Installing dependencies...
==> Starting server with gunicorn...
==> Your service is live 🎉
```

---

## 🌐 Access Your Deployed Application

Once deployment completes, you'll get a URL:

**Format:** `https://stockpredictor-XXXX.onrender.com`

Example: `https://stockpredictor-a1b2.onrender.com`

**Test these endpoints:**
- Homepage: `https://your-app.onrender.com/`
- StockScore: `https://your-app.onrender.com/stockscore`
- API: `https://your-app.onrender.com/api/top-stocks`

---

## 🔧 Post-Deployment Configuration

### Enable Custom Domain (Optional)

1. Go to your service dashboard
2. Click **"Settings"** tab
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain (e.g., `stockpredictor.com`)
6. Follow DNS configuration instructions

### Monitor Your Application

**View Logs:**
1. Go to service dashboard
2. Click **"Logs"** tab
3. See real-time application logs

**Monitor Metrics:**
1. Click **"Metrics"** tab
2. View CPU, memory, bandwidth usage

**Set Up Alerts:**
1. Click **"Settings"**
2. Scroll to **"Health Check Path"**
3. Enter: `/` (monitors homepage availability)

---

## 🐛 Troubleshooting Common Issues

### Issue 1: Build Fails - Dependency Error

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Locally test dependencies
pip install -r requirements.txt
```

### Issue 2: Application Won't Start

**Error:** `Error: bind: address already in use`

**Solution:** Check your Procfile uses `gunicorn app:app` (no port specification needed)

### Issue 3: 502 Bad Gateway

**Causes:**
- App crashed during startup
- Out of memory
- Build completed but start command failed

**Solution:**
1. Check **Logs** tab for error messages
2. Look for Python errors or import failures
3. Verify environment variables are set correctly

### Issue 4: Slow First Request (Free Tier)

**Cause:** Free tier spins down after 15 min inactivity

**Solution:** Upgrade to Starter tier ($7/mo) for always-on service

### Issue 5: Memory Errors

**Error:** `MemoryError` or `Killed` in logs

**Solution:**
- Upgrade to Standard tier (2 GB RAM)
- Or optimize code to use less memory

---

## 🔄 Updating Your Deployment

**Automatic Deploys:**
Render watches your GitHub repository. Any push to `main` branch triggers automatic redeployment.

```bash
# Make changes locally
git add .
git commit -m "Update stock analysis algorithm"
git push origin main

# Render automatically deploys within 2-3 minutes
```

**Manual Deploy:**
1. Go to service dashboard
2. Click **"Manual Deploy"** dropdown (top right)
3. Select **"Deploy latest commit"**

---

## 📊 Performance Optimization Tips

### 1. Enable Caching
Add Redis for faster repeated queries:
- Add Redis instance on Render
- Update code to cache stock data

### 2. Background Jobs
For `/api/top-stocks` endpoint (long-running):
- Consider using Render Background Workers
- Pre-compute daily and cache results

### 3. Database for Results
Add PostgreSQL to store analysis results:
- Faster repeated lookups
- Historical data tracking

---

## 💰 Cost Estimation

| Usage Pattern | Recommended Plan | Monthly Cost |
|---------------|------------------|--------------|
| Personal/Testing | Free | $0 |
| Small production | Starter (512 MB) | $7 |
| Medium traffic | Standard (2 GB) | $25 |
| High traffic + DB | Standard + Redis + PostgreSQL | $50-75 |

---

## 🔐 Security Best Practices

### 1. Rotate API Keys
Your current HF_API_KEY is exposed in .env file:
```bash
# Generate new key at https://huggingface.co/settings/tokens
# Update in Render environment variables
```

### 2. Enable HTTPS
✅ Render provides free SSL certificates automatically

### 3. Set Up CORS Properly
Your app already has Flask-CORS configured ✓

### 4. Environment Variables
✅ Never commit .env to git (already in .gitignore)

---

## 📞 Support & Resources

**Render Documentation:**
- Deploying Python apps: https://render.com/docs/deploy-flask
- Environment variables: https://render.com/docs/environment-variables
- Monitoring: https://render.com/docs/monitoring

**Your Project Docs:**
- README.md - Project overview
- QUICKSTART.md - Local development setup
- PROJECT_SUMMARY.md - Technical architecture

**Get Help:**
- Render Community: https://community.render.com
- Render Status: https://status.render.com

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] Service deployed successfully
- [ ] Environment variables configured (HF_API_KEY)
- [ ] Homepage loads without errors
- [ ] StockScore page loads correctly
- [ ] Can search for stocks (try AAPL, TSLA)
- [ ] AI Consensus Analysis generates results
- [ ] Alternative Investment Opportunities display
- [ ] Check logs for any errors
- [ ] Test on mobile device
- [ ] Set up health check monitoring
- [ ] Configure custom domain (optional)
- [ ] Enable automatic deploys from GitHub
- [ ] Share URL with test users

---

## 🎉 You're Ready to Deploy!

Your StockPredictor application is fully configured for Render deployment. Simply follow Steps 1-7 above and you'll have a live production application in under 10 minutes.

**Quick Start:** Go to https://render.com and click "Get Started" now!

---

*Generated for StockPredictor v1.0 | Last Updated: October 2025*
