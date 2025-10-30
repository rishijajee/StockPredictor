import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

class StockPredictionEngine:
    def __init__(self):
        # Popular stocks to analyze (mix of sectors)
        self.stock_universe = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'JPM', 'JNJ', 'V', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC',
            'ADBE', 'CRM', 'NFLX', 'CSCO', 'PEP', 'KO', 'INTC', 'AMD', 'NKE',
            'PYPL', 'CMCSA', 'XOM', 'CVX', 'LLY', 'PFE', 'ABBV', 'TMO', 'COST',
            'MRK', 'AVGO', 'ORCL', 'ACN', 'TXN', 'DHR', 'NEE', 'VZ', 'PM',
            'UNP', 'RTX', 'BMY', 'HON', 'QCOM', 'LOW', 'IBM', 'SBUX', 'AMT'
        ]

    def get_stock_data(self, ticker, period='1y'):
        """Fetch stock data using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            info = stock.info
            return hist, info
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None, None

    def calculate_technical_indicators(self, df):
        """Calculate various technical indicators"""
        if df is None or len(df) < 50:
            return None

        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # EMA
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        df['BB_middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

        # Volume trends
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

        return df

    def calculate_prediction_score(self, df, info):
        """Calculate a prediction score based on multiple factors"""
        if df is None or len(df) < 50:
            return 0, "Insufficient data"

        score = 50  # Start neutral
        reasons = []

        latest = df.iloc[-1]

        # Technical Analysis (30 points)
        # Trend following
        if latest['Close'] > latest['SMA_50']:
            score += 5
            reasons.append("Price above 50-day MA")
        if latest['Close'] > latest['SMA_200']:
            score += 5
            reasons.append("Price above 200-day MA")
        if latest['SMA_50'] > latest['SMA_200']:
            score += 5
            reasons.append("Golden cross formation")

        # Momentum
        if 30 <= latest['RSI'] <= 70:
            score += 5
            reasons.append(f"Healthy RSI ({latest['RSI']:.1f})")
        elif latest['RSI'] < 30:
            score += 3
            reasons.append("Oversold condition (potential bounce)")
        elif latest['RSI'] > 70:
            score -= 3
            reasons.append("Overbought condition")

        # MACD
        if latest['MACD'] > latest['Signal_Line']:
            score += 5
            reasons.append("Bullish MACD crossover")

        # Volume
        if latest['Volume'] > latest['Volume_SMA']:
            score += 5
            reasons.append("Above-average volume")

        # Fundamental factors (20 points)
        try:
            if 'forwardPE' in info and info['forwardPE'] is not None:
                pe = info['forwardPE']
                if 10 <= pe <= 25:
                    score += 10
                    reasons.append(f"Reasonable P/E ratio ({pe:.1f})")
                elif pe < 10:
                    score += 5
                    reasons.append(f"Low P/E ratio ({pe:.1f})")

            if 'profitMargins' in info and info['profitMargins'] is not None:
                if info['profitMargins'] > 0.15:
                    score += 5
                    reasons.append(f"Strong profit margins ({info['profitMargins']*100:.1f}%)")

            if 'returnOnEquity' in info and info['returnOnEquity'] is not None:
                if info['returnOnEquity'] > 0.15:
                    score += 5
                    reasons.append(f"High ROE ({info['returnOnEquity']*100:.1f}%)")
        except:
            pass

        return min(max(score, 0), 100), " | ".join(reasons[:5])  # Limit to top 5 reasons

    def predict_price(self, df, timeframe='short'):
        """Predict future price based on timeframe"""
        if df is None or len(df) < 20:
            return None

        try:
            current_price = df['Close'].iloc[-1]

            # Simple prediction based on moving averages and trend
            if timeframe == 'short':  # 1-3 months
                sma = df['SMA_20'].iloc[-1]
                rsi = df['RSI'].iloc[-1]

                # Momentum-based prediction
                if pd.isna(rsi):
                    predicted = current_price * 1.03  # Default 3% increase
                elif rsi > 60:
                    predicted = current_price * 1.05  # 5% up
                elif rsi < 40:
                    predicted = current_price * 1.08  # 8% up (oversold bounce)
                else:
                    if pd.isna(sma):
                        predicted = current_price * 1.03
                    else:
                        predicted = (current_price + sma) / 2

            elif timeframe == 'mid':  # 3-12 months
                if len(df) >= 60:
                    sma_50 = df['SMA_50'].iloc[-1]
                    trend = (df['Close'].iloc[-1] - df['Close'].iloc[-60]) / df['Close'].iloc[-60]
                    predicted = current_price * (1 + trend * 1.5)
                else:
                    predicted = current_price * 1.10  # Default 10% increase

            else:  # long term 1-3 years
                sma_200 = df['SMA_200'].iloc[-1]
                annual_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
                predicted = current_price * (1 + annual_return * 2)

            return round(predicted, 2)
        except Exception as e:
            print(f"Error predicting price for {timeframe}: {e}")
            # Return a conservative estimate
            return round(df['Close'].iloc[-1] * 1.03, 2)

    def analyze_single_stock(self, ticker):
        """Analyze a single stock"""
        try:
            hist, info = self.get_stock_data(ticker)
            if hist is None or hist.empty:
                return None

            df = self.calculate_technical_indicators(hist)
            if df is None:
                return None

            score, reasons = self.calculate_prediction_score(df, info)

            # Get the last close price (this is what yfinance returns)
            current_price = float(df['Close'].iloc[-1])
            price_timestamp = df.index[-1]

            # Determine if this is a close price, intraday price, or pre/post-market
            price_label = "Last Close Price"  # Default
            try:
                import pytz
                now = datetime.now(pytz.timezone('America/New_York'))

                # Handle timezone-aware and naive timestamps
                if price_timestamp.tzinfo is None:
                    price_date = price_timestamp.tz_localize('UTC').tz_convert('America/New_York')
                else:
                    price_date = price_timestamp.tz_convert('America/New_York')

                is_same_day = now.date() == price_date.date()
                is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4

                if is_weekday:
                    # Define market hours (all times in ET)
                    pre_market_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
                    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
                    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
                    post_market_end = now.replace(hour=20, minute=0, second=0, microsecond=0)

                    # Determine the appropriate label based on current time
                    if market_open <= now <= market_close:
                        # During regular market hours
                        if is_same_day:
                            price_label = "Current Price"
                        else:
                            price_label = "Previous Close Price"
                    elif pre_market_start <= now < market_open:
                        # Pre-market hours (4:00 AM - 9:30 AM ET)
                        price_label = "Previous Close Price (Pre-Market)"
                    elif market_close < now <= post_market_end:
                        # Post-market hours (4:00 PM - 8:00 PM ET)
                        price_label = "Previous Close Price (Post-Market)"
                    else:
                        # After hours (8:00 PM - 4:00 AM ET)
                        price_label = "Previous Close Price"
                else:
                    # Weekend
                    price_label = "Last Close Price (Weekend)"
            except Exception as e:
                print(f"Timezone handling error: {e}")
                # Default to "Last Close Price" on error

            # Ensure all predictions return valid values
            short_predicted = self.predict_price(df, 'short')
            if short_predicted is None:
                short_predicted = round(current_price * 1.03, 2)

            mid_predicted = self.predict_price(df, 'mid')
            if mid_predicted is None:
                mid_predicted = round(current_price * 1.10, 2)

            long_predicted = self.predict_price(df, 'long')
            if long_predicted is None:
                long_predicted = round(current_price * 1.25, 2)

            result = {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': round(current_price, 2),
                'price_label': price_label,
                'price_timestamp': price_timestamp.isoformat(),
                'short_term': {
                    'predicted_price': float(short_predicted),
                    'timeframe': '1-3 months',
                    'score': score
                },
                'mid_term': {
                    'predicted_price': float(mid_predicted),
                    'timeframe': '3-12 months',
                    'score': score
                },
                'long_term': {
                    'predicted_price': float(long_predicted),
                    'timeframe': '1-3 years',
                    'score': score
                },
                'prediction_score': score,
                'reasons': reasons,
                'last_updated': datetime.now().isoformat()
            }

            return result
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_top_20_stocks(self):
        """Get top 20 stocks for each timeframe"""
        all_stocks = []

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.analyze_single_stock, ticker): ticker
                      for ticker in self.stock_universe}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_stocks.append(result)

        # Sort by prediction score and get top 20
        all_stocks.sort(key=lambda x: x['prediction_score'], reverse=True)
        top_20 = all_stocks[:20]

        # Safe sorting with None checks
        def safe_sort_by_gain(stocks, timeframe_key):
            return sorted(
                stocks,
                key=lambda x: (x[timeframe_key]['predicted_price'] or x['current_price']) - x['current_price'],
                reverse=True
            )[:20]

        return {
            'short_term': top_20,
            'mid_term': safe_sort_by_gain(all_stocks, 'mid_term'),
            'long_term': safe_sort_by_gain(all_stocks, 'long_term'),
            'generated_at': datetime.now().isoformat()
        }
