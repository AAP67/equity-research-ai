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


# Test
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