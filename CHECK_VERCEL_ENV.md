# How to Verify HF_API_KEY is Set on Vercel

## Check in Vercel Dashboard:

1. Go to: https://vercel.com/dashboard
2. Click your StockPredictor project
3. Go to: Settings → Environment Variables
4. Look for: HF_API_KEY

You should see:
```
HF_API_KEY = hf_************************ (hidden)
Environments: Production, Preview, Development
```

## After Setting/Updating:

Always redeploy after changing environment variables:
- Go to: Deployments tab
- Click: ••• (three dots) on latest deployment
- Click: "Redeploy"

OR just push a new commit:
```bash
git push
```

## Testing After Deployment:

Visit your deployed app and test StockScore:
- https://your-app.vercel.app/stockscore
- Enter ticker: AAPL
- Click: "Analyze with AI"

With HF_API_KEY set, you should see:
- Real sentiment (positive/negative/neutral)
- Confidence scores (70-95%)
- Specific price predictions
- Detailed AI analysis summaries

Without HF_API_KEY, you'll see:
- Always neutral sentiment
- Always 50% confidence
- Generic "moderate stability" messages
