# 🚀 Render Deployment - Quick Reference Card

## Essential Information

**Repository:** https://github.com/rishijajee/StockPredictor.git
**Deployment Platform:** Render.com
**Status:** ✅ Ready to Deploy

---

## 🔑 Required Environment Variables

Copy these into Render's Environment Variables section:

```
HF_API_KEY=your_huggingface_api_key_here
PYTHON_VERSION=3.11.5
FLASK_ENV=production
```

**Note:** Replace `your_huggingface_api_key_here` with your actual Hugging Face API key from https://huggingface.co/settings/tokens

⚠️ **Security Note:** Consider regenerating HF_API_KEY at https://huggingface.co/settings/tokens for production use.

---

## ⚙️ Render Configuration Values

| Setting | Value |
|---------|-------|
| **Name** | `stockpredictor` (or your choice) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Branch** | `main` |
| **Instance Type** | Starter ($7/mo recommended) |

---

## 📝 5-Minute Deployment Steps

1. **Go to:** https://render.com
2. **Click:** "Get Started" or "Sign In"
3. **Sign in with:** GitHub (recommended)
4. **Click:** "New +" → "Web Service"
5. **Connect:** rishijajee/StockPredictor repository
6. **Configure:** Use values from table above
7. **Add:** Environment variables from section above
8. **Click:** "Create Web Service"
9. **Wait:** 2-5 minutes for build to complete
10. **Access:** Your live URL: `https://stockpredictor-XXXX.onrender.com`

---

## 🧪 Test Your Deployment

After deployment completes, test these:

```
✓ Homepage: https://your-app.onrender.com/
✓ StockScore: https://your-app.onrender.com/stockscore
✓ Search: Enter "AAPL" and click "Generate Analysis"
✓ Check: AI Consensus Analysis appears
✓ Verify: Alternative Investment Opportunities section
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Build fails** | Check logs tab, verify requirements.txt |
| **502 Error** | Check environment variables are set |
| **Slow response** | Expected on free tier (spins down) - upgrade to Starter |
| **Memory error** | Upgrade to Standard tier (2 GB RAM) |
| **No AI results** | Verify HF_API_KEY is correctly set |

---

## 🔄 Update Deployment

**Automatic:** Push to GitHub main branch
```bash
git add .
git commit -m "Your changes"
git push origin main
# Render auto-deploys in 2-3 minutes
```

**Manual:** Dashboard → "Manual Deploy" → "Deploy latest commit"

---

## 💰 Pricing Recommendation

- **Testing:** Free tier (spins down after 15 min)
- **Production:** Starter $7/mo (always on)
- **High traffic:** Standard $25/mo (2 GB RAM)

---

## 📞 Need Help?

- **Full Guide:** See RENDER_DEPLOYMENT_GUIDE.md
- **Render Docs:** https://render.com/docs/deploy-flask
- **Community:** https://community.render.com
- **Status:** https://status.render.com

---

*Ready to deploy? Go to https://render.com now! 🚀*
