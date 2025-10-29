# StockPredictor - AI-Powered Stock Analysis Platform

A comprehensive web application that provides AI-powered stock predictions and analysis using multiple data sources including technical indicators, market sentiment, economic factors, and geopolitical analysis.

## Features

- **Top 20 Stock Predictions**: View the best performing stocks for short, mid, and long-term investments
- **Stock Search**: Search and analyze any stock ticker with comprehensive insights
- **Multi-Factor Analysis**:
  - Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
  - Financial LLM-based analysis
  - Sector and industry performance
  - Market sentiment analysis
  - Interest rate impact assessment
  - Economic indicators (inflation, GDP, employment)
  - Geopolitical risk analysis
- **Real-Time Data**: Live market prices and predictions
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Multiple Timeframes**: Short (1-3 months), Mid (3-12 months), Long (1-3 years)

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Sources**: yfinance, financial APIs
- **Deployment**: Compatible with both Render and Vercel

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd StockPredictor
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Mac/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Deployment

### Deploy to Render

1. Create a new account on [Render](https://render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: StockPredictor
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts and your application will be deployed

Alternatively, you can deploy directly from GitHub:
1. Go to [Vercel](https://vercel.com/)
2. Import your GitHub repository
3. Vercel will automatically detect the configuration from `vercel.json`
4. Click "Deploy"

## Project Structure

```
StockPredictor/
├── app.py                    # Main Flask application
├── prediction_engine.py      # Stock prediction logic
├── analysis_engine.py        # Comprehensive analysis engine
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
├── vercel.json              # Vercel deployment config
├── wsgi.py                  # WSGI entry point
├── static/
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       └── app.js           # Frontend JavaScript
└── templates/
    └── index.html           # Main HTML template
```

## API Endpoints

- `GET /` - Main application interface
- `GET /api/top-stocks` - Get top 20 stocks for all timeframes
- `GET /api/search/<ticker>` - Get comprehensive analysis for a specific stock
- `GET /api/methodology` - Get analysis methodology description

## Analysis Methodology

The application uses a comprehensive multi-factor analysis approach:

1. **Technical Analysis**: Price patterns, moving averages, RSI, MACD, Bollinger Bands
2. **Financial LLM**: AI-powered analysis of market sentiment and news
3. **Sector Analysis**: Industry and sector performance comparison
4. **Market Analysis**: Overall market trends and correlations
5. **Interest Rates**: Federal Reserve policy and yield curve analysis
6. **Economic Calendar**: GDP, inflation, employment, consumer confidence
7. **Geopolitical**: Global events and trade policy impact

## Customization

### Adding More Stocks

Edit the `stock_universe` list in `prediction_engine.py`:

```python
self.stock_universe = [
    'AAPL', 'MSFT', 'GOOGL',  # Add your tickers here
    # ... more tickers
]
```

### Adjusting Prediction Algorithms

Modify the `calculate_prediction_score()` and `predict_price()` methods in `prediction_engine.py` to implement your own prediction logic.

### Styling

Edit `static/css/style.css` to customize the appearance.

## Performance Considerations

- Initial load may take 30-60 seconds as it analyzes 50+ stocks
- Stock search is faster as it analyzes only the requested ticker
- Consider implementing caching for production use
- Rate limiting may apply to free financial data APIs

## Limitations

- Uses free financial data sources which may have rate limits
- Predictions are based on historical data and should not be solely relied upon
- Some data sources may have delays
- LLM analysis is simulated (integrate with actual LLM APIs for production)

## Disclaimer

**This application is for educational and informational purposes only.**

The information provided does not constitute investment advice, financial advice, trading advice, or any other sort of advice. You should not treat any of the application's content as such. Do your own research and consult with financial advisors before making any investment decisions. Past performance does not guarantee future results.

## Future Enhancements

- [ ] Real-time data streaming with WebSockets
- [ ] User authentication and personalized watchlists
- [ ] Portfolio tracking and performance monitoring
- [ ] Email/SMS alerts for price targets
- [ ] Integration with actual financial LLM APIs (GPT-4, Claude, etc.)
- [ ] Machine learning models for enhanced predictions
- [ ] Historical accuracy tracking
- [ ] Social sentiment analysis from Twitter/Reddit
- [ ] Options analysis and recommendations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for stock market enthusiasts
