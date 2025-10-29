# Quick Start Guide

Get StockPredictor up and running in minutes!

## Local Development (Easiest Way)

### Windows Users

1. Double-click `start.bat`
2. Wait for the server to start
3. Open your browser to `http://localhost:5000`

### Mac/Linux Users

1. Open terminal in the project directory
2. Run `./start.sh`
3. Open your browser to `http://localhost:5000`

## Manual Setup

If the automated scripts don't work, follow these steps:

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Open Browser
Navigate to: `http://localhost:5000`

## First Time Use

When you first load the application:

1. **Wait for Initial Load**: The first load takes 30-60 seconds as it analyzes 50+ stocks
2. **Browse Top Stocks**: View the top 20 predictions in three tabs (Short/Mid/Long term)
3. **Search Stocks**: Type any ticker (e.g., AAPL, MSFT, TSLA) in the search box
4. **Read Analysis**: Scroll down to see the comprehensive methodology

## Deployment to Cloud

### Option 1: Render (Recommended for Python apps)

1. Sign up at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy!

### Option 2: Vercel (Fast and Free)

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel`
4. Follow the prompts

## Troubleshooting

### "Python not found"
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### "pip not found"
- Python 3.4+ includes pip by default
- If missing, run: `python -m ensurepip --upgrade`

### "Port 5000 already in use"
- Change the port in `app.py`:
  ```python
  port = int(os.environ.get('PORT', 8080))  # Changed from 5000
  ```

### Dependencies installation fails
- Upgrade pip: `pip install --upgrade pip`
- Try installing individually: `pip install Flask yfinance pandas`

### Application is slow
- First load is always slower (analyzing many stocks)
- Subsequent searches are faster
- Consider reducing the `stock_universe` list in `prediction_engine.py`

## What to Try First

1. **Search for a popular stock**: Try `AAPL`, `TSLA`, or `MSFT`
2. **Check the predictions**: Look at the three timeframe predictions
3. **Read the AI analysis**: See the comprehensive market context
4. **Browse Top 20**: Switch between Short/Mid/Long term tabs

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review the code comments in the Python files
- Open an issue on GitHub

---

Happy stock analyzing! 📈
