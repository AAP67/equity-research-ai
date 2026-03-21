import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from data_fetchers import (
    get_stock_data,
    get_fundamental_data,
    get_company_news,
    get_comprehensive_peer_data,
    format_market_cap,
    get_revenue_segmentation,
    get_earnings_transcript,
    get_historical_financials,
    compute_financial_trends,
    get_analyst_estimates,
    compute_valuation_context,
    get_catalyst_events
)
from ai_analyzer import (
    analyze_financial_health,
    analyze_peer_comparison,
    analyze_price_trend,
    analyze_news_sentiment,
    generate_investment_summary,
    run_business_deep_dive,
    analyze_financial_trends,
    analyze_forward_scenarios,
    analyze_relative_valuation,
    analyze_risk_framework,
    analyze_catalyst_timeline
)
from sec_parser import SECParser

def generate_html_report(ticker, company_name, sector, analyses, stock_data, fund_data, peer_data):
    """Generate standalone HTML report covering all 8 phases — for download and PDF conversion"""
    
    def _safe(val, fmt=None):
        if val is None or val == 'N/A' or val == '':
            return 'N/A'
        if fmt and isinstance(val, (int, float)):
            return fmt.format(val)
        return str(val)
    
    def _section(title, content):
        if not content or content.startswith('Error') or 'not available' in content.lower():
            return ''
        return f"""
        <div class="section">
            <h2>{title}</h2>
            <div class="analysis-box">{content}</div>
        </div>"""
    
    pe_display = _safe(fund_data.get('pe_ratio'), '{:.2f}') if fund_data else 'N/A'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{ticker} Analysis Report</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .company-info {{ background: #f8fafc; padding: 20px; border-left: 5px solid #2563eb; margin: 20px 0; border-radius: 8px; }}
        .quick-take {{ background: #fef3c7; border-left: 5px solid #f59e0b; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .quick-take h2 {{ color: #78350f; margin-top: 0; }}
        .summary {{ background: #eff6ff; border-left: 5px solid #2563eb; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .section {{ margin: 30px 0; page-break-inside: avoid; }}
        h1 {{ margin: 0; }}
        h2 {{ color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; page-break-after: avoid; margin-top: 30px; }}
        .analysis-box {{ background: #f8fafc; padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px; margin: 15px 0; white-space: pre-wrap; }}
        .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 15px 0; }}
        .metric {{ padding: 10px; background: white; border-radius: 5px; }}
        .metric strong {{ display: block; color: #64748b; font-size: 0.9em; margin-bottom: 5px; }}
        .metric-value {{ font-size: 1.2em; font-weight: 600; color: #1e293b; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; page-break-inside: avoid; }}
        th, td {{ padding: 12px; text-align: left; border: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; color: #1e293b; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 2px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.9em; }}
        @media print {{ body {{ margin: 20px; }} .no-print {{ display: none; }} * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Equity Analyst Assistant</h1>
        <p>AI-Powered Stock Analysis Report</p>
    </div>
    
    <div class="company-info">
        <h1>{company_name} ({ticker})</h1>
        <p style="margin: 5px 0; color: #64748b;">{sector}</p>
        <p style="margin: 5px 0; font-size: 0.9em; color: #64748b;">Analysis generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="quick-take">
        <h2>Quick Take</h2>
        <div class="metrics">
            <div class="metric">
                <strong>Price</strong>
                <div class="metric-value">${stock_data['current_price']}</div>
                <div style="color: {'#059669' if stock_data['price_change_pct_30d'] > 0 else '#dc2626'}; font-size: 0.9em;">{stock_data['price_change_pct_30d']:+.2f}% (30D)</div>
            </div>
            <div class="metric">
                <strong>Market Cap</strong>
                <div class="metric-value">{format_market_cap(fund_data.get('market_cap', 'N/A')) if fund_data else 'N/A'}</div>
            </div>
            <div class="metric">
                <strong>P/E Ratio</strong>
                <div class="metric-value">{pe_display}</div>
            </div>
            <div class="metric">
                <strong>Profit Margin</strong>
                <div class="metric-value">{fund_data.get('profit_margin', 'N/A') if fund_data else 'N/A'}</div>
            </div>
        </div>
    </div>
    
    <div class="summary">
        <h2>Investment Summary</h2>
        <div style="margin: 10px 0; line-height: 1.8;">{analyses.get('investment_summary', 'N/A')}</div>
    </div>
    
    {_section('Phase 2: Business Model Deep Dive', analyses.get('business_deep_dive', ''))}
    {_section('Phase 3: Financial Health Analysis', analyses.get('health_analysis', ''))}
    {_section('Phase 3: 5-Year Financial Trajectory', analyses.get('financial_trends', ''))}
    {_section('Phase 4: Forward Estimates & Scenario Analysis', analyses.get('forward_scenarios', ''))}
    {_section('Phase 5: Relative Valuation', analyses.get('relative_valuation', ''))}
    {_section('Phase 2: Peer Comparison', analyses.get('peer_analysis', ''))}
    {_section('Phase 6: Risk Framework', analyses.get('risk_framework', ''))}
    {_section('Phase 7: Catalyst Timeline', analyses.get('catalyst_timeline', ''))}
    
    <div class="section">
        <h2>Price Trend (30 Days)</h2>
        <div class="metrics">
            <div class="metric"><strong>30-Day High</strong><div class="metric-value">${stock_data['high_30d']}</div></div>
            <div class="metric"><strong>30-Day Low</strong><div class="metric-value">${stock_data['low_30d']}</div></div>
        </div>
        <div class="analysis-box">{analyses.get('trend_analysis', 'N/A')}</div>
    </div>
    
    {_section('News & Sentiment', analyses.get('news_analysis', ''))}
    
    <div style="margin-top: 30px; padding: 15px; background: #fef3c7; border-radius: 8px; font-size: 0.9em;">
        <strong>Disclaimer:</strong> This AI-generated analysis is for informational purposes only and should not be considered investment advice. 
        Always conduct your own research and consult with financial professionals before making investment decisions.
    </div>
    
    <div class="footer">
        <p><strong>Karan Rajpal</strong></p>
        <p>UC Berkeley Haas MBA '25 | LLM Validation @ Handshake AI</p>
        <p style="margin-top: 10px;"><em>Built with Claude AI (Sonnet 4), SEC EDGAR, and Financial Modeling Prep</em></p>
    </div>
</body>
</html>"""
    return html

# NOW continue with st.set_page_config...
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
            
            progress.info("📊 Step 1/11: Fetching stock data and financials...")
            stock_data = get_stock_data(ticker_input)
            fund_data = get_fundamental_data(ticker_input)
            
            if not stock_data or not fund_data:
                st.error(f"❌ Could not fetch data for {ticker_input}. Please check the ticker symbol.")
                st.stop()
            
            progress.info("📰 Step 2/11: Fetching news and peer data...")
            news = get_company_news(ticker_input, ticker_input)
            peer_data = get_comprehensive_peer_data(ticker_input, peers) if peers else {}
            
            progress.info("📜 Step 3/11: Downloading SEC filing and business data...")
            # Phase 2 data: SEC filing, revenue segments, transcripts
            sec_sections = {}
            try:
                parser = SECParser()
                filing_info = parser.get_latest_10k(ticker_input)
                if "error" not in filing_info:
                    sec_sections = parser.extract_all_sections(filing_info['file_path'])
                else:
                    print(f"SEC filing not available: {filing_info['error']}")
            except Exception as e:
                print(f"SEC parser error: {e}")
            
            segmentation_data = get_revenue_segmentation(ticker_input)
            transcript_data = get_earnings_transcript(ticker_input)
            
            progress.info("🔬 Step 4/11: AI deep dive — business model, moat, management signals...")
            deep_dive_result = run_business_deep_dive(
                ticker_input, sec_sections, segmentation_data, transcript_data
            )
            
            progress.info("📊 Step 5/11: Fetching 5-year financial history...")
            historical_data = get_historical_financials(ticker_input)
            financial_trends = compute_financial_trends(historical_data) if historical_data else None
            
            progress.info("🔮 Step 6/11: Fetching analyst estimates...")
            analyst_estimates = get_analyst_estimates(ticker_input)
            
            progress.info("🧠 Step 7/11: AI analyzing financials, trends, and scenarios...")
            health_analysis = analyze_financial_health(ticker_input, fund_data)
            trend_analysis = analyze_price_trend(ticker_input, stock_data)
            historical_trend_analysis = analyze_financial_trends(ticker_input, financial_trends) if financial_trends else None
            forward_scenarios = analyze_forward_scenarios(
                ticker_input,
                analyst_estimates,
                financial_trends.get('summary', {}) if financial_trends else {},
                stock_data.get('current_price') if stock_data else None,
                fund_data.get('pe_ratio') if fund_data else None
            ) if analyst_estimates else None
            
            progress.info("🧠 Step 8/11: AI analyzing peers and valuation...")
            valuation_context = compute_valuation_context(historical_data) if historical_data else None
            peer_analysis = analyze_peer_comparison(ticker_input, peer_data) if peer_data else "No peer data provided."
            relative_valuation = analyze_relative_valuation(ticker_input, valuation_context, peer_data) if (valuation_context or peer_data) else None
            
            progress.info("🧠 Step 9/11: AI analyzing news and risks...")
            news_analysis = analyze_news_sentiment(ticker_input, news)
            
            # Phase 6: Risk framework — uses data already fetched
            risk_framework = analyze_risk_framework(
                ticker_input,
                sec_sections.get('risk_factors', ''),
                deep_dive_result.get('stage1', {}).get('moat_signals', '') if deep_dive_result else '',
                fund_data,
                news_analysis
            )
            
            progress.info("📅 Step 10/11: Building catalyst timeline...")
            catalyst_events = get_catalyst_events(ticker_input)
            catalyst_timeline = analyze_catalyst_timeline(
                ticker_input,
                catalyst_events,
                news,
                forward_scenarios if forward_scenarios else '',
                risk_framework if risk_framework else ''
            )
            
            progress.info("🧠 Step 11/11: Generating investment summary...")
            
            # Generate summary — feed ALL phase outputs
            all_analyses = {
                'financial_health': health_analysis,
                'peer_comparison': peer_analysis,
                'price_trend': trend_analysis,
                'news_sentiment': news_analysis,
                'business_deep_dive': deep_dive_result.get('synthesis', '') if deep_dive_result else '',
                'financial_trends': historical_trend_analysis or '',
                'forward_scenarios': forward_scenarios or '',
                'relative_valuation': relative_valuation or '',
                'risk_framework': risk_framework or '',
                'catalyst_timeline': catalyst_timeline or '',
            }
            investment_summary = generate_investment_summary(ticker_input, all_analyses)
            
            progress.empty()
            st.success("✅ Analysis complete!")
            
            # Signal to Francium parent
            import json as _json
            _signal_data = _json.dumps({
                "type": "francium_signal",
                "toolId": "equity-research",
                "event": "analysis_complete",
                "data": {
                    "ticker": ticker_input,
                    "peers": peers,
                    "current_price": stock_data.get("current_price"),
                    "price_change_30d": stock_data.get("price_change_pct_30d"),
                    "pe_ratio": fund_data.get("pe_ratio") if isinstance(fund_data.get("pe_ratio"), (int, float)) else None,
                    "profit_margin": fund_data.get("profit_margin"),
                }
            })
            components.html(f"<script>window.top.postMessage({_signal_data}, '*');</script>", height=0)
            
            # Generate HTML report for download — all 8 phases
            all_analyses_dict = {
                'investment_summary': investment_summary,
                'health_analysis': health_analysis,
                'peer_analysis': peer_analysis,
                'trend_analysis': trend_analysis,
                'news_analysis': news_analysis,
                'business_deep_dive': deep_dive_result.get('synthesis', '') if deep_dive_result else '',
                'financial_trends': historical_trend_analysis or '',
                'forward_scenarios': forward_scenarios or '',
                'relative_valuation': relative_valuation or '',
                'risk_framework': risk_framework or '',
                'catalyst_timeline': catalyst_timeline or '',
            }
            
            company_name_full = fund_data.get('company_name', ticker_input) if fund_data else ticker_input
            sector_display = f"{fund_data.get('sector', 'N/A')} • {fund_data.get('industry', 'N/A')}" if fund_data else "N/A"
            
            html_report = generate_html_report(
                ticker=ticker_input,
                company_name=company_name_full,
                sector=sector_display,
                analyses=all_analyses_dict,
                stock_data=stock_data,
                fund_data=fund_data,
                peer_data=peer_data
            )
            
            # Download buttons — HTML and PDF
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="📄 Download HTML",
                    data=html_report,
                    file_name=f"{ticker_input}_Analysis_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    help="Full report as HTML — open in browser"
                )
            with col2:
                try:
                    from fpdf import FPDF
                    import io, re
                    
                    class ResearchPDF(FPDF):
                        def header(self):
                            self.set_font('Helvetica', 'B', 10)
                            self.set_text_color(100, 100, 100)
                            self.cell(0, 8, f'{ticker_input} Equity Research Report', align='R', new_x="LMARGIN", new_y="NEXT")
                            self.line(10, self.get_y(), 200, self.get_y())
                            self.ln(4)
                        def footer(self):
                            self.set_y(-15)
                            self.set_font('Helvetica', 'I', 8)
                            self.set_text_color(150, 150, 150)
                            self.cell(0, 10, f'Page {self.page_no()} | Generated {datetime.now().strftime("%B %d, %Y")} | Karan Rajpal', align='C')
                    
                    def clean_md(text):
                        if not text: return ''
                        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                        text = re.sub(r'#{1,3}\s*', '', text)
                        replacements = {
                            '\u2014': '-', '\u2013': '-', '\u2012': '-',
                            '\u2019': "'", '\u2018': "'",
                            '\u201c': '"', '\u201d': '"',
                            '\u2026': '...', '\u2022': '-',
                            '\u2192': '->', '\u2190': '<-',
                            '\u2265': '>=', '\u2264': '<=',
                            '\u00d7': 'x', '\u2212': '-',
                            '\u200b': '', '\u00a0': ' ',
                        }
                        for old, new in replacements.items():
                            text = text.replace(old, new)
                        text = text.encode('latin-1', errors='replace').decode('latin-1')
                        return text.strip()
                    
                    def add_section(pdf, title, content):
                        if not content or 'not available' in content.lower() or content.startswith('Error'):
                            return
                        pdf.set_font('Helvetica', 'B', 13)
                        pdf.set_text_color(30, 58, 138)
                        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.ln(3)
                        pdf.set_font('Helvetica', '', 9.5)
                        pdf.set_text_color(30, 41, 59)
                        pdf.multi_cell(0, 5, clean_md(content))
                        pdf.ln(5)
                    
                    company_name_pdf = fund_data.get('company_name', ticker_input) if fund_data else ticker_input
                    sector_pdf = f"{fund_data.get('sector', 'N/A')} - {fund_data.get('industry', 'N/A')}" if fund_data else "N/A"
                    
                    pdf = ResearchPDF()
                    pdf.set_auto_page_break(auto=True, margin=20)
                    pdf.add_page()
                    
                    # Title
                    pdf.set_font('Helvetica', 'B', 22)
                    pdf.set_text_color(30, 58, 138)
                    pdf.cell(0, 12, company_name_pdf, new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font('Helvetica', '', 12)
                    pdf.set_text_color(100, 116, 139)
                    pdf.cell(0, 8, f'{sector_pdf} | {datetime.now().strftime("%B %d, %Y")}', new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(3)
                    
                    # Quick Take
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.set_text_color(30, 41, 59)
                    pe_str = f"{fund_data.get('pe_ratio', 'N/A'):.1f}x" if isinstance(fund_data.get('pe_ratio'), (int, float)) else 'N/A'
                    quick = f"Price: ${stock_data['current_price']}  |  30D: {stock_data['price_change_pct_30d']:+.1f}%  |  Mkt Cap: {format_market_cap(fund_data.get('market_cap', 'N/A'))}  |  P/E: {pe_str}  |  Margin: {fund_data.get('profit_margin', 'N/A')}"
                    pdf.cell(0, 8, quick, new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(5)
                    
                    # All sections
                    add_section(pdf, 'Investment Summary', investment_summary)
                    add_section(pdf, 'Business Model Deep Dive', deep_dive_result.get('synthesis', '') if deep_dive_result else '')
                    add_section(pdf, 'Financial Health', health_analysis)
                    add_section(pdf, '5-Year Financial Trajectory', historical_trend_analysis or '')
                    add_section(pdf, 'Forward Estimates & Scenarios', forward_scenarios or '')
                    add_section(pdf, 'Relative Valuation', relative_valuation or '')
                    add_section(pdf, 'Peer Comparison', peer_analysis)
                    add_section(pdf, 'Risk Framework', risk_framework or '')
                    add_section(pdf, 'Catalyst Timeline', catalyst_timeline or '')
                    add_section(pdf, 'Price Trend (30D)', trend_analysis)
                    add_section(pdf, 'News & Sentiment', news_analysis)
                    
                    # Disclaimer
                    pdf.ln(5)
                    pdf.set_font('Helvetica', 'I', 8)
                    pdf.set_text_color(150, 150, 150)
                    pdf.multi_cell(0, 4, 'Disclaimer: This AI-generated analysis is for informational purposes only and should not be considered investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.')
                    
                    pdf_buffer = io.BytesIO()
                    pdf.output(pdf_buffer)
                    pdf_bytes = pdf_buffer.getvalue()
                    
                    st.download_button(
                        label="📕 Download PDF",
                        data=pdf_bytes,
                        file_name=f"{ticker_input}_Analysis_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        type="primary",
                    )
                except Exception as e:
                    st.caption(f"PDF generation error: {e}")
            
            # Timestamp
            analysis_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f'<div class="timestamp">Analysis generated on {analysis_time}</div>', unsafe_allow_html=True)            
            # Company Header — uses FMP profile data already fetched
            company_name = fund_data.get('company_name', ticker_input) if fund_data else ticker_input
            sector = fund_data.get('sector', 'N/A') if fund_data else 'N/A'
            industry = fund_data.get('industry', 'N/A') if fund_data else 'N/A'
            
            st.markdown(f"""
            <div class="company-header">
                <div class="company-name">{company_name} ({ticker_input})</div>
                <div class="company-info">{sector} • {industry}</div>
            </div>
            """, unsafe_allow_html=True)
            
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
            
            # ============================================================
            # PHASE 2: Business Model Deep Dive
            # ============================================================
            st.markdown('<div class="section-header">🏢 Business Model Deep Dive</div>', unsafe_allow_html=True)
            
            # Data source status indicator
            if deep_dive_result and deep_dive_result.get('data_sources'):
                sources = deep_dive_result['data_sources']
                status_parts = []
                for source, available in sources.items():
                    status_parts.append(f"{'✅' if available else '❌'} {source}")
                st.caption("Data sources: " + " · ".join(status_parts))
            
            # Show the synthesis (guard against error strings and None)
            synthesis = deep_dive_result.get('synthesis') if deep_dive_result else None
            if synthesis and not synthesis.startswith('Error'):
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">🤖 AI Business Analysis (sourced from 10-K, earnings calls, revenue data)</div>', unsafe_allow_html=True)
                st.markdown(synthesis)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Business deep dive data not available for this ticker. Ensure SEC_EMAIL and FMP_API_KEY are configured.")
            
            # Revenue segmentation charts (if available)
            if segmentation_data:
                seg_col1, seg_col2 = st.columns(2)
                
                with seg_col1:
                    if segmentation_data.get('by_product'):
                        st.markdown("**Revenue by Segment**")
                        prod_df = pd.DataFrame(segmentation_data['by_product'])
                        prod_df['revenue_display'] = prod_df['revenue'].apply(
                            lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else f"${x/1e6:.0f}M"
                        )
                        display_df = prod_df[['segment', 'revenue_display', 'percentage']].rename(
                            columns={'segment': 'Segment', 'revenue_display': 'Revenue', 'percentage': '% of Total'}
                        )
                        st.dataframe(display_df, hide_index=True, use_container_width=True)
                
                with seg_col2:
                    if segmentation_data.get('by_geography'):
                        st.markdown("**Revenue by Geography**")
                        geo_df = pd.DataFrame(segmentation_data['by_geography'])
                        geo_df['revenue_display'] = geo_df['revenue'].apply(
                            lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else f"${x/1e6:.0f}M"
                        )
                        display_df = geo_df[['segment', 'revenue_display', 'percentage']].rename(
                            columns={'segment': 'Region', 'revenue_display': 'Revenue', 'percentage': '% of Total'}
                        )
                        st.dataframe(display_df, hide_index=True, use_container_width=True)
            
            # Expandable: show Stage 1 details for transparency
            if deep_dive_result and deep_dive_result.get('stage1'):
                with st.expander("📋 View Detailed Source Analyses"):
                    stage1 = deep_dive_result['stage1']
                    has_any = False
                    
                    if stage1.get('business_model') and not stage1['business_model'].startswith(("10-K", "Error")):
                        st.markdown("**Business Model (from 10-K)**")
                        st.markdown(stage1['business_model'])
                        st.divider()
                        has_any = True
                    
                    if stage1.get('revenue_quality') and not stage1['revenue_quality'].startswith(("Revenue seg", "Error")):
                        st.markdown("**Revenue Quality Assessment**")
                        st.markdown(stage1['revenue_quality'])
                        st.divider()
                        has_any = True
                    
                    if stage1.get('management_signals') and not stage1['management_signals'].startswith(("Earnings call", "Error")):
                        st.markdown("**Management Signals (from Earnings Calls)**")
                        st.markdown(stage1['management_signals'])
                        st.divider()
                        has_any = True
                    
                    if stage1.get('moat_signals') and not stage1['moat_signals'].startswith(("10-K Risk", "Error")):
                        st.markdown("**Competitive Moat Analysis**")
                        st.markdown(stage1['moat_signals'])
                        has_any = True
                    
                    if not has_any:
                        st.info("No detailed source analyses available — data sources may be unreachable.")
            
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
            
            # ============================================================
            # PHASE 3: Historical Financial Trends
            # ============================================================
            if financial_trends and financial_trends.get('years'):
                st.markdown('<div class="section-header">📈 5-Year Financial Trajectory</div>', unsafe_allow_html=True)
                
                summary = financial_trends.get('summary', {})
                
                # Summary metrics row
                tcol1, tcol2, tcol3, tcol4 = st.columns(4)
                with tcol1:
                    cagr_3 = summary.get('revenue_cagr_3yr')
                    st.metric("Revenue CAGR (3Y)", f"{cagr_3}%" if cagr_3 is not None else "N/A")
                with tcol2:
                    cagr_5 = summary.get('revenue_cagr_5yr')
                    st.metric("Revenue CAGR (5Y)", f"{cagr_5}%" if cagr_5 is not None else "N/A")
                with tcol3:
                    cc = summary.get('avg_cash_conversion')
                    st.metric("Avg Cash Conversion", f"{cc}%" if cc else "N/A")
                with tcol4:
                    capex = summary.get('latest_capex_pct')
                    st.metric("Capex / Revenue", f"{capex}%" if capex else "N/A")
                
                # Trend direction indicators
                tcol1, tcol2, tcol3, tcol4 = st.columns(4)
                def _trend_icon(trend):
                    if trend == 'expanding': return '🟢 Expanding'
                    elif trend == 'compressing': return '🔴 Compressing'
                    elif trend == 'stable': return '🟡 Stable'
                    else: return '⚪ N/A'
                
                with tcol1:
                    st.metric("Gross Margin", _trend_icon(summary.get('gross_margin_trend', '')))
                with tcol2:
                    st.metric("Operating Margin", _trend_icon(summary.get('operating_margin_trend', '')))
                with tcol3:
                    st.metric("Net Margin", _trend_icon(summary.get('net_margin_trend', '')))
                with tcol4:
                    st.metric("ROE", _trend_icon(summary.get('roe_trend', '')))
                
                # Historical data table
                with st.expander("📋 View 5-Year Data Table"):
                    hist_rows = []
                    for i, year in enumerate(financial_trends['years']):
                        row = {'Year': year}
                        row['Revenue'] = f"${financial_trends['revenue'][i]/1e9:.1f}B" if i < len(financial_trends['revenue']) else ''
                        row['Net Income'] = f"${financial_trends['net_income'][i]/1e9:.1f}B" if i < len(financial_trends['net_income']) else ''
                        row['Gross Margin'] = f"{financial_trends['gross_margin'][i]}%" if i < len(financial_trends['gross_margin']) else ''
                        row['Op Margin'] = f"{financial_trends['operating_margin'][i]}%" if i < len(financial_trends['operating_margin']) else ''
                        row['ROE'] = f"{financial_trends['roe'][i]}%" if i < len(financial_trends['roe']) else ''
                        row['FCF'] = f"${financial_trends['fcf'][i]/1e9:.1f}B" if i < len(financial_trends['fcf']) else ''
                        hist_rows.append(row)
                    st.dataframe(pd.DataFrame(hist_rows), hide_index=True, use_container_width=True)
                
                # AI trend analysis
                if historical_trend_analysis and not historical_trend_analysis.startswith('Error'):
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.markdown('<div class="analysis-title">🤖 AI Financial Trajectory Analysis (5-Year Trends)</div>', unsafe_allow_html=True)
                    st.markdown(historical_trend_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # ============================================================
            # PHASE 4: Forward Estimates & Scenario Analysis
            # ============================================================
            if analyst_estimates:
                st.markdown('<div class="section-header">🔮 Forward Estimates & Scenario Analysis</div>', unsafe_allow_html=True)
                
                # Consensus estimates table
                est_rows = []
                for est in analyst_estimates:
                    est_rows.append({
                        'Period': est['date'],
                        'Revenue (Avg)': f"${est['revenue_avg']/1e9:.1f}B",
                        'Revenue Range': f"${est['revenue_low']/1e9:.1f}B – ${est['revenue_high']/1e9:.1f}B",
                        'EPS (Avg)': f"${est['eps_avg']:.2f}",
                        'EPS Range': f"${est['eps_low']:.2f} – ${est['eps_high']:.2f}",
                        'Net Income (Avg)': f"${est['net_income_avg']/1e9:.1f}B",
                        'Analysts': est.get('num_analysts_eps', 'N/A'),
                    })
                st.dataframe(pd.DataFrame(est_rows), hide_index=True, use_container_width=True)
                
                # AI scenario analysis
                if forward_scenarios and not forward_scenarios.startswith('Error'):
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.markdown('<div class="analysis-title">🤖 AI Scenario Analysis (Bull / Base / Bear)</div>', unsafe_allow_html=True)
                    st.markdown(forward_scenarios)
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
            
            # ============================================================
            # PHASE 5: Relative Valuation
            # ============================================================
            if valuation_context and valuation_context.get('multiples'):
                st.markdown('<div class="section-header">⚖️ Valuation Context</div>', unsafe_allow_html=True)
                
                # Historical valuation bands table
                val_rows = []
                for m_key, m_data in valuation_context['multiples'].items():
                    if m_data.get('current') is not None:
                        vs_avg = f"{m_data['vs_avg_pct']:+.1f}%" if m_data.get('vs_avg_pct') is not None else "N/A"
                        val_rows.append({
                            'Metric': m_data['label'],
                            'Current': f"{m_data['current']:.1f}x",
                            '5Y Avg': f"{m_data['avg_5yr']:.1f}x",
                            '5Y High': f"{m_data['high_5yr']:.1f}x",
                            '5Y Low': f"{m_data['low_5yr']:.1f}x",
                            'vs Avg': vs_avg,
                        })
                
                if val_rows:
                    st.dataframe(pd.DataFrame(val_rows), hide_index=True, use_container_width=True)
                
                # AI relative valuation analysis
                if relative_valuation and not relative_valuation.startswith('Error'):
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.markdown('<div class="analysis-title">🤖 AI Relative Valuation Analysis (vs. History & Peers)</div>', unsafe_allow_html=True)
                    st.markdown(relative_valuation)
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
            
            # ============================================================
            # PHASE 6: Risk Framework
            # ============================================================
            if risk_framework and not risk_framework.startswith('Error') and not risk_framework.startswith('Insufficient'):
                st.markdown('<div class="section-header">⚠️ Risk Framework</div>', unsafe_allow_html=True)
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">🤖 AI Structured Risk Assessment (sourced from 10-K, financials, news)</div>', unsafe_allow_html=True)
                st.markdown(risk_framework)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # ============================================================
            # PHASE 7: Catalyst Timeline
            # ============================================================
            if catalyst_timeline and not catalyst_timeline.startswith('Error') and not catalyst_timeline.startswith('Insufficient'):
                st.markdown('<div class="section-header">📅 Catalyst Timeline</div>', unsafe_allow_html=True)
                
                # Show earnings surprise history if available
                if catalyst_events and catalyst_events.get('earnings'):
                    recent_earnings = [e for e in catalyst_events['earnings'] if e.get('eps_actual') and e.get('eps_estimated')]
                    if recent_earnings:
                        earn_rows = []
                        for e in recent_earnings[:4]:
                            surprise = ((e['eps_actual'] - e['eps_estimated']) / abs(e['eps_estimated'])) * 100 if e['eps_estimated'] else 0
                            earn_rows.append({
                                'Date': e['date'],
                                'EPS Est': f"${e['eps_estimated']:.2f}",
                                'EPS Actual': f"${e['eps_actual']:.2f}",
                                'Surprise': f"{surprise:+.1f}%",
                            })
                        if earn_rows:
                            st.markdown("**Recent Earnings History**")
                            st.dataframe(pd.DataFrame(earn_rows), hide_index=True, use_container_width=True)
                
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">🤖 AI Catalyst Map (Next 6-12 Months)</div>', unsafe_allow_html=True)
                st.markdown(catalyst_timeline)
                st.markdown('</div>', unsafe_allow_html=True)
            
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