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
    Generate comprehensive investment summary
    """
    prompt = f"""Synthesize an investment summary for {ticker} based on:

FINANCIAL HEALTH:
{all_analyses.get('financial_health', '')}

PEER COMPARISON:
{all_analyses.get('peer_comparison', '')}

PRICE TREND:
{all_analyses.get('price_trend', '')}

NEWS SENTIMENT:
{all_analyses.get('news_sentiment', '')}

Provide a 4-5 sentence investment summary:
- Overall assessment (buy/hold/avoid territory?)
- Key strengths and risks
- What type of investor would this suit?

Write like you're advising a friend."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
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


def extract_management_signals(ticker, transcript_data):
    """
    Stage 1, Call 3: Extract management signals from earnings call transcripts.
    """
    if not transcript_data:
        return "Earnings call transcripts not available."
    
    # Combine transcripts
    transcript_text = ""
    for t in transcript_data[:2]:
        transcript_text += f"\n--- {t['quarter']} {t['year']} EARNINGS CALL ---\n"
        transcript_text += t['content'][:10000]  # Cap per transcript for token limits
    
    prompt = f"""You are an equity research analyst reading {ticker}'s recent earnings call transcripts. Extract the key signals:

{transcript_text[:18000]}

Produce a structured analysis (300 words max):

1. **Management's narrative**: What 2-3 themes is management emphasizing? What are they most excited about?
2. **Guidance signals**: Did they raise, maintain, or lower forward guidance? Any specific numbers mentioned?
3. **Analyst pressure points**: What questions did analysts push hardest on? What topics came up repeatedly?
4. **Red flags or dodges**: Did management deflect any questions? Any topics they seemed uncomfortable on?
5. **Tone shift**: Compared to prior quarter (if available), is management more or less confident?

Ground every observation in what was actually said. Do not infer beyond the text."""

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
    
    management_signals = extract_management_signals(ticker, transcript_data)
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
    data_sources = {
        '10-K Filing': _is_valid(business_model) or _is_valid(moat_signals),
        'Revenue Segmentation': _is_valid(revenue_quality),
        'Earnings Transcripts': _is_valid(management_signals),
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