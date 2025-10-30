import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import time
from prediction_engine import StockPredictionEngine

class AnalysisEngine:
    def __init__(self):
        self.prediction_engine = StockPredictionEngine()

    def get_market_sentiment(self):
        """Analyze overall market sentiment"""
        try:
            # Get major indices
            time.sleep(0.5)  # Rate limiting
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1mo")

            if spy_hist is None or spy_hist.empty:
                raise Exception("No SPY data")

            # Calculate market trend
            current = spy_hist['Close'].iloc[-1]
            month_ago = spy_hist['Close'].iloc[0]
            change = ((current - month_ago) / month_ago) * 100

            if change > 3:
                sentiment = "Bullish"
            elif change < -3:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"

            return {
                'sentiment': sentiment,
                'spy_change': round(change, 2),
                'description': f"Market has moved {change:.2f}% in the last month"
            }
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return {
                'sentiment': 'Neutral',
                'spy_change': 0,
                'description': 'Market data unavailable'
            }

    def analyze_sector_performance(self, sector):
        """Analyze sector performance"""
        sector_etfs = {
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

        try:
            etf = sector_etfs.get(sector, 'SPY')
            time.sleep(0.5)  # Rate limiting
            ticker = yf.Ticker(etf)
            hist = ticker.history(period='3mo')

            if hist is None or hist.empty:
                raise Exception(f"No data for {etf}")

            current = hist['Close'].iloc[-1]
            three_months_ago = hist['Close'].iloc[0]
            change = ((current - three_months_ago) / three_months_ago) * 100

            return {
                'sector': sector,
                'performance': round(change, 2),
                'trend': 'Outperforming' if change > 5 else 'Underperforming' if change < -5 else 'In-line',
                'description': f"{sector} sector has moved {change:.2f}% in the last 3 months"
            }
        except Exception as e:
            print(f"Error analyzing sector {sector}: {e}")
            return {
                'sector': sector,
                'performance': 0,
                'trend': 'Unknown',
                'description': 'Sector data unavailable'
            }

    def analyze_interest_rate_impact(self):
        """Analyze interest rate environment"""
        try:
            # Get 10-year treasury yield as proxy
            time.sleep(0.5)  # Rate limiting
            tnx = yf.Ticker("^TNX")
            tnx_hist = tnx.history(period="3mo")

            if tnx_hist is None or tnx_hist.empty:
                raise Exception("No TNX data")

            current_yield = tnx_hist['Close'].iloc[-1]
            three_months_ago = tnx_hist['Close'].iloc[0]
            change = current_yield - three_months_ago

            if current_yield > 4.5:
                impact = "Negative for growth stocks, positive for financials"
            elif current_yield < 3.5:
                impact = "Positive for growth stocks, lower bank margins"
            else:
                impact = "Neutral environment for equities"

            return {
                'current_yield': round(current_yield, 2),
                'change_3m': round(change, 2),
                'impact': impact,
                'description': f"10-year yield at {current_yield:.2f}%, {change:+.2f}% change in 3 months"
            }
        except Exception as e:
            print(f"Error analyzing interest rates: {e}")
            return {
                'current_yield': 4.0,
                'change_3m': 0,
                'impact': 'Data unavailable',
                'description': 'Interest rate data unavailable'
            }

    def get_economic_indicators(self):
        """Get economic indicators context"""
        # This is a simplified version - in production, you'd use economic data APIs
        return {
            'inflation': {
                'status': 'Moderating',
                'description': 'Inflation trending downward from recent highs',
                'impact': 'Positive for equity valuations'
            },
            'gdp_growth': {
                'status': 'Stable',
                'description': 'GDP growth remains positive',
                'impact': 'Supportive for corporate earnings'
            },
            'unemployment': {
                'status': 'Low',
                'description': 'Unemployment near historic lows',
                'impact': 'Strong consumer spending support'
            }
        }

    def get_geopolitical_context(self):
        """Get geopolitical context"""
        return {
            'risk_level': 'Moderate',
            'factors': [
                'Global trade relations remain complex',
                'Regional conflicts affecting energy markets',
                'Central bank policies diverging globally',
                'Currency fluctuations impacting multinationals'
            ],
            'recommendation': 'Diversification across geographies recommended'
        }

    def generate_llm_analysis(self, ticker, data):
        """Generate AI-powered analysis summary"""
        # Simulated LLM analysis based on data
        # In production, integrate with Hugging Face or other LLM APIs

        score = data.get('prediction_score', 50)
        reasons = data.get('reasons', '')

        if score >= 70:
            outlook = "Strong Buy"
            summary = f"{ticker} shows strong technical and fundamental indicators. "
        elif score >= 60:
            outlook = "Buy"
            summary = f"{ticker} demonstrates positive momentum with favorable conditions. "
        elif score >= 50:
            outlook = "Hold"
            summary = f"{ticker} presents a balanced risk-reward profile. "
        elif score >= 40:
            outlook = "Cautious"
            summary = f"{ticker} shows mixed signals requiring careful monitoring. "
        else:
            outlook = "Avoid"
            summary = f"{ticker} exhibits concerning technical patterns. "

        # Add reasoning
        summary += f"Key factors: {reasons}. "

        # Add sector context
        sector = data.get('sector', 'N/A')
        sector_analysis = self.analyze_sector_performance(sector)
        summary += f"The {sector} sector is currently {sector_analysis['trend']}. "

        return {
            'outlook': outlook,
            'summary': summary,
            'confidence': 'High' if score > 70 or score < 30 else 'Moderate'
        }

    def analyze_stock(self, ticker):
        """Comprehensive stock analysis"""
        # Get base prediction
        stock_data = self.prediction_engine.analyze_single_stock(ticker)

        if not stock_data:
            return {
                'error': f'Could not analyze {ticker}. Please check the ticker symbol.'
            }

        # Get market context
        market_sentiment = self.get_market_sentiment()
        sector_analysis = self.analyze_sector_performance(stock_data['sector'])
        interest_rate = self.analyze_interest_rate_impact()
        economic = self.get_economic_indicators()
        geopolitical = self.get_geopolitical_context()

        # Generate LLM analysis
        llm_analysis = self.generate_llm_analysis(ticker, stock_data)

        # Combine all analyses
        comprehensive_analysis = {
            **stock_data,
            'market_context': {
                'market_sentiment': market_sentiment,
                'sector_analysis': sector_analysis,
                'interest_rate_environment': interest_rate,
                'economic_indicators': economic,
                'geopolitical_context': geopolitical
            },
            'ai_analysis': llm_analysis,
            'recommendations': {
                'short_term': self._get_recommendation(stock_data['short_term']['predicted_price'], stock_data['current_price']),
                'mid_term': self._get_recommendation(stock_data['mid_term']['predicted_price'], stock_data['current_price']),
                'long_term': self._get_recommendation(stock_data['long_term']['predicted_price'], stock_data['current_price'])
            }
        }

        return comprehensive_analysis

    def _get_recommendation(self, predicted, current):
        """Get investment recommendation based on predicted vs current price"""
        if predicted is None:
            return 'Hold'

        change = ((predicted - current) / current) * 100

        if change > 15:
            return 'Strong Buy'
        elif change > 5:
            return 'Buy'
        elif change > -5:
            return 'Hold'
        elif change > -15:
            return 'Sell'
        else:
            return 'Strong Sell'
