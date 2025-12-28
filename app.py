import streamlit as st
from datetime import datetime
from data_fetchers import get_stock_data, get_company_news, get_sec_filings, get_peer_comparison, get_fundamental_data
from ai_analyzer import analyze_news_sentiment, analyze_price_action, identify_risks_catalysts, generate_executive_summary, analyze_fundamentals

st.set_page_config(
    page_title="AI Equity Research | Karan Rajpal",
    page_icon="📊",
    layout="wide"
)

# Clean readable styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem; 
        font-weight: 700; 
        color: #ffffff; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem; 
        border-radius: 10px; 
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.1rem; 
        color: #333; 
        margin-bottom: 0.5rem;
    }
    .author {
        font-size: 0.95rem; 
        color: #666; 
        font-style: italic; 
        margin-bottom: 2rem;
    }
    .section-title {
        font-size: 1.4rem; 
        font-weight: 600; 
        color: #1a1a1a; 
        margin-top: 2rem; 
        padding-bottom: 0.5rem; 
        border-bottom: 2px solid #4285f4;
    }
    .exec-box {
        background-color: #f0f7ff; 
        border-left: 4px solid #4285f4; 
        padding: 1.2rem; 
        border-radius: 5px; 
        margin: 1rem 0;
        color: #1a1a1a;
    }
    .analysis-box {
        background-color: #fafafa; 
        padding: 1.2rem; 
        border-radius: 5px; 
        border: 1px solid #e0e0e0; 
        margin: 1rem 0;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📊 AI Equity Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Institutional-Grade Research Briefs Powered by AI</div>', unsafe_allow_html=True)
st.markdown('<div class="author">Developed by Karan Rajpal | Model Validation Expert @ Handshake AI</div>', unsafe_allow_html=True)

# Input Section
col1, col2 = st.columns([3, 1])

with col1:
    ticker_input = st.text_input(
        "Enter Stock Ticker",
        placeholder="e.g., NVDA, AAPL, TSLA, MSFT",
        key="ticker"
    ).upper()

with col2:
    st.write("")
    st.write("")
    generate_btn = st.button("🔍 Generate Report", type="primary", use_container_width=True)

peer_tickers = st.text_input(
    "Peer Tickers (Optional)",
    placeholder="e.g., AMD, INTC",
    key="peers"
)

st.markdown("---")

# Generate Report
if generate_btn and ticker_input:
    
    with st.spinner(f"Generating research brief for {ticker_input}..."):
        
        try:
            # Fetch Data
            st.info("📥 Fetching market data...")
            stock_data = get_stock_data(ticker_input)
            
            if "error" in stock_data:
                st.error(f"❌ {stock_data['error']}")
                st.stop()
            
            news_data = get_company_news(ticker_input, ticker_input)
            sec_data = get_sec_filings(ticker_input)
            fundamental_data = get_fundamental_data(ticker_input)
            
            peer_data = None
            if peer_tickers:
                peers_list = [p.strip().upper() for p in peer_tickers.split(",")]
                peer_data = get_peer_comparison(ticker_input, peers_list)
            
            # AI Analysis
            st.info("🧠 Running AI analysis...")
            sentiment = analyze_news_sentiment(ticker_input, news_data['articles'])
            price_analysis = analyze_price_action(ticker_input, stock_data, peer_data)
            risks = identify_risks_catalysts(ticker_input, news_data['articles'], stock_data)
            fundamental_analysis = analyze_fundamentals(ticker_input, fundamental_data)
            
            all_analyses = {
                'sentiment': sentiment.get('sentiment_analysis', ''),
                'price_action': price_analysis.get('price_analysis', ''),
                'risks_catalysts': risks.get('risks_catalysts', ''),
                'fundamentals': fundamental_analysis.get('fundamental_analysis', '')
            }
            exec_summary = generate_executive_summary(ticker_input, all_analyses)
            
            st.success("✅ Report generated!")
            
            # Display Report
            st.markdown("##")
            st.markdown(f"## {ticker_input} Research Brief")
            st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
            
            # Executive Summary
            st.markdown("### 📋 Executive Summary")
            st.markdown(f'<div class="exec-box">{exec_summary.get("executive_summary", "Not available")}</div>', 
                       unsafe_allow_html=True)
            
            # Key Metrics
            st.markdown("### 📊 Key Metrics (30-Day)")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${stock_data['current_price']}", 
                       f"{stock_data['price_change_pct_30d']}%")
            col2.metric("30-Day High", f"${stock_data['high_30d']}")
            col3.metric("30-Day Low", f"${stock_data['low_30d']}")
            col4.metric("Avg Volume", f"{stock_data['avg_volume_30d']/1e6:.1f}M")
            
            # Price Action
            st.markdown("### 📈 Price Action Analysis")
            st.markdown(f'<div class="analysis-box">{price_analysis.get("price_analysis", "Not available")}</div>', 
                       unsafe_allow_html=True)
            
            # Sentiment
            st.markdown("### 📰 News Sentiment")
            st.markdown(f'<div class="analysis-box">{sentiment.get("sentiment_analysis", "Not available")}</div>', 
                       unsafe_allow_html=True)
            
            # Headlines
            if news_data.get('articles'):
                with st.expander(f"📑 Recent Headlines ({news_data['news_count']} articles)"):
                    for i, article in enumerate(news_data['articles'][:5], 1):
                        st.markdown(f"**{i}. [{article['source']}]** {article['title']}")
                        if article['url']:
                            st.markdown(f"[Read more →]({article['url']})")
                        st.markdown("")
            
            # Risks & Catalysts
            st.markdown("### ⚠️ Risks & Catalysts")
            st.markdown(f'<div class="analysis-box">{risks.get("risks_catalysts", "Not available")}</div>', 
                       unsafe_allow_html=True)
            
            # Peers
            if peer_data and peer_data.get('comparison_data'):
                st.markdown("### 🔄 Peer Comparison")
                peer_cols = st.columns(min(len(peer_data['comparison_data']), 4))
                for i, comp in enumerate(peer_data['comparison_data']):
                    with peer_cols[i % len(peer_cols)]:
                        label = f"{comp['ticker']}" + (" ⭐" if comp['is_primary'] else "")
                        st.metric(label, f"${comp['price']}", f"{comp['change_30d_pct']:+.2f}%")
            
            # SEC Filings
            st.markdown("### 📄 SEC Filings")
            if sec_data.get('filings'):
                for filing in sec_data['filings'][:3]:
                    st.write(f"**{filing['type']}** - {filing['date']}")
                    if filing.get('url') and filing['url'] != 'N/A':
                        st.markdown(f"[View Filing →]({filing['url']})")
            
            st.info("**Disclaimer:** AI-generated for informational purposes only. Not investment advice.")
            
        except Exception as e:
            st.error("❌ Error generating report")
            st.exception(e)

elif generate_btn:
    st.warning("⚠️ Please enter a ticker")

# Footer
st.markdown("---")
st.markdown("""
**Karan Rajpal**  
Model Validation Expert @ Handshake AI | Partnering with OpenAI  
Former 5th Hire @ Borderless Capital | UC Berkeley Haas MBA '25

*Built with Streamlit, Claude AI, and Alpha Vantage*
""")