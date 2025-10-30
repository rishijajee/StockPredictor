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
                'description': 'Analyzes historical price patterns and trading data using multiple indicators to identify trends, momentum, and potential entry/exit points.',
                'what': 'Technical analysis studies past market data, primarily price and volume, to forecast future price movements. It operates on the principle that historical trading activity and price changes are indicators of future price behavior.',
                'how': 'Our system calculates and analyzes 6 key technical indicators in real-time, comparing current values against historical patterns and established thresholds. Each indicator is weighted and contributes to a composite technical score.',
                'details': {
                    'indicators': [
                        {
                            'name': 'Simple Moving Averages (SMA 20, 50, 200)',
                            'what': 'Averages of closing prices over specified periods that smooth out price data to identify trend direction',
                            'how': 'We calculate 20-day, 50-day, and 200-day SMAs. When price is above SMA, it signals uptrend (+5 points each for 50-day and 200-day). The "Golden Cross" (50-day crossing above 200-day) adds +5 points, indicating strong bullish momentum',
                            'interpretation': 'Price above SMA = bullish, below = bearish. Multiple timeframe alignment increases confidence'
                        },
                        {
                            'name': 'Exponential Moving Averages (EMA 12, 26)',
                            'what': 'Weighted moving averages that give more importance to recent prices, making them more responsive to new information',
                            'how': 'EMA 12 and 26 are calculated with exponential weighting. Used primarily for MACD calculation to capture short-term price momentum',
                            'interpretation': 'Faster response to price changes than SMA, better for identifying trend reversals early'
                        },
                        {
                            'name': 'Relative Strength Index (RSI)',
                            'what': 'Momentum oscillator measuring speed and magnitude of price changes on a 0-100 scale',
                            'how': 'Calculated using 14-period average gains vs losses. RSI 30-70 adds +5 points (healthy), RSI < 30 adds +3 points (oversold bounce potential), RSI > 70 subtracts 3 points (overbought risk)',
                            'interpretation': 'RSI > 70 = overbought (potential sell), RSI < 30 = oversold (potential buy), 40-60 = neutral trend'
                        },
                        {
                            'name': 'MACD (Moving Average Convergence Divergence)',
                            'what': 'Trend-following momentum indicator showing relationship between two moving averages',
                            'how': 'MACD Line = EMA(12) - EMA(26), Signal Line = 9-day EMA of MACD. Bullish crossover (MACD above signal) adds +5 points',
                            'interpretation': 'MACD above signal = buy signal, below = sell signal. Divergences between MACD and price indicate potential reversals'
                        },
                        {
                            'name': 'Bollinger Bands',
                            'what': 'Volatility bands placed above and below a moving average, adapting to volatility changes',
                            'how': 'Middle band = 20-day SMA, upper/lower bands = ±2 standard deviations. Price position relative to bands indicates overbought/oversold conditions',
                            'interpretation': 'Price at upper band = overbought, at lower band = oversold. Band squeeze indicates low volatility before potential breakout'
                        },
                        {
                            'name': 'Volume Analysis',
                            'what': 'Analysis of trading volume to confirm price movements and identify institutional activity',
                            'how': 'Compares current volume to 20-day average. Above-average volume adds +5 points as it confirms the price trend validity',
                            'interpretation': 'High volume + price increase = strong buy pressure. Low volume rallies often fail'
                        }
                    ],
                    'scoring': 'Technical indicators contribute up to 30 points to the overall prediction score. Base score starts at 50 (neutral), technical factors add or subtract based on signal strength',
                    'source': 'Historical OHLCV (Open, High, Low, Close, Volume) data from Yahoo Finance',
                    'refresh_frequency': 'Indicators recalculated on every analysis request using latest available data'
                }
            },
            {
                'name': 'Fundamental Analysis',
                'description': 'Evaluates company financial health, profitability, and valuation metrics to assess intrinsic value and long-term viability.',
                'what': 'Fundamental analysis examines a company\'s financial statements, management quality, competitive advantages, and industry position to determine whether a stock is overvalued or undervalued relative to its true worth.',
                'how': 'We extract key financial metrics from company reports and calculate ratios that indicate financial health. These metrics are compared against industry benchmarks and historical averages to generate a fundamental score.',
                'details': {
                    'metrics': [
                        {
                            'name': 'Forward P/E Ratio (Price-to-Earnings)',
                            'what': 'Valuation ratio comparing stock price to projected future earnings per share',
                            'how': 'Forward P/E = Current Stock Price ÷ Expected Earnings Per Share (next 12 months). We score: 10-25 (+10 points for reasonable valuation), <10 (+5 points for potentially undervalued), >25 (neutral to negative)',
                            'interpretation': 'Lower P/E suggests undervaluation or lower growth expectations. Industry comparison is critical - tech stocks typically have higher P/E than utilities',
                            'benchmark': 'S&P 500 average P/E: ~15-20. Growth stocks: 25-40+. Value stocks: 10-15'
                        },
                        {
                            'name': 'Profit Margins',
                            'what': 'Net profit as percentage of total revenue, indicating pricing power and operational efficiency',
                            'how': 'Profit Margin = (Net Income ÷ Revenue) × 100. Margins >15% add +5 points, indicating strong profitability and competitive moats',
                            'interpretation': 'High margins suggest strong pricing power, efficient operations, or monopolistic advantages. Declining margins may indicate increased competition',
                            'benchmark': 'Software: 20-30%, Retail: 2-5%, Banks: 20-25%, Manufacturing: 5-10%'
                        },
                        {
                            'name': 'Return on Equity (ROE)',
                            'what': 'Measures how efficiently company uses shareholder equity to generate profits',
                            'how': 'ROE = (Net Income ÷ Shareholders\' Equity) × 100. ROE >15% adds +5 points, indicating management efficiently deploys capital',
                            'interpretation': 'High ROE indicates effective management and competitive advantage. Consistently high ROE (>20%) is rare and valuable',
                            'benchmark': 'Excellent: >20%, Good: 15-20%, Average: 10-15%, Poor: <10%'
                        }
                    ],
                    'scoring': 'Fundamental metrics contribute up to 20 points to the overall prediction score. Combined with technical analysis (30 points), total possible score is 100',
                    'source': 'Company financial data from Yahoo Finance API, updated quarterly with earnings reports',
                    'limitations': 'Some companies (especially newer/smaller) may have incomplete fundamental data. In such cases, technical analysis is weighted more heavily',
                    'note': 'All stocks start with a baseline score of 50 (neutral), with technical and fundamental factors adding or subtracting points'
                }
            },
            {
                'name': 'AI-Powered Financial Sentiment Analysis',
                'description': 'Uses FinBERT, a pre-trained NLP model fine-tuned on financial text, to provide AI-driven sentiment analysis that complements quantitative scores.',
                'what': 'FinBERT (Financial BERT) is a state-of-the-art natural language processing model specifically trained on financial news, earnings calls, and market commentary. It classifies financial text sentiment as positive, negative, or neutral with confidence scores.',
                'how': 'We send stock-specific text to Hugging Face\'s free FinBERT API (ProsusAI/finbert model). The model analyzes the context and returns sentiment probabilities. This AI sentiment is combined with our quantitative technical and fundamental scores to generate comprehensive investment outlooks.',
                'details': {
                    'model': 'ProsusAI/finbert - Pre-trained on 1.8M financial news articles, fine-tuned for financial sentiment classification',
                    'implementation': 'Real-time API calls to Hugging Face Inference API (free tier) - OPTIONAL: Requires HF_API_KEY environment variable',
                    'setup': 'See FINBERT_SETUP.md for instructions. Application works perfectly without FinBERT using rule-based analysis.',
                    'sentiment_categories': {
                        'positive': 'Bullish outlook - favorable market conditions, strong fundamentals, positive momentum',
                        'neutral': 'Mixed signals - balanced risk-reward, requires further monitoring',
                        'negative': 'Bearish outlook - weak indicators, concerning patterns, unfavorable conditions'
                    },
                    'score_interpretation': [
                        'Score 70-100: "Strong Buy" - High confidence positive outlook, strong technical & fundamental alignment',
                        'Score 60-69: "Buy" - Positive momentum and fundamentals, favorable entry point',
                        'Score 50-59: "Hold" - Balanced risk-reward profile, monitor for trend development',
                        'Score 40-49: "Cautious" - Mixed signals requiring careful monitoring before position entry',
                        'Score 0-39: "Avoid" - Concerning technical patterns, weak fundamentals'
                    ],
                    'output': 'AI-generated natural language summary combining FinBERT sentiment, quantitative score, technical reasons, and sector context',
                    'accuracy': 'FinBERT achieves ~97% accuracy on financial sentiment classification tasks (significantly better than general-purpose sentiment models)',
                    'fallback': 'If FinBERT API is unavailable, system falls back to rule-based analysis using quantitative scores only'
                }
            },
            {
                'name': 'Sector & Industry Analysis',
                'description': 'Evaluates performance of stock sectors relative to overall market to identify sector rotation trends and relative strength.',
                'what': 'Sector analysis examines the performance of industry groups to understand which areas of the economy are in favor. Sector rotation is the movement of investment dollars from one industry sector to another as investors anticipate different phases of the economic cycle.',
                'how': 'We track 11 major S&P sectors using their corresponding SPDR Select Sector ETFs as proxies. Each sector ETF\'s 3-month performance is calculated and compared to the overall market (SPY). Stocks in outperforming sectors receive positive bias.',
                'details': {
                    'sectors_tracked': {
                        'XLK': 'Technology - Software, hardware, semiconductors, IT services',
                        'XLV': 'Healthcare - Pharmaceuticals, biotechnology, medical devices, healthcare providers',
                        'XLF': 'Financials - Banks, insurance, investment firms, real estate finance',
                        'XLE': 'Energy - Oil & gas exploration, production, refining, equipment',
                        'XLY': 'Consumer Discretionary - Retail, automotive, hotels, restaurants',
                        'XLP': 'Consumer Staples - Food, beverages, household products, tobacco',
                        'XLI': 'Industrials - Aerospace, defense, construction, machinery',
                        'XLB': 'Materials - Chemicals, metals & mining, packaging, paper',
                        'XLRE': 'Real Estate - REITs, real estate management, development',
                        'XLU': 'Utilities - Electric, gas, water utilities, independent power producers',
                        'XLC': 'Communication Services - Telecom, media, entertainment'
                    },
                    'calculation': 'Performance = ((Current Price - Price 3 Months Ago) / Price 3 Months Ago) × 100',
                    'classification': {
                        'Outperforming': '>+5% relative performance - Strong sector momentum, institutional buying',
                        'In-line': '-5% to +5% - Neutral sector trend, tracking broader market',
                        'Underperforming': '<-5% relative performance - Weak sector, potential rotation away'
                    },
                    'impact': 'Individual stocks tend to move with their sector. A great company in a weak sector faces headwinds. A mediocre company in a strong sector gets tailwinds.',
                    'use_case': 'Identify sector rotation opportunities (shift from defensive to cyclical sectors during expansion, etc.) and avoid stocks in systematically weak sectors',
                    'economic_cycle': 'Early cycle: Financials, Tech. Mid cycle: Industrials, Materials. Late cycle: Energy, Staples. Recession: Utilities, Healthcare'
                }
            },
            {
                'name': 'Market Sentiment Analysis',
                'description': 'Assesses overall market conditions and investor psychology using major indices to determine market regime and risk appetite.',
                'what': 'Market sentiment represents the overall attitude of investors toward a particular security or financial market. It is the "mood" of the market - whether investors are feeling bullish (optimistic) or bearish (pessimistic).',
                'how': 'We calculate the 1-month performance of SPY (S&P 500 ETF) as our primary market sentiment gauge. The S&P 500 represents ~80% of US market capitalization, making it the best proxy for overall market health. Performance is categorized into three regimes that influence individual stock recommendations.',
                'details': {
                    'primary_indicator': 'SPY (S&P 500 ETF) - Tracks 500 largest US companies, market-cap weighted',
                    'calculation': 'Monthly Change = ((Current SPY Price - Price 1 Month Ago) / Price 1 Month Ago) × 100',
                    'classification': {
                        'Bullish Market': '>+3% monthly change - Risk-on environment, investors favoring growth stocks, high-beta names, and speculative plays. Positive momentum broadly across sectors',
                        'Neutral Market': '-3% to +3% monthly change - Balanced market where stock-specific factors (earnings, guidance, product launches) dominate. Stock picking matters most',
                        'Bearish Market': '<-3% monthly change - Risk-off environment, flight to safety. Favor defensive stocks (staples, utilities, healthcare), quality over growth, dividend payers'
                    },
                    'application': 'Market sentiment provides crucial context for individual stock recommendations. In bearish markets, even technically strong stocks face selling pressure. In bullish markets, mediocre stocks can rally on momentum.',
                    'impact_on_recommendations': {
                        'Bullish': 'Increases confidence in "Buy" ratings, favorable for momentum and growth stocks',
                        'Neutral': 'Recommendations based primarily on stock-specific technical and fundamental factors',
                        'Bearish': 'Increases caution, raises bar for "Buy" ratings, favors defensive positioning'
                    },
                    'additional_context': 'While SPY is primary indicator, we also consider volatility (VIX), market breadth, and sector rotation patterns',
                    'refresh_rate': 'Recalculated with each analysis request using latest closing prices'
                }
            },
            {
                'name': 'Interest Rate Analysis',
                'description': 'Monitors interest rate environment and its impact on equity valuations, sector preferences, and overall market dynamics.',
                'what': 'Interest rates are the cost of borrowing money, set by Federal Reserve policy and reflected in Treasury yields. They are one of the most important drivers of stock valuations because they affect: (1) discount rates for future cash flows, (2) corporate borrowing costs, (3) consumer spending, and (4) alternative investment attractiveness.',
                'how': 'We track the 10-Year Treasury Yield (^TNX) as our primary interest rate proxy. This is considered the "risk-free rate" used in valuation models. We analyze both the current level and the 3-month trend to determine if rates are rising, falling, or stable, then assess sector-specific impacts.',
                'details': {
                    'data_source': '10-Year Treasury Yield (^TNX) - Most widely watched bond yield, benchmark for mortgage rates and corporate bonds',
                    'calculation': 'Track current yield level and calculate 3-month change to identify trend',
                    'rate_environments': {
                        'High Rates (>4.5%)': {
                            'negative_for': 'Growth stocks (high P/E tech), Real Estate (REITs), Utilities (bond proxies), High-debt companies',
                            'positive_for': 'Financials (higher net interest margins for banks), Value stocks (lower duration)',
                            'rationale': 'High rates increase discount rates, making far-future earnings less valuable. Bonds become attractive alternative to stocks'
                        },
                        'Low Rates (<3.5%)': {
                            'negative_for': 'Financials (banks earn less on deposits), Value stocks',
                            'positive_for': 'Growth stocks (future earnings more valuable), Tech, Real Estate (cheap mortgages), High-growth companies',
                            'rationale': 'Low rates make bonds unattractive, pushing money into stocks. Future cash flows worth more when discounted at low rates'
                        },
                        'Moderate Rates (3.5-4.5%)': {
                            'impact': 'Neutral environment where stock-specific factors (earnings growth, margins, competitive position) dominate',
                            'note': 'This is often the "goldilocks" zone - not too hot, not too cold'
                        }
                    },
                    'trend_analysis': {
                        'Rising Rates': 'Generally negative for stocks short-term (compression of multiples), but may signal strong economy. Sector rotation from growth to value',
                        'Falling Rates': 'Generally positive for stocks (multiple expansion), but may signal economic weakness. Favor growth over value',
                        'Stable Rates': 'Allows focus on fundamentals and earnings growth rather than macro factors'
                    },
                    'valuation_impact': 'Stock Price = Future Cash Flows ÷ (1 + discount rate)^years. Higher rates = higher discount rate = lower present value',
                    'practical_example': 'A growth stock trading at 40x P/E with earnings 5 years out is hurt much more by rising rates than a value stock at 12x P/E with current earnings'
                }
            },
            {
                'name': 'Economic Indicators',
                'description': 'Provides contextual framework for macroeconomic conditions that drive corporate earnings, consumer behavior, and market valuations.',
                'what': 'Economic indicators are statistics about economic activities that help analysts understand the current state and future direction of the economy. They fall into three categories: leading (predict future), coincident (current state), and lagging (confirm patterns).',
                'how': 'Currently, we provide qualitative assessment of key economic indicators based on recent trends and Fed commentary. Each indicator\'s status (improving/stable/deteriorating) and impact on equities is evaluated to provide macro context for stock recommendations.',
                'details': {
                    'current_implementation': 'Qualitative assessment framework based on recent economic trends, Fed policy statements, and market consensus',
                    'indicators_analyzed': {
                        'Inflation (CPI/PPI)': {
                            'what': 'Consumer Price Index measures price changes in basket of consumer goods. Producer Price Index tracks wholesale prices',
                            'why_it_matters': 'High inflation erodes corporate profit margins and purchasing power. Moderating inflation allows Fed to ease policy, supporting stock multiples',
                            'impact_on_stocks': 'Rising inflation → Fed tightening → higher rates → lower P/E multiples. Moderating inflation → potential rate cuts → multiple expansion',
                            'current_status': 'Moderating from recent highs - Positive for equity valuations'
                        },
                        'GDP Growth': {
                            'what': 'Gross Domestic Product measures total economic output - the broadest measure of economic health',
                            'why_it_matters': 'GDP growth drives corporate revenue growth. Strong GDP = strong earnings. Negative GDP (recession) = earnings contraction',
                            'impact_on_stocks': 'Positive GDP growth (2-3% ideal) supports earnings. >4% may cause Fed tightening. Negative GDP triggers defensive positioning',
                            'current_status': 'Stable positive growth - Supportive for corporate earnings'
                        },
                        'Unemployment Rate': {
                            'what': 'Percentage of labor force actively seeking employment',
                            'why_it_matters': 'Low unemployment = strong consumer spending (70% of GDP). Also indicates tight labor market which can push wages higher',
                            'impact_on_stocks': 'Low unemployment (<4%) = strong consumer spending, supports retail/discretionary. Very low (<3.5%) may cause wage inflation concerns',
                            'current_status': 'Near historic lows - Strong consumer spending support'
                        }
                    },
                    'future_enhancement': 'Integration with FRED API (Federal Reserve Economic Data) for real-time automated economic data ingestion. Will include ISM PMI, retail sales, housing starts, durable goods orders.',
                    'usage': 'Economic indicators provide top-down macro context that influences: (1) Sector selection (cyclicals vs defensives), (2) Growth vs value tilt, (3) Risk appetite calibration',
                    'investment_implications': {
                        'Strong Economy': 'Favor cyclicals (industrials, materials, discretionary), small-caps, higher-risk growth',
                        'Weak Economy': 'Favor defensives (staples, utilities, healthcare), large-caps, dividend aristocrats',
                        'Recovery': 'Favor financials, industrials, materials - early cycle beneficiaries'
                    }
                }
            },
            {
                'name': 'Geopolitical Analysis',
                'description': 'Assesses global risk factors, policy changes, and international events that can create market volatility or sector-specific opportunities/risks.',
                'what': 'Geopolitical analysis examines how political events, international relations, conflicts, and policy decisions affect financial markets. These "exogenous shocks" can override fundamental analysis temporarily and create sudden market moves.',
                'how': 'We evaluate current geopolitical landscape across multiple dimensions (trade policy, conflicts, policy divergence, political stability) and assign a qualitative risk level. This risk assessment influences: (1) Overall market risk appetite, (2) Sector preferences (defensive vs cyclical), (3) Geographic/currency exposure considerations.',
                'details': {
                    'risk_framework': 'Three-tier assessment (Low/Moderate/High) based on probability and magnitude of market-impacting geopolitical events',
                    'factors_monitored': {
                        'Global Trade Relations': {
                            'what': 'Tariffs, trade agreements, export/import restrictions, trade wars',
                            'impact': 'Affects multinational companies, supply chains, input costs. Tariffs reduce global trade flows and corporate margins',
                            'affected_sectors': 'Technology (global supply chains), Industrials (exports), Materials (commodities), Agriculture'
                        },
                        'Regional Conflicts': {
                            'what': 'Military conflicts, territorial disputes, sanctions, embargoes',
                            'impact': 'Disrupts energy/commodity supplies, creates flight-to-safety flows, increases risk premiums',
                            'affected_sectors': 'Energy (supply disruptions), Defense (government contracts), Safe havens (gold, Treasuries)'
                        },
                        'Central Bank Policy Divergence': {
                            'what': 'Different central banks pursuing different monetary policies (tightening vs easing)',
                            'impact': 'Creates currency fluctuations affecting multinationals\' overseas earnings, changes relative attractiveness of markets',
                            'affected_sectors': 'Exporters (weak home currency helps), Importers (strong home currency helps), Multinationals (translation risk)'
                        },
                        'Political Stability & Elections': {
                            'what': 'Election outcomes, policy shifts, regulatory changes, government stability',
                            'impact': 'Affects fiscal policy (taxes, spending), regulations, business confidence, policy continuity',
                            'affected_sectors': 'Sector-specific based on party platform (renewable energy, healthcare, defense, finance)'
                        }
                    },
                    'risk_level_implications': {
                        'Low Risk': 'Favorable environment for risk assets. Favor growth stocks, emerging markets, cyclicals, higher-beta names. Normal risk-taking appropriate',
                        'Moderate Risk': 'Current environment (Oct 2025). Selective approach recommended. Balance growth with quality. Maintain diversification across geographies and sectors',
                        'High Risk': 'Defensive positioning critical. Favor domestic large-caps, utilities, consumer staples, healthcare, dividend aristocrats. Reduce emerging market exposure'
                    },
                    'current_assessment': {
                        'risk_level': 'Moderate',
                        'key_factors': [
                            'Global trade relations remain complex with ongoing negotiations',
                            'Regional conflicts affecting energy markets and supply chain reliability',
                            'Central bank policies diverging globally (Fed vs ECB vs BoJ)',
                            'Currency fluctuations impacting multinational corporate earnings'
                        ],
                        'recommendation': 'Diversification across geographies and sectors recommended. Focus on companies with pricing power and resilient supply chains'
                    },
                    'future_enhancement': 'Integration with news APIs (NewsAPI, Finnhub, Bloomberg) for real-time event detection and sentiment analysis of geopolitical developments',
                    'historical_examples': 'COVID-19 (2020): Massive flight to safety. Brexit (2016): UK market volatility. US-China Trade War (2018-19): Tech/industrials weakness'
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
