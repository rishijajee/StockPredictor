# Optional: FinBERT AI Sentiment Analysis

StockPredictor now supports **FinBERT**, a state-of-the-art financial sentiment analysis model that provides AI-driven insights to complement quantitative analysis.

## What is FinBERT?

FinBERT is a pre-trained NLP model specifically fine-tuned on 1.8 million financial news articles, earnings calls, and market commentary. It achieves ~97% accuracy on financial sentiment classification tasks - significantly better than general-purpose sentiment models.

## Current Status

- **Default Mode**: Rule-based analysis using quantitative scores (works without any setup)
- **Enhanced Mode**: FinBERT AI sentiment analysis (requires free Hugging Face API key)

## How to Enable FinBERT (Optional)

### Step 1: Get a Free Hugging Face API Key

1. Visit [Hugging Face](https://huggingface.co/join) and create a free account
2. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Click "New token" and create a token with "Read" permissions
4. Copy your API key

### Step 2: Set Environment Variable

#### On Vercel:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add a new variable:
   - **Key**: `HF_API_KEY`
   - **Value**: Your Hugging Face API token
   - **Environment**: Production, Preview, Development
4. Redeploy your application

#### Local Development:
```bash
# Linux/Mac
export HF_API_KEY="your_hugging_face_token_here"

# Windows
set HF_API_KEY=your_hugging_face_token_here
```

Or create a `.env` file:
```
HF_API_KEY=your_hugging_face_token_here
```

### Step 3: Verify

When FinBERT is enabled, stock analysis will include:
- AI sentiment classification (positive/negative/neutral)
- Confidence scores from the FinBERT model
- Enhanced natural language summaries

## Benefits of FinBERT

- **Financial-Specific**: Trained on financial text, understands market terminology
- **High Accuracy**: ~97% accuracy on sentiment classification
- **Complementary**: Combines AI sentiment with quantitative technical/fundamental analysis
- **Free**: Hugging Face Inference API free tier is sufficient for personal use

## Rate Limits

Hugging Face free tier includes:
- ~30,000 characters/month
- Sufficient for personal stock analysis
- Model may take 20-30 seconds to load on first request (cold start)

## Fallback Behavior

If FinBERT is unavailable (no API key, rate limit, or API down):
- System automatically falls back to rule-based analysis
- All functionality continues to work normally
- No errors or degraded user experience

## Privacy & Security

- API key is only used to authenticate with Hugging Face
- Stock tickers are sent to FinBERT for sentiment analysis
- No personal or financial data is transmitted
- All analysis is performed server-side

## Support

For issues with FinBERT integration, please check:
1. API key is correctly set in environment variables
2. Hugging Face account is active
3. No rate limiting on your account

The application works perfectly without FinBERT - it's an optional enhancement!
