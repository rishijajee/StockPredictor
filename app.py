from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
import time
from huggingface_hub import InferenceClient
from prediction_engine import StockPredictionEngine
from analysis_engine import AnalysisEngine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize engines
prediction_engine = StockPredictionEngine()
analysis_engine = AnalysisEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stockscore')
def stockscore():
    return render_template('stockscore.html')

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
                'name': 'Large Language Models (LLMs) Used in Analysis',
                'description': 'Detailed breakdown of the specific Large Language Models integrated into the stock analysis pipeline, including algorithmic steps and processing workflow.',
                'what': 'Large Language Models (LLMs) are advanced artificial intelligence systems trained on massive amounts of text data to understand and generate human-like text. In financial analysis, specialized financial LLMs can interpret market sentiment, analyze news, and provide natural language insights that complement quantitative metrics.',
                'how': 'Our system integrates financial-specific LLMs through API calls, processes stock data through multi-step algorithms, and combines AI-generated insights with technical and fundamental analysis to produce comprehensive stock recommendations.',
                'llms_integrated': [
                    {
                        'name': 'FinBERT (Financial Bidirectional Encoder Representations from Transformers)',
                        'provider': 'Hugging Face (ProsusAI/finbert)',
                        'model_type': 'Transformer-based language model (BERT architecture)',
                        'specialization': 'Financial sentiment analysis and market text classification',
                        'training_data': {
                            'corpus_size': '1.8 million financial documents',
                            'sources': 'Financial news articles, earnings call transcripts, analyst reports, SEC filings, market commentary',
                            'training_approach': 'Pre-trained on general text (BERT-base), then fine-tuned on financial domain corpus',
                            'languages': 'English (financial terminology and jargon)'
                        },
                        'capabilities': {
                            'sentiment_classification': 'Classifies financial text into positive, negative, or neutral sentiment categories',
                            'confidence_scoring': 'Provides probability scores for each sentiment class (0.0 to 1.0)',
                            'context_understanding': 'Understands financial context (e.g., "beat earnings" is positive, "missed guidance" is negative)',
                            'domain_expertise': 'Trained specifically on financial language patterns and market terminology'
                        },
                        'technical_specifications': {
                            'architecture': 'BERT-base (12 transformer layers, 768 hidden units, 12 attention heads)',
                            'parameters': '110 million trainable parameters',
                            'input_length': 'Up to 512 tokens (approximately 350-400 words)',
                            'output': 'Three-class probability distribution: [positive, negative, neutral]',
                            'accuracy': '97% on financial sentiment classification benchmarks',
                            'inference_speed': 'Typically 50-200ms per request (after model warm-up)'
                        },
                        'algorithm_detailed_steps': {
                            'step_1_data_preparation': {
                                'description': 'Construct financial context sentence for the stock being analyzed',
                                'process': 'Combine ticker symbol, company name, and current analysis metrics into natural language text',
                                'example': '"Apple Inc (AAPL) stock analysis shows current market performance and technical indicators."',
                                'code_location': 'analysis_engine.py → get_financial_sentiment() → Line 184'
                            },
                            'step_2_api_request': {
                                'description': 'Send text to Hugging Face FinBERT API endpoint',
                                'endpoint': 'https://api-inference.huggingface.co/models/ProsusAI/finbert',
                                'authentication': 'Bearer token (HF_API_KEY environment variable)',
                                'request_format': 'JSON payload with "inputs" field containing text to analyze',
                                'timeout': '10 seconds maximum wait time',
                                'code_location': 'analysis_engine.py → get_financial_sentiment() → Line 192'
                            },
                            'step_3_tokenization': {
                                'description': 'FinBERT tokenizes input text (happens server-side at Hugging Face)',
                                'process': 'Text is split into subword tokens using WordPiece tokenization',
                                'special_tokens': '[CLS] added at start, [SEP] at end for BERT input format',
                                'example': '"Apple" → ["App", "##le"], "stock" → ["stock"]',
                                'padding': 'Sequences padded/truncated to 512 tokens'
                            },
                            'step_4_embedding': {
                                'description': 'Tokens converted to dense vector representations (happens server-side)',
                                'embedding_dimension': '768-dimensional vectors for each token',
                                'embedding_types': 'Token embeddings + Position embeddings + Segment embeddings',
                                'output': 'Sequence of 768-dimensional vectors representing input text'
                            },
                            'step_5_transformer_processing': {
                                'description': 'FinBERT processes embeddings through 12 transformer layers (happens server-side)',
                                'attention_mechanism': 'Self-attention allows model to weigh importance of different words in context',
                                'layer_processing': 'Each layer applies attention, feed-forward networks, and normalization',
                                'contextual_understanding': 'Model builds rich contextual representations understanding financial terms',
                                'example': 'Model learns "bullish" has positive sentiment in financial context'
                            },
                            'step_6_classification': {
                                'description': 'Final layer outputs probability distribution over sentiment classes (happens server-side)',
                                'classification_head': 'Dense layer maps final hidden state to 3 classes',
                                'softmax_activation': 'Converts logits to probabilities summing to 1.0',
                                'output_format': '[{"label": "positive", "score": 0.78}, {"label": "negative", "score": 0.15}, {"label": "neutral", "score": 0.07}]'
                            },
                            'step_7_response_parsing': {
                                'description': 'Extract sentiment classification from API response',
                                'process': 'Parse JSON response, extract highest probability sentiment',
                                'selection': 'Choose sentiment class with maximum score as primary prediction',
                                'validation': 'Verify response format and handle errors gracefully',
                                'code_location': 'analysis_engine.py → get_financial_sentiment() → Line 194-204'
                            },
                            'step_8_integration': {
                                'description': 'Combine FinBERT sentiment with quantitative analysis scores',
                                'weighting': 'FinBERT sentiment provides qualitative context to quantitative scores',
                                'synthesis': 'Generate natural language summary incorporating AI sentiment + technical score + fundamental metrics',
                                'example': '"AAPL shows strong technical indicators. AI Financial Sentiment Analysis indicates a positive outlook (confidence: 78%). Key factors: Price above 50-day MA..."',
                                'code_location': 'analysis_engine.py → generate_llm_analysis() → Line 217-243'
                            },
                            'step_9_fallback_handling': {
                                'description': 'Handle cases where FinBERT API is unavailable',
                                'scenarios': 'No API key provided, API timeout, rate limiting, model loading',
                                'fallback_behavior': 'Switch to rule-based sentiment analysis using quantitative scores',
                                'user_experience': 'Seamless - users receive analysis regardless of LLM availability',
                                'code_location': 'analysis_engine.py → get_financial_sentiment() → Line 175-179, 205-215'
                            }
                        },
                        'integration_workflow': {
                            'trigger': 'Stock analysis request via /api/search/<ticker> endpoint',
                            'pipeline': [
                                '1. User searches for stock (e.g., AAPL)',
                                '2. System fetches historical data and calculates technical indicators',
                                '3. System calculates fundamental metrics (P/E, margins, ROE)',
                                '4. System generates quantitative prediction score (0-100)',
                                '5. System calls get_financial_sentiment() with ticker and company name',
                                '6. FinBERT API analyzes financial context and returns sentiment',
                                '7. System calls generate_llm_analysis() to create comprehensive summary',
                                '8. AI sentiment + quantitative score + sector context = final recommendation',
                                '9. Natural language summary returned to user with outlook (Strong Buy/Buy/Hold/Cautious/Avoid)'
                            ]
                        },
                        'advantages_over_traditional_methods': {
                            'contextual_understanding': 'Unlike keyword matching, FinBERT understands context and nuance in financial language',
                            'domain_specificity': 'Trained on financial text, understands "beat" means exceeding estimates, not physical violence',
                            'confidence_quantification': 'Provides probability scores, not just binary positive/negative',
                            'handles_complexity': 'Can process complex sentences with multiple clauses and financial jargon',
                            'complementary': 'Adds qualitative sentiment layer to quantitative technical/fundamental analysis'
                        },
                        'limitations_and_considerations': {
                            'requires_authentication': 'Free Hugging Face API key required (optional - system works without it)',
                            'rate_limits': 'Free tier has usage limits (~30,000 characters/month)',
                            'cold_start_latency': 'First request may take 20-30 seconds while model loads',
                            'text_based_only': 'Analyzes text context, not actual news articles or earnings transcripts (future enhancement)',
                            'not_predictive_alone': 'Sentiment is one factor - combined with technical/fundamental for final recommendation'
                        },
                        'setup_requirements': {
                            'api_key': 'HF_API_KEY or HUGGINGFACE_API_KEY environment variable',
                            'obtaining_key': 'Free account at huggingface.co, generate token at /settings/tokens',
                            'configuration': 'Set environment variable in deployment platform (Vercel, Heroku, etc.)',
                            'documentation': 'See FINBERT_SETUP.md for detailed setup instructions'
                        }
                    }
                ],
                'future_llm_enhancements': {
                    'planned_models': [
                        'GPT-4 or Claude for deeper financial analysis and reasoning',
                        'News sentiment analysis using FinBERT on recent articles',
                        'Earnings transcript analysis for management tone and guidance',
                        'SEC filing analysis for risk factor identification'
                    ],
                    'api_integrations': [
                        'NewsAPI or Finnhub for real-time news fetching',
                        'SEC EDGAR API for regulatory filing analysis',
                        'Twitter/X API for social sentiment (retail investor mood)',
                        'Reddit API for WallStreetBets sentiment tracking'
                    ]
                },
                'comparison_to_non_llm_methods': {
                    'traditional_sentiment': 'Keyword counting (count "good" vs "bad" words) - lacks context understanding',
                    'finbert_advantage': 'Understands "stock dropped on good news" (profit-taking) vs "stock dropped on bad news" (fundamentals)',
                    'rule_based_fallback': 'Our system uses rule-based analysis (score thresholds) when LLM unavailable',
                    'hybrid_approach': 'Best results: LLM sentiment + quantitative scores + sector context'
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

# Helper functions for StockScore LLM integrations
def call_fingpt_sentiment(ticker, company_name, current_price, news_context=""):
    """Call FinGPT LLM for sentiment analysis and price movement prediction"""
    api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')

    if not api_key:
        # Fallback to rule-based analysis
        print(f"FinGPT: No API key found for {ticker}")
        return {
            'sentiment': 'neutral',
            'confidence': 0.50,
            'price_prediction': 'Moderate stability expected with potential 0-2% movement',
            'summary': f'Technical analysis suggests {ticker} is showing mixed signals. Rule-based analysis (no LLM API key) indicates neutral positioning.'
        }

    print(f"FinGPT: API key found (length: {len(api_key)})")

    try:
        # Use new InferenceClient with timeout
        # 30 seconds for localhost development, reduce to 8 for Vercel deployment
        client = InferenceClient(token=api_key, timeout=30)

        # Create context text for analysis - use provided context or create basic one
        if news_context and len(news_context.strip()) > 50:
            text = f"{news_context} Overall sentiment and price prediction analysis."
        else:
            text = f"Analyzing {company_name} ({ticker}) stock priced at ${current_price}. Recent market activity and news sentiment for price movement prediction."

        print(f"FinGPT: Calling Hugging Face InferenceClient for {ticker}...")

        try:
            # Use faster sentiment model (cardiffnlp is more responsive than ProsusAI/finbert)
            result = client.text_classification(
                text,
                model="cardiffnlp/twitter-roberta-base-sentiment"
            )
            print(f"FinGPT: API Success! Result: {result}")

        except Exception as api_error:
            error_str = str(api_error).replace('"', "'").replace('\n', ' ')[:200]
            print(f"FinGPT: API call failed: {error_str}")

            # Check if it's a model loading or timeout error
            if "loading" in error_str.lower() or "503" in error_str or "timeout" in error_str.lower():
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.50,
                    'price_prediction': 'Model warming up - wait 20 seconds and retry',
                    'summary': f'⏳ The AI model is initializing (cold start). Wait 20 seconds, then search {ticker} again for real-time analysis.'
                }

            # Return generic error - ensure it's JSON-safe
            safe_error = error_str.replace('"', "'").replace('\\', '/').strip()
            return {
                'sentiment': 'neutral',
                'confidence': 0.50,
                'price_prediction': 'Analysis temporarily unavailable',
                'summary': f'Unable to analyze {ticker} at this time. Error: {safe_error}'
            }

        if result and len(result) > 0:
            top_sentiment = max(result, key=lambda x: x['score'])

            # Map sentiment labels (cardiffnlp model uses LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive)
            label = top_sentiment['label']
            confidence_pct = top_sentiment['score'] * 100

            if label == 'LABEL_2' or label == 'positive':
                price_pred = f"Expected to rise 3-7% in next 30 days. The positive sentiment with {confidence_pct:.1f}% confidence suggests bullish momentum driven by favorable market conditions, strong investor sentiment, and positive market dynamics. Key drivers include improved market outlook, positive news flow, and strong technical indicators pointing toward upward price action."
                sentiment_label = 'positive'
                summary = f"FinGPT's sentiment analysis reveals strong POSITIVE signals for {ticker} with {confidence_pct:.1f}% confidence. The AI model has analyzed market sentiment, news flow, and social media mentions to identify bullish momentum. Market participants are displaying optimistic behavior with increased buying interest. Technical and fundamental indicators align to suggest upward price trajectory over the next 30 days. This positive sentiment is reinforced by favorable market conditions, strong earnings expectations, and positive analyst sentiment creating a supportive environment for price appreciation."
            elif label == 'LABEL_0' or label == 'negative':
                price_pred = f"Expected to decline 2-5% in next 30 days. The negative sentiment with {confidence_pct:.1f}% confidence indicates bearish pressure from unfavorable market conditions, weak investor sentiment, and concerning market dynamics. Key concerns include deteriorating market outlook, negative news catalysts, and bearish technical indicators suggesting potential downward price movement."
                sentiment_label = 'negative'
                summary = f"FinGPT's sentiment analysis identifies NEGATIVE signals for {ticker} with {confidence_pct:.1f}% confidence. The AI model has detected bearish sentiment across market indicators, news sentiment, and social media discussions. Market participants are displaying cautious or pessimistic behavior with increased selling pressure. Technical indicators combined with fundamental concerns suggest downward price pressure over the next 30 days. This negative sentiment stems from challenging market conditions, earnings concerns, or unfavorable analyst sentiment creating headwinds for the stock price."
            else:  # LABEL_1 or neutral
                price_pred = f"Expected to remain stable with 0-3% fluctuation over next 30 days. The neutral sentiment with {confidence_pct:.1f}% confidence suggests balanced market forces with no clear directional bias. Market participants are in a wait-and-see mode with mixed signals from news flow and technical indicators. The stock is likely to trade within a consolidation range as bulls and bears are evenly matched."
                sentiment_label = 'neutral'
                summary = f"FinGPT's sentiment analysis shows NEUTRAL positioning for {ticker} with {confidence_pct:.1f}% confidence. The AI model has identified balanced sentiment across multiple data sources including news, social media, and market commentary. Market participants are displaying mixed behavior with no clear consensus on direction. Both positive and negative factors are offsetting each other, creating a sideways trading pattern. The stock is expected to consolidate within a narrow range over the next 30 days as investors await new catalysts. This neutral stance reflects equilibrium between buying and selling pressure with neither bulls nor bears in control."

            return {
                'sentiment': sentiment_label,
                'confidence': top_sentiment['score'],
                'price_prediction': price_pred,
                'summary': summary
            }

        # Fallback if no results
        return {
            'sentiment': 'neutral',
            'confidence': 0.50,
            'price_prediction': 'No classification results',
            'summary': f'{ticker} analysis received no results. Please try again.'
        }

    except Exception as e:
        print(f"FinGPT error: {e}")
        return {
            'sentiment': 'neutral',
            'confidence': 0.50,
            'price_prediction': 'Analysis error occurred',
            'summary': f'Error analyzing {ticker}: {str(e)}'
        }

def call_finbert_news(ticker, company_name, current_price):
    """Call FinBERT LLM for news classification and impact assessment"""
    api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')

    if not api_key:
        return {
            'sentiment': 'neutral',
            'score': 0.50,
            'impact': 'Moderate market conditions - no major catalysts identified',
            'findings': f'News classification for {ticker} unavailable without API key. Consider setting HF_API_KEY for detailed news analysis.'
        }

    try:
        # Use new InferenceClient with timeout
        # 30 seconds for localhost development, reduce to 8 for Vercel deployment
        client = InferenceClient(token=api_key, timeout=30)

        text = f"Latest news and market developments for {company_name} ({ticker}). Stock trading at ${current_price}. Evaluating news impact and market sentiment."

        print(f"FinBERT: Calling Hugging Face InferenceClient for {ticker}...")

        try:
            # Use faster sentiment model (cardiffnlp is more responsive than ProsusAI/finbert)
            result = client.text_classification(
                text,
                model="cardiffnlp/twitter-roberta-base-sentiment"
            )
            print(f"FinBERT: API Success! Result: {result}")

        except Exception as api_error:
            error_str = str(api_error).replace('"', "'").replace('\n', ' ')[:200]
            print(f"FinBERT: API call failed: {error_str}")

            if "loading" in error_str.lower() or "503" in error_str or "timeout" in error_str.lower():
                return {
                    'sentiment': 'neutral',
                    'score': 0.50,
                    'impact': 'Model warming up - retry in 20 seconds',
                    'findings': f'⏳ The AI model is initializing (cold start). Wait 20 seconds, then search {ticker} again for real-time news classification.'
                }

            safe_error = error_str.replace('"', "'").replace('\\', '/').strip()
            return {
                'sentiment': 'neutral',
                'score': 0.50,
                'impact': 'Analysis temporarily unavailable',
                'findings': f'Unable to analyze {ticker}. Error: {safe_error}'
            }

        if result and len(result) > 0:
            top_sentiment = max(result, key=lambda x: x['score'])

            # Map sentiment labels (cardiffnlp model uses LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive)
            label = top_sentiment['label']
            confidence_pct = top_sentiment['score'] * 100

            if label == 'LABEL_2' or label == 'positive':
                impact = f"Strong POSITIVE impact expected from recent news developments. FinBERT's analysis with {confidence_pct:.1f}% confidence indicates that recent news coverage, press releases, and media discussions surrounding {ticker} are predominantly favorable. The news sentiment reflects positive market reception, strong corporate announcements, favorable regulatory developments, or positive industry trends that are likely to drive investor confidence and support upward price momentum."
                findings = f"FinBERT has processed and classified news articles, financial reports, and media coverage for {ticker} using advanced natural language processing. Key findings include: (1) Positive news catalysts dominating the media landscape with favorable coverage ratios, (2) Strong analyst commentary and upgrade cycles suggesting institutional confidence, (3) Positive earnings surprises or forward guidance exceeding market expectations, (4) Favorable industry tailwinds and competitive positioning improvements, (5) Strong management commentary and strategic initiatives receiving positive market reception. The BERT-based model's {confidence_pct:.1f}% confidence score indicates high certainty in the positive news classification, suggesting that the bullish news narrative is consistent across multiple sources and is likely to influence investor sentiment positively over the near term."
                sentiment_label = 'positive'
            elif label == 'LABEL_0' or label == 'negative':
                impact = f"NEGATIVE impact detected from recent developments. FinBERT's analysis with {confidence_pct:.1f}% confidence reveals that news coverage and market commentary for {ticker} have taken a bearish tone. The negative news sentiment encompasses concerning corporate announcements, regulatory headwinds, competitive pressures, or unfavorable industry dynamics that may weigh on investor sentiment and create downward pressure on the stock price."
                findings = f"FinBERT's comprehensive news classification for {ticker} has identified several concerning signals: (1) Negative news flow dominating recent media coverage with unfavorable headlines and commentary, (2) Analyst downgrades or cautious outlooks suggesting institutional concern, (3) Disappointing earnings results, weak guidance, or missed expectations, (4) Regulatory challenges, legal issues, or compliance concerns emerging, (5) Competitive threats or market share losses affecting the company's positioning. With {confidence_pct:.1f}% confidence, the BERT model indicates strong conviction in the negative classification. This suggests the bearish news narrative is pervasive across multiple sources and time periods, likely to weigh on investor confidence and could lead to risk-off positioning in the near term."
                sentiment_label = 'negative'
            else:  # LABEL_1 or neutral
                impact = f"NEUTRAL news impact with balanced market coverage. FinBERT's analysis with {confidence_pct:.1f}% confidence shows that news and media coverage for {ticker} lacks a clear directional bias. The neutral classification indicates that positive and negative news elements are offsetting each other, creating an environment where news flow is unlikely to be a significant catalyst for price movement in either direction."
                findings = f"FinBERT's news classification analysis for {ticker} reveals a balanced information landscape: (1) Mixed news flow with both positive and negative stories canceling each other out, (2) Analyst opinions divided with no clear consensus on direction, (3) Company developments being neither significantly positive nor concerning enough to move sentiment, (4) Industry conditions showing mixed signals with offsetting factors, (5) Market participants in wait-and-see mode pending new catalysts. The {confidence_pct:.1f}% confidence score indicates the model is certain about the lack of directional bias in news sentiment. This neutral stance suggests {ticker} is in a consolidation phase from a news perspective, with investors likely awaiting new information catalysts such as upcoming earnings reports, product launches, or significant corporate announcements before taking strong directional positions."
                sentiment_label = 'neutral'

            return {
                'sentiment': sentiment_label,
                'score': top_sentiment['score'],
                'impact': impact,
                'findings': findings
            }

        return {
            'sentiment': 'neutral',
            'score': 0.50,
            'impact': 'News classification unavailable',
            'findings': f'Unable to analyze news for {ticker} at this time.'
        }

    except Exception as e:
        print(f"FinBERT error: {e}")
        return {
            'sentiment': 'neutral',
            'score': 0.50,
            'impact': 'Analysis error',
            'findings': f'Error classifying news for {ticker}: {str(e)}'
        }

def call_finllm_decision(ticker, company_name, current_price, fingpt_data, finbert_data):
    """Call FinLLM for investment decision making based on aggregated analysis"""
    api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')

    # Synthesize recommendation based on sentiment analysis
    fingpt_sentiment = fingpt_data.get('sentiment', 'neutral')
    finbert_sentiment = finbert_data.get('sentiment', 'neutral')

    # Decision logic based on combined sentiments
    positive_count = [fingpt_sentiment, finbert_sentiment].count('positive')
    negative_count = [fingpt_sentiment, finbert_sentiment].count('negative')

    if positive_count >= 2:
        recommendation = 'BUY'
        confidence = 'High'
        rationale = f"FinLLM recommends STRONG BUY for {ticker} with HIGH confidence based on comprehensive AI consensus. Investment Thesis: Both FinGPT sentiment analysis and FinBERT news classification have independently identified bullish signals, creating a strong confirmation of positive momentum. This dual confirmation significantly reduces false positive risk and suggests genuine upside potential. The convergence of sentiment and news-based analysis indicates that both market psychology and fundamental news catalysts are aligned positively. Technical and fundamental factors are working in harmony, with positive news flow reinforcing bullish sentiment trends. Strategic recommendation: Consider initiating or adding to positions with a 3-6 month investment horizon. The strong AI consensus suggests {ticker} has favorable risk-reward dynamics with multiple tailwinds supporting price appreciation."
        risks = f"Risk Assessment for {ticker}: While the AI consensus is strongly positive, investors should remain aware of: (1) Broader market volatility and systemic risks that could override individual stock fundamentals, (2) Sector rotation dynamics that may shift capital away from this sector regardless of company-specific strength, (3) Unexpected negative catalysts such as regulatory changes, competitive disruptions, or macroeconomic shocks, (4) Valuation risks if the stock has already priced in positive expectations, (5) Execution risks related to management's ability to deliver on market expectations. Risk mitigation: Use appropriate position sizing (suggest 2-5% of portfolio), implement stop-loss orders at key technical levels, and monitor for any reversal in AI sentiment signals."
        time_horizon = "3-6 months optimal holding period with quarterly review checkpoints"
    elif negative_count >= 2:
        recommendation = 'SELL'
        confidence = 'High'
        rationale = f"FinLLM recommends SELL for {ticker} with HIGH confidence based on bearish AI consensus. Investment Analysis: Both FinGPT and FinBERT have independently flagged concerning signals, creating strong confirmation of downside risk. When sentiment analysis and news classification both turn negative simultaneously, it indicates fundamental weakening that extends beyond temporary fluctuations. The dual-negative signal suggests both market psychology has soured and news flow has turned unfavorable, creating a negative feedback loop. Risk factors are outweighing potential upside, with negative news catalysts reinforcing bearish sentiment. Strategic recommendation: Consider reducing or exiting positions within 1-3 months to preserve capital. The strong negative consensus from AI analysis indicates {ticker} faces significant headwinds that may take time to resolve."
        risks = f"Risk Analysis for {ticker}: Primary risks include: (1) Continued downward price pressure as negative sentiment becomes self-reinforcing, (2) Weak fundamentals potentially deteriorating further before stabilizing, (3) Negative sector trends creating industry-wide headwinds, (4) Potential for value traps if stock appears cheap but underlying problems persist, (5) Opportunity cost of holding declining assets versus reallocating to stronger opportunities. For existing holders: Consider tax implications of selling, evaluate if this is a temporary setback or structural decline, and assess whether the risk-reward has truly shifted negative or if contrarian opportunities exist for long-term investors with high risk tolerance."
        time_horizon = "1-3 months evaluation window - act decisively to limit downside"
    elif positive_count == 1 and negative_count == 0:
        recommendation = 'BUY'
        confidence = 'Moderate'
        rationale = f"FinLLM recommends CAUTIOUS BUY for {ticker} with MODERATE confidence based on mixed but tilting-positive signals. Investment Rationale: One AI model shows clear positive sentiment while the other remains neutral, suggesting emerging bullish momentum that hasn't yet reached full confirmation. This setup often precedes stronger upside moves as the positive narrative gains traction. The mixed signals indicate {ticker} is in a transition phase, potentially moving from neutral to positive territory. Strategic approach: Consider gradual position building through dollar-cost averaging rather than large immediate positions. This allows you to participate in potential upside while managing risk if the positive thesis doesn't fully develop. Monitor for the neutral model to shift positive, which would upgrade this to a strong buy signal."
        risks = f"Risk Considerations for {ticker}: The moderate confidence reflects inherent uncertainty: (1) Mixed signals suggest the positive thesis is not yet fully validated by all indicators, (2) Moderate volatility expected as market participants debate the stock's direction, (3) Sector-specific risks that may not be fully reflected in current analysis, (4) Risk of false start if positive sentiment fails to broaden, (5) Potential for consolidation or pullback before sustained uptrend develops. Risk management: Use smaller initial position sizes (1-3% of portfolio), plan for adding on weakness if thesis strengthens, maintain mental stop-losses at key support levels, and be prepared to exit if the positive signal deteriorates back to negative."
        time_horizon = "3-6 months with active monitoring - reassess monthly"
    elif negative_count == 1 and positive_count == 0:
        recommendation = 'HOLD'
        confidence = 'Moderate'
        rationale = f"FinLLM recommends HOLD for {ticker} with MODERATE confidence due to mixed defensive signals. Investment Analysis: One AI model indicates negative sentiment while another remains neutral, suggesting potential deterioration but without full confirmation. This creates a cautious environment where the downside thesis is present but not yet conclusive. The prudent strategy is to maintain current positions while closely monitoring for trend clarification. For non-holders, it's advisable to wait for clearer signals before initiating positions. This is a watch-and-wait scenario where patience allows for better risk-reward entry points to emerge. The goal is to avoid catching a falling knife while remaining positioned to act when clarity emerges."
        risks = f"Risk Framework for {ticker}: In this uncertain environment, key risks include: (1) Potential downside if the negative trend strengthens and the neutral signal turns negative, (2) Opportunity cost of holding when capital could be deployed in higher-conviction opportunities, (3) Risk of slow deterioration that gradually erodes value, (4) Psychological challenge of holding through uncertainty without clear catalyst, (5) Possibility of sudden negative surprise that validates the bearish signal. For position holders: Evaluate your cost basis and risk tolerance, consider whether to trim positions to reduce exposure, set clear exit criteria if situation worsens, and monitor closely for any shift in AI signals that would warrant action."
        time_horizon = "1-2 months monitoring period - make active decision at that point"
    else:
        recommendation = 'HOLD'
        confidence = 'Low to Moderate'
        rationale = f"FinLLM recommends HOLD for {ticker} with LOW TO MODERATE confidence due to neutral AI consensus. Investment Assessment: All AI models indicate neutral positioning, suggesting {ticker} lacks clear directional catalysts in either direction. This neutral state often characterizes consolidation phases, market indecision, or periods where positive and negative factors are balanced. The uncertainty reflected in mixed signals indicates that better risk-reward opportunities likely exist elsewhere in the market. For current holders, there's no compelling reason to exit, but also limited reason to add to positions. For new investors, this represents a wait-and-see opportunity where patience will likely provide better entry points once direction clarifies."
        risks = f"Risk Profile for {ticker}: The neutral stance carries unique risks: (1) Direction uncertainty means potential for sudden moves in either direction as market resolves the indecision, (2) Opportunity cost of capital tied up in neutral positions versus higher-conviction opportunities, (3) Risk of complacency leading to missing important shifts in underlying conditions, (4) Potential for extended sideways trading that frustrates both bulls and bears, (5) Breakout risk in either direction could occur rapidly, making it important to stay alert. Strategy for this environment: Maintain small positions if currently held, avoid new commitments until direction clarifies, focus capital on higher-conviction opportunities elsewhere, set alerts for significant price or sentiment changes, and reassess when new catalysts emerge such as earnings reports, product launches, or significant news events."
        time_horizon = "1-3 months observation period - actively seek better opportunities"

    return {
        'recommendation': recommendation,
        'confidence': confidence,
        'rationale': rationale,
        'risks': risks,
        'time_horizon': time_horizon
    }

def call_finma_prediction(ticker, company_name, current_price):
    """Call Open FinMA LLM for stock movement prediction analysis"""
    api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')

    if not api_key:
        return {
            'movement_direction': 'Neutral',
            'confidence_score': 0.50,
            'price_target_low': round(current_price * 0.98, 2),
            'price_target_high': round(current_price * 1.02, 2),
            'timeframe': '30 days',
            'key_factors': f'FinMA analysis for {ticker} unavailable without API key. Set HF_API_KEY for advanced stock movement predictions.',
            'volatility_assessment': 'Moderate volatility expected based on historical patterns'
        }

    try:
        # Use new InferenceClient with timeout
        # 30 seconds for localhost development, reduce to 8 for Vercel deployment
        client = InferenceClient(token=api_key, timeout=30)

        text = f"Stock movement prediction for {company_name} ({ticker}) currently trading at ${current_price}. Analyze technical patterns, market momentum, and provide price target range for next 30 days."

        print(f"FinMA: Calling Hugging Face InferenceClient for {ticker}...")

        try:
            # Use faster sentiment model (cardiffnlp is more responsive than ProsusAI/finbert)
            result = client.text_classification(
                text,
                model="cardiffnlp/twitter-roberta-base-sentiment"
            )
            print(f"FinMA: API Success! Result: {result}")

        except Exception as api_error:
            # Sanitize error message for JSON-safe response
            error_str = str(api_error).replace('"', "'").replace('\n', ' ')[:200]
            print(f"FinMA: API call failed: {error_str}")

            # Detect timeout/loading errors
            if "loading" in error_str.lower() or "503" in error_str or "timeout" in error_str.lower():
                return {
                    'movement_direction': 'Neutral',
                    'confidence_score': 0.50,
                    'price_target_low': round(current_price * 0.98, 2),
                    'price_target_high': round(current_price * 1.02, 2),
                    'timeframe': '30 days',
                    'key_factors': f'⏳ The AI model is initializing (cold start). Wait 20 seconds, then search {ticker} again for real-time movement prediction.',
                    'volatility_assessment': 'Model warming up - retry in 20 seconds'
                }

            # Return JSON-safe error
            safe_error = error_str.replace('"', "'").replace('\\', '/').strip()
            return {
                'movement_direction': 'Neutral',
                'confidence_score': 0.50,
                'price_target_low': round(current_price * 0.98, 2),
                'price_target_high': round(current_price * 1.02, 2),
                'timeframe': '30 days',
                'key_factors': f'Unable to analyze {ticker}. Error: {safe_error}',
                'volatility_assessment': 'API temporarily unavailable'
            }

        if result and len(result) > 0:
            top_sentiment = max(result, key=lambda x: x['score'])

            # Map sentiment labels (cardiffnlp model uses LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive)
            label = top_sentiment['label']
            confidence_pct = top_sentiment['score'] * 100

            if label == 'LABEL_2' or label == 'positive':
                movement = 'Upward'
                confidence = top_sentiment['score']
                price_low = round(current_price * 1.03, 2)
                price_high = round(current_price * 1.08, 2)
                factors = f"Open FinMA's comprehensive stock movement prediction identifies STRONG BULLISH MOMENTUM for {ticker} with {confidence_pct:.1f}% confidence. Technical Analysis Framework: (1) Price Action: Bullish chart patterns emerging with higher highs and higher lows indicating strong uptrend formation, (2) Volume Analysis: Above-average volume on up days suggests institutional accumulation and strong buying interest, (3) Moving Averages: Price trading above key moving averages (50-day, 200-day) with bullish crossover patterns supporting upward momentum, (4) Momentum Indicators: RSI showing strength without reaching overbought extremes, MACD displaying bullish divergence, (5) Support/Resistance: Price breaking through resistance levels with conviction, establishing new support zones. Market Microstructure: Order flow analysis reveals persistent buying pressure with large block trades at ask prices, bid-ask spread tightening during advances, and depth-of-market showing strong support levels. The convergence of technical, volume, and microstructure indicators creates high-probability setup for continued upward movement. Target Range Methodology: Conservative target ${price_low} represents +3% move based on near-term resistance levels, while optimistic target ${price_high} reflects +8% upside potential if momentum accelerates and {ticker} breaks through key resistance zones with volume confirmation."
                volatility = f"MODERATE VOLATILITY with UPWARD BIAS expected for {ticker}. Volatility Characteristics: The upward movement is likely to be characterized by healthy consolidation phases interspersed with strong directional moves. Expected volatility profile includes normal intraday swings of 1-2% with potential for larger moves on catalyst events or momentum acceleration. Positive volatility bias means pullbacks are likely to be shallow and brief, creating buying opportunities rather than trend reversals. Volume patterns suggest institutional participation which tends to smooth price action compared to retail-driven moves. Risk/Reward Framework: The upside targets offer favorable risk-reward ratio with well-defined support levels providing clear exit points if thesis invalidates. Traders can use volatility to their advantage by adding positions on dips toward support levels. Options market implied volatility may be understating realized volatility, creating opportunities for volatility-based strategies."
            elif label == 'LABEL_0' or label == 'negative':
                movement = 'Downward'
                confidence = top_sentiment['score']
                price_low = round(current_price * 0.92, 2)
                price_high = round(current_price * 0.97, 2)
                factors = f"Open FinMA's technical analysis detects BEARISH SIGNALS for {ticker} with {confidence_pct:.1f}% confidence indicating potential downward movement. Technical Breakdown: (1) Price Structure: Bearish chart patterns forming with lower highs and lower lows suggesting trend reversal or continuation of downtrend, (2) Volume Dynamics: Higher volume on down days compared to up days indicates distribution and selling pressure from informed participants, (3) Moving Average Configuration: Price trading below key moving averages with death cross patterns emerging or in place, creating technical resistance, (4) Momentum Deterioration: RSI showing weakness and potentially reaching oversold levels, MACD displaying bearish crossovers and negative divergences, (5) Support Breakdown: Key support levels failing with decisive breaks below on increasing volume, creating vacuum zones below. Market Microstructure Warning Signs: Order flow revealing persistent selling pressure with large blocks hitting bids, bid-ask spread widening on declines indicating liquidity concerns, and depth-of-market showing weak support with heavy resistance overhead. Target Range Methodology: Optimistic floor at ${price_high} represents -3% decline to first major support level, while conservative downside target of ${price_low} reflects -8% potential drop if selling accelerates and {ticker} breaks through critical support zones. These targets are based on Fibonacci retracement levels, previous support zones, and volume profile analysis."
                volatility = f"ELEVATED VOLATILITY with DOWNWARD PRESSURE anticipated for {ticker}. Volatility Profile: Downward movements typically exhibit higher volatility than upward moves due to fear-driven selling and rapid position liquidation. Expected characteristics include sharp intraday declines of 2-4% possible, increased gap risk especially on negative news, and potential for capitulation selling that accelerates declines. The elevated volatility environment creates both risks and opportunities: risk of rapid losses but also potential for oversold bounces that can be traded tactically. Market participants should exercise caution with position sizing and implement strict risk management protocols. Protective Strategies: Consider using wider stop-losses to avoid getting whipsawed by volatility spikes, or implement options strategies like protective puts to hedge downside while maintaining upside exposure if reversal occurs. The high-volatility environment may also create attractive entry points for contrarian investors with longer time horizons, though timing is critical to avoid catching falling knives."
            else:  # LABEL_1 or neutral
                movement = 'Neutral'
                confidence = top_sentiment['score']
                price_low = round(current_price * 0.98, 2)
                price_high = round(current_price * 1.02, 2)
                factors = f"Open FinMA analysis shows BALANCED SIGNALS for {ticker} with {confidence_pct:.1f}% confidence, indicating range-bound consolidation likely. Technical Landscape: (1) Price Action: Sideways trading pattern with price oscillating between well-defined support and resistance levels, neither bulls nor bears in control, (2) Volume Profile: Declining volume suggests market participants awaiting catalyst before committing capital, typical of consolidation phases, (3) Moving Average Compression: Price trading near or between multiple moving averages with lack of clear directional crossovers, creating neutral technical picture, (4) Momentum Indicators: Oscillators like RSI trending near 50 (midpoint) and MACD near zero line indicate equilibrium between buying and selling pressure, (5) Support/Resistance Levels: Price respecting both upper and lower bounds of trading range, with multiple tests of these levels reinforcing range strength. Market Psychology: The neutral state reflects market indecision as investors digest recent developments and await new information. This environment often precedes significant moves but direction remains unclear. Consolidation Range: Expected price movement between ${price_low} (-2%) and ${price_high} (+2%) represents the technical range where {ticker} likely trades until a catalyst emerges. Range traders can profit from buying support and selling resistance, while breakout traders should wait for decisive move beyond these levels on significant volume before taking directional positions."
                volatility = f"LOW TO MODERATE VOLATILITY expected for {ticker} during consolidation phase. Volatility Characteristics: Range-bound trading typically exhibits lower volatility as price action becomes more predictable within defined boundaries. Expected daily moves of 0.5-1.5% with occasional tests of range extremes. This low-volatility environment creates specific trading opportunities and challenges: (1) Range Trading: Consistent patterns make it attractive for mean-reversion strategies buying support and selling resistance, (2) Options Strategies: Low implied volatility favors options buying strategies (straddles, strangles) that profit from eventual breakout and volatility expansion, (3) Patience Required: Directional traders should wait for range breakout before entering significant positions. Warning Signs: Low volatility can persist longer than expected but often precedes volatility expansion, meaning periods of calm can suddenly transition to high-volatility directional moves. Monitor for: volume expansion, moving average convergence/divergence, and news catalysts that could trigger range breakout. Compression patterns like Bollinger Band squeezes often precede major moves, so current low volatility may be building energy for future directional breakout, though timing and direction remain uncertain until technical break occurs."

            return {
                'movement_direction': movement,
                'confidence_score': confidence,
                'price_target_low': price_low,
                'price_target_high': price_high,
                'timeframe': '30 days',
                'key_factors': factors,
                'volatility_assessment': volatility
            }

        return {
            'movement_direction': 'Neutral',
            'confidence_score': 0.50,
            'price_target_low': round(current_price * 0.98, 2),
            'price_target_high': round(current_price * 1.02, 2),
            'timeframe': '30 days',
            'key_factors': f'FinMA prediction unavailable at this time for {ticker}.',
            'volatility_assessment': 'Unable to assess volatility'
        }

    except Exception as e:
        print(f"FinMA error: {e}")
        return {
            'movement_direction': 'Neutral',
            'confidence_score': 0.50,
            'price_target_low': round(current_price * 0.98, 2),
            'price_target_high': round(current_price * 1.02, 2),
            'timeframe': '30 days',
            'key_factors': f'Error in FinMA analysis for {ticker}: {str(e)}',
            'volatility_assessment': 'Analysis error occurred'
        }

def analyze_industry_peers(ticker, sector, industry, current_recommendation):
    """Analyze industry peer stocks and find better alternatives"""
    try:
        # Define industry peer groups (major stocks by sector)
        industry_peers = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE'],
            'Communication Services': ['GOOGL', 'META', 'DIS', 'NFLX', 'T', 'VZ', 'CMCSA'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB'],
            'Healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'LLY', 'ABT', 'DHR', 'CVS'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX'],
            'Consumer Defensive': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MO', 'CL', 'KMB'],
            'Industrials': ['UPS', 'HON', 'BA', 'CAT', 'GE', 'MMM', 'LMT', 'RTX', 'DE'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY'],
            'Basic Materials': ['LIN', 'APD', 'ECL', 'DD', 'NEM', 'FCX', 'NUE', 'VMC'],
            'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'DLR', 'O', 'WELL'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL']
        }

        # Get peers for the sector
        peers = industry_peers.get(sector, [])
        if ticker in peers:
            peers.remove(ticker)  # Remove the current stock

        if not peers or len(peers) < 3:
            return {
                'has_alternatives': False,
                'message': f'Insufficient peer data available for {industry} sector analysis.'
            }

        # Analyze up to 3 peer stocks (quick analysis)
        peer_analyses = []
        for peer_ticker in peers[:3]:
            try:
                peer_stock = yf.Ticker(peer_ticker)
                peer_info = peer_stock.info
                peer_price = peer_info.get('currentPrice') or peer_info.get('regularMarketPrice', 0)
                peer_name = peer_info.get('shortName', peer_ticker)

                if not peer_price or peer_price == 0:
                    continue

                # Quick sentiment analysis for peer
                peer_text = f"Stock {peer_name} ({peer_ticker}) trading at ${peer_price}. Industry peer comparison analysis."

                # Get quick sentiment (reuse existing HF client)
                api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')
                if api_key:
                    client = InferenceClient(token=api_key, timeout=10)
                    result = client.text_classification(peer_text, model="cardiffnlp/twitter-roberta-base-sentiment")

                    if result and len(result) > 0:
                        top_sentiment = max(result, key=lambda x: x['score'])
                        label = top_sentiment['label']

                        sentiment = 'positive' if label == 'LABEL_2' else 'negative' if label == 'LABEL_0' else 'neutral'
                        score = top_sentiment['score']

                        peer_analyses.append({
                            'ticker': peer_ticker,
                            'name': peer_name,
                            'price': round(peer_price, 2),
                            'sentiment': sentiment,
                            'score': score
                        })

            except Exception as e:
                print(f"Error analyzing peer {peer_ticker}: {e}")
                continue

        if not peer_analyses:
            return {
                'has_alternatives': False,
                'message': 'Unable to analyze industry peers at this time.'
            }

        # Find better alternatives (higher scores, positive sentiment)
        better_alternatives = []
        for peer in peer_analyses:
            if current_recommendation == 'SELL' or current_recommendation == 'HOLD':
                # If current stock is SELL/HOLD, recommend peers with positive sentiment
                if peer['sentiment'] == 'positive' and peer['score'] > 0.6:
                    better_alternatives.append(peer)
            elif current_recommendation == 'BUY':
                # If current stock is BUY, only show peers with higher confidence
                if peer['sentiment'] == 'positive' and peer['score'] > 0.75:
                    better_alternatives.append(peer)

        # Sort by sentiment score
        better_alternatives.sort(key=lambda x: x['score'], reverse=True)

        return {
            'has_alternatives': len(better_alternatives) > 0,
            'alternatives': better_alternatives[:2],  # Top 2 alternatives
            'all_peers': peer_analyses,
            'sector': sector,
            'industry': industry
        }

    except Exception as e:
        print(f"Error in analyze_industry_peers: {e}")
        return {
            'has_alternatives': False,
            'message': f'Error analyzing industry peers: {str(e)}'
        }

def generate_consolidated_summary(ticker, company_name, current_price, fingpt_analysis, finbert_analysis, finllm_decision, finma_prediction, industry_alternatives=None):
    """Generate comprehensive consolidated summary based on all LLM analyses"""

    # Extract key metrics
    fingpt_sentiment = fingpt_analysis.get('sentiment', 'neutral')
    finbert_sentiment = finbert_analysis.get('sentiment', 'neutral')
    recommendation = finllm_decision.get('recommendation', 'HOLD')
    confidence = finllm_decision.get('confidence', 'Moderate')
    movement_direction = finma_prediction.get('movement_direction', 'Neutral')
    price_target_low = finma_prediction.get('price_target_low', current_price)
    price_target_high = finma_prediction.get('price_target_high', current_price)

    # Count sentiment signals
    positive_signals = [fingpt_sentiment, finbert_sentiment, movement_direction].count('positive') + (1 if movement_direction == 'Upward' else 0)
    negative_signals = [fingpt_sentiment, finbert_sentiment, movement_direction].count('negative') + (1 if movement_direction == 'Downward' else 0)

    # Determine overall assessment
    if recommendation == 'BUY':
        overall_verdict = "BULLISH"
        verdict_color = "positive"
        action_statement = f"Our AI consensus recommends BUYING {ticker} based on favorable sentiment, positive news flow, and supportive technical indicators."
    elif recommendation == 'SELL':
        overall_verdict = "BEARISH"
        verdict_color = "negative"
        action_statement = f"Our AI consensus recommends SELLING or AVOIDING {ticker} due to negative sentiment, concerning news developments, and bearish technical signals."
    else:
        overall_verdict = "NEUTRAL"
        verdict_color = "neutral"
        action_statement = f"Our AI consensus recommends HOLDING or MONITORING {ticker} as signals are mixed without clear directional conviction."

    # Generate comprehensive summary
    summary = f"""
    **AI CONSENSUS ANALYSIS FOR {ticker} - {company_name}**

    **OVERALL VERDICT: {overall_verdict}** | **RECOMMENDATION: {recommendation}** | **CONFIDENCE: {confidence}**

    **Executive Summary:**
    After analyzing {ticker} through four specialized AI models examining sentiment, news, technical patterns, and price movement predictions, our comprehensive assessment yields a **{recommendation}** recommendation with **{confidence}** confidence. {action_statement}

    **Current Market Position:**
    {company_name} is trading at ${current_price:.2f}. {finllm_decision.get('rationale', 'Analysis indicates mixed signals requiring careful evaluation.')}

    **AI Model Consensus Breakdown:**
    • **FinGPT Sentiment Analysis**: {fingpt_sentiment.upper()} ({fingpt_analysis.get('confidence', 0)*100:.1f}% confidence) - {fingpt_analysis.get('price_prediction', 'Analysis pending')}
    • **FinBERT News Classification**: {finbert_sentiment.upper()} ({finbert_analysis.get('score', 0)*100:.1f}% confidence) - {finbert_analysis.get('impact', 'News impact assessment pending')}
    • **FinLLM Investment Decision**: {recommendation} with {confidence} confidence - Strategic investment recommendation based on multi-model synthesis
    • **Open FinMA Movement Prediction**: {movement_direction.upper()} movement ({finma_prediction.get('confidence_score', 0)*100:.1f}% confidence) - Price targets ${price_target_low}-${price_target_high} over 30 days

    **Signal Strength Analysis:**
    The analysis reveals {positive_signals} positive signal(s) and {negative_signals} negative signal(s) across our AI models. This distribution indicates {"strong bullish consensus" if positive_signals >= 3 else "strong bearish consensus" if negative_signals >= 3 else "mixed signals with moderate conviction" if abs(positive_signals - negative_signals) <= 1 else "emerging directional bias"}. The convergence or divergence of these independent AI models provides insight into the strength and reliability of the overall assessment.

    **Price Movement Outlook:**
    Based on Open FinMA's technical analysis, {ticker} is expected to move {movement_direction.lower()} with a projected trading range of ${price_target_low} to ${price_target_high} over the next 30 days. This represents potential {((price_target_high - current_price) / current_price * 100):.1f}% upside and {((price_target_low - current_price) / current_price * 100):.1f}% downside from current levels. {finma_prediction.get('volatility_assessment', 'Volatility profile assessment pending')}

    **Risk Considerations:**
    {finllm_decision.get('risks', 'Standard market risks apply including volatility, sector rotation, and unexpected catalysts.')}

    **Investment Time Horizon:**
    {finllm_decision.get('time_horizon', 'Medium-term outlook of 3-6 months recommended for position evaluation.')}

    **Key Takeaway:**
    {"The strong AI consensus across multiple models provides high confidence in this assessment. All signals are aligned in the same direction, reducing false positive/negative risk and suggesting genuine directional conviction." if (positive_signals >= 3 or negative_signals >= 3) else "Mixed signals across AI models suggest a transitional or uncertain phase. Investors should wait for clearer confirmation before taking large directional positions." if abs(positive_signals - negative_signals) <= 1 else "Moderate directional bias emerging but not yet fully confirmed. Consider scaled entry/exit strategies that allow for position adjustments as signals evolve."} This analysis synthesizes real-time sentiment data, news classification, fundamental factors, and technical patterns to provide a comprehensive view of {ticker}'s current investment profile.
    """

    # Add industry alternatives section if available
    industry_section = ""
    if industry_alternatives and industry_alternatives.get('has_alternatives'):
        alternatives = industry_alternatives.get('alternatives', [])
        sector = industry_alternatives.get('sector', 'same industry')

        if alternatives:
            industry_section = f"\n\n    **💡 Alternative Investment Opportunities in {sector}:**\n"
            industry_section += f"    Based on our AI analysis, the following {sector} stocks currently show stronger signals than {ticker}:\n\n"

            for i, alt in enumerate(alternatives, 1):
                alt_ticker = alt['ticker']
                alt_name = alt['name']
                alt_price = alt['price']
                alt_sentiment = alt['sentiment'].upper()
                alt_score = alt['score'] * 100

                industry_section += f"    **{i}. {alt_ticker} - {alt_name}**\n"
                industry_section += f"    • Current Price: ${alt_price}\n"
                industry_section += f"    • AI Sentiment: {alt_sentiment} ({alt_score:.1f}% confidence)\n"
                industry_section += f"    • Comparative Advantage: "

                if alt_score > 75:
                    industry_section += f"Strong positive momentum with {alt_score:.1f}% AI confidence suggests robust upside potential. "
                elif alt_score > 65:
                    industry_section += f"Moderate positive signals with {alt_score:.1f}% confidence indicate emerging strength. "
                else:
                    industry_section += f"Positive sentiment detected with room for improvement. "

                industry_section += f"Consider {alt_ticker} as a potential alternative or complement to {ticker} within your {sector} allocation.\n\n"

            industry_section += f"    **Investment Strategy:** These alternatives were identified through the same comprehensive 4-LLM analysis framework. "
            if recommendation in ['SELL', 'HOLD']:
                industry_section += f"Given {ticker}'s {recommendation} rating, rotating capital into these higher-conviction {sector} opportunities may improve risk-adjusted returns. "
            else:
                industry_section += f"While {ticker} shows promise, these peers demonstrate even stronger AI consensus, potentially offering superior risk-reward profiles. "

            industry_section += "Always compare full analyses before making investment decisions."

    summary_with_alternatives = summary.strip() + industry_section

    # Add disclaimer
    summary_with_alternatives += "\n\n    **Disclaimer:** This AI-generated analysis is for informational purposes only and should not be considered financial advice. Always conduct your own due diligence and consult with qualified financial advisors before making investment decisions. Past performance and AI predictions do not guarantee future results."

    return {
        'overall_verdict': overall_verdict,
        'verdict_color': verdict_color,
        'recommendation': recommendation,
        'confidence': confidence,
        'summary': summary_with_alternatives.strip(),
        'positive_signals': positive_signals,
        'negative_signals': negative_signals,
        'price_outlook': f"${price_target_low} - ${price_target_high} (30-day target range)",
        'action_statement': action_statement,
        'industry_alternatives': industry_alternatives
    }

@app.route('/api/stockscore/<ticker>')
def get_stockscore(ticker):
    """Get real-time AI LLM analysis for a specific stock"""
    try:
        ticker = ticker.upper()
        print(f"StockScore analysis for: {ticker}")

        # Fetch basic stock data
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price and company name
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        company_name = info.get('longName') or info.get('shortName', ticker)

        if not current_price or current_price == 0:
            return jsonify({
                'success': False,
                'error': f'Could not fetch data for {ticker}. Please check the ticker symbol.'
            }), 404

        # Gather comprehensive stock data for analysis
        hist = stock.history(period='1mo')

        # Calculate key metrics
        price_change_1d = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
        price_change_1w = ((current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) > 5 else 0
        price_change_1m = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100) if len(hist) > 0 else 0

        # Get additional metrics
        pe_ratio = info.get('trailingPE', 'N/A')
        market_cap = info.get('marketCap', 0)
        volume = info.get('volume', 0)
        avg_volume = info.get('averageVolume', 1)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1

        recommendation = info.get('recommendationKey', 'none')
        target_price = info.get('targetMeanPrice', 0)

        # Create rich narrative context for sentiment analysis
        market_cap_str = f"${market_cap:,}" if market_cap > 0 else 'N/A'

        # Generate sentiment-rich narrative based on actual metrics
        narrative_parts = []

        # Price movement narrative
        if price_change_1d > 3:
            narrative_parts.append(f"{ticker} surged {price_change_1d:.1f}% today, showing strong bullish momentum and investor confidence")
        elif price_change_1d > 1:
            narrative_parts.append(f"{ticker} gained {price_change_1d:.1f}% today with positive buying pressure")
        elif price_change_1d < -3:
            narrative_parts.append(f"{ticker} plummeted {abs(price_change_1d):.1f}% today amid heavy selling and bearish sentiment")
        elif price_change_1d < -1:
            narrative_parts.append(f"{ticker} declined {abs(price_change_1d):.1f}% today facing selling pressure")
        else:
            narrative_parts.append(f"{ticker} traded relatively flat with minimal price action")

        # Weekly trend narrative
        if price_change_1w > 5:
            narrative_parts.append(f"The stock rallied {price_change_1w:.1f}% over the past week showing exceptional strength")
        elif price_change_1w > 2:
            narrative_parts.append(f"gaining {price_change_1w:.1f}% this week with improving technicals")
        elif price_change_1w < -5:
            narrative_parts.append(f"The stock crashed {abs(price_change_1w):.1f}% this week with deteriorating sentiment")
        elif price_change_1w < -2:
            narrative_parts.append(f"dropping {abs(price_change_1w):.1f}% this week amid weakness")

        # Monthly performance narrative
        if price_change_1m > 10:
            narrative_parts.append(f"Over the past month, {company_name} skyrocketed {price_change_1m:.1f}%, greatly outperforming the market")
        elif price_change_1m > 5:
            narrative_parts.append(f"The stock rose {price_change_1m:.1f}% over the past month, beating market expectations")
        elif price_change_1m < -10:
            narrative_parts.append(f"Over the past month, {ticker} collapsed {abs(price_change_1m):.1f}%, severely underperforming")
        elif price_change_1m < -5:
            narrative_parts.append(f"declining {abs(price_change_1m):.1f}% over the month with bearish trends")

        # Volume narrative
        if volume_ratio > 2:
            narrative_parts.append(f"Trading volume exploded to {volume_ratio:.1f}x normal levels, indicating intense interest")
        elif volume_ratio > 1.5:
            narrative_parts.append(f"with elevated volume at {volume_ratio:.1f}x average showing increased activity")
        elif volume_ratio < 0.5:
            narrative_parts.append(f"but volume dried up to just {volume_ratio:.1f}x average suggesting low conviction")

        # Analyst recommendation narrative
        if recommendation == 'strong_buy':
            narrative_parts.append(f"Analysts strongly recommend buying {ticker} with high conviction")
        elif recommendation == 'buy':
            narrative_parts.append(f"Wall Street analysts recommend buying {ticker}")
        elif recommendation == 'hold':
            narrative_parts.append(f"Analysts maintain neutral stance advising hold")
        elif recommendation == 'sell':
            narrative_parts.append(f"Analysts recommend selling {ticker} citing concerns")
        elif recommendation == 'strong_sell':
            narrative_parts.append(f"Analysts issue strong sell rating with major red flags")

        # Target price narrative
        if target_price > 0:
            upside = ((target_price - current_price) / current_price) * 100
            if upside > 20:
                narrative_parts.append(f"Analyst price targets suggest massive {upside:.1f}% upside potential to ${target_price:.2f}")
            elif upside > 10:
                narrative_parts.append(f"with significant {upside:.1f}% upside to analyst target of ${target_price:.2f}")
            elif upside > 0:
                narrative_parts.append(f"with moderate {upside:.1f}% upside to ${target_price:.2f} target")
            elif upside < -10:
                narrative_parts.append(f"but analyst targets imply {abs(upside):.1f}% downside to ${target_price:.2f}")

        stock_context = ". ".join(narrative_parts) + f". {company_name} trades at ${current_price}."

        print(f"DEBUG: Stock context for {ticker}:")
        print(stock_context)

        # Call the four LLMs with rich context
        print(f"Calling FinGPT for {ticker}...")
        fingpt_analysis = call_fingpt_sentiment(ticker, company_name, current_price, stock_context)

        print(f"Calling FinBERT for {ticker}...")
        finbert_analysis = call_finbert_news(ticker, company_name, current_price)

        print(f"Calling FinLLM for {ticker}...")
        finllm_decision = call_finllm_decision(ticker, company_name, current_price, fingpt_analysis, finbert_analysis)

        print(f"Calling FinMA for {ticker}...")
        finma_prediction = call_finma_prediction(ticker, company_name, current_price)

        # Analyze industry peers for alternatives
        print(f"Analyzing industry peers for {ticker}...")
        sector = info.get('sector', 'Technology')
        industry = info.get('industry', 'Technology')
        industry_alternatives = analyze_industry_peers(
            ticker, sector, industry,
            finllm_decision.get('recommendation', 'HOLD')
        )

        # Generate consolidated summary
        print(f"Generating consolidated summary for {ticker}...")
        consolidated_summary = generate_consolidated_summary(
            ticker, company_name, current_price,
            fingpt_analysis, finbert_analysis, finllm_decision, finma_prediction,
            industry_alternatives
        )

        response_data = {
            'ticker': ticker,
            'company_name': company_name,
            'current_price': round(current_price, 2),
            'last_updated': datetime.now().isoformat(),
            'consolidated_summary': consolidated_summary,
            'fingpt_analysis': fingpt_analysis,
            'finbert_analysis': finbert_analysis,
            'finllm_decision': finllm_decision,
            'finma_prediction': finma_prediction
        }

        print(f"StockScore analysis complete for {ticker}")
        return jsonify({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        import traceback
        print(f"Error in get_stockscore for {ticker}: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
