// Global variables
let stocksData = null;

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTopStocks();
    loadMethodology();
});

// Tab switching
function showTab(timeframe) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab
    event.target.classList.add('active');
    document.getElementById(timeframe).classList.add('active');
}

// Load top 20 stocks
async function loadTopStocks() {
    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const response = await fetch('/api/top-stocks');
        const data = await response.json();

        if (data.success) {
            stocksData = data.data;
            displayStocks('short', stocksData.short_term);
            displayStocks('mid', stocksData.mid_term);
            displayStocks('long', stocksData.long_term);
            updateLastUpdate(stocksData.generated_at);
        } else {
            showError('Failed to load stock data: ' + data.error);
        }
    } catch (error) {
        showError('Error loading stocks: ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// Display stocks in table
function displayStocks(timeframe, stocks) {
    const container = document.getElementById(timeframe);

    if (!stocks || stocks.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No stocks available for this timeframe.</div>';
        return;
    }

    // Create table
    let html = `
        <div class="table-responsive">
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Ticker</th>
                        <th>Company</th>
                        <th>Sector</th>
                        <th>Current Price</th>
                        <th>Predicted Price</th>
                        <th>Change %</th>
                        <th>Score</th>
                        <th>Analysis Reasons</th>
                    </tr>
                </thead>
                <tbody>
    `;

    stocks.forEach((stock, index) => {
        const prediction = stock[timeframe.replace('tab-', '') + '_term'] || stock.short_term;
        const predictedPrice = prediction.predicted_price;

        // Safe price formatting
        const currentPriceStr = stock.current_price ? `$${stock.current_price.toFixed(2)}` : 'N/A';
        const predictedPriceStr = predictedPrice ? `$${predictedPrice.toFixed(2)}` : 'N/A';

        // Safe change calculation
        let changePercent = 0;
        let changePercentStr = 'N/A';
        if (predictedPrice && stock.current_price) {
            changePercent = ((predictedPrice - stock.current_price) / stock.current_price * 100);
            changePercentStr = `${changePercent > 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
        }

        const scoreClass = stock.prediction_score >= 60 ? 'high' : stock.prediction_score >= 40 ? 'medium' : 'low';
        const changeClass = changePercent >= 0 ? 'positive' : 'negative';

        html += `
            <tr>
                <td>${index + 1}</td>
                <td><span class="ticker">${stock.ticker}</span></td>
                <td>
                    <div class="company-name">${stock.company_name}</div>
                </td>
                <td><span class="sector-badge">${stock.sector}</span></td>
                <td><span class="price">${currentPriceStr}</span></td>
                <td><span class="price">${predictedPriceStr}</span></td>
                <td><span class="price-change ${changeClass}">${changePercentStr}</span></td>
                <td><span class="score ${scoreClass}">${stock.prediction_score}</span></td>
                <td><div class="reasons">${stock.reasons || 'Analysis in progress'}</div></td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    // Mobile cards for responsive design
    html += '<div class="mobile-cards">';
    stocks.forEach((stock, index) => {
        const prediction = stock[timeframe.replace('tab-', '') + '_term'] || stock.short_term;
        const predictedPrice = prediction.predicted_price;

        // Safe price formatting
        const currentPriceStr = stock.current_price ? `$${stock.current_price.toFixed(2)}` : 'N/A';
        const predictedPriceStr = predictedPrice ? `$${predictedPrice.toFixed(2)}` : 'N/A';

        // Safe change calculation
        let changePercent = 0;
        let changePercentStr = 'N/A';
        if (predictedPrice && stock.current_price) {
            changePercent = ((predictedPrice - stock.current_price) / stock.current_price * 100);
            changePercentStr = `${changePercent > 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
        }

        const scoreClass = stock.prediction_score >= 60 ? 'high' : stock.prediction_score >= 40 ? 'medium' : 'low';
        const changeClass = changePercent >= 0 ? 'positive' : 'negative';

        html += `
            <div class="stock-card">
                <div class="stock-card-header">
                    <div>
                        <span class="ticker">${stock.ticker}</span>
                        <div class="company-name">${stock.company_name}</div>
                    </div>
                    <span class="score ${scoreClass}">${stock.prediction_score}</span>
                </div>
                <div class="stock-card-body">
                    <div><strong>Sector:</strong> ${stock.sector}</div>
                    <div><strong>Current:</strong> ${currentPriceStr}</div>
                    <div><strong>Predicted:</strong> ${predictedPriceStr}</div>
                    <div class="${changeClass}"><strong>Change:</strong> ${changePercentStr}</div>
                    <div style="grid-column: 1 / -1;"><strong>Reasons:</strong> ${stock.reasons}</div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

// Search stock
async function searchStock() {
    const searchInput = document.getElementById('stockSearch');
    const ticker = searchInput.value.trim().toUpperCase();

    if (!ticker) {
        showError('Please enter a stock ticker');
        return;
    }

    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing ' + ticker + '...</p></div>';

    try {
        const response = await fetch(`/api/search/${ticker}`);
        const data = await response.json();

        if (data.success) {
            displayStockDetail(data.data);
        } else {
            resultsContainer.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
}

// Handle Enter key in search box
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('stockSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchStock();
            }
        });
    }
});

// Display detailed stock analysis
function displayStockDetail(stock) {
    const container = document.getElementById('searchResults');

    const ai = stock.ai_analysis || {};
    const market = stock.market_context || {};

    // Helper function to safely format price
    const formatPrice = (price) => {
        if (price === null || price === undefined || isNaN(price)) {
            return 'N/A';
        }
        return `$${parseFloat(price).toFixed(2)}`;
    };

    let html = `
        <div class="stock-detail">
            <div class="stock-header">
                <div class="stock-info">
                    <h3>${stock.ticker}</h3>
                    <div class="company-name">${stock.company_name}</div>
                    <span class="sector-badge">${stock.sector}</span>
                    <span class="sector-badge" style="background: #ffe7f0; color: #c2185b;">${stock.industry}</span>
                </div>
                <div class="current-price">
                    <div class="label">${stock.price_label || 'Current Price'}</div>
                    <div class="price">${formatPrice(stock.current_price)}</div>
                </div>
            </div>

            <div class="analysis-section">
                <h4>🤖 AI Analysis</h4>
                <div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 20px;">
                    <div style="margin-bottom: 10px;">
                        <strong>Outlook:</strong>
                        <span style="color: #667eea; font-size: 1.2em; font-weight: 600;">${ai.outlook || 'N/A'}</span>
                        <span style="margin-left: 15px; color: #6c757d;">Confidence: ${ai.confidence || 'N/A'}</span>
                    </div>
                    <p style="color: #495057; line-height: 1.8;">${ai.summary || 'Analysis unavailable'}</p>
                </div>
            </div>

            <div class="predictions-grid">
                <div class="prediction-card">
                    <h4>Short Term</h4>
                    <div class="timeframe">${stock.short_term.timeframe}</div>
                    <div class="predicted-price">${formatPrice(stock.short_term.predicted_price)}</div>
                    <div class="price-change ${getPriceChangeClass(stock.short_term.predicted_price, stock.current_price)}">
                        ${getPriceChange(stock.short_term.predicted_price, stock.current_price)}
                    </div>
                    <div class="recommendation">${stock.recommendations.short_term}</div>
                </div>

                <div class="prediction-card">
                    <h4>Mid Term</h4>
                    <div class="timeframe">${stock.mid_term.timeframe}</div>
                    <div class="predicted-price">${formatPrice(stock.mid_term.predicted_price)}</div>
                    <div class="price-change ${getPriceChangeClass(stock.mid_term.predicted_price, stock.current_price)}">
                        ${getPriceChange(stock.mid_term.predicted_price, stock.current_price)}
                    </div>
                    <div class="recommendation">${stock.recommendations.mid_term}</div>
                </div>

                <div class="prediction-card">
                    <h4>Long Term</h4>
                    <div class="timeframe">${stock.long_term.timeframe}</div>
                    <div class="predicted-price">${formatPrice(stock.long_term.predicted_price)}</div>
                    <div class="price-change ${getPriceChangeClass(stock.long_term.predicted_price, stock.current_price)}">
                        ${getPriceChange(stock.long_term.predicted_price, stock.current_price)}
                    </div>
                    <div class="recommendation">${stock.recommendations.long_term}</div>
                </div>
            </div>

            <div class="analysis-section">
                <h4>📊 Market & Economic Context</h4>
                <div class="analysis-grid">
                    ${market.market_sentiment ? `
                    <div class="analysis-item">
                        <h5>Market Sentiment</h5>
                        <p><strong>${market.market_sentiment.sentiment}</strong></p>
                        <p>${market.market_sentiment.description}</p>
                    </div>
                    ` : ''}

                    ${market.sector_analysis ? `
                    <div class="analysis-item">
                        <h5>Sector Performance</h5>
                        <p><strong>${market.sector_analysis.trend}</strong></p>
                        <p>${market.sector_analysis.description}</p>
                    </div>
                    ` : ''}

                    ${market.interest_rate_environment ? `
                    <div class="analysis-item">
                        <h5>Interest Rate Environment</h5>
                        <p><strong>10Y Yield: ${market.interest_rate_environment.current_yield}%</strong></p>
                        <p>${market.interest_rate_environment.impact}</p>
                    </div>
                    ` : ''}

                    ${market.economic_indicators ? `
                    <div class="analysis-item">
                        <h5>Economic Indicators</h5>
                        <p><strong>Inflation:</strong> ${market.economic_indicators.inflation.status} - ${market.economic_indicators.inflation.impact}</p>
                        <p><strong>GDP:</strong> ${market.economic_indicators.gdp_growth.status} - ${market.economic_indicators.gdp_growth.impact}</p>
                    </div>
                    ` : ''}

                    ${market.geopolitical_context ? `
                    <div class="analysis-item">
                        <h5>Geopolitical Factors</h5>
                        <p><strong>Risk Level:</strong> ${market.geopolitical_context.risk_level}</p>
                        <p>${market.geopolitical_context.recommendation}</p>
                    </div>
                    ` : ''}
                </div>
            </div>

            <div class="analysis-section">
                <h4>📝 Key Analysis Factors</h4>
                <p style="color: #495057; line-height: 1.8; padding: 15px; background: white; border-radius: 8px;">
                    ${stock.reasons}
                </p>
            </div>

            <div class="analysis-section">
                <h4>📊 Score Breakdown (Total: ${stock.prediction_score})</h4>
                <div style="background: white; padding: 20px; border-radius: 8px;">
    `;

    if (stock.score_breakdown) {
        const breakdown = stock.score_breakdown;
        html += `
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <strong>Baseline Score:</strong> ${breakdown.baseline} points
                            </div>
                            <div style="background: #e7f3ff; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                ${breakdown.baseline_pct}%
                            </div>
                        </div>
                        <div style="background: #e7f3ff; height: 30px; border-radius: 5px; overflow: hidden;">
                            <div style="background: #0066cc; height: 100%; width: ${breakdown.baseline_pct}%;"></div>
                        </div>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <strong>Technical Analysis:</strong> ${breakdown.technical > 0 ? '+' : ''}${breakdown.technical} points
                            </div>
                            <div style="background: #d4edda; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                ${breakdown.technical_pct}%
                            </div>
                        </div>
                        <div style="background: #d4edda; height: 30px; border-radius: 5px; overflow: hidden;">
                            <div style="background: #28a745; height: 100%; width: ${breakdown.technical_pct}%;"></div>
                        </div>
                        <p style="font-size: 13px; color: #666; margin-top: 5px;">
                            SMA trends, RSI momentum, MACD signals, volume analysis
                        </p>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <strong>Fundamental Analysis:</strong> ${breakdown.fundamental > 0 ? '+' : ''}${breakdown.fundamental} points
                            </div>
                            <div style="background: #fff3cd; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                ${breakdown.fundamental_pct}%
                            </div>
                        </div>
                        <div style="background: #fff3cd; height: 30px; border-radius: 5px; overflow: hidden;">
                            <div style="background: #ffc107; height: 100%; width: ${breakdown.fundamental_pct}%;"></div>
                        </div>
                        <p style="font-size: 13px; color: #666; margin-top: 5px;">
                            P/E ratio, profit margins, return on equity (ROE)
                        </p>
                    </div>

                    <div style="border-top: 2px solid #ddd; padding-top: 15px; margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 18px;">Total Score:</strong>
                            <strong style="font-size: 24px; color: #667eea;">${breakdown.total}</strong>
                        </div>
                        <p style="font-size: 13px; color: #666; margin-top: 5px;">
                            Baseline (50) + Technical (${breakdown.technical > 0 ? '+' : ''}${breakdown.technical}) + Fundamental (${breakdown.fundamental > 0 ? '+' : ''}${breakdown.fundamental}) = ${breakdown.total}
                        </p>
                    </div>
        `;
    }

    html += `
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Helper functions
function getPriceChange(predicted, current) {
    if (predicted === null || predicted === undefined || isNaN(predicted) ||
        current === null || current === undefined || isNaN(current)) {
        return 'N/A';
    }
    const change = ((predicted - current) / current * 100).toFixed(2);
    return `${change > 0 ? '+' : ''}${change}%`;
}

function getPriceChangeClass(predicted, current) {
    if (predicted === null || predicted === undefined || isNaN(predicted) ||
        current === null || current === undefined || isNaN(current)) {
        return '';
    }
    return predicted >= current ? 'positive' : 'negative';
}

// Load methodology
async function loadMethodology() {
    try {
        const response = await fetch('/api/methodology');
        const data = await response.json();

        const container = document.getElementById('methodologyContent');

        let html = `
            <div class="methodology-intro">
                ${data.description}
            </div>

            <div class="components-grid">
        `;

        data.components.forEach(component => {
            html += `
                <div class="component-card">
                    <h4>${component.name}</h4>
                    <p>${component.description}</p>
                </div>
            `;
        });

        html += `
            </div>

            <div class="llm-section" style="margin-top: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
                <h3 style="margin-bottom: 20px; font-size: 24px;">🤖 Large Language Models (LLMs) Used in Analysis</h3>
        `;

        // Find and display LLM component details
        const llmComponent = data.components.find(c => c.name && c.name.includes('LLM'));
        if (llmComponent && llmComponent.llms_integrated) {
            html += `
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="font-size: 16px; line-height: 1.8; margin-bottom: 15px;"><strong>What:</strong> ${llmComponent.what}</p>
                    <p style="font-size: 16px; line-height: 1.8;"><strong>How:</strong> ${llmComponent.how}</p>
                </div>
            `;

            llmComponent.llms_integrated.forEach(llm => {
                html += `
                    <div style="background: white; color: #333; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                        <h4 style="color: #667eea; font-size: 22px; margin-bottom: 15px;">📊 ${llm.name}</h4>
                        <div style="margin-bottom: 20px;">
                            <p><strong>Provider:</strong> ${llm.provider}</p>
                            <p><strong>Model Type:</strong> ${llm.model_type}</p>
                            <p><strong>Specialization:</strong> ${llm.specialization}</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                            <h5 style="color: #667eea; margin-bottom: 10px;">Training Data</h5>
                            <p><strong>Corpus Size:</strong> ${llm.training_data.corpus_size}</p>
                            <p><strong>Sources:</strong> ${llm.training_data.sources}</p>
                            <p><strong>Approach:</strong> ${llm.training_data.training_approach}</p>
                        </div>

                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                            <h5 style="color: #667eea; margin-bottom: 10px;">Technical Specifications</h5>
                            <p><strong>Architecture:</strong> ${llm.technical_specifications.architecture}</p>
                            <p><strong>Parameters:</strong> ${llm.technical_specifications.parameters}</p>
                            <p><strong>Accuracy:</strong> ${llm.technical_specifications.accuracy}</p>
                            <p><strong>Inference Speed:</strong> ${llm.technical_specifications.inference_speed}</p>
                        </div>

                        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                            <h5 style="color: #856404; margin-bottom: 15px;">🔄 Detailed Algorithm Steps</h5>
                `;

                // Render all 9 steps
                const steps = llm.algorithm_detailed_steps;
                Object.keys(steps).forEach((stepKey, index) => {
                    const step = steps[stepKey];
                    html += `
                        <div style="background: white; padding: 15px; margin-bottom: 15px; border-radius: 6px; border-left: 3px solid #667eea;">
                            <h6 style="color: #667eea; margin-bottom: 8px;">Step ${index + 1}: ${stepKey.replace(/_/g, ' ').replace('step ' + (index + 1) + ' ', '').toUpperCase()}</h6>
                            <p style="margin-bottom: 8px;"><strong>Description:</strong> ${step.description}</p>
                    `;

                    if (step.process) html += `<p style="margin-bottom: 8px;"><strong>Process:</strong> ${step.process}</p>`;
                    if (step.endpoint) html += `<p style="margin-bottom: 8px;"><strong>Endpoint:</strong> <code style="background: #f1f1f1; padding: 2px 6px; border-radius: 3px;">${step.endpoint}</code></p>`;
                    if (step.example) html += `<p style="margin-bottom: 8px;"><strong>Example:</strong> <em>${step.example}</em></p>`;
                    if (step.code_location) html += `<p style="font-size: 13px; color: #666;"><strong>Code:</strong> ${step.code_location}</p>`;
                    if (step.attention_mechanism) html += `<p style="margin-bottom: 8px;"><strong>Attention:</strong> ${step.attention_mechanism}</p>`;
                    if (step.output_format) html += `<p style="margin-bottom: 8px;"><strong>Output:</strong> <code style="background: #f1f1f1; padding: 2px 6px; border-radius: 3px; font-size: 12px;">${step.output_format}</code></p>`;
                    if (step.scenarios) html += `<p style="margin-bottom: 8px;"><strong>Scenarios:</strong> ${step.scenarios}</p>`;
                    if (step.fallback_behavior) html += `<p style="margin-bottom: 8px;"><strong>Fallback:</strong> ${step.fallback_behavior}</p>`;

                    html += `</div>`;
                });

                html += `
                        </div>

                        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #0c5460; margin-bottom: 15px;">
                            <h5 style="color: #0c5460; margin-bottom: 10px;">Integration Workflow</h5>
                            <ol style="padding-left: 20px;">
                `;

                llm.integration_workflow.pipeline.forEach(step => {
                    html += `<li style="margin-bottom: 5px;">${step}</li>`;
                });

                html += `
                            </ol>
                        </div>

                        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h5 style="color: #155724; margin-bottom: 10px;">✅ Advantages Over Traditional Methods</h5>
                            ${Object.entries(llm.advantages_over_traditional_methods).map(([key, value]) =>
                                `<p style="margin-bottom: 8px;"><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</p>`
                            ).join('')}
                        </div>

                        <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h5 style="color: #721c24; margin-bottom: 10px;">⚠️ Limitations & Considerations</h5>
                            ${Object.entries(llm.limitations_and_considerations).map(([key, value]) =>
                                `<p style="margin-bottom: 8px;"><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</p>`
                            ).join('')}
                        </div>

                        <div style="background: #e7f3ff; padding: 15px; border-radius: 8px;">
                            <h5 style="color: #004085; margin-bottom: 10px;">🔧 Setup Requirements (Optional)</h5>
                            <p><strong>API Key:</strong> ${llm.setup_requirements.api_key}</p>
                            <p><strong>How to Obtain:</strong> ${llm.setup_requirements.obtaining_key}</p>
                            <p><strong>Configuration:</strong> ${llm.setup_requirements.configuration}</p>
                            <p><strong>Documentation:</strong> ${llm.setup_requirements.documentation}</p>
                        </div>
                    </div>
                `;
            });
        }

        html += `
            </div>

            <div class="timeframes">
                <h4>Investment Timeframes & Prediction Algorithms</h4>
                <div class="timeframe-item">
                    <strong>Short Term (${data.prediction_algorithms.short_term.timeframe}):</strong><br>
                    ${data.prediction_algorithms.short_term.methodology}
                </div>
                <div class="timeframe-item">
                    <strong>Mid Term (${data.prediction_algorithms.mid_term.timeframe}):</strong><br>
                    ${data.prediction_algorithms.mid_term.methodology}
                </div>
                <div class="timeframe-item">
                    <strong>Long Term (${data.prediction_algorithms.long_term.timeframe}):</strong><br>
                    ${data.prediction_algorithms.long_term.methodology}
                </div>
            </div>

            <div class="scoring-system">
                <h4>Scoring System</h4>
                <p><strong>Total Range:</strong> ${data.scoring_system.total_range}</p>
                <p><strong>Baseline:</strong> ${data.scoring_system.baseline} points</p>
                <p><strong>Technical Analysis:</strong> Up to ${data.scoring_system.technical_points} points</p>
                <p><strong>Fundamental Analysis:</strong> Up to ${data.scoring_system.fundamental_points} points</p>
                <div style="margin-top: 10px;">
                    <strong>Score Interpretation:</strong><br>
                    ${Object.entries(data.scoring_system.interpretation).map(([range, desc]) =>
                        `<div style="margin: 5px 0;"><strong>${range}:</strong> ${desc}</div>`
                    ).join('')}
                </div>
            </div>

            <div class="data-sources">
                <h4>Data Sources</h4>
                <p><strong>Primary:</strong> ${data.data_sources.primary}</p>
                <p><strong>Data Types:</strong> ${data.data_sources.data_types}</p>
                <p><strong>Update Frequency:</strong> ${data.data_sources.update_frequency}</p>
            </div>

            <div class="disclaimer-box">
                <strong>⚠️ Disclaimer</strong>
                <p>${data.disclaimer}</p>
            </div>
        `;

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading methodology:', error);
    }
}

// Update last update time
function updateLastUpdate(timestamp) {
    const date = new Date(timestamp);
    const formatted = date.toLocaleString();
    document.getElementById('lastUpdate').textContent = formatted;
}

// Show error
function showError(message) {
    const container = document.getElementById('searchResults') || document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.textContent = message;
    container.insertBefore(alert, container.firstChild);

    setTimeout(() => alert.remove(), 5000);
}
