# 🚂 Railway.app Deployment Guide - StockPredictor

## ✅ Why Railway is Perfect for Your Project

Railway.app is the **easiest** deployment platform for your StockPredictor AI application:

- ✅ **$5 free credit monthly** (enough for development + light production)
- ✅ **Zero code changes needed** - Your project is already configured
- ✅ **No timeout limits** - LLM calls can take as long as needed
- ✅ **No sleep/spin-down** - Always responsive
- ✅ **Simple GitHub integration** - Deploy in 5 minutes
- ✅ **Better than Render** for AI/ML workloads
- ✅ **No credit card required** for initial $5 credit

---

## 🎯 Your Project Status: 100% Ready

All required files are already configured:
- ✅ `Procfile` → `web: gunicorn app:app`
- ✅ `requirements.txt` → All dependencies listed
- ✅ `runtime.txt` → Python 3.11.5
- ✅ GitHub repository → https://github.com/rishijajee/StockPredictor.git

**No changes needed. Deploy as-is!**

---

## 🚀 5-Minute Deployment Process

### **Step 1: Sign Up for Railway (1 minute)**

1. **Go to:** https://railway.app
2. **Click:** "Login" or "Start a New Project"
3. **Sign in with GitHub** (recommended for easy repo access)
   - Click "Login with GitHub"
   - Authorize Railway to access your repositories
   - No credit card required initially

**Alternative:** You can also sign in with email, but GitHub integration is easier.

---

### **Step 2: Create New Project (30 seconds)**

1. After logging in, you'll see the Railway dashboard
2. **Click:** "New Project" button (big purple button)
3. You'll see several options:
   - Deploy from GitHub repo
   - Deploy from template
   - Empty project

4. **Select:** "Deploy from GitHub repo"

---

### **Step 3: Connect Your Repository (1 minute)**

1. Railway will show your GitHub repositories
2. **Search for:** "StockPredictor"
3. **Click:** "rishijajee/StockPredictor"

**If you don't see your repository:**
- Click "Configure GitHub App"
- Grant Railway access to the StockPredictor repository
- Return and refresh the list

---

### **Step 4: Configure Deployment Settings (1 minute)**

Railway will **automatically detect** your configuration from:
- `Procfile` (identifies it as a web service)
- `requirements.txt` (installs Python dependencies)
- `runtime.txt` (uses Python 3.11.5)

**You'll see a deployment starting automatically!**

Railway creates:
- A service named "StockPredictor" (or similar)
- Automatic builds from your `main` branch
- A generated URL like: `stockpredictor-production-XXXX.up.railway.app`

---

### **Step 5: Add Environment Variables (1 minute)**

**CRITICAL:** Your app needs the Hugging Face API key to work.

1. In your Railway project, click on the **service card** (shows your app name)
2. Click the **"Variables"** tab at the top
3. Click **"+ New Variable"**
4. Add these environment variables:

| Variable Name | Value |
|---------------|-------|
| `HF_API_KEY` | `your_huggingface_api_key_here` |
| `PYTHON_VERSION` | `3.11.5` |
| `PORT` | `8080` (Railway auto-assigns, but good to set) |

**Note:** Get your HF_API_KEY from https://huggingface.co/settings/tokens

5. **Click** each variable to save
6. Railway will **automatically redeploy** with the new variables

---

### **Step 6: Wait for Build to Complete (2-3 minutes)**

Watch the deployment logs in real-time:

1. Click the **"Deployments"** tab
2. Click on the latest deployment (should show "Building" or "Deploying")
3. You'll see live logs:

```
Installing dependencies from requirements.txt...
✓ Flask==3.0.0
✓ yfinance>=0.2.66
✓ pandas==2.1.3
✓ numpy==1.26.2
✓ huggingface-hub>=0.20.0
✓ gunicorn==21.2.0
Building...
Starting server with: gunicorn app:app
✓ Deployment successful!
```

**When you see "✓ Deployment successful!"** → Your app is live! 🎉

---

### **Step 7: Access Your Live Application (10 seconds)**

1. Click the **"Settings"** tab
2. Scroll to **"Domains"** section
3. You'll see a generated domain like:
   ```
   stockpredictor-production-a1b2.up.railway.app
   ```

4. **Click** the URL or copy it to your browser

**Your StockPredictor is now live!** 🚀

---

## 🧪 Test Your Deployment

### **Essential Tests:**

1. **Homepage:**
   ```
   https://your-app.up.railway.app/
   ```
   ✓ Should load the main dashboard

2. **StockScore Page:**
   ```
   https://your-app.up.railway.app/stockscore
   ```
   ✓ Should show the professional StockScore AI interface

3. **Search Functionality:**
   - Enter "AAPL" in the search box
   - Click "Generate Analysis"
   - Wait 30-60 seconds
   - ✓ Should show AI Consensus Analysis
   - ✓ Should show Alternative Investment Opportunities (if applicable)

4. **API Endpoint:**
   ```
   https://your-app.up.railway.app/api/top-stocks
   ```
   - This will take 3-5 minutes (analyzes 100+ stocks)
   - ✓ Should return JSON with short/mid/long term recommendations

---

## 💰 Understanding Railway Pricing

### **Free Trial Credit: $5**
When you sign up, you get **$5 in free credit** (no credit card required).

**What $5 Gets You:**
- **~1000 hours** of compute time (if app uses 5 MB RAM average)
- Enough for **1-2 months** of development + testing
- Or **several days** of production traffic

### **Usage Calculation:**
Railway charges based on **resource usage**:
- **Formula:** `Cost = RAM (GB) × Hours × $0.000463`

**Example for StockPredictor:**
- Average RAM usage: ~200 MB (0.2 GB)
- Running 24/7 for 1 month: 720 hours
- **Cost:** `0.2 GB × 720 hours × $0.000463 = ~$0.67/month`

**Your $5 credit lasts ~7.5 months at this rate!**

### **After Free Credit Runs Out:**
- Add a credit card to continue (pay-as-you-go)
- Railway charges only for what you use
- Typical cost: **$1-3/month** for light traffic
- **$5-10/month** for moderate production traffic

### **Monitor Usage:**
- Dashboard shows real-time usage
- Set up billing alerts
- Can add more credit anytime

---

## ⚙️ Railway Configuration Details

### **Auto-Detected Settings:**

Railway reads your files and automatically configures:

**From `Procfile`:**
```
web: gunicorn app:app
```
→ Railway knows to run this as a web service on port 8080

**From `requirements.txt`:**
```
Flask==3.0.0
yfinance>=0.2.66
pandas==2.1.3
numpy==1.26.2
...
```
→ Railway installs all dependencies during build

**From `runtime.txt`:**
```
python-3.11.5
```
→ Railway uses Python 3.11.5 runtime

**No railway.json or Dockerfile needed!**

---

## 🔧 Advanced Configuration (Optional)

### **Custom Domain (Optional):**

1. Go to **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Enter your domain: `stockpredictor.com`
4. Add CNAME record to your DNS:
   ```
   CNAME: your-app.up.railway.app
   ```
5. Railway provides free SSL certificates automatically

### **Increase Resources (If Needed):**

If you get memory errors:
1. Go to **Settings** → **Resources**
2. Increase memory limit (default is usually fine)
3. Railway charges based on usage

### **Set Up Health Checks:**

1. Go to **Settings** → **Health Check**
2. Set path: `/`
3. Interval: 60 seconds
4. Railway restarts if health check fails

### **Environment-Specific Variables:**

You can set different variables for production/staging:
1. Create multiple services from same repo
2. Use different branch for each (main, staging, dev)
3. Set different env variables per service

---

## 🔄 Continuous Deployment (Auto-Updates)

**Railway watches your GitHub repository!**

Every time you push to `main` branch:
1. Railway automatically detects the push
2. Triggers a new build
3. Runs tests (if configured)
4. Deploys the new version
5. Zero downtime deployment

**To update your app:**
```bash
# Make changes locally
git add .
git commit -m "Update stock analysis algorithm"
git push origin main

# Railway automatically deploys in 2-3 minutes!
```

---

## 📊 Monitoring & Logs

### **View Real-Time Logs:**

1. Click your service card
2. Click **"Deployments"** tab
3. Click active deployment
4. See live application logs:
   ```
   [INFO] Starting Flask app...
   [INFO] Analyzing stock: AAPL
   [INFO] Fetching data from yfinance
   [INFO] Calling Hugging Face API
   [INFO] Analysis complete
   ```

### **Monitor Resource Usage:**

1. Click **"Metrics"** tab (if available)
2. View CPU, Memory, Network usage
3. Identify performance bottlenecks

### **Deployment History:**

- See all past deployments
- Roll back to previous version if needed
- Compare deployment times

---

## 🐛 Troubleshooting Guide

### **Issue 1: Build Fails**

**Error:** `ERROR: Could not install packages...`

**Solution:**
```bash
# Test dependencies locally first
pip install -r requirements.txt

# If successful locally but fails on Railway:
# - Check Python version matches runtime.txt
# - Verify all packages are available on PyPI
```

### **Issue 2: Application Crashes on Startup**

**Error:** `Application failed to respond`

**Solution:**
1. Check **Logs** tab for Python errors
2. Common causes:
   - Missing environment variables (add HF_API_KEY)
   - Import errors (check requirements.txt)
   - Port binding issues (Railway uses PORT env var)

**Fix port binding in app.py:**
```python
# Add this to end of app.py if not present:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

### **Issue 3: 502 Bad Gateway**

**Causes:**
- App is still starting up (wait 30 seconds)
- App crashed during request
- Out of memory

**Solution:**
1. Check logs for crash messages
2. Look for memory errors
3. Test locally to reproduce error

### **Issue 4: Slow API Responses**

**Cause:** Free tier has limited resources

**Solution:**
- Expected for `/api/top-stocks` (analyzes 100+ stocks)
- Consider caching results
- Or upgrade Railway plan for more resources

### **Issue 5: "Out of Credit" Error**

**Cause:** Used up $5 free credit

**Solution:**
1. Go to **Account** → **Billing**
2. Add credit card
3. Add $5-10 credit
4. Set up billing alerts

---

## 🔐 Security Best Practices

### **1. Rotate API Keys:**

Your HF_API_KEY is currently in .env file. For production:

1. Generate new key at: https://huggingface.co/settings/tokens
2. Update in Railway Variables tab
3. Delete old key from Hugging Face

### **2. Use Railway's Secret Management:**

- ✅ Environment variables are encrypted
- ✅ Not visible in logs
- ✅ Not exposed in client-side code

### **3. Enable HTTPS (Free):**

Railway provides SSL certificates automatically ✓

### **4. Set Up Access Logs:**

Monitor who's accessing your app:
- Check Metrics tab regularly
- Set up alerts for unusual traffic
- Use Railway's built-in analytics

---

## 📈 Scaling Your Application

### **When You Need More Resources:**

**Signs you need to scale:**
- Slow response times (>5 seconds)
- Memory errors in logs
- High CPU usage (>80% sustained)
- Increased traffic (>1000 requests/day)

**Scaling Options:**

1. **Vertical Scaling (More Resources):**
   - Railway automatically allocates resources
   - Pay based on actual usage
   - No configuration needed

2. **Horizontal Scaling (Multiple Instances):**
   - Railway Pro plan allows multiple replicas
   - Load balancing handled automatically
   - Cost: $20/month + usage

3. **Add Caching Layer:**
   - Deploy Redis on Railway
   - Cache stock analysis results
   - Significantly faster repeated queries

---

## 🆚 Railway vs Render Comparison

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Setup Time** | 5 minutes | 5 minutes |
| **GitHub Integration** | ✅ Excellent | ✅ Excellent |
| **Auto-deploy** | ✅ Yes | ✅ Yes |
| **Timeout Limits** | ❌ None | ❌ None |
| **Spin-down** | ❌ No | ✅ Yes (free tier) |
| **Custom Domains** | ✅ Free | ✅ Free |
| **Pricing After Free** | Pay-as-you-go | $7/month minimum |
| **Best For** | Development + Small prod | Production apps |

**Railway Advantages:**
- More predictable costs (pay only what you use)
- No spin-down on free tier
- Simpler billing model

**Render Advantages:**
- Always-on service on paid plan
- More established platform
- Better for high-traffic production

---

## ✅ Post-Deployment Checklist

After successful deployment, verify:

- [ ] Application loads at Railway URL
- [ ] Homepage displays correctly
- [ ] StockScore page accessible
- [ ] Can search for stocks (test with AAPL, TSLA)
- [ ] AI Consensus Analysis generates properly
- [ ] Alternative Investment Opportunities display
- [ ] No errors in deployment logs
- [ ] Environment variables set correctly
- [ ] Mobile-responsive design works
- [ ] Share URL with test users
- [ ] Set up usage monitoring
- [ ] Add billing alerts (if applicable)

---

## 📞 Support & Resources

**Railway Documentation:**
- Getting Started: https://docs.railway.app/getting-started
- Python Deployment: https://docs.railway.app/guides/python
- Environment Variables: https://docs.railway.app/develop/variables
- Pricing: https://railway.app/pricing

**Railway Community:**
- Discord: https://discord.gg/railway
- Forum: https://help.railway.app
- Status Page: https://status.railway.app

**Your Project Resources:**
- GitHub: https://github.com/rishijajee/StockPredictor
- Local Guides: QUICKSTART.md, PROJECT_SUMMARY.md

---

## 🎉 You're Ready to Deploy!

Your StockPredictor application is **100% ready** for Railway deployment with zero code changes.

**Quick Start:**
1. Go to https://railway.app
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub"
4. Select StockPredictor
5. Add HF_API_KEY environment variable
6. Wait 3 minutes
7. Access your live app!

**Estimated time:** 5 minutes from start to live application 🚀

---

*Generated for StockPredictor v1.0 | Railway.app Deployment Guide | Last Updated: October 2025*
