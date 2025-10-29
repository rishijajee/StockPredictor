# StockPredictor - Data Sources & Analysis Summary

## Quick Reference Guide

---

## 📊 Primary Data Source

### Yahoo Finance (yfinance)
- **Library**: `yfinance` v0.2.32
- **Cost**: FREE (no API key required)
- **Data Quality**: Professional-grade financial data
- **Coverage**: 50,000+ stocks worldwide
- **Documentation**: https://pypi.org/project/yfinance/

**What We Get**:
- ✅ Real-time & historical stock prices
- ✅ Company fundamentals (P/E, margins, ROE)
- ✅ Sector and industry classifications
- ✅ Market indices (SPY, ^TNX)
- ✅ Sector ETFs (XLK, XLV, XLF, etc.)
- ✅ Volume data

---

## 🤖 LLM & AI Analysis

### Current Status: **SIMULATED**

⚠️ The current version does NOT use actual LLM APIs. Instead, it uses:
- Rule-based logic for outlook classification
- Template-based text generation
- Score-driven analysis summaries

### Why Simulated?
- Zero API costs
- No API key management
- Instant responses
- Educational demonstration

### Future Integration (Easy to Add):

#### Option 1: OpenAI GPT-4 (Paid)
```python
import openai
# Monthly cost: ~$20-100 depending on usage
```

#### Option 2: Anthropic Claude (Paid)
```python
import anthropic
# Monthly cost: ~$20-100 depending on usage
```

#### Option 3: FREE LLM Options
1. **FinBERT** (Hugging Face)
   - Specialized for financial sentiment
   - Completely free
   - Run locally or on Hugging Face API

2. **Llama 2** (Meta)
   - Open-source, free to use
   - Via Hugging Face

3. **GPT-J / GPT-Neo**
   - Open-source alternatives
   - Free via Hugging Face

**Code Location**: `analysis_engine.py` lines 145-185

---

## 📈 Technical Analysis

### Data Source: yfinance historical prices

### Indicators:
1. **Moving Averages** (SMA 20, 50, 200)
   - Trend identification
   - Support/resistance levels

2. **Exponential Moving Averages** (EMA 12, 26)
   - Responsive to recent changes
   - MACD calculation

3. **RSI (Relative Strength Index)**
   - Range: 0-100
   - Overbought: >70
   - Oversold: <30

4. **MACD**
   - Momentum indicator
   - Crossover signals

5. **Bollinger Bands**
   - Volatility measurement
   - Price extremes

6. **Volume Analysis**
   - Confirmation indicator

**Source**: All calculated from yfinance historical data

---

## 💼 Fundamental Analysis

### Data Source: yfinance company info

### Metrics:
1. **Forward P/E Ratio**
   - Valuation metric
   - Optimal: 10-25

2. **Profit Margins**
   - Profitability indicator
   - Good: >15%

3. **Return on Equity (ROE)**
   - Efficiency metric
   - Strong: >15%

**All FREE from yfinance**

---

## 🌍 Market Analysis

### Overall Market Sentiment
- **Source**: SPY (S&P 500 ETF) via yfinance
- **Method**: 1-month price change
- **Cost**: FREE

### Classification:
- Bullish: >+3% change
- Bearish: <-3% change
- Neutral: -3% to +3%

---

## 🏢 Sector Analysis

### Data Source: Sector ETFs via yfinance

### Sector ETFs Used:
| Sector | ETF | Coverage |
|--------|-----|----------|
| Technology | XLK | Tech stocks |
| Healthcare | XLV | Healthcare |
| Financials | XLF | Banks, insurance |
| Energy | XLE | Oil, gas |
| Consumer Discretionary | XLY | Retail, leisure |
| Consumer Staples | XLP | Food, essentials |
| Industrials | XLI | Manufacturing |
| Materials | XLB | Raw materials |
| Real Estate | XLRE | REITs, property |
| Utilities | XLU | Electric, water |
| Communication | XLC | Telecom, media |

**Cost**: FREE (all via yfinance)

---

## 💰 Interest Rate Analysis

### Data Source: 10-Year Treasury Yield (^TNX)

- **Access**: Via yfinance
- **Cost**: FREE
- **Metric**: Current yield and 3-month trend

### Impact:
- High rates (>4.5%): Bad for growth stocks
- Low rates (<3.5%): Good for growth stocks
- Moderate: Neutral

---

## 📊 Economic Indicators

### Current Status: **CONTEXTUAL FRAMEWORK**

Currently provides interpretation, NOT real-time API data.

### Indicators Discussed:
1. Inflation (CPI/PPI)
2. GDP Growth
3. Unemployment Rate

### Future FREE Integration Options:

#### FRED API (Federal Reserve Economic Data)
- **Cost**: FREE
- **API Key**: Free registration
- **Coverage**: 818,000+ economic time series
- **Website**: https://fred.stlouisfed.org/
- **Data**: CPI, GDP, unemployment, etc.

**Implementation Ready**:
```python
from fredapi import Fred
fred = Fred(api_key='your-free-key')
```

#### Alpha Vantage Economic Indicators
- **Cost**: FREE tier (500 requests/day)
- **Coverage**: Economic indicators
- **Website**: https://www.alphavantage.co/

---

## 🌐 Geopolitical Analysis

### Current Status: **QUALITATIVE FRAMEWORK**

Provides risk assessment framework, not real-time news analysis.

### Future FREE Integration Options:

#### GDELT Project
- **Cost**: COMPLETELY FREE
- **Coverage**: Real-time global news and events
- **Scale**: Monitors news in 100+ languages
- **Website**: https://www.gdeltproject.org/

#### News API (Free Tier)
- **Cost**: FREE (100 requests/day)
- **Coverage**: News from 80,000+ sources
- **Website**: https://newsapi.org/

#### Finnhub (Free Tier)
- **Cost**: FREE (60 API calls/minute)
- **Coverage**: Financial news, sentiment
- **Website**: https://finnhub.io/

---

## 🔮 Prediction Algorithms

### Source: Custom Mathematical Models

**Based on**:
- Historical price patterns (yfinance data)
- Technical indicators (calculated)
- Statistical methods (trend extrapolation)

### Timeframes:

#### Short-Term (1-3 months)
- **Method**: RSI-based momentum
- **Input**: RSI, 20-day SMA, current price

#### Mid-Term (3-12 months)
- **Method**: Trend continuation
- **Input**: 60-day price trend

#### Long-Term (1-3 years)
- **Method**: Historical returns extrapolation
- **Input**: Annual return pattern

**No external APIs needed - all calculated locally**

---

## 💯 Scoring System

### Source: Proprietary Algorithm

**Components**:
- Technical Analysis: 30 points
- Fundamental Analysis: 20 points
- Baseline: 50 points (neutral)

**Total Range**: 0-100

**No external APIs - all calculated from yfinance data**

---

## 💸 Total Monthly Cost

### Current Implementation: **$0/month**

- yfinance: FREE ✅
- All calculations: Local (FREE) ✅
- LLM: Simulated (FREE) ✅
- Economic data: Contextual (FREE) ✅

### With Full Integration: Still Mostly FREE!

**FREE Options**:
- yfinance: FREE ✅
- FRED API: FREE ✅
- FinBERT (Hugging Face): FREE ✅
- NewsAPI free tier: FREE ✅
- Finnhub free tier: FREE ✅

**Optional Paid (if you want premium):**
- OpenAI GPT-4: ~$20-50/month
- Claude API: ~$20-50/month
- Premium news APIs: ~$50-200/month

**Recommended**: Start with 100% free, add paid features later if needed.

---

## 🚀 Upgrade Path

### Phase 1: Current (100% Free)
✅ yfinance for all stock data
✅ Simulated LLM analysis
✅ Contextual economic framework

### Phase 2: Add Free APIs
- FRED API for economic data
- FinBERT for sentiment analysis
- NewsAPI free tier for news
- GDELT for geopolitical events

**Cost**: Still $0/month

### Phase 3: Premium Features (Optional)
- OpenAI GPT-4 or Claude for advanced analysis
- Premium news APIs
- Real-time data feeds

**Cost**: ~$50-100/month

---

## 📝 Data Flow Summary

```
User Query
    ↓
[FREE] yfinance API → Historical Prices
    ↓
[FREE] Local Calculation → Technical Indicators
    ↓
[FREE] Local Algorithm → Predictions
    ↓
[FREE] Local Scoring → Stock Score
    ↓
[FREE] Simulated LLM → Analysis Summary
    ↓
[FREE] yfinance → Market Context (SPY, TNX, Sector ETFs)
    ↓
Response to User
```

**Total API Costs**: $0.00

---

## ⚡ Rate Limits & Restrictions

### yfinance (FREE tier):
- ⚠️ Rate limiting during heavy usage
- ⚠️ 15-20 minute data delay during market hours
- ⚠️ No guaranteed uptime (community project)
- ✅ No hard request limits
- ✅ No API key required

### Best Practices:
1. Cache results when possible
2. Don't hammer APIs with rapid requests
3. Analyze in batches (like our top 20 feature)
4. Consider implementing request delays

---

## 🔒 API Keys Required

### Current Version: **ZERO API KEYS**

No registration, no API keys, no configuration!

### With Full Free Integration:
- FRED API: Free key (instant registration)
- NewsAPI: Free key (instant registration)
- Finnhub: Free key (instant registration)

**All FREE, all instant registration**

---

## 📚 Official Documentation

### Primary Tools:
1. **yfinance**: https://pypi.org/project/yfinance/
2. **pandas**: https://pandas.pydata.org/
3. **numpy**: https://numpy.org/

### Future Integration:
1. **FRED API**: https://fred.stlouisfed.org/docs/api/
2. **Hugging Face**: https://huggingface.co/docs
3. **NewsAPI**: https://newsapi.org/docs
4. **Alpha Vantage**: https://www.alphavantage.co/documentation/

---

## ✅ What's Real vs Simulated

### ✅ REAL (Actual API Data):
- Stock prices (yfinance)
- Historical data (yfinance)
- Company fundamentals (yfinance)
- Market indices (yfinance)
- Sector ETFs (yfinance)
- Technical indicators (calculated from real data)
- Predictions (calculated from real data)

### ⚠️ SIMULATED (Rule-Based):
- LLM analysis summaries
- Economic indicator values
- Geopolitical risk assessment

### 🔄 READY TO INTEGRATE (Easy to make real):
- Real LLM APIs (FinBERT, GPT-4, Claude)
- FRED economic data
- News sentiment APIs

---

## 🎯 Bottom Line

**StockPredictor provides REAL stock analysis using 100% FREE data sources.**

The predictions, technical analysis, and scores are all based on actual market data from Yahoo Finance. Only the LLM summaries and economic context are simulated for now, but they're easy to upgrade to real APIs (many of which are also FREE).

**No hidden costs. No API subscriptions. Just solid, data-driven stock analysis.**

---

**For complete technical details, see**: `ANALYSIS_METHODOLOGY_DETAILED.md`

**Last Updated**: October 29, 2025
