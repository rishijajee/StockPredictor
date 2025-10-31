// StockScore JavaScript

// Format summary with highlighted sections
function formatSummaryWithHighlights(summary) {
    if (!summary) return '';

    // Split summary into main content and alternatives section
    const alternativesMarker = '💡 Alternative Investment';

    if (summary.includes(alternativesMarker)) {
        const parts = summary.split(alternativesMarker);
        const mainSummary = parts[0];
        const alternativesSection = alternativesMarker + parts[1];

        // Format the alternatives section with special highlighting
        const formattedAlternatives = `
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        margin-top: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <div style="font-size: 22px; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center;">
                    💡 Alternative Investment Opportunities
                </div>
                <div style="background: rgba(255,255,255,0.95);
                            color: #333;
                            padding: 20px;
                            border-radius: 8px;
                            white-space: pre-wrap;
                            line-height: 1.8;">
                    ${parts[1].trim()}
                </div>
            </div>
        `;

        return `<div style="white-space: pre-wrap;">${mainSummary}</div>${formattedAlternatives}`;
    }

    // No alternatives section, return plain summary
    return `<div style="white-space: pre-wrap;">${summary}</div>`;
}

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

    // Determine colors for consolidated summary
    const summaryBgColor = data.consolidated_summary.verdict_color === 'positive' ? '#d4edda' :
                           data.consolidated_summary.verdict_color === 'negative' ? '#f8d7da' : '#fff3cd';
    const summaryBorderColor = data.consolidated_summary.verdict_color === 'positive' ? '#28a745' :
                              data.consolidated_summary.verdict_color === 'negative' ? '#dc3545' : '#ffc107';
    const verdictIcon = data.consolidated_summary.overall_verdict === 'BULLISH' ? '📈🟢' :
                       data.consolidated_summary.overall_verdict === 'BEARISH' ? '📉🔴' : '➡️🟡';

    let html = `
        <div style="margin-top: 30px;">
            <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h2 style="color: #333; margin-bottom: 10px;">${data.ticker} - ${data.company_name}</h2>
                <p style="color: #666; font-size: 14px;">Current Price: <strong style="font-size: 20px; color: #667eea;">$${data.current_price}</strong></p>
                <p style="color: #666; font-size: 14px;">Last Updated: ${new Date(data.last_updated).toLocaleString()}</p>
            </div>

            <!-- Consolidated AI Consensus Summary -->
            <div class="llm-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; margin-bottom: 30px;">
                <div class="llm-header" style="border-bottom-color: rgba(255,255,255,0.3);">
                    <div class="llm-icon" style="font-size: 40px;">${verdictIcon}</div>
                    <div>
                        <div class="llm-title" style="color: white; font-size: 24px;">AI Consensus Analysis</div>
                        <div class="llm-subtitle" style="color: rgba(255,255,255,0.9);">Comprehensive Summary from 4 Financial AI Models</div>
                    </div>
                </div>
                <div style="padding: 20px; background: rgba(255,255,255,0.1); border-radius: 8px; margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px;">
                        <div style="flex: 1; min-width: 200px;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Overall Verdict</div>
                            <div style="font-size: 32px; font-weight: bold;">${data.consolidated_summary.overall_verdict}</div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Recommendation</div>
                            <div style="font-size: 32px; font-weight: bold;">${data.consolidated_summary.recommendation}</div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Confidence Level</div>
                            <div style="font-size: 24px; font-weight: 600;">${data.consolidated_summary.confidence}</div>
                        </div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong style="font-size: 18px; display: block; margin-bottom: 10px;">Action Statement:</strong>
                        <p style="font-size: 16px; line-height: 1.6; margin: 0;">${data.consolidated_summary.action_statement}</p>
                    </div>
                    <div style="background: white; color: #333; padding: 20px; border-radius: 8px; line-height: 1.8;">
                        ${formatSummaryWithHighlights(data.consolidated_summary.summary)}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px; gap: 10px; flex-wrap: wrap;">
                        <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; flex: 1; min-width: 150px;">
                            <div style="font-size: 12px; opacity: 0.9;">Positive Signals</div>
                            <div style="font-size: 24px; font-weight: bold;">${data.consolidated_summary.positive_signals}</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; flex: 1; min-width: 150px;">
                            <div style="font-size: 12px; opacity: 0.9;">Negative Signals</div>
                            <div style="font-size: 24px; font-weight: bold;">${data.consolidated_summary.negative_signals}</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; flex: 2; min-width: 200px;">
                            <div style="font-size: 12px; opacity: 0.9;">30-Day Price Outlook</div>
                            <div style="font-size: 20px; font-weight: bold;">${data.consolidated_summary.price_outlook}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div style="background: #f0f4ff; padding: 20px; border-radius: 12px; margin-bottom: 25px; border-left: 4px solid #667eea;">
                <h3 style="margin-top: 0; color: #667eea; font-size: 20px;">📊 Detailed Model Analysis Below</h3>
                <p style="color: #666; margin-bottom: 0; line-height: 1.6;">The consolidated summary above synthesizes insights from the four AI models detailed below. Each model provides specialized analysis from different perspectives to create a comprehensive investment assessment.</p>
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
