import streamlit as st
import pandas as pd
from datetime import datetime
from data_fetchers import (
    get_stock_data,
    get_fundamental_data,
    get_company_news,
    get_comprehensive_peer_data,
    format_market_cap
)
from ai_analyzer import (
    analyze_financial_health,
    analyze_peer_comparison,
    analyze_price_trend,
    analyze_news_sentiment,
    generate_investment_summary
)

st.set_page_config(
    page_title="Equity Analyst Assistant | Karan Rajpal",
    page_icon="📊",
    layout="wide"
)

# Professional styling with color coding
st.markdown("""
<style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .subtitle {
        color: #e0e7ff !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Company header */
    .company-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2563eb;
    }
    
    .company-name {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .company-info {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    
    /* Quick take box */
    .quick-take {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
    }
    
    .quick-take-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #78350f;
        margin-bottom: 1rem;
    }
    
    /* Summary box */
    .summary-box {
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .summary-title {
        color: #1e40af;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.75rem;
    }
    
    /* Analysis box */
    .analysis-box {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .analysis-title {
        color: #1e40af;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Metric cards */
    .metric-positive {
        color: #059669 !important;
    }
    
    .metric-negative {
        color: #dc2626 !important;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.95rem;
    }
    
    /* Timestamp */
    .timestamp {
        color: #64748b;
        font-size: 0.85rem;
        text-align: right;
        margin-bottom: 1rem;
    }
    
    /* Highlight primary company in tables */
    .primary-row {
        background-color: #dbeafe !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Equity Analyst Assistant</h1>
    <p class="subtitle">Your AI research partner for instant stock analysis</p>
</div>
""", unsafe_allow_html=True)

st.info("💡 **Built for analysts**: Get financials, peer comparisons, price trends, and AI-powered insights in one dashboard")

# Input Section
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    ticker_input = st.text_input(
        "Stock Ticker",
        placeholder="e.g., NVDA, AAPL, MSFT",
        key="ticker"
    ).upper()

with col2:
    peers_input = st.text_input(
        "Peer Tickers (comma-separated)",
        placeholder="e.g., AMD, INTC",
        key="peers"
    )

with col3:
    st.write("")
    st.write("")
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

st.divider()

# Main Analysis
if analyze_btn and ticker_input:
    
    # Parse peers
    peers = [p.strip().upper() for p in peers_input.split(",")] if peers_input else []
    
    with st.spinner(f"Analyzing {ticker_input}..."):
        
        try:
            # Fetch all data
            progress = st.empty()
            
            progress.info("📊 Step 1/4: Fetching stock data and financials...")
            stock_data = get_stock_data(ticker_input)
            fund_data = get_fundamental_data(ticker_input)
            
            if not stock_data or not fund_data:
                st.error(f"❌ Could not fetch data for {ticker_input}. Please check the ticker symbol.")
                st.stop()
            
            progress.info("📰 Step 2/4: Fetching news and peer data...")
            news = get_company_news(ticker_input, ticker_input)
            peer_data = get_comprehensive_peer_data(ticker_input, peers) if peers else {}
            
            progress.info("🧠 Step 3/4: AI analyzing financials and trends...")
            health_analysis = analyze_financial_health(ticker_input, fund_data)
            trend_analysis = analyze_price_trend(ticker_input, stock_data)
            
            progress.info("🧠 Step 4/4: AI analyzing peers and news...")
            peer_analysis = analyze_peer_comparison(ticker_input, peer_data) if peer_data else "No peer data provided."
            news_analysis = analyze_news_sentiment(ticker_input, news)
            
            # Generate summary
            all_analyses = {
                'financial_health': health_analysis,
                'peer_comparison': peer_analysis,
                'price_trend': trend_analysis,
                'news_sentiment': news_analysis
            }
            investment_summary = generate_investment_summary(ticker_input, all_analyses)
            
            progress.empty()
            st.success("✅ Analysis complete!")
            
            # Timestamp
            analysis_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f'<div class="timestamp">Analysis generated on {analysis_time}</div>', unsafe_allow_html=True)
            
            # Company Header
            import yfinance as yf
            try:
                company = yf.Ticker(ticker_input)
                company_name = company.info.get('longName', ticker_input)
                sector = company.info.get('sector', 'N/A')
                industry = company.info.get('industry', 'N/A')
                
                st.markdown(f"""
                <div class="company-header">
                    <div class="company-name">{company_name} ({ticker_input})</div>
                    <div class="company-info">{sector} • {industry}</div>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown(f"## {ticker_input} Analysis Dashboard")
            
            # Quick Take Box
            price_change_color = "metric-positive" if stock_data['price_change_pct_30d'] > 0 else "metric-negative"
            price_arrow = "↑" if stock_data['price_change_pct_30d'] > 0 else "↓"
            
            # Format PE ratio properly
            pe_value = fund_data['pe_ratio']
            if isinstance(pe_value, (int, float)):
                pe_display = f"{pe_value:.2f}"
            else:
                pe_display = str(pe_value)
            
            st.markdown(f"""
            <div class="quick-take">
                <div class="quick-take-title">📌 Quick Take</div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                    <div>
                        <div style="font-size: 0.85rem; color: #78350f; font-weight: 500;">Price</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #78350f;">${stock_data['current_price']}</div>
                        <div class="{price_change_color}" style="font-size: 0.9rem;">{price_arrow} {stock_data['price_change_pct_30d']:+.2f}% (30D)</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #78350f; font-weight: 500;">Market Cap</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #78350f;">{format_market_cap(fund_data['market_cap'])}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #78350f; font-weight: 500;">P/E Ratio</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #78350f;">{pe_display}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: #78350f; font-weight: 500;">Profit Margin</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #78350f;">{fund_data['profit_margin']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Investment Summary - MOVED TO TOP
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.markdown('<div class="summary-title">🎯 Investment Summary</div>', unsafe_allow_html=True)
            st.markdown(investment_summary)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Key Metrics Row
            st.markdown('<div class="section-header">💰 Key Metrics</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${stock_data['current_price']}",
                    f"{stock_data['price_change_pct_30d']:+.2f}% (30D)",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "Market Cap",
                    format_market_cap(fund_data['market_cap'])
                )
            
            with col3:
                pe = fund_data['pe_ratio']
                st.metric(
                    "P/E Ratio",
                    f"{pe:.2f}" if isinstance(pe, (int, float)) else pe
                )
            
            with col4:
                st.metric(
                    "Profit Margin",
                    fund_data['profit_margin']
                )
            
            # Additional metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "ROE",
                    fund_data.get('roe', 'N/A')
                )
            
            with col2:
                st.metric(
                    "Revenue Growth (YoY)",
                    fund_data.get('revenue_growth_yoy', 'N/A')
                )
            
            with col3:
                st.metric(
                    "30-Day High",
                    f"${stock_data['high_30d']}"
                )
            
            with col4:
                st.metric(
                    "30-Day Low",
                    f"${stock_data['low_30d']}"
                )
            
            # Detailed Financials Table
            st.markdown('<div class="section-header">📊 Financial Health Metrics</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Valuation Metrics**")
                val_df = pd.DataFrame({
                    'Metric': ['P/E Ratio', 'Forward P/E', 'PEG Ratio', 'EV/EBITDA'],
                    'Value': [
                        f"{fund_data.get('pe_ratio', 'N/A'):.2f}" if isinstance(fund_data.get('pe_ratio'), (int, float)) else 'N/A',
                        f"{fund_data.get('forward_pe', 'N/A'):.2f}" if isinstance(fund_data.get('forward_pe'), (int, float)) else 'N/A',
                        f"{fund_data.get('peg_ratio', 'N/A'):.2f}" if isinstance(fund_data.get('peg_ratio'), (int, float)) else 'N/A',
                        f"{fund_data.get('ev_to_ebitda', 'N/A'):.2f}" if isinstance(fund_data.get('ev_to_ebitda'), (int, float)) else 'N/A'
                    ]
                })
                st.dataframe(val_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("**Profitability & Growth**")
                prof_df = pd.DataFrame({
                    'Metric': ['Profit Margin', 'ROE', 'ROA', 'Revenue Growth'],
                    'Value': [
                        fund_data.get('profit_margin', 'N/A'),
                        fund_data.get('roe', 'N/A'),
                        f"{fund_data.get('roa', 'N/A'):.2f}%" if isinstance(fund_data.get('roa'), (int, float)) else 'N/A',
                        fund_data.get('revenue_growth_yoy', 'N/A')
                    ]
                })
                st.dataframe(prof_df, hide_index=True, use_container_width=True)
            
            # AI Analysis
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            st.markdown('<div class="analysis-title">🤖 AI Financial Health Analysis</div>', unsafe_allow_html=True)
            st.markdown(health_analysis)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Peer Comparison
            if peer_data:
                st.markdown('<div class="section-header">🔄 Peer Comparison</div>', unsafe_allow_html=True)
                
                # Build comparison dataframe
                comp_data = []
                for ticker_sym, metrics in peer_data.items():
                    mc = metrics['market_cap']
                    change_pct = metrics['change_30d']
                    
                    # Format with color indicators
                    if change_pct != 'N/A':
                        change_str = f"{change_pct:+.2f}%" if isinstance(change_pct, (int, float)) else f"{change_pct}%"
                    else:
                        change_str = 'N/A'
                    
                    comp_data.append({
                        'Ticker': ticker_sym,
                        'Price': f"${metrics['price']}" if metrics['price'] != 'N/A' else 'N/A',
                        '30D Change': change_str,
                        'P/E': f"{metrics['pe_ratio']:.2f}" if isinstance(metrics['pe_ratio'], (int, float)) else metrics['pe_ratio'],
                        'Profit Margin': metrics['profit_margin'],
                        'ROE': metrics['roe'],
                        'Market Cap': format_market_cap(mc) if mc != 'N/A' else 'N/A'
                    })
                
                comp_df = pd.DataFrame(comp_data)
                
                # Highlight primary ticker
                def highlight_primary(row):
                    if row['Ticker'] == ticker_input:
                        return ['background-color: #dbeafe; font-weight: 600'] * len(row)
                    return [''] * len(row)
                
                styled_df = comp_df.style.apply(highlight_primary, axis=1)
                st.dataframe(styled_df, hide_index=True, use_container_width=True)
                
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">🤖 AI Peer Analysis</div>', unsafe_allow_html=True)
                st.markdown(peer_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Price Trend
            st.markdown('<div class="section-header">📈 Price Trend (30 Days)</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("30-Day High", f"${stock_data['high_30d']}")
            with col2:
                st.metric("30-Day Low", f"${stock_data['low_30d']}")
            with col3:
                st.metric("Avg Volume", f"{stock_data['avg_volume_30d']:,}")
            
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            st.markdown('<div class="analysis-title">🤖 AI Trend Analysis</div>', unsafe_allow_html=True)
            st.markdown(trend_analysis)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # News & Sentiment
            st.markdown('<div class="section-header">📰 Recent News & Sentiment</div>', unsafe_allow_html=True)
            
            if news:
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">🤖 AI Sentiment Analysis</div>', unsafe_allow_html=True)
                st.markdown(news_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
                
                with st.expander(f"📄 View {len(news)} Recent Headlines"):
                    for i, article in enumerate(news, 1):
                        st.markdown(f"**{i}. [{article['title']}]({article['url']})**")
                        st.markdown(f"*{article['source']} - {article['published_at']}*")
                        if article['description']:
                            st.markdown(f"{article['description']}")
                        st.divider()
            else:
                st.info("No recent news articles found.")
            
            # Disclaimer
            st.divider()
            st.warning("⚠️ **Disclaimer:** This AI-generated analysis is for informational purposes only and should not be considered investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.")
            
        except Exception as e:
            st.error("❌ An error occurred during analysis")
            st.exception(e)

elif analyze_btn:
    st.warning("⚠️ Please enter a stock ticker")

# Footer
st.divider()
st.markdown("""
**Karan Rajpal**  
Model Validation Expert @ Handshake AI | Partnering with OpenAI on LLM Fine-Tuning  
Former 5th Hire @ Borderless Capital | UC Berkeley Haas MBA '25

*Built with Streamlit, Claude AI (Sonnet 4), and yfinance*
""")