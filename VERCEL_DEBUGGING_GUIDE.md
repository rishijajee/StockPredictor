# Debugging StockScore on Vercel

## Issue: Static Values & "Analysis Unavailable" Messages

This guide will help you debug why the LLM analysis isn't working on Vercel.

---

## Step 1: Check Vercel Logs

Logs will show exactly what's happening with the API calls.

### How to View Logs:

1. Go to: https://vercel.com/dashboard
2. Click your **StockPredictor** project
3. Click **"Deployments"** tab
4. Click your **latest deployment**
5. Click **"Functions"** tab
6. Click **"Real-time Logs"** or scroll down to see logs

### What to Look For:

```
✅ GOOD - API Key Found:
FinGPT: API key found (length: 37)
FinGPT: Calling Hugging Face API for AAPL...
FinGPT: API Response Status: 200
FinGPT: API Success! Result: [{'label': 'positive', 'score': 0.85}]

❌ BAD - No API Key:
FinGPT: No API key found for AAPL

❌ BAD - Model Loading (First Request):
FinGPT: API Response Status: 503
FinGPT: Model is loading (503). This can take 20-30 seconds on first request.

❌ BAD - API Error:
FinGPT: API Response Status: 401
FinGPT: API Error Response: {"error": "Invalid token"}
```

---

## Step 2: Verify HF_API_KEY is Set Correctly

1. Go to: https://vercel.com/dashboard → Your Project → **Settings** → **Environment Variables**

2. Verify you see:
   ```
   Name: HF_API_KEY
   Value: hf_************************ (hidden)
   Environments: ✓ Production  ✓ Preview  ✓ Development
   ```

3. **Common Issues:**
   - Variable name is wrong (should be exactly `HF_API_KEY`)
   - Not applied to Production environment
   - Token is invalid or expired

---

## Step 3: Test Your HF_API_KEY Manually

Test if your Hugging Face token works:

```bash
# Replace YOUR_TOKEN with your actual token
curl https://api-inference.huggingface.co/models/ProsusAI/finbert \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Apple stock shows strong growth potential."}'
```

**Expected Response (Success):**
```json
[[
  {"label": "positive", "score": 0.85},
  {"label": "neutral", "score": 0.10},
  {"label": "negative", "score": 0.05}
]]
```

**Error Responses:**
- `{"error": "Invalid token"}` → Token is wrong
- `{"error": "Model loading"}` → Wait 20-30 seconds and try again
- `401 Unauthorized` → Check token permissions

---

## Step 4: Common Issues & Solutions

### Issue 1: "Analysis unavailable" for all stocks
**Cause:** No API key or API key not being read  
**Solution:**
1. Double-check environment variable name: `HF_API_KEY`
2. Redeploy after setting variable
3. Check logs for "No API key found"

### Issue 2: "Model loading - try again in 30 seconds"
**Cause:** First request to Hugging Face model (cold start)  
**Solution:**
- Wait 30 seconds
- Try the same stock again
- Subsequent requests will be faster (2-5 seconds)

### Issue 3: Static neutral values for everything
**Cause:** Fallback mode is activating (no real AI calls happening)  
**Solution:**
1. Check Vercel logs to see why API calls fail
2. Verify HF_API_KEY is valid
3. Test token manually (Step 3 above)

### Issue 4: Works for some stocks but not others
**Cause:** Rate limiting or timeout  
**Solution:**
- Free Hugging Face tier has rate limits
- Wait a few seconds between requests
- Consider upgrading to Hugging Face Pro ($9/month for higher limits)

---

## Step 5: Deploy Latest Changes

The latest code has improved logging. Deploy it:

```bash
git push
```

Then:
1. Wait for deployment to complete (~2 minutes)
2. Test StockScore page: https://your-app.vercel.app/stockscore
3. Try analyzing AAPL
4. Check Vercel logs immediately after

---

## Step 6: Quick Test Checklist

After deploying:

- [ ] Visit Vercel logs in real-time mode
- [ ] Go to your StockScore page
- [ ] Enter ticker: AAPL
- [ ] Click "Analyze with AI"
- [ ] Watch logs for:
  - "API key found (length: XX)"
  - "API Response Status: XXX"
  - Success or error messages

---

## Expected Behavior

**First Request (Cold Start):**
- Takes 20-30 seconds
- May show "Model loading" message
- Try again after 30 seconds

**Subsequent Requests:**
- Takes 2-5 seconds
- Returns real sentiment (positive/negative/neutral)
- Confidence scores vary (60-95%)
- Specific price predictions

**With Real API:**
- AAPL might show: Positive, 82% confidence, "Expected to rise 3-7%"
- TSLA might show: Neutral, 65% confidence, "Expected to remain stable"
- Different stocks = different results

**Without API (Fallback):**
- ALL stocks show: Neutral, 50% confidence, same message

---

## Need More Help?

Share your Vercel logs showing:
1. The line with "API key found" or "No API key found"
2. The line with "API Response Status: XXX"
3. Any error messages

This will help identify the exact issue!
