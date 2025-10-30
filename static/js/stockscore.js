// StockScore JavaScript

// Handle Enter key in search box
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('stockScoreSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeStock();
            }
        });
    }
});

async function analyzeStock() {
    const searchInput = document.getElementById('stockScoreSearch');
    const ticker = searchInput.value.trim().toUpperCase();

    if (!ticker) {
        alert('Please enter a stock ticker');
        return;
    }

    const resultsContainer = document.getElementById('stockScoreResults');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Show loading
    loadingIndicator.style.display = 'block';
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch(`/api/stockscore/${ticker}`);
        const data = await response.json();

        loadingIndicator.style.display = 'none';

        if (data.success) {
            displayStockScoreResults(data.data);
        } else {
            resultsContainer.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        resultsContainer.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
}

function displayStockScoreResults(data) {
    const container = document.getElementById('stockScoreResults');

    let html = `
        <div style="margin-top: 30px;">
            <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h2 style="color: #333; margin-bottom: 10px;">${data.ticker} - ${data.company_name}</h2>
                <p style="color: #666; font-size: 14px;">Current Price: <strong style="font-size: 20px; color: #667eea;">$${data.current_price}</strong></p>
                <p style="color: #666; font-size: 14px;">Last Updated: ${new Date(data.last_updated).toLocaleString()}</p>
            </div>

            <!-- FinGPT Sentiment Analysis -->
            <div class="llm-card">
                <div class="llm-header">
                    <div class="llm-icon">📊</div>
                    <div>
                        <div class="llm-title">FinGPT - Sentiment Analysis & Price Movement Prediction</div>
                        <div class="llm-subtitle">GPT-based financial sentiment model</div>
                    </div>
                </div>
                <div class="sentiment-result sentiment-${data.fingpt_analysis.sentiment.toLowerCase()}">
                    <p><strong>Sentiment:</strong> <span style="font-size: 18px;">${data.fingpt_analysis.sentiment.toUpperCase()}</span></p>
                    <p><strong>Confidence:</strong> ${(data.fingpt_analysis.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Price Movement Prediction:</strong> ${data.fingpt_analysis.price_prediction}</p>
                    <p><strong>Analysis:</strong> ${data.fingpt_analysis.summary}</p>
                </div>
            </div>

            <!-- FinBERT News Classification -->
            <div class="llm-card">
                <div class="llm-header">
                    <div class="llm-icon">📰</div>
                    <div>
                        <div class="llm-title">FinBERT - News Classification</div>
                        <div class="llm-subtitle">BERT-based financial news analyzer</div>
                    </div>
                </div>
                <div class="sentiment-result sentiment-${data.finbert_analysis.sentiment.toLowerCase()}">
                    <p><strong>News Sentiment:</strong> <span style="font-size: 18px;">${data.finbert_analysis.sentiment.toUpperCase()}</span></p>
                    <p><strong>Confidence:</strong> ${(data.finbert_analysis.score * 100).toFixed(1)}%</p>
                    <p><strong>Impact Assessment:</strong> ${data.finbert_analysis.impact}</p>
                    <p><strong>Key Findings:</strong> ${data.finbert_analysis.findings}</p>
                </div>
            </div>

            <!-- FinLLM Investment Decision -->
            <div class="llm-card">
                <div class="llm-header">
                    <div class="llm-icon">💼</div>
                    <div>
                        <div class="llm-title">FinLLM - Investment Decision Making</div>
                        <div class="llm-subtitle">Instruction-tuned financial decision model</div>
                    </div>
                </div>
                <div class="sentiment-result" style="background: ${
                    data.finllm_decision.recommendation === 'BUY' ? '#d4edda' :
                    data.finllm_decision.recommendation === 'SELL' ? '#f8d7da' : '#fff3cd'
                }; border-left: 4px solid ${
                    data.finllm_decision.recommendation === 'BUY' ? '#28a745' :
                    data.finllm_decision.recommendation === 'SELL' ? '#dc3545' : '#ffc107'
                };">
                    <p><strong>Recommendation:</strong> <span style="font-size: 24px; font-weight: bold;">${data.finllm_decision.recommendation}</span></p>
                    <p><strong>Confidence:</strong> ${data.finllm_decision.confidence}</p>
                    <p><strong>Rationale:</strong> ${data.finllm_decision.rationale}</p>
                    <p><strong>Risk Factors:</strong> ${data.finllm_decision.risks}</p>
                    <p><strong>Time Horizon:</strong> ${data.finllm_decision.time_horizon}</p>
                </div>
            </div>

            <!-- FinMA Stock Movement Prediction -->
            <div class="llm-card">
                <div class="llm-header">
                    <div class="llm-icon">📈</div>
                    <div>
                        <div class="llm-title">Open FinMA - Stock Movement Prediction</div>
                        <div class="llm-subtitle">Advanced financial movement analysis model</div>
                    </div>
                </div>
                <div class="sentiment-result" style="background: ${
                    data.finma_prediction.movement_direction === 'Upward' ? '#d4edda' :
                    data.finma_prediction.movement_direction === 'Downward' ? '#f8d7da' : '#e7f3ff'
                }; border-left: 4px solid ${
                    data.finma_prediction.movement_direction === 'Upward' ? '#28a745' :
                    data.finma_prediction.movement_direction === 'Downward' ? '#dc3545' : '#17a2b8'
                };">
                    <p><strong>Movement Direction:</strong> <span style="font-size: 24px; font-weight: bold;">${data.finma_prediction.movement_direction}</span></p>
                    <p><strong>Confidence Score:</strong> ${(data.finma_prediction.confidence_score * 100).toFixed(1)}%</p>
                    <p><strong>Price Target Range (${data.finma_prediction.timeframe}):</strong> $${data.finma_prediction.price_target_low} - $${data.finma_prediction.price_target_high}</p>
                    <p><strong>Key Factors:</strong> ${data.finma_prediction.key_factors}</p>
                    <p><strong>Volatility Assessment:</strong> ${data.finma_prediction.volatility_assessment}</p>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}
