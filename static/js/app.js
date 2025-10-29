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
        const changePercent = ((predictedPrice - stock.current_price) / stock.current_price * 100).toFixed(2);
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
                <td><span class="price">$${stock.current_price.toFixed(2)}</span></td>
                <td><span class="price">$${predictedPrice.toFixed(2)}</span></td>
                <td><span class="price-change ${changeClass}">${changePercent > 0 ? '+' : ''}${changePercent}%</span></td>
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
        const changePercent = ((predictedPrice - stock.current_price) / stock.current_price * 100).toFixed(2);
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
                    <div><strong>Current:</strong> $${stock.current_price.toFixed(2)}</div>
                    <div><strong>Predicted:</strong> $${predictedPrice.toFixed(2)}</div>
                    <div class="${changeClass}"><strong>Change:</strong> ${changePercent > 0 ? '+' : ''}${changePercent}%</div>
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
                    <div class="label">Current Price</div>
                    <div class="price">$${stock.current_price.toFixed(2)}</div>
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
                    <div class="predicted-price">$${stock.short_term.predicted_price.toFixed(2)}</div>
                    <div class="price-change ${getPriceChangeClass(stock.short_term.predicted_price, stock.current_price)}">
                        ${getPriceChange(stock.short_term.predicted_price, stock.current_price)}
                    </div>
                    <div class="recommendation">${stock.recommendations.short_term}</div>
                </div>

                <div class="prediction-card">
                    <h4>Mid Term</h4>
                    <div class="timeframe">${stock.mid_term.timeframe}</div>
                    <div class="predicted-price">$${stock.mid_term.predicted_price.toFixed(2)}</div>
                    <div class="price-change ${getPriceChangeClass(stock.mid_term.predicted_price, stock.current_price)}">
                        ${getPriceChange(stock.mid_term.predicted_price, stock.current_price)}
                    </div>
                    <div class="recommendation">${stock.recommendations.mid_term}</div>
                </div>

                <div class="prediction-card">
                    <h4>Long Term</h4>
                    <div class="timeframe">${stock.long_term.timeframe}</div>
                    <div class="predicted-price">$${stock.long_term.predicted_price.toFixed(2)}</div>
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
        </div>
    `;

    container.innerHTML = html;
}

// Helper functions
function getPriceChange(predicted, current) {
    const change = ((predicted - current) / current * 100).toFixed(2);
    return `${change > 0 ? '+' : ''}${change}%`;
}

function getPriceChangeClass(predicted, current) {
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

            <div class="timeframes">
                <h4>Investment Timeframes</h4>
                <div class="timeframe-item">
                    <strong>Short Term:</strong> ${data.timeframes.short_term}
                </div>
                <div class="timeframe-item">
                    <strong>Mid Term:</strong> ${data.timeframes.mid_term}
                </div>
                <div class="timeframe-item">
                    <strong>Long Term:</strong> ${data.timeframes.long_term}
                </div>
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
