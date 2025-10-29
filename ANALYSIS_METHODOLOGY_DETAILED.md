# StockPredictor - Comprehensive Analysis Methodology

## Table of Contents
1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [LLM Integration](#llm-integration)
4. [Technical Analysis](#technical-analysis)
5. [Fundamental Analysis](#fundamental-analysis)
6. [Market Analysis](#market-analysis)
7. [Sector & Industry Analysis](#sector--industry-analysis)
8. [Interest Rate Analysis](#interest-rate-analysis)
9. [Economic Indicators](#economic-indicators)
10. [Geopolitical Analysis](#geopolitical-analysis)
11. [Prediction Algorithms](#prediction-algorithms)
12. [Scoring System](#scoring-system)

---

## Overview

StockPredictor uses a **multi-factor quantitative analysis** approach combining 7 major analytical dimensions to predict stock performance across three timeframes (short: 1-3 months, mid: 3-12 months, long: 1-3 years).

---

## Data Sources

### Primary Data Source: Yahoo Finance (yfinance)
**Library**: `yfinance` v0.2.32
**Type**: Free, Open-Source Python Library
**Documentation**: https://pypi.org/project/yfinance/

#### What We Get from yfinance:
1. **Historical Price Data**
   - Daily OHLCV (Open, High, Low, Close, Volume)
   - Up to 10+ years of historical data
   - Real-time and delayed quotes

2. **Company Information**
   - Company name (`longName`)
   - Sector classification
   - Industry classification
   - Market cap
   - Forward P/E ratio (`forwardPE`)
   - Profit margins (`profitMargins`)
   - Return on Equity (`returnOnEquity`)

3. **Market Indices**
   - SPY (S&P 500 ETF) - Overall market sentiment
   - ^TNX (10-Year Treasury Yield) - Interest rate proxy

4. **Sector ETFs** for sector performance tracking:
   - XLK - Technology
   - XLV - Healthcare
   - XLF - Financials
   - XLE - Energy
   - XLY - Consumer Discretionary
   - XLP - Consumer Staples
   - XLI - Industrials
   - XLB - Materials
   - XLRE - Real Estate
   - XLU - Utilities
   - XLC - Communication Services

**API Limitations**:
- Free tier (no API key required)
- Rate limiting may apply during heavy usage
- Data is typically delayed 15-20 minutes during market hours
- Historical data is end-of-day

**Code Location**: `prediction_engine.py` lines 22-31, `get_stock_data()` method

---

## LLM Integration

### Current Status: **SIMULATED LLM ANALYSIS**

⚠️ **IMPORTANT**: The current version uses **simulated AI analysis** based on rule-based logic, NOT actual LLM API calls.

### How It Works:
The `generate_llm_analysis()` function (in `analysis_engine.py`, lines 145-185) creates natural language summaries using:

1. **Score-Based Outlook Classification**:
   - Score ≥ 70: "Strong Buy"
   - Score ≥ 60: "Buy"
   - Score ≥ 50: "Hold"
   - Score ≥ 40: "Cautious"
   - Score < 40: "Avoid"

2. **Template-Based Summaries**:
   - Combines prediction score, reasoning factors, and sector analysis
   - Uses string concatenation to create human-readable text
   - Confidence levels based on score extremes

### Ready for Real LLM Integration:

The architecture is designed to easily integrate with real LLMs. To add actual AI analysis, replace the `generate_llm_analysis()` function with API calls to:

#### Option 1: OpenAI GPT-4
```python
import openai
openai.api_key = "your-api-key"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "system", "content": "You are a financial analyst..."}]
)
```

#### Option 2: Anthropic Claude
```python
import anthropic
client = anthropic.Client(api_key="your-api-key")
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": f"Analyze {ticker}..."}]
)
```

#### Option 3: Hugging Face (Free Options)
```python
from transformers import pipeline
classifier = pipeline("text-classification", model="ProsusAI/finbert")
sentiment = classifier(news_text)
```

**Free LLM Options for Integration**:
1. **FinBERT** (Hugging Face) - Financial sentiment analysis
2. **BloombergGPT** (if available) - Financial domain model
3. **Llama 2** (via Hugging Face) - Open-source general purpose
4. **GPT-J** or **GPT-Neo** - Free alternatives to GPT-3/4

**Code Location**: `analysis_engine.py` lines 145-185

---

## Technical Analysis

### Indicators Calculated:

#### 1. Simple Moving Averages (SMA)
- **SMA 20**: 20-day average (short-term trend)
- **SMA 50**: 50-day average (medium-term trend)
- **SMA 200**: 200-day average (long-term trend)

**Purpose**: Identify trend direction and support/resistance levels

**Formula**:
```
SMA = (Sum of closing prices over N days) / N
```

#### 2. Exponential Moving Averages (EMA)
- **EMA 12**: Fast EMA
- **EMA 26**: Slow EMA

**Purpose**: More responsive to recent price changes

**Formula**:
```
EMA = (Close - EMA_prev) × (2 / (N + 1)) + EMA_prev
```

#### 3. Relative Strength Index (RSI)
- **Period**: 14 days
- **Range**: 0 to 100

**Interpretation**:
- RSI > 70: Overbought (potential sell signal)
- RSI < 30: Oversold (potential buy signal)
- 30-70: Neutral zone

**Formula**:
```
RS = Average Gain / Average Loss
RSI = 100 - (100 / (1 + RS))
```

#### 4. MACD (Moving Average Convergence Divergence)
- **MACD Line**: EMA(12) - EMA(26)
- **Signal Line**: 9-day EMA of MACD

**Signals**:
- MACD crosses above Signal: Bullish
- MACD crosses below Signal: Bearish

#### 5. Bollinger Bands
- **Middle Band**: 20-day SMA
- **Upper Band**: Middle + (2 × Standard Deviation)
- **Lower Band**: Middle - (2 × Standard Deviation)

**Purpose**: Measure volatility and identify overbought/oversold conditions

#### 6. Volume Analysis
- **Volume SMA**: 20-day average volume
- **Comparison**: Current volume vs average volume

**Significance**: High volume confirms price movements

**Code Location**: `prediction_engine.py` lines 33-67, `calculate_technical_indicators()`

---

## Fundamental Analysis

### Metrics Evaluated:

#### 1. Forward P/E Ratio
**Source**: yfinance `info['forwardPE']`

**Scoring**:
- 10-25: +10 points (reasonable valuation)
- < 10: +5 points (undervalued)
- > 25: 0 points (potentially overvalued)

#### 2. Profit Margins
**Source**: yfinance `info['profitMargins']`

**Scoring**:
- > 15%: +5 points (strong profitability)

#### 3. Return on Equity (ROE)
**Source**: yfinance `info['returnOnEquity']`

**Scoring**:
- > 15%: +5 points (efficient use of equity)

**Total Fundamental Points**: 20 out of 100

**Code Location**: `prediction_engine.py` lines 112-133

---

## Market Analysis

### Overall Market Sentiment

**Data Source**: SPY (S&P 500 ETF) via yfinance

**Calculation**:
1. Get SPY price from 1 month ago
2. Calculate percentage change
3. Classify sentiment:
   - Change > +3%: Bullish
   - Change < -3%: Bearish
   - -3% to +3%: Neutral

**Impact on Stock Analysis**:
- Bullish market: Positive for growth stocks
- Bearish market: Favor defensive stocks
- Neutral: Stock-specific factors dominate

**Code Location**: `analysis_engine.py` lines 11-29

---

## Sector & Industry Analysis

### Methodology:

#### Sector Performance Tracking
**Data Source**: Sector ETFs (SPDR Select Sector ETFs)

**Process**:
1. Identify stock's sector from yfinance data
2. Get corresponding sector ETF (e.g., XLK for Technology)
3. Calculate 3-month performance
4. Compare to overall market (SPY)

**Classification**:
- > +5% change: Outperforming
- < -5% change: Underperforming
- -5% to +5%: In-line

**Sector ETF Mapping**:
```python
{
    'Technology': 'XLK',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Energy': 'XLE',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Utilities': 'XLU',
    'Communication Services': 'XLC'
}
```

**Impact**:
- Stocks in outperforming sectors get positive bias
- Stocks in underperforming sectors get negative bias

**Code Location**: `analysis_engine.py` lines 31-56

---

## Interest Rate Analysis

### Data Source: 10-Year Treasury Yield (^TNX)

**Access**: Via yfinance

**Analysis**:
1. Current yield level
2. 3-month trend (rising or falling)

**Impact on Stocks**:

**High Rates (>4.5%)**:
- Negative for: Growth stocks, tech, unprofitable companies
- Positive for: Financials (banks), value stocks

**Low Rates (<3.5%)**:
- Positive for: Growth stocks, tech, real estate
- Negative for: Banks (lower net interest margins)

**Moderate Rates (3.5-4.5%)**:
- Neutral environment
- Stock-specific factors dominate

**Code Location**: `analysis_engine.py` lines 58-80

---

## Economic Indicators

### Current Implementation: Contextual Framework

⚠️ **Note**: The current version provides **contextual interpretation** rather than real-time economic data API integration.

### Indicators Considered:

#### 1. Inflation (CPI/PPI)
**Status Assessed**:
- Moderating: Positive for equity valuations
- Rising: Negative (erodes profit margins)
- Stable: Neutral

**Real-World Source** (for future integration):
- FRED API (Federal Reserve Economic Data)
- US Bureau of Labor Statistics API

#### 2. GDP Growth
**Status Assessed**:
- Stable Growth: Positive for corporate earnings
- Negative Growth: Recessionary concerns
- Rapid Growth: May lead to rate hikes

**Real-World Source**:
- BEA (Bureau of Economic Analysis) API

#### 3. Unemployment Rate
**Status Assessed**:
- Low: Strong consumer spending support
- Rising: Economic weakness concerns

**Real-World Source**:
- Bureau of Labor Statistics API

### Future Integration Options:

#### FRED API (Recommended - Free)
```python
from fredapi import Fred
fred = Fred(api_key='your-api-key')
cpi = fred.get_series('CPIAUCSL')
gdp = fred.get_series('GDP')
unemployment = fred.get_series('UNRATE')
```

**Website**: https://fred.stlouisfed.org/docs/api/

#### Alpha Vantage (Free Tier Available)
```python
import requests
url = f"https://www.alphavantage.co/query?function=REAL_GDP&apikey={key}"
```

**Code Location**: `analysis_engine.py` lines 82-99

---

## Geopolitical Analysis

### Current Implementation: Risk Framework

The system provides a **qualitative risk assessment framework** considering:

1. **Global Trade Relations**
   - Trade wars impact multinationals
   - Tariffs affect manufacturing

2. **Regional Conflicts**
   - Energy market disruptions
   - Supply chain impacts

3. **Central Bank Policies**
   - Diverging monetary policies
   - Currency fluctuations

4. **Political Stability**
   - Election cycles
   - Policy changes

**Risk Levels**:
- Low: Favorable for risk assets
- Moderate: Selective opportunities
- High: Defensive positioning recommended

### Future Integration Options:

#### GDELT Project (Free)
- Real-time news and events database
- API: https://www.gdeltproject.org/

#### News APIs:
1. **NewsAPI.org** (Free tier: 100 requests/day)
2. **Finnhub** (Financial news - Free tier available)
3. **Alpha Vantage News Sentiment** (Free)

**Code Location**: `analysis_engine.py` lines 101-113

---

## Prediction Algorithms

### Short-Term Prediction (1-3 Months)

**Primary Factor**: Momentum

**Algorithm**:
```python
if RSI > 60:
    predicted = current_price × 1.05  # 5% increase
elif RSI < 40:
    predicted = current_price × 1.08  # 8% increase (oversold bounce)
else:
    predicted = (current_price + SMA_20) / 2  # Mean reversion
```

**Rationale**:
- Oversold stocks tend to bounce
- Strong momentum continues
- Neutral RSI suggests mean reversion to 20-day average

### Mid-Term Prediction (3-12 Months)

**Primary Factor**: Trend Continuation

**Algorithm**:
```python
trend = (current_price - price_60_days_ago) / price_60_days_ago
predicted = current_price × (1 + trend × 1.5)
```

**Rationale**:
- Extrapolates 60-day trend forward
- 1.5x multiplier assumes trend continuation with moderation

### Long-Term Prediction (1-3 Years)

**Primary Factor**: Historical Returns

**Algorithm**:
```python
annual_return = (current_price - price_1_year_ago) / price_1_year_ago
predicted = current_price × (1 + annual_return × 2)
```

**Rationale**:
- Uses historical performance as baseline
- 2x multiplier for multi-year projection
- Assumes mean reversion and growth continuation

### Fallback Logic:

If insufficient data:
- Short-term: +3% default
- Mid-term: +10% default
- Long-term: +25% default

**Code Location**: `prediction_engine.py` lines 137-180

---

## Scoring System

### Total Score Range: 0-100

#### Technical Analysis (30 points):
- Price > SMA 50: +5 points
- Price > SMA 200: +5 points
- SMA 50 > SMA 200 (Golden Cross): +5 points
- Healthy RSI (30-70): +5 points
- Bullish MACD: +5 points
- Above-average volume: +5 points

#### Fundamental Analysis (20 points):
- Reasonable P/E (10-25): +10 points
- Strong profit margins (>15%): +5 points
- High ROE (>15%): +5 points

#### Baseline: 50 points (Neutral)

### Score Interpretation:

| Score Range | Rating | Recommendation |
|------------|---------|----------------|
| 70-100 | Strong Buy | High confidence positive outlook |
| 60-69 | Buy | Positive momentum and fundamentals |
| 50-59 | Hold | Balanced risk-reward |
| 40-49 | Cautious | Mixed signals, monitor closely |
| 0-39 | Avoid | Concerning patterns |

### Top 20 Selection:

Stocks are ranked by:
1. **Short-term**: Highest prediction scores
2. **Mid-term**: Largest predicted gains
3. **Long-term**: Largest predicted gains

**Code Location**: `prediction_engine.py` lines 69-135, 249-280

---

## Data Flow Architecture

```
User Request
    ↓
Flask API Route (app.py)
    ↓
Analysis Engine (analysis_engine.py)
    ↓
Prediction Engine (prediction_engine.py)
    ↓
yfinance API
    ↓
Raw Data Processing
    ↓
Technical Indicators Calculation
    ↓
Prediction Algorithms
    ↓
Scoring System
    ↓
LLM Summary Generation (simulated)
    ↓
Market Context Integration
    ↓
JSON Response
    ↓
Frontend Display (app.js)
```

---

## Limitations & Disclaimers

### Current Limitations:

1. **LLM Analysis**: Simulated, not using real AI models
2. **Economic Data**: Contextual framework, not real-time API integration
3. **News Sentiment**: Not integrated (future enhancement)
4. **Real-time Data**: 15-20 minute delay from yfinance
5. **Rate Limits**: Free tier has usage restrictions
6. **Historical Bias**: Predictions based on past performance

### Not Financial Advice:

This system is for **educational and informational purposes only**. It:
- Does NOT constitute financial advice
- Should NOT be the sole basis for investment decisions
- Past performance does NOT guarantee future results
- Users should conduct independent research
- Consult with licensed financial advisors before investing

---

## Future Enhancement Roadmap

### Phase 1: Real LLM Integration
- Integrate FinBERT for news sentiment
- Add OpenAI GPT-4 or Anthropic Claude for analysis
- Implement prompt engineering for financial context

### Phase 2: Economic Data APIs
- Integrate FRED API for real-time economic indicators
- Add Alpha Vantage for additional financial data
- Implement economic calendar tracking

### Phase 3: News & Sentiment
- Integrate NewsAPI or Finnhub
- Implement social media sentiment (Twitter, Reddit)
- Add earnings call transcript analysis

### Phase 4: Machine Learning Models
- Train custom ML models on historical data
- Implement ensemble methods
- Add backtesting framework for accuracy tracking

### Phase 5: Advanced Features
- Portfolio optimization algorithms
- Risk assessment and VaR calculations
- Options pricing and Greeks
- Correlation analysis

---

## Technical Stack Summary

| Component | Technology | Version | Cost |
|-----------|-----------|---------|------|
| Backend | Python | 3.11+ | Free |
| Web Framework | Flask | 3.0.0 | Free |
| Data Source | yfinance | 0.2.32 | Free |
| Data Processing | pandas | 2.1.3 | Free |
| Numerical | numpy | 1.26.2 | Free |
| Timezone | pytz | 2024.1 | Free |
| Frontend | JavaScript | ES6 | Free |
| LLM (Current) | Simulated | N/A | Free |
| LLM (Future) | OpenAI/Claude | N/A | Paid |

---

## Contributing to Analysis Methodology

Want to improve the analysis? Areas for contribution:

1. **Add Real LLM Integration**
2. **Integrate Economic Data APIs**
3. **Implement News Sentiment Analysis**
4. **Improve Prediction Algorithms**
5. **Add Machine Learning Models**
6. **Enhance Fundamental Analysis**
7. **Add Options Analysis**
8. **Implement Backtesting**

---

## References & Resources

### Documentation:
- yfinance: https://pypi.org/project/yfinance/
- pandas: https://pandas.pydata.org/docs/
- Technical Analysis: https://www.investopedia.com/

### APIs for Future Integration:
- FRED API: https://fred.stlouisfed.org/docs/api/
- Alpha Vantage: https://www.alphavantage.co/documentation/
- NewsAPI: https://newsapi.org/docs
- Finnhub: https://finnhub.io/docs/api
- Hugging Face: https://huggingface.co/models

### Financial Education:
- Investopedia: https://www.investopedia.com/
- Yahoo Finance: https://finance.yahoo.com/
- FINRA: https://www.finra.org/

---

**Last Updated**: October 29, 2025
**Version**: 1.0
**Status**: Production Ready (with simulated LLM)
