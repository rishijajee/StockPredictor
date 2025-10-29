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
        'description': '''Our comprehensive stock prediction system utilizes multiple data sources and analytical approaches:''',
        'components': [
            {
                'name': 'Technical Analysis',
                'description': 'Historical price patterns, trading volumes, moving averages (SMA, EMA), RSI, MACD, and Bollinger Bands to identify trends and momentum.'
            },
            {
                'name': 'Financial LLM Analysis',
                'description': 'Leveraging AI models to process financial news, earnings reports, and market sentiment from multiple sources.'
            },
            {
                'name': 'Sector & Industry Analysis',
                'description': 'Comparative analysis within sectors and industries, identifying leaders and laggards, sector rotation patterns.'
            },
            {
                'name': 'Market Analysis',
                'description': 'Overall market trends, index correlations, market breadth indicators, and volatility metrics (VIX).'
            },
            {
                'name': 'Interest Rate Analysis',
                'description': 'Federal Reserve policy impact, yield curve analysis, and correlation between rates and equity valuations.'
            },
            {
                'name': 'Economic Calendar',
                'description': 'GDP data, unemployment figures, inflation metrics (CPI, PPI), consumer confidence, and manufacturing indices.'
            },
            {
                'name': 'Geopolitical Analysis',
                'description': 'Global events, trade policies, political stability, and international relations impact on markets.'
            }
        ],
        'timeframes': {
            'short_term': '1-3 months: Focus on momentum, technical indicators, and immediate catalysts',
            'mid_term': '3-12 months: Balance of technical and fundamental factors, sector trends',
            'long_term': '1-3 years: Fundamental strength, industry position, macroeconomic trends'
        },
        'disclaimer': 'This analysis is for educational purposes only. Past performance does not guarantee future results. Always conduct your own research and consult with financial advisors before making investment decisions.'
    }
    return jsonify(methodology)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
