// StockScore JavaScript

// Format summary with highlighted sections
function formatSummaryWithHighlights(summary) {
    if (!summary) return '';

    // Split summary into main content and alternatives section
    const alternativesMarker = '💡 Alternative Investment';

    if (summary.includes(alternativesMarker)) {
        const parts = summary.split(alternativesMarker);
        const mainSummary = parts[0];
        const alternativesContent = parts[1].trim();

        // Parse the alternatives content to extract structured data
        const formattedAlternatives = `
            <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFA500 100%);
                        color: white;
                        padding: 32px;
                        border-radius: 20px;
                        margin-top: 30px;
                        box-shadow: 0 12px 40px rgba(255, 107, 107, 0.3);
                        position: relative;
                        overflow: hidden;">

                <!-- Decorative circles -->
                <div style="position: absolute; top: -50px; right: -50px; width: 150px; height: 150px;
                            background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
                <div style="position: absolute; bottom: -30px; left: -30px; width: 100px; height: 100px;
                            background: rgba(255,255,255,0.1); border-radius: 50%;"></div>

                <div style="position: relative; z-index: 1;">
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                        <div style="background: rgba(255,255,255,0.25);
                                    width: 60px;
                                    height: 60px;
                                    border-radius: 16px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 32px;
                                    backdrop-filter: blur(10px);">💡</div>
                        <div>
                            <div style="font-size: 28px; font-weight: 800; margin-bottom: 4px; letter-spacing: -0.5px;">
                                Alternative Investment Opportunities
                            </div>
                            <div style="font-size: 14px; opacity: 0.95; font-weight: 500;">
                                Better options discovered in the same industry
                            </div>
                        </div>
                    </div>

                    <div style="background: white;
                                color: #1a202c;
                                padding: 28px;
                                border-radius: 16px;
                                line-height: 1.9;
                                box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                                white-space: pre-wrap;
                                font-size: 15px;">
                        ${alternativesContent}
                    </div>
                </div>
            </div>
        `;

        // Format main summary with better structure
        const formattedMainSummary = formatMainSummary(mainSummary);
        return formattedMainSummary + formattedAlternatives;
    }

    // No alternatives section, return formatted summary
    return formatMainSummary(summary);
}

// Format the main consensus summary with better structure
function formatMainSummary(summary) {
    // Split by double line breaks to create sections
    const sections = summary.split('\n\n').filter(s => s.trim());

    let formattedHTML = '<div style="line-height: 1.9;">';

    sections.forEach(section => {
        const trimmed = section.trim();

        // Check if this is a header (contains **)
        if (trimmed.includes('**') && trimmed.split('**').length > 2) {
            // Extract the bold text
            const parts = trimmed.split('**');
            let sectionHTML = '<div style="margin-bottom: 24px;">';

            for (let i = 0; i < parts.length; i++) {
                if (i % 2 === 1) {
                    // This is the bold part - make it a header
                    if (parts[i].includes(':')) {
                        sectionHTML += `<h4 style="color: #667eea;
                                                   font-size: 17px;
                                                   font-weight: 700;
                                                   margin: 16px 0 10px 0;
                                                   display: flex;
                                                   align-items: center;
                                                   gap: 8px;">
                                         <span style="font-size: 20px;">📊</span>
                                         ${parts[i].replace(':', '')}
                                       </h4>`;
                    } else {
                        sectionHTML += `<strong style="color: #1a202c; font-weight: 700;">${parts[i]}</strong>`;
                    }
                } else {
                    sectionHTML += parts[i];
                }
            }
            sectionHTML += '</div>';
            formattedHTML += sectionHTML;
        } else {
            // Regular paragraph
            formattedHTML += `<p style="margin-bottom: 16px; color: #4a5568;">${trimmed}</p>`;
        }
    });

    formattedHTML += '</div>';
    return formattedHTML;
}

// Toggle collapsible sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById(sectionId + '-icon');

    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.textContent = '▼';
    } else {
        section.style.display = 'none';
        icon.textContent = '▶';
    }
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

    // Scroll to results area
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

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
    const verdictIcon = data.consolidated_summary.overall_verdict === 'BULLISH' ? '📈' :
                       data.consolidated_summary.overall_verdict === 'BEARISH' ? '📉' : '➡️';
    const verdictColor = data.consolidated_summary.overall_verdict === 'BULLISH' ? '#28a745' :
                        data.consolidated_summary.overall_verdict === 'BEARISH' ? '#dc3545' : '#ffc107';

    let html = `
        <div style="max-width: 1200px; margin: 30px auto;">

            <!-- Stock Header Card -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px;
                        border-radius: 16px;
                        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                        margin-bottom: 30px;
                        color: white;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px;">
                    <div style="flex: 1; min-width: 300px;">
                        <h1 style="margin: 0 0 10px 0; font-size: 36px; font-weight: 700;">${data.ticker}</h1>
                        <p style="margin: 0 0 15px 0; font-size: 18px; opacity: 0.95;">${data.company_name}</p>
                        <div style="display: flex; align-items: baseline; gap: 15px; flex-wrap: wrap;">
                            <div style="font-size: 48px; font-weight: 700;">$${data.current_price.toFixed(2)}</div>
                            <div style="font-size: 14px; opacity: 0.85;">as of ${new Date(data.last_updated).toLocaleString()}</div>
                        </div>
                    </div>
                    <div style="text-align: right; min-width: 200px;">
                        <div style="background: rgba(255,255,255,0.2);
                                    padding: 20px;
                                    border-radius: 12px;
                                    backdrop-filter: blur(10px);">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">AI Verdict</div>
                            <div style="font-size: 36px; margin-bottom: 5px;">${verdictIcon}</div>
                            <div style="font-size: 24px; font-weight: 700;">${data.consolidated_summary.overall_verdict}</div>
                            <div style="font-size: 18px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">
                                ${data.consolidated_summary.recommendation}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Stats Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #28a745;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Positive Signals</div>
                    <div style="font-size: 42px; font-weight: 700; color: #28a745;">${data.consolidated_summary.positive_signals}</div>
                    <div style="font-size: 12px; color: #999; margin-top: 5px;">AI models detecting bullish trends</div>
                </div>
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #dc3545;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Negative Signals</div>
                    <div style="font-size: 42px; font-weight: 700; color: #dc3545;">${data.consolidated_summary.negative_signals}</div>
                    <div style="font-size: 12px; color: #999; margin-top: 5px;">AI models detecting bearish trends</div>
                </div>
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #667eea;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Confidence</div>
                    <div style="font-size: 32px; font-weight: 700; color: #667eea;">${data.consolidated_summary.confidence}</div>
                    <div style="font-size: 12px; color: #999; margin-top: 5px;">AI consensus strength</div>
                </div>
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #17a2b8;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">30-Day Outlook</div>
                    <div style="font-size: 18px; font-weight: 700; color: #17a2b8; line-height: 1.3;">${data.consolidated_summary.price_outlook}</div>
                    <div style="font-size: 12px; color: #999; margin-top: 5px;">Predicted price range</div>
                </div>
            </div>

            <!-- Action Statement Card -->
            <div style="background: ${verdictColor};
                        color: white;
                        padding: 25px;
                        border-radius: 12px;
                        margin-bottom: 30px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 12px;">
                    <div style="font-size: 32px;">${verdictIcon}</div>
                    <div style="font-size: 20px; font-weight: 700;">Recommended Action</div>
                </div>
                <div style="font-size: 18px; line-height: 1.6; font-weight: 500;">
                    ${data.consolidated_summary.action_statement}
                </div>
            </div>

            <!-- AI Consensus Analysis (Collapsible) - Ultra Modern Design -->
            <div style="background: white;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                        margin-bottom: 24px;
                        overflow: hidden;
                        border: 1px solid rgba(102, 126, 234, 0.1);">
                <div onclick="toggleSection('consensus-details')"
                     style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 32px;
                            cursor: pointer;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            user-select: none;
                            position: relative;
                            overflow: hidden;
                            transition: all 0.3s;">

                    <!-- Decorative animated gradient circles -->
                    <div style="position: absolute;
                                top: -60px;
                                right: -60px;
                                width: 180px;
                                height: 180px;
                                background: rgba(255,255,255,0.1);
                                border-radius: 50%;
                                animation: pulse 3s ease-in-out infinite;"></div>
                    <div style="position: absolute;
                                bottom: -40px;
                                left: -40px;
                                width: 120px;
                                height: 120px;
                                background: rgba(255,255,255,0.08);
                                border-radius: 50%;"></div>

                    <div style="position: relative; z-index: 1; display: flex; align-items: center; gap: 20px;">
                        <div style="background: rgba(255,255,255,0.25);
                                    width: 70px;
                                    height: 70px;
                                    border-radius: 18px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 38px;
                                    backdrop-filter: blur(10px);
                                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);">🤖</div>
                        <div>
                            <div style="font-size: 28px;
                                        font-weight: 800;
                                        margin-bottom: 6px;
                                        letter-spacing: -0.5px;">AI Consensus Analysis</div>
                            <div style="font-size: 15px;
                                        opacity: 0.95;
                                        font-weight: 500;">Comprehensive insights from 4 specialized financial AI models</div>
                        </div>
                    </div>
                    <div id="consensus-details-icon"
                         style="font-size: 28px;
                                transition: transform 0.3s;
                                position: relative;
                                z-index: 1;
                                background: rgba(255,255,255,0.2);
                                width: 48px;
                                height: 48px;
                                border-radius: 12px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                backdrop-filter: blur(10px);">▼</div>
                </div>
                <div id="consensus-details"
                     style="padding: 40px;
                            background: linear-gradient(to bottom, #f8f9fa 0%, white 100%);
                            font-size: 15px;">
                    ${formatSummaryWithHighlights(data.consolidated_summary.summary)}
                </div>
            </div>

            <style>
                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 0.1; }
                    50% { transform: scale(1.1); opacity: 0.15; }
                }
            </style>

            <!-- Individual Model Analysis Header -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                <h3 style="margin: 0 0 10px 0; color: #667eea; font-size: 20px;">📊 Detailed Model Breakdown</h3>
                <p style="color: #666; margin: 0; line-height: 1.6;">Click on each model below to view detailed analysis. Each AI model specializes in different aspects of financial analysis.</p>
            </div>

            <!-- FinGPT (Collapsible) -->
            <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; overflow: hidden;">
                <div onclick="toggleSection('fingpt-details')"
                     style="padding: 20px;
                            cursor: pointer;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            background: linear-gradient(90deg, ${data.fingpt_analysis.sentiment === 'positive' ? '#d4edda' : data.fingpt_analysis.sentiment === 'negative' ? '#f8d7da' : '#fff3cd'} 0%, white 50%);
                            border-left: 4px solid ${data.fingpt_analysis.sentiment === 'positive' ? '#28a745' : data.fingpt_analysis.sentiment === 'negative' ? '#dc3545' : '#ffc107'};
                            user-select: none;">
                    <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                        <div style="font-size: 36px;">📊</div>
                        <div>
                            <div style="font-size: 18px; font-weight: 700; color: #333; margin-bottom: 4px;">FinGPT - Sentiment Analysis</div>
                            <div style="font-size: 14px; color: #666;">Sentiment: <strong style="color: ${data.fingpt_analysis.sentiment === 'positive' ? '#28a745' : data.fingpt_analysis.sentiment === 'negative' ? '#dc3545' : '#856404'};">${data.fingpt_analysis.sentiment.toUpperCase()}</strong> (${(data.fingpt_analysis.confidence * 100).toFixed(1)}% confidence)</div>
                        </div>
                    </div>
                    <div id="fingpt-details-icon" style="font-size: 20px; transition: transform 0.3s;">▶</div>
                </div>
                <div id="fingpt-details" style="display: none; padding: 25px; background: #fafbfc; border-top: 1px solid #e9ecef;">
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">💹 Price Movement Prediction</div>
                        <div style="color: #333; line-height: 1.6;">${data.fingpt_analysis.price_prediction}</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">📝 Detailed Analysis</div>
                        <div style="color: #555; line-height: 1.7;">${data.fingpt_analysis.summary}</div>
                    </div>
                </div>
            </div>

            <!-- FinBERT (Collapsible) -->
            <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; overflow: hidden;">
                <div onclick="toggleSection('finbert-details')"
                     style="padding: 20px;
                            cursor: pointer;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            background: linear-gradient(90deg, ${data.finbert_analysis.sentiment === 'positive' ? '#d4edda' : data.finbert_analysis.sentiment === 'negative' ? '#f8d7da' : '#fff3cd'} 0%, white 50%);
                            border-left: 4px solid ${data.finbert_analysis.sentiment === 'positive' ? '#28a745' : data.finbert_analysis.sentiment === 'negative' ? '#dc3545' : '#ffc107'};
                            user-select: none;">
                    <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                        <div style="font-size: 36px;">📰</div>
                        <div>
                            <div style="font-size: 18px; font-weight: 700; color: #333; margin-bottom: 4px;">FinBERT - News Classification</div>
                            <div style="font-size: 14px; color: #666;">News Sentiment: <strong style="color: ${data.finbert_analysis.sentiment === 'positive' ? '#28a745' : data.finbert_analysis.sentiment === 'negative' ? '#dc3545' : '#856404'};">${data.finbert_analysis.sentiment.toUpperCase()}</strong> (${(data.finbert_analysis.score * 100).toFixed(1)}% confidence)</div>
                        </div>
                    </div>
                    <div id="finbert-details-icon" style="font-size: 20px; transition: transform 0.3s;">▶</div>
                </div>
                <div id="finbert-details" style="display: none; padding: 25px; background: #fafbfc; border-top: 1px solid #e9ecef;">
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">📊 Impact Assessment</div>
                        <div style="color: #333; line-height: 1.6;">${data.finbert_analysis.impact}</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">🔍 Key Findings</div>
                        <div style="color: #555; line-height: 1.7;">${data.finbert_analysis.findings}</div>
                    </div>
                </div>
            </div>

            <!-- FinLLM (Collapsible) -->
            <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; overflow: hidden;">
                <div onclick="toggleSection('finllm-details')"
                     style="padding: 20px;
                            cursor: pointer;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            background: linear-gradient(90deg, ${data.finllm_decision.recommendation === 'BUY' ? '#d4edda' : data.finllm_decision.recommendation === 'SELL' ? '#f8d7da' : '#fff3cd'} 0%, white 50%);
                            border-left: 4px solid ${data.finllm_decision.recommendation === 'BUY' ? '#28a745' : data.finllm_decision.recommendation === 'SELL' ? '#dc3545' : '#ffc107'};
                            user-select: none;">
                    <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                        <div style="font-size: 36px;">💼</div>
                        <div>
                            <div style="font-size: 18px; font-weight: 700; color: #333; margin-bottom: 4px;">FinLLM - Investment Decision</div>
                            <div style="font-size: 14px; color: #666;">Recommendation: <strong style="color: ${data.finllm_decision.recommendation === 'BUY' ? '#28a745' : data.finllm_decision.recommendation === 'SELL' ? '#dc3545' : '#856404'};">${data.finllm_decision.recommendation}</strong> (${data.finllm_decision.confidence} confidence)</div>
                        </div>
                    </div>
                    <div id="finllm-details-icon" style="font-size: 20px; transition: transform 0.3s;">▶</div>
                </div>
                <div id="finllm-details" style="display: none; padding: 25px; background: #fafbfc; border-top: 1px solid #e9ecef;">
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">💡 Investment Rationale</div>
                        <div style="color: #333; line-height: 1.6;">${data.finllm_decision.rationale}</div>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #dc3545; margin-bottom: 8px;">⚠️ Risk Factors</div>
                        <div style="color: #555; line-height: 1.7;">${data.finllm_decision.risks}</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">⏰ Time Horizon</div>
                        <div style="color: #555;">${data.finllm_decision.time_horizon}</div>
                    </div>
                </div>
            </div>

            <!-- FinMA (Collapsible) -->
            <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; overflow: hidden;">
                <div onclick="toggleSection('finma-details')"
                     style="padding: 20px;
                            cursor: pointer;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            background: linear-gradient(90deg, ${data.finma_prediction.movement_direction === 'Upward' ? '#d4edda' : data.finma_prediction.movement_direction === 'Downward' ? '#f8d7da' : '#e7f3ff'} 0%, white 50%);
                            border-left: 4px solid ${data.finma_prediction.movement_direction === 'Upward' ? '#28a745' : data.finma_prediction.movement_direction === 'Downward' ? '#dc3545' : '#17a2b8'};
                            user-select: none;">
                    <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                        <div style="font-size: 36px;">📈</div>
                        <div>
                            <div style="font-size: 18px; font-weight: 700; color: #333; margin-bottom: 4px;">Open FinMA - Stock Movement Prediction</div>
                            <div style="font-size: 14px; color: #666;">Direction: <strong style="color: ${data.finma_prediction.movement_direction === 'Upward' ? '#28a745' : data.finma_prediction.movement_direction === 'Downward' ? '#dc3545' : '#17a2b8'};">${data.finma_prediction.movement_direction}</strong> (${(data.finma_prediction.confidence_score * 100).toFixed(1)}% confidence)</div>
                        </div>
                    </div>
                    <div id="finma-details-icon" style="font-size: 20px; transition: transform 0.3s;">▶</div>
                </div>
                <div id="finma-details" style="display: none; padding: 25px; background: #fafbfc; border-top: 1px solid #e9ecef;">
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">🎯 Price Target Range (${data.finma_prediction.timeframe})</div>
                        <div style="font-size: 24px; font-weight: 700; color: #17a2b8;">$${data.finma_prediction.price_target_low} - $${data.finma_prediction.price_target_high}</div>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">📊 Key Technical Factors</div>
                        <div style="color: #555; line-height: 1.7;">${data.finma_prediction.key_factors}</div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">📉 Volatility Assessment</div>
                        <div style="color: #555; line-height: 1.7;">${data.finma_prediction.volatility_assessment}</div>
                    </div>
                </div>
            </div>

        </div>
    `;

    container.innerHTML = html;
}
