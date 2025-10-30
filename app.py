from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from prediction_engine import StockPredictionEngine
from analysis_engine import AnalysisEngine

app = Flask(__name__)
CORS(app)

# Initialize engines
prediction_engine = StockPredictionEngine()
analysis_engine = AnalysisEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/top-stocks')
def get_top_stocks():
    """Get top 20 stocks for short, mid, and long term"""
    try:
        print("Starting top stocks analysis...")
        top_stocks = prediction_engine.get_top_20_stocks()
        print(f"Analysis complete. Found {len(top_stocks.get('short_term', []))} stocks")
        return jsonify({
            'success': True,
            'data': top_stocks
        })
    except Exception as e:
        import traceback
        print(f"Error in get_top_stocks: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

@app.route('/api/search/<ticker>')
def search_stock(ticker):
    """Search and analyze a specific stock"""
    try:
        ticker = ticker.upper()
        print(f"Searching for ticker: {ticker}")
        analysis = analysis_engine.analyze_stock(ticker)

        if analysis and 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 404

        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        import traceback
        print(f"Error in search_stock for {ticker}: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

@app.route('/api/methodology')
def get_methodology():
    """Get the analysis methodology description"""
    methodology = {
        'title': 'Stock Analysis Methodology',
        'description': '''Our comprehensive stock prediction system utilizes multiple data sources and analytical approaches to provide multi-factor quantitative analysis across three timeframes (short: 1-3 months, mid: 3-12 months, long: 1-3 years).''',
        'components': [
            {
                'name': 'Technical Analysis',
                'description': 'Analyzes historical price patterns and trading data using multiple indicators.',
                'details': {
                    'indicators': [
                        'Simple Moving Averages (SMA 20, 50, 200) - Identify trend direction and support/resistance levels',
                        'Exponential Moving Averages (EMA 12, 26) - More responsive to recent price changes',
                        'Relative Strength Index (RSI) - Measures momentum on a 0-100 scale. RSI > 70 indicates overbought conditions, RSI < 30 indicates oversold conditions',
                        'MACD (Moving Average Convergence Divergence) - Tracks relationship between two EMAs. Bullish when MACD crosses above signal line',
                        'Bollinger Bands - Measures volatility using standard deviations. Price touching upper band suggests overbought, lower band suggests oversold',
                        'Volume Analysis - Compares current volume to 20-day average. High volume confirms price movements'
                    ],
                    'scoring': 'Technical indicators contribute up to 30 points to the overall prediction score',
                    'source': 'Historical OHLCV (Open, High, Low, Close, Volume) data from Yahoo Finance'
                }
            },
            {
                'name': 'Fundamental Analysis',
                'description': 'Evaluates company financial health and valuation metrics.',
                'details': {
                    'metrics': [
                        'Forward P/E Ratio - Price-to-Earnings ratio using projected earnings. Scores: 10-25 (+10 points for reasonable valuation), <10 (+5 points for undervalued)',
                        'Profit Margins - Net profit as percentage of revenue. >15% profit margin adds +5 points (indicates strong profitability)',
                        'Return on Equity (ROE) - Measures efficiency of equity use. >15% ROE adds +5 points (indicates efficient management)'
                    ],
                    'scoring': 'Fundamental metrics contribute up to 20 points to the overall prediction score',
                    'source': 'Company financial data from Yahoo Finance',
                    'note': 'All stocks start with a baseline score of 50 (neutral), with technical and fundamental factors adding or subtracting points'
                }
            },
            {
                'name': 'AI-Powered Analysis',
                'description': 'Generates natural language investment outlooks based on quantitative scores.',
                'details': {
                    'current_implementation': 'Rule-based analysis engine that interprets prediction scores',
                    'score_interpretation': [
                        'Score 70-100: "Strong Buy" - High confidence positive outlook',
                        'Score 60-69: "Buy" - Positive momentum and fundamentals',
                        'Score 50-59: "Hold" - Balanced risk-reward profile',
                        'Score 40-49: "Cautious" - Mixed signals requiring monitoring',
                        'Score 0-39: "Avoid" - Concerning technical patterns'
                    ],
                    'factors_analyzed': 'Combines prediction score, technical reasons, and sector performance into coherent summary',
                    'future_enhancement': 'Ready for integration with real LLM APIs (OpenAI GPT-4, Anthropic Claude, or Hugging Face FinBERT for sentiment analysis)'
                }
            },
            {
                'name': 'Sector & Industry Analysis',
                'description': 'Evaluates performance of stock sectors relative to overall market.',
                'details': {
                    'methodology': 'Tracks 11 major sectors using SPDR Select Sector ETFs (XLK-Technology, XLV-Healthcare, XLF-Financials, XLE-Energy, XLY-Consumer Discretionary, XLP-Consumer Staples, XLI-Industrials, XLB-Materials, XLRE-Real Estate, XLU-Utilities, XLC-Communication Services)',
                    'calculation': 'Compares 3-month sector ETF performance to classify as Outperforming (>+5%), In-line (-5% to +5%), or Underperforming (<-5%)',
                    'impact': 'Stocks in outperforming sectors receive positive bias in recommendations, underperforming sectors receive negative bias',
                    'use_case': 'Helps identify sector rotation opportunities and avoid weak sectors'
                }
            },
            {
                'name': 'Market Sentiment Analysis',
                'description': 'Assesses overall market conditions using major indices.',
                'details': {
                    'primary_indicator': 'SPY (S&P 500 ETF) 1-month performance',
                    'classification': [
                        'Bullish Market: >+3% monthly change - Favorable for growth stocks',
                        'Neutral Market: -3% to +3% change - Stock-specific factors dominate',
                        'Bearish Market: <-3% monthly change - Favor defensive stocks'
                    ],
                    'application': 'Market sentiment provides context for individual stock recommendations and adjusts risk assessment',
                    'refresh_rate': 'Updated with each analysis request'
                }
            },
            {
                'name': 'Interest Rate Analysis',
                'description': 'Monitors interest rate environment and its impact on equity valuations.',
                'details': {
                    'data_source': '10-Year Treasury Yield (^TNX) as proxy for interest rate environment',
                    'analysis': 'Tracks current yield level and 3-month trend (rising or falling)',
                    'impact_assessment': [
                        'High Rates (>4.5%): Negative for growth stocks and tech, positive for financials and value stocks',
                        'Low Rates (<3.5%): Positive for growth stocks, tech, and real estate, negative for banks (lower margins)',
                        'Moderate Rates (3.5-4.5%): Neutral environment where stock-specific factors dominate'
                    ],
                    'rationale': 'Higher rates increase discount rates for future cash flows, making growth stocks less attractive while benefiting financial sector margins'
                }
            },
            {
                'name': 'Economic Indicators',
                'description': 'Provides contextual framework for macroeconomic conditions.',
                'details': {
                    'current_implementation': 'Qualitative assessment providing economic context',
                    'indicators_considered': [
                        'Inflation (CPI/PPI): Moderating inflation is positive for equity valuations, rising inflation erodes margins',
                        'GDP Growth: Stable growth supports corporate earnings, negative growth raises recession concerns',
                        'Unemployment: Low unemployment indicates strong consumer spending power'
                    ],
                    'future_enhancement': 'Integration with FRED API (Federal Reserve Economic Data) for real-time economic data',
                    'usage': 'Economic indicators provide macro context that influences sector and stock selection'
                }
            },
            {
                'name': 'Geopolitical Analysis',
                'description': 'Assesses global risk factors affecting markets.',
                'details': {
                    'risk_framework': 'Evaluates qualitative geopolitical risk on Low/Moderate/High scale',
                    'factors_monitored': [
                        'Global trade relations and tariff policies affecting multinationals',
                        'Regional conflicts impacting energy markets and supply chains',
                        'Central bank policy divergence creating currency fluctuations',
                        'Political stability and election cycles affecting policy continuity'
                    ],
                    'recommendations': [
                        'Low Risk: Favorable for risk assets and growth stocks',
                        'Moderate Risk: Selective opportunities with diversification',
                        'High Risk: Defensive positioning recommended (utilities, consumer staples, healthcare)'
                    ],
                    'future_enhancement': 'Integration with news APIs (NewsAPI, Finnhub) for real-time event tracking'
                }
            }
        ],
        'prediction_algorithms': {
            'short_term': {
                'timeframe': '1-3 months',
                'primary_factor': 'Momentum and technical indicators',
                'methodology': 'RSI-based prediction: Oversold stocks (RSI<40) predicted +8%, strong momentum (RSI>60) predicted +5%, neutral RSI uses mean reversion to 20-day SMA',
                'focus': 'Technical indicators, momentum patterns, and immediate catalysts'
            },
            'mid_term': {
                'timeframe': '3-12 months',
                'primary_factor': 'Trend continuation',
                'methodology': 'Extrapolates 60-day price trend forward with 1.5x multiplier, assuming trend continuation with moderation',
                'focus': 'Balance of technical and fundamental factors, sector trends, earnings growth trajectory'
            },
            'long_term': {
                'timeframe': '1-3 years',
                'primary_factor': 'Historical returns and fundamentals',
                'methodology': 'Uses 1-year historical return as baseline, applies 2x multiplier for multi-year projection with mean reversion assumption',
                'focus': 'Fundamental strength, competitive position, industry growth trends, macroeconomic factors'
            }
        },
        'scoring_system': {
            'total_range': '0-100 points',
            'baseline': 50,
            'technical_points': 30,
            'fundamental_points': 20,
            'interpretation': {
                '70-100': 'Strong Buy - High confidence positive outlook',
                '60-69': 'Buy - Positive momentum and fundamentals',
                '50-59': 'Hold - Balanced risk-reward',
                '40-49': 'Cautious - Mixed signals',
                '0-39': 'Avoid - Concerning patterns'
            }
        },
        'data_sources': {
            'primary': 'Yahoo Finance (yfinance library) - Free, no API key required',
            'data_types': 'Historical OHLCV data, company fundamentals, sector ETFs, market indices',
            'limitations': '15-20 minute delay during market hours, free tier rate limiting may apply',
            'update_frequency': 'Real-time analysis on each request using latest available data'
        },
        'disclaimer': 'This analysis is for educational and informational purposes only. It does NOT constitute financial advice and should NOT be the sole basis for investment decisions. Past performance does NOT guarantee future results. Users should conduct independent research and consult with licensed financial advisors before making any investment decisions. The system uses historical data and technical indicators which have inherent limitations and may not predict future market movements accurately.'
    }
    return jsonify(methodology)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
