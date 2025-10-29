"""
Basic test script to verify StockPredictor functionality
Run this to check if the application is working correctly
"""

import sys
from prediction_engine import StockPredictionEngine
from analysis_engine import AnalysisEngine

def test_prediction_engine():
    """Test the prediction engine"""
    print("=" * 60)
    print("Testing Prediction Engine")
    print("=" * 60)

    engine = StockPredictionEngine()

    # Test single stock analysis
    print("\n1. Testing single stock analysis (AAPL)...")
    try:
        result = engine.analyze_single_stock('AAPL')
        if result:
            print("✓ Successfully analyzed AAPL")
            print(f"  - Company: {result['company_name']}")
            print(f"  - Current Price: ${result['current_price']}")
            print(f"  - Price Label: {result['price_label']}")
            print(f"  - Score: {result['prediction_score']}")
            print(f"  - Short-term prediction: ${result['short_term']['predicted_price']}")
            print(f"  - Mid-term prediction: ${result['mid_term']['predicted_price']}")
            print(f"  - Long-term prediction: ${result['long_term']['predicted_price']}")
        else:
            print("✗ Failed to analyze AAPL")
            return False
    except Exception as e:
        print(f"✗ Error analyzing AAPL: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n2. Testing with multiple tickers...")
    test_tickers = ['MSFT', 'GOOGL', 'TSLA']
    success_count = 0

    for ticker in test_tickers:
        try:
            result = engine.analyze_single_stock(ticker)
            if result:
                print(f"✓ {ticker}: ${result['current_price']} - Score: {result['prediction_score']}")
                success_count += 1
            else:
                print(f"✗ {ticker}: Failed to analyze")
        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")

    print(f"\nSuccessfully analyzed {success_count}/{len(test_tickers)} stocks")
    return success_count > 0

def test_analysis_engine():
    """Test the analysis engine"""
    print("\n" + "=" * 60)
    print("Testing Analysis Engine")
    print("=" * 60)

    engine = AnalysisEngine()

    print("\n1. Testing comprehensive stock analysis (AAPL)...")
    try:
        result = engine.analyze_stock('AAPL')
        if result and 'error' not in result:
            print("✓ Successfully performed comprehensive analysis")
            print(f"  - Ticker: {result['ticker']}")
            print(f"  - Current Price: ${result['current_price']}")

            if 'ai_analysis' in result:
                print(f"  - AI Outlook: {result['ai_analysis'].get('outlook', 'N/A')}")
                print(f"  - Confidence: {result['ai_analysis'].get('confidence', 'N/A')}")

            if 'market_context' in result:
                print(f"  - Market Sentiment: {result['market_context']['market_sentiment']['sentiment']}")

            if 'recommendations' in result:
                print(f"  - Short-term: {result['recommendations']['short_term']}")
                print(f"  - Mid-term: {result['recommendations']['mid_term']}")
                print(f"  - Long-term: {result['recommendations']['long_term']}")

            return True
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            print(f"✗ Failed: {error_msg}")
            return False
    except Exception as e:
        print(f"✗ Error in comprehensive analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_market_analysis():
    """Test market analysis components"""
    print("\n" + "=" * 60)
    print("Testing Market Analysis Components")
    print("=" * 60)

    engine = AnalysisEngine()

    print("\n1. Testing market sentiment...")
    try:
        sentiment = engine.get_market_sentiment()
        print(f"✓ Market Sentiment: {sentiment['sentiment']}")
        print(f"  SPY Change: {sentiment['spy_change']}%")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    print("\n2. Testing interest rate analysis...")
    try:
        rates = engine.analyze_interest_rate_impact()
        print(f"✓ 10Y Yield: {rates['current_yield']}%")
        print(f"  Change (3M): {rates['change_3m']}%")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    print("\n3. Testing sector analysis...")
    try:
        sector = engine.analyze_sector_performance('Technology')
        print(f"✓ Technology Sector: {sector['trend']}")
        print(f"  Performance: {sector['performance']}%")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("StockPredictor - Basic Functionality Tests")
    print("=" * 60)

    results = []

    # Test 1: Prediction Engine
    results.append(("Prediction Engine", test_prediction_engine()))

    # Test 2: Analysis Engine
    results.append(("Analysis Engine", test_analysis_engine()))

    # Test 3: Market Analysis
    results.append(("Market Analysis", test_market_analysis()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your StockPredictor is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
