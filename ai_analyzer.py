import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def analyze_financial_health(ticker, fundamental_data):
    """
    Analyze company's financial health based on key metrics
    """
    prompt = f"""Analyze {ticker}'s financial health based on these metrics:

- P/E Ratio: {fundamental_data.get('pe_ratio', 'N/A')}
- Profit Margin: {fundamental_data.get('profit_margin', 'N/A')}
- ROE: {fundamental_data.get('roe', 'N/A')}
- Revenue Growth: {fundamental_data.get('revenue_growth_yoy', 'N/A')}
- EV/EBITDA: {fundamental_data.get('ev_to_ebitda', 'N/A')}

Provide a brief analysis (150 words max):
1. **Valuation Assessment**: Is the P/E reasonable? Expensive or cheap relative to growth?
2. **Profitability**: How strong are the margins and returns?
3. **Overall Health**: Quick verdict on financial strength.

Be specific and actionable. Write like you're texting a fellow analyst."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_peer_comparison(ticker, peer_data):
    """
    Compare company against peers
    """
    # Format peer data for prompt
    comparison_text = ""
    for company, metrics in peer_data.items():
        comparison_text += f"\n{company}:"
        comparison_text += f"\n  Price: ${metrics['price']}"
        comparison_text += f"\n  30D Change: {metrics['change_30d']}%"
        comparison_text += f"\n  P/E: {metrics['pe_ratio']}"
        comparison_text += f"\n  Profit Margin: {metrics['profit_margin']}"
        comparison_text += f"\n  ROE: {metrics['roe']}"
        comparison_text += f"\n"
    
    prompt = f"""Compare {ticker} vs its peers based on this data:

{comparison_text}

Provide analysis (200 words max):
1. **Relative Valuation**: Where does {ticker} stand on P/E and other metrics?
2. **Competitive Position**: Is {ticker} the leader or laggard?
3. **Investment Implication**: Which company looks most attractive and why?

Be direct and specific."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_price_trend(ticker, stock_data):
    """
    Analyze recent price action
    """
    prompt = f"""Analyze {ticker}'s recent price action:

- Current Price: ${stock_data['current_price']}
- 30-Day Change: {stock_data['price_change_pct_30d']}%
- 30-Day High: ${stock_data['high_30d']}
- 30-Day Low: ${stock_data['low_30d']}

Brief analysis (100 words):
1. **Trend**: What's the momentum? Bullish/bearish/sideways?
2. **Position in Range**: Trading near highs, lows, or middle?
3. **Technical Take**: Simple observation on price action.

Keep it conversational."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_news_sentiment(ticker, news_articles):
    """
    Analyze sentiment from recent news
    """
    if not news_articles:
        return "No recent news articles found."
    
    # Extract headlines and descriptions
    news_text = ""
    for i, article in enumerate(news_articles[:5], 1):
        news_text += f"{i}. {article['title']}\n"
        if article['description']:
            news_text += f"   {article['description']}\n"
        news_text += "\n"
    
    prompt = f"""Analyze sentiment for {ticker} based on these recent headlines:

{news_text}

Provide (150 words):
1. **Overall Sentiment**: Bullish, bearish, or neutral?
2. **Key Themes**: What's driving the narrative?
3. **Catalysts/Risks**: Anything noteworthy investors should watch?

Be concise and specific."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def generate_investment_summary(ticker, all_analyses):
    """
    Phase 8: Final synthesis — structured research note pulling from all phases.
    """
    prompt = f"""You are a senior equity research analyst writing the Executive Summary for a research report on {ticker}. 
This goes at the top of the report — it's the first thing the portfolio manager reads.

Below are the outputs from your team's analysis across 7 research modules. Synthesize everything into a single, decisive research note.

BUSINESS MODEL (Phase 2):
{all_analyses.get('business_deep_dive', 'Not available')[:1500]}

FINANCIAL TRENDS (Phase 3):
{all_analyses.get('financial_trends', 'Not available')[:1000]}

FORWARD ESTIMATES (Phase 4):
{all_analyses.get('forward_scenarios', 'Not available')[:1000]}

VALUATION (Phase 5):
{all_analyses.get('relative_valuation', 'Not available')[:1000]}

RISK FRAMEWORK (Phase 6):
{all_analyses.get('risk_framework', 'Not available')[:1000]}

CATALYST TIMELINE (Phase 7):
{all_analyses.get('catalyst_timeline', 'Not available')[:800]}

FINANCIAL HEALTH:
{all_analyses.get('financial_health', '')[:500]}

PEER COMPARISON:
{all_analyses.get('peer_comparison', '')[:500]}

NEWS SENTIMENT:
{all_analyses.get('news_sentiment', '')[:500]}

Produce the Executive Summary (500 words max) with this exact structure:

## Rating: [BUY / HOLD / SELL] — [One-line thesis in 15 words or less]

**Target Price**: $[base case target] (Bull: $[bull] / Bear: $[bear])
**Current Price**: Reference from the data
**Expected Return**: [X]% to base case target

## Investment Thesis
3-4 sentences. Why own (or avoid) this stock? What's the core insight that the market may be mispricing?

## Key Strengths
Top 3 reasons to own, one sentence each. Each must reference specific data.

## Key Risks
Top 3 risks, one sentence each. Reference the risk framework analysis.

## Catalysts to Watch
The 2-3 most important upcoming events that could prove or disprove the thesis.

## Investor Fit
One sentence: Growth / Value / Income / Speculative — and why.

Write with conviction. A PM should read this and know whether to put the name on the buy list or pass. No hedging with "it depends" — take a stance."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# PHASE 2: BUSINESS MODEL DEEP DIVE
# Stage 1 — Focused extraction from each source
# Stage 2 — Synthesis across all sources
# ============================================================

def extract_business_model(ticker, business_description):
    """
    Stage 1, Call 1: Extract how the company makes money from 10-K Item 1.
    """
    if not business_description or business_description.startswith("Could not") or business_description.startswith("Error"):
        return "10-K Business Description not available."
    
    prompt = f"""You are an equity research analyst. From this 10-K Business Description for {ticker}, extract ONLY what is stated in the text:

{business_description[:12000]}

Produce a structured summary (300 words max):

1. **What they sell**: Products and/or services, described plainly
2. **Who they sell to**: Customer types, end markets, any named key customers
3. **How they monetize**: Revenue model — subscription, licensing, one-time sales, usage-based, etc.
4. **Value chain position**: Where do they sit — supplier, platform, distributor, end-product?
5. **Key dependencies**: Critical inputs, suppliers, partnerships, or regulatory requirements mentioned

IMPORTANT: Only state facts from the filing. If something is not mentioned, say so. Do not speculate."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def extract_revenue_quality(ticker, segmentation_data):
    """
    Stage 1, Call 2: Analyze revenue quality from segmentation data.
    """
    if not segmentation_data:
        return "Revenue segmentation data not available."
    
    # Format the data for the prompt
    seg_text = ""
    
    if segmentation_data.get('by_product'):
        seg_text += "REVENUE BY PRODUCT/SEGMENT:\n"
        for s in segmentation_data['by_product']:
            seg_text += f"  - {s['segment']}: ${s['revenue']:,.0f} ({s['percentage']}%)\n"
    
    if segmentation_data.get('by_geography'):
        seg_text += "\nREVENUE BY GEOGRAPHY:\n"
        for s in segmentation_data['by_geography']:
            seg_text += f"  - {s['segment']}: ${s['revenue']:,.0f} ({s['percentage']}%)\n"
    
    prompt = f"""You are an equity research analyst. Analyze {ticker}'s revenue quality from this segmentation data:

{seg_text}

Produce a structured assessment (250 words max):

1. **Concentration risk**: Is revenue heavily dependent on one segment or geography? Quantify it.
2. **Diversification**: How broad is the revenue base? Is there a healthy mix or single-product risk?
3. **Geographic exposure**: What regions dominate? Flag any geopolitical or currency risk.
4. **Revenue quality signals**: Based on segment types, is this likely recurring/subscription or transactional? Sticky or volatile?

Be specific with percentages. Flag anything above 40% concentration as a risk."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def extract_management_signals(ticker, transcript_data, mda_text=None):
    """
    Stage 1, Call 3: Extract management signals from earnings call transcripts.
    Falls back to MD&A from 10-K if transcripts are unavailable.
    """
    if not transcript_data and not mda_text:
        return "Earnings call transcripts not available."
    
    # Primary: use earnings call transcripts
    if transcript_data:
        transcript_text = ""
        for t in transcript_data[:2]:
            transcript_text += f"\n--- {t['quarter']} {t['year']} EARNINGS CALL ---\n"
            transcript_text += t['content'][:10000]
        
        prompt = f"""You are an equity research analyst reading {ticker}'s recent earnings call transcripts. Extract the key signals:

{transcript_text[:18000]}

Produce a structured analysis (300 words max):

1. **Management's narrative**: What 2-3 themes is management emphasizing? What are they most excited about?
2. **Guidance signals**: Did they raise, maintain, or lower forward guidance? Any specific numbers mentioned?
3. **Analyst pressure points**: What questions did analysts push hardest on? What topics came up repeatedly?
4. **Red flags or dodges**: Did management deflect any questions? Any topics they seemed uncomfortable on?
5. **Tone shift**: Compared to prior quarter (if available), is management more or less confident?

Ground every observation in what was actually said. Do not infer beyond the text."""

    # Fallback: use MD&A from 10-K
    else:
        prompt = f"""You are an equity research analyst reading {ticker}'s Management Discussion & Analysis (MD&A) from their most recent 10-K filing. Extract management signals:

{mda_text[:15000]}

Produce a structured analysis (300 words max):

1. **Management's narrative**: What 2-3 themes is management emphasizing about the business and its direction?
2. **Forward-looking signals**: What does management say about future growth drivers, investments, or strategic priorities?
3. **Risk acknowledgments**: What risks or challenges does management explicitly call out?
4. **Tone and confidence**: Does management sound cautious or aggressive about the outlook?
5. **Key metrics highlighted**: What financial metrics or operational KPIs does management focus on?

Note: This analysis is based on the annual 10-K filing (MD&A section), not a quarterly earnings call. The tone may be more formal and backward-looking than a live call.

Ground every observation in what was actually stated. Do not infer beyond the text."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def extract_moat_signals(ticker, risk_factors):
    """
    Stage 1, Call 4: Identify competitive moat from risk factors.
    Risk factors often reveal moat vulnerabilities and competitive dynamics.
    """
    if not risk_factors or risk_factors.startswith("Could not") or risk_factors.startswith("Error"):
        return "10-K Risk Factors not available."
    
    prompt = f"""You are an equity research analyst. Analyze {ticker}'s competitive position from these 10-K Risk Factors:

{risk_factors[:12000]}

Map findings to Morningstar's moat framework. For each, cite specific evidence from the risk factors:

1. **Switching costs**: Do the risks mention customer lock-in, integration complexity, or migration difficulty? (High/Medium/Low/None)
2. **Network effects**: Any mention of platform dynamics, user base advantages, or ecosystem dependencies? (High/Medium/Low/None)
3. **Intangible assets**: Patents, brands, licenses, regulatory approvals mentioned? (High/Medium/Low/None)
4. **Cost advantage**: Scale economies, proprietary technology, or structural cost mentions? (High/Medium/Low/None)
5. **Efficient scale**: Market size limitations, natural monopoly dynamics? (High/Medium/Low/None)

Then provide:
6. **Overall moat assessment**: Narrow / Wide / None — with a one-sentence justification
7. **Biggest moat threat**: The single risk factor that most directly threatens competitive position

250 words max. Be direct."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def synthesize_business_deep_dive(ticker, stage1_outputs):
    """
    Stage 2: Synthesize all Stage 1 outputs into the final Business Model Deep Dive.
    This is the single synthesis call that produces the user-facing output.
    """
    # Don't waste an API call if all inputs failed
    unavailable_markers = ["not available", "Error:", "Could not"]
    available_inputs = []
    for key, value in stage1_outputs.items():
        if value and not any(m in value for m in unavailable_markers):
            available_inputs.append(key)
    
    if not available_inputs:
        return None
    
    prompt = f"""You are a senior equity research analyst writing the Business Model section of a research report on {ticker}.

Below are four research inputs from your junior analysts. Synthesize them into a cohesive deep dive.

BUSINESS MODEL ANALYSIS:
{stage1_outputs.get('business_model', 'Not available')}

REVENUE QUALITY ASSESSMENT:
{stage1_outputs.get('revenue_quality', 'Not available')}

MANAGEMENT SIGNALS (from earnings calls):
{stage1_outputs.get('management_signals', 'Not available')}

COMPETITIVE MOAT ANALYSIS:
{stage1_outputs.get('moat_signals', 'Not available')}

Produce the final Business Model Deep Dive with these four sections:

## Business Model Summary
How does this company make money? 3-4 sentences, plain English. A smart non-finance person should understand it.

## Revenue Quality
Is the revenue high quality (recurring, diversified, growing) or risky (concentrated, one-time, volatile)? Rate it: Strong / Adequate / Weak with specific evidence.

## Competitive Moat
What structural advantages does this company have? Rate the moat: Wide / Narrow / None. What's the biggest threat to the moat?

## Management Assessment
What is management focused on? Are they credible? Any concerning signals from recent earnings calls?

End with a one-line **Bottom Line** that captures the business quality in a single sentence.

Write in a professional but conversational tone. 500 words max total."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def run_business_deep_dive(ticker, sec_sections, segmentation_data, transcript_data):
    """
    Main orchestrator for Phase 2.
    Runs Stage 1 (4 extraction calls) then Stage 2 (1 synthesis call).
    Returns: dict with stage1 outputs, final synthesis, and data_sources status.
    """
    unavailable_markers = ["not available", "Error:", "Could not"]
    
    def _is_valid(text):
        return text and not any(m in text for m in unavailable_markers)
    
    # Stage 1: Parallel-ready extraction calls
    # (Running sequentially for now — can be parallelized with asyncio later)
    print(f"[Phase 2] Stage 1: Extracting business signals for {ticker}...")
    
    business_model = extract_business_model(
        ticker, 
        sec_sections.get('business_description', '')
    )
    print(f"    ✓ Business model extracted")
    
    revenue_quality = extract_revenue_quality(ticker, segmentation_data)
    print(f"    ✓ Revenue quality assessed")
    
    management_signals = extract_management_signals(
        ticker, transcript_data,
        mda_text=sec_sections.get('mda', '')
    )
    print(f"    ✓ Management signals extracted")
    
    moat_signals = extract_moat_signals(
        ticker, 
        sec_sections.get('risk_factors', '')
    )
    print(f"    ✓ Moat signals identified")
    
    stage1_outputs = {
        'business_model': business_model,
        'revenue_quality': revenue_quality,
        'management_signals': management_signals,
        'moat_signals': moat_signals,
    }
    
    # Track which data sources succeeded — for UI transparency
    mgmt_source = 'Earnings Transcripts' if transcript_data else 'MD&A (10-K fallback)'
    data_sources = {
        '10-K Filing': _is_valid(business_model) or _is_valid(moat_signals),
        'Revenue Segmentation': _is_valid(revenue_quality),
        mgmt_source: _is_valid(management_signals),
    }
    
    # Stage 2: Synthesis (skipped if all inputs failed)
    print(f"[Phase 2] Stage 2: Synthesizing deep dive for {ticker}...")
    synthesis = synthesize_business_deep_dive(ticker, stage1_outputs)
    if synthesis:
        print(f"    ✓ Deep dive synthesized")
    else:
        print(f"    ✗ All inputs unavailable — synthesis skipped")
    
    return {
        'stage1': stage1_outputs,
        'synthesis': synthesis,
        'data_sources': data_sources,
    }


# ============================================================
# PHASE 3: HISTORICAL FINANCIAL TREND ANALYSIS
# ============================================================

def analyze_financial_trends(ticker, trends):
    """
    Analyze 5-year financial trends. One Claude call.
    Input: trends dict from compute_financial_trends().
    """
    if not trends or not trends.get('years'):
        return "Historical financial data not available."
    
    summary = trends.get('summary', {})
    
    # Build a trend table for the prompt
    table = "YEAR | REVENUE | NET INCOME | GROSS MARGIN | OP MARGIN | NET MARGIN | ROE | FCF | CAPEX % REV | CASH CONVERSION\n"
    table += "-" * 120 + "\n"
    
    for i, year in enumerate(trends['years']):
        rev = f"${trends['revenue'][i]/1e9:.1f}B" if i < len(trends['revenue']) else "?"
        ni = f"${trends['net_income'][i]/1e9:.1f}B" if i < len(trends['net_income']) else "?"
        gm = f"{trends['gross_margin'][i]}%" if i < len(trends['gross_margin']) else "?"
        om = f"{trends['operating_margin'][i]}%" if i < len(trends['operating_margin']) else "?"
        nm = f"{trends['net_margin'][i]}%" if i < len(trends['net_margin']) else "?"
        roe = f"{trends['roe'][i]}%" if i < len(trends['roe']) else "?"
        fcf = f"${trends['fcf'][i]/1e9:.1f}B" if i < len(trends['fcf']) else "?"
        capex = f"{trends['capex_pct_revenue'][i]}%" if i < len(trends['capex_pct_revenue']) else "?"
        cc = f"{trends['cash_conversion'][i]}%" if i < len(trends['cash_conversion']) else "?"
        table += f"{year} | {rev} | {ni} | {gm} | {om} | {nm} | {roe} | {fcf} | {capex} | {cc}\n"
    
    # Summary stats for prompt
    summary_text = ""
    if summary.get('revenue_cagr_3yr') is not None:
        summary_text += f"- Revenue 3-Year CAGR: {summary['revenue_cagr_3yr']}%\n"
    if summary.get('revenue_cagr_5yr') is not None:
        summary_text += f"- Revenue 5-Year CAGR: {summary['revenue_cagr_5yr']}%\n"
    if summary.get('gross_margin_trend'):
        summary_text += f"- Gross Margin Trend: {summary['gross_margin_trend']}\n"
    if summary.get('operating_margin_trend'):
        summary_text += f"- Operating Margin Trend: {summary['operating_margin_trend']}\n"
    if summary.get('net_margin_trend'):
        summary_text += f"- Net Margin Trend: {summary['net_margin_trend']}\n"
    if summary.get('roe_trend'):
        summary_text += f"- ROE Trend: {summary['roe_trend']}\n"
    if summary.get('avg_cash_conversion'):
        summary_text += f"- Avg Cash Conversion (FCF/NI): {summary['avg_cash_conversion']}%\n"
    if summary.get('capex_intensity_trend'):
        summary_text += f"- Capex Intensity Trend: {summary['capex_intensity_trend']} (latest: {summary.get('latest_capex_pct', '?')}% of revenue)\n"
    
    prompt = f"""You are an equity research analyst reviewing {ticker}'s 5-year financial trajectory.

HISTORICAL DATA:
{table}

COMPUTED TRENDS:
{summary_text}

Produce a trend analysis (350 words max) with these sections:

## Growth Trajectory
Is revenue growth accelerating, decelerating, or steady? What's the CAGR telling us vs. the year-over-year pattern? Is this sustainable?

## Margin Story
Are margins expanding or compressing? Is the company getting more efficient (operating leverage) or are costs growing faster than revenue? Highlight any inflection points.

## Earnings Quality
Is the company converting profits to cash (cash conversion ratio)? A ratio well above 100% is strong. Below 80% is a red flag. What does capex intensity tell us — growth investment or maintenance?

## ROE Trajectory
Is return on equity improving? If so, is it from better margins, better asset utilization, or more leverage? (DuPont decomposition logic)

## Key Inflection
Identify the single most important trend change in the data — the one number or shift that would most affect an investment thesis.

Use specific numbers from the data. Write like an analyst briefing a PM, not a textbook."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# PHASE 4: FORWARD ESTIMATES & SCENARIO ANALYSIS
# ============================================================

def analyze_forward_scenarios(ticker, estimates, trends_summary, current_price, pe_ratio):
    """
    Generate bull/base/bear scenario table from consensus estimates + historical context.
    One Claude call.
    """
    if not estimates:
        return "Analyst estimates not available."
    
    # Format consensus estimates for prompt
    est_text = "CONSENSUS ANALYST ESTIMATES:\n"
    for est in estimates:
        rev_avg = est['revenue_avg'] / 1e9
        rev_low = est['revenue_low'] / 1e9
        rev_high = est['revenue_high'] / 1e9
        est_text += f"\n{est['date']}:\n"
        est_text += f"  Revenue: ${rev_low:.1f}B (low) / ${rev_avg:.1f}B (avg) / ${rev_high:.1f}B (high)\n"
        est_text += f"  EPS: ${est['eps_low']:.2f} (low) / ${est['eps_avg']:.2f} (avg) / ${est['eps_high']:.2f} (high)\n"
        est_text += f"  Net Income: ${est['net_income_low']/1e9:.1f}B (low) / ${est['net_income_avg']/1e9:.1f}B (avg) / ${est['net_income_high']/1e9:.1f}B (high)\n"
        if est.get('num_analysts_revenue'):
            est_text += f"  Coverage: {est['num_analysts_revenue']} analysts (revenue), {est['num_analysts_eps']} (EPS)\n"
    
    # Historical context
    hist_text = ""
    if trends_summary:
        if trends_summary.get('revenue_cagr_3yr') is not None:
            hist_text += f"- Historical 3-Year Revenue CAGR: {trends_summary['revenue_cagr_3yr']}%\n"
        if trends_summary.get('revenue_cagr_5yr') is not None:
            hist_text += f"- Historical 5-Year Revenue CAGR: {trends_summary['revenue_cagr_5yr']}%\n"
        if trends_summary.get('net_margin_trend'):
            hist_text += f"- Net Margin Trend: {trends_summary['net_margin_trend']}\n"
        if trends_summary.get('avg_cash_conversion'):
            hist_text += f"- Avg Cash Conversion: {trends_summary['avg_cash_conversion']}%\n"
    
    # Current valuation
    price_text = f"Current Price: ${current_price}\n" if current_price else ""
    pe_text = f"Current P/E: {pe_ratio:.1f}x\n" if isinstance(pe_ratio, (int, float)) else ""
    
    prompt = f"""You are an equity research analyst building a scenario analysis for {ticker}.

{est_text}

HISTORICAL CONTEXT:
{hist_text}

CURRENT VALUATION:
{price_text}{pe_text}

Produce a scenario analysis (400 words max) with these sections:

## Consensus View
What are analysts expecting? Is consensus revenue growth accelerating or decelerating vs. historical rates? How wide is the bull-bear spread (indicates uncertainty)?

## Bull Case
State the key assumption (1 sentence). What revenue growth and margin would need to hold? Using the HIGH EPS estimate and a reasonable bull-case P/E multiple, what is the implied price target? Show the math: EPS × P/E = target price.

## Base Case
Anchored to consensus AVG estimates. Using the AVG EPS and the current P/E multiple, what is the implied price? How does this compare to current price — upside or downside?

## Bear Case
State the risk assumption (1 sentence). Using the LOW EPS estimate and a compressed P/E multiple, what is the implied downside target? Show the math.

## Probability-Weighted View
Assign rough probabilities (e.g., Bull 25%, Base 50%, Bear 25%) and compute an expected return. Is the risk/reward skewed favorably?

Be specific with numbers. Every target price must show the EPS × P/E calculation."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# PHASE 5: RELATIVE VALUATION ANALYSIS
# ============================================================

def analyze_relative_valuation(ticker, valuation_context, peer_data):
    """
    Analyze valuation vs. own history and vs. peers. One Claude call.
    Combines historical valuation bands with peer comparison.
    """
    if not valuation_context and not peer_data:
        return "Valuation data not available."
    
    # Format historical valuation context
    hist_text = ""
    if valuation_context and valuation_context.get('multiples'):
        hist_text = f"HISTORICAL VALUATION BANDS ({ticker} vs. own 5-year history):\n"
        hist_text += f"{'Metric':<15} {'Current':>10} {'5Y Avg':>10} {'5Y High':>10} {'5Y Low':>10} {'vs Avg':>10}\n"
        hist_text += "-" * 70 + "\n"
        for m_key, m_data in valuation_context['multiples'].items():
            if m_data.get('current') is not None:
                vs_avg = f"{m_data['vs_avg_pct']:+.1f}%" if m_data.get('vs_avg_pct') is not None else "N/A"
                hist_text += f"{m_data['label']:<15} {m_data['current']:>10.1f} {m_data['avg_5yr']:>10.1f} {m_data['high_5yr']:>10.1f} {m_data['low_5yr']:>10.1f} {vs_avg:>10}\n"
    
    # Format peer data
    peer_text = ""
    if peer_data:
        peer_text = f"\nPEER COMPARISON:\n"
        peer_text += f"{'Ticker':<10} {'Price':>10} {'30D Chg':>10} {'P/E':>10} {'Margin':>12} {'ROE':>10} {'EV/EBITDA':>12}\n"
        peer_text += "-" * 80 + "\n"
        for t, m in peer_data.items():
            pe = f"{m['pe_ratio']:.1f}" if isinstance(m.get('pe_ratio'), (int, float)) else str(m.get('pe_ratio', 'N/A'))
            ev = f"{m['ev_to_ebitda']:.1f}" if isinstance(m.get('ev_to_ebitda'), (int, float)) else str(m.get('ev_to_ebitda', 'N/A'))
            chg = f"{m['change_30d']:+.1f}%" if isinstance(m.get('change_30d'), (int, float)) else str(m.get('change_30d', 'N/A'))
            peer_text += f"{t:<10} ${m.get('price','?'):>8} {chg:>10} {pe:>10} {str(m.get('profit_margin','N/A')):>12} {str(m.get('roe','N/A')):>10} {ev:>12}\n"
    
    prompt = f"""You are an equity research analyst writing the Valuation section of a research report on {ticker}.

{hist_text}

{peer_text}

Produce a valuation analysis (350 words max) with these sections:

## Valuation vs. Own History
Where does {ticker} trade now vs. its 5-year average on each multiple? Is it at a premium or discount to itself? Is the premium/discount justified by changes in growth or quality?

## Valuation vs. Peers
How does {ticker}'s valuation compare to the peer group? Which peer looks cheapest on each metric? Is {ticker}'s premium (if any) justified by superior growth or margins?

## Valuation Verdict
One-paragraph synthesis: Is {ticker} expensive, fairly valued, or cheap? On what basis? What multiple would you anchor a valuation to and why?

Use specific numbers. Flag any multiple that's more than 20% above or below the 5-year average as noteworthy."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# PHASE 6: STRUCTURED RISK FRAMEWORK
# ============================================================

def analyze_risk_framework(ticker, risk_factors, moat_signals, fund_data, news_analysis):
    """
    Identify top 3 thesis-breaking risks with probability, impact, and early warnings.
    Synthesizes across 10-K risk factors, moat analysis, financial data, and news.
    One Claude call.
    """
    # Build context from available sources
    context = ""
    
    if risk_factors and not any(m in risk_factors for m in ["not available", "Error:", "Could not"]):
        context += f"10-K RISK FACTORS (excerpt):\n{risk_factors[:8000]}\n\n"
    
    if moat_signals and not any(m in moat_signals for m in ["not available", "Error:", "Could not"]):
        context += f"MOAT ANALYSIS:\n{moat_signals}\n\n"
    
    if fund_data:
        context += "KEY FINANCIAL METRICS:\n"
        for key in ['pe_ratio', 'profit_margin', 'roe', 'revenue_growth_yoy', 'beta', 'ev_to_ebitda']:
            val = fund_data.get(key, 'N/A')
            if isinstance(val, (int, float)):
                context += f"  {key}: {val}\n"
            else:
                context += f"  {key}: {val}\n"
        context += "\n"
    
    if news_analysis and not news_analysis.startswith("Error") and not news_analysis.startswith("No recent"):
        context += f"RECENT NEWS SENTIMENT:\n{news_analysis}\n\n"
    
    if not context.strip():
        return "Insufficient data to build risk framework."
    
    prompt = f"""You are a senior equity research analyst building the Risk Framework section for {ticker}.

{context}

Produce a structured risk assessment (400 words max). Do NOT produce a generic list. Identify the risks that would specifically break an investment thesis for {ticker}.

## Top 3 Thesis-Breaking Risks

For each risk:

### Risk 1: [Name it in 5 words or less]
- **What**: One sentence describing the specific risk
- **Probability**: Low / Medium / High — with one sentence justification
- **Impact if realized**: Quantify it — what happens to revenue, margins, or valuation? (e.g., "Could compress margins by 500-800bps" or "Would eliminate ~30% of revenue")
- **Early warning signal**: What specific, observable metric or event would indicate this risk is materializing?
- **Thesis impact**: Would this be thesis-damaging (recoverable) or thesis-breaking (permanent impairment)?

### Risk 2: [Name]
(same structure)

### Risk 3: [Name]
(same structure)

## Risk-Reward Summary
One paragraph: Given these risks, is the current valuation adequately compensating investors for the risk profile? Are the risks priced in or is the market complacent?

Ground every risk in specific evidence from the data provided. No generic risks like "macroeconomic downturn" unless there's specific evidence it's relevant."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================
# PHASE 7: CATALYST TIMELINE
# ============================================================

def analyze_catalyst_timeline(ticker, catalyst_events, news_articles, forward_scenarios_text, risk_framework_text):
    """
    Build a forward-looking catalyst map for the next 6-12 months.
    Combines earnings dates, dividends, news signals, and scenario triggers.
    One Claude call.
    """
    context = ""
    
    # Earnings events
    if catalyst_events and catalyst_events.get('earnings'):
        context += "EARNINGS HISTORY & UPCOMING:\n"
        for e in catalyst_events['earnings'][:6]:
            actual = f"  Actual EPS: ${e['eps_actual']}" if e.get('eps_actual') else "  (upcoming)"
            est = f"  Est EPS: ${e['eps_estimated']}" if e.get('eps_estimated') else ""
            beat = ""
            if e.get('eps_actual') and e.get('eps_estimated') and e['eps_estimated']:
                surprise = ((e['eps_actual'] - e['eps_estimated']) / abs(e['eps_estimated'])) * 100
                beat = f"  Surprise: {surprise:+.1f}%"
            context += f"  {e['date']}{actual}{est}{beat}\n"
        context += "\n"
    
    # Dividends
    if catalyst_events and catalyst_events.get('dividends'):
        context += "RECENT DIVIDENDS:\n"
        for d in catalyst_events['dividends'][:4]:
            context += f"  {d['date']}: ${d['dividend']} ({d['frequency']}), Payment: {d['payment_date']}\n"
        context += "\n"
    
    # News themes
    if news_articles:
        context += "RECENT NEWS HEADLINES:\n"
        for i, article in enumerate(news_articles[:5], 1):
            context += f"  {i}. {article.get('title', '')} ({article.get('source', '')})\n"
        context += "\n"
    
    # Forward scenario context
    if forward_scenarios_text and not any(m in forward_scenarios_text for m in ["not available", "Error:"]):
        context += f"SCENARIO ANALYSIS CONTEXT:\n{forward_scenarios_text[:1500]}\n\n"
    
    # Risk context
    if risk_framework_text and not any(m in risk_framework_text for m in ["not available", "Error:", "Insufficient"]):
        context += f"KEY RISKS:\n{risk_framework_text[:1500]}\n\n"
    
    if not context.strip():
        return "Insufficient data to build catalyst timeline."
    
    prompt = f"""You are an equity research analyst building the Catalyst Timeline for {ticker}.

{context}

Produce a catalyst map (300 words max) with these sections:

## Upcoming Catalysts (Next 6 Months)
List 3-5 specific events or dates that could move the stock. For each:
- **Date/Timeframe**: When (be specific — quarter or month)
- **Event**: What is it
- **Direction**: Potential positive catalyst (+), negative catalyst (−), or informational (→)
- **Why it matters**: One sentence on thesis impact

## Earnings Track Record
Based on the earnings history, does management typically beat, meet, or miss estimates? What's the pattern? Is the beat magnitude shrinking (expectations catching up)?

## What Would Change the Thesis
In one sentence each: What specific event would make you upgrade from Hold to Buy? What would make you downgrade to Sell?

Be specific and actionable. An investor should read this and know exactly what to watch for."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    from data_fetchers import (
        get_stock_data, 
        get_fundamental_data, 
        get_company_news,
        get_comprehensive_peer_data
    )
    
    print("Testing AI Analysis...")
    print("="*60)
    
    ticker = "NVDA"
    
    # Get data
    print(f"\n[1/5] Fetching data for {ticker}...")
    stock_data = get_stock_data(ticker)
    fund_data = get_fundamental_data(ticker)
    news = get_company_news(ticker, "NVIDIA")
    peers = get_comprehensive_peer_data(ticker, ["AMD", "INTC"])
    
    # Run analyses
    print("\n[2/5] Analyzing financial health...")
    health = analyze_financial_health(ticker, fund_data)
    print(health[:150] + "...")
    
    print("\n[3/5] Analyzing peer comparison...")
    peer_analysis = analyze_peer_comparison(ticker, peers)
    print(peer_analysis[:150] + "...")
    
    print("\n[4/5] Analyzing price trend...")
    trend = analyze_price_trend(ticker, stock_data)
    print(trend[:150] + "...")
    
    print("\n[5/5] Analyzing news sentiment...")
    sentiment = analyze_news_sentiment(ticker, news)
    print(sentiment[:150] + "...")
    
    print("\n" + "="*60)
    print("AI ANALYSIS TEST COMPLETE ✅")
    print("="*60)