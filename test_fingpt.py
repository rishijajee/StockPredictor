#!/usr/bin/env python3
"""Test FinGPT analysis for multiple stocks"""

import requests
import json

def test_fingpt(ticker):
    print(f"\n{'='*60}")
    print(f"Testing FinGPT Analysis for {ticker}")
    print('='*60)
    
    response = requests.get(f"http://127.0.0.1:5000/api/stockscore/{ticker}")
    data = response.json()
    
    if data['success']:
        stock_data = data['data']
        fingpt = stock_data['fingpt_analysis']
        
        print(f"\nCompany: {stock_data['company_name']}")
        print(f"Current Price: ${stock_data['current_price']}")
        print(f"\n--- FinGPT Analysis ---")
        print(f"Sentiment: {fingpt['sentiment'].upper()}")
        print(f"Confidence: {fingpt['confidence']*100:.1f}%")
        print(f"Price Prediction: {fingpt['price_prediction']}")
        print(f"Summary: {fingpt['summary']}")
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")

# Test multiple stocks
tickers = ['AAPL', 'TSLA', 'NVDA']

for ticker in tickers:
    test_fingpt(ticker)

print(f"\n{'='*60}")
print("FinGPT Test Complete")
print(f"{'='*60}")
print("\nNote: Currently using fallback mode (no HF_API_KEY set locally).")
print("When deployed to Vercel with HF_API_KEY, FinGPT will provide:")
print("  - Real AI sentiment analysis (positive/negative/neutral)")
print("  - Higher confidence scores (up to 95%+)")
print("  - Specific price movement predictions (3-7% rise, 2-5% decline, etc.)")
print("  - Detailed market analysis summaries")
