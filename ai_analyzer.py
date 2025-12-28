import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def analyze_news_sentiment(ticker, news_articles):
    """
    Use Claude to analyze sentiment from news articles
    """
    # Prepare news summary for Claude
    news_text = f"Recent news about {ticker}:\n\n"
    for i, article in enumerate(news_articles[:5], 1):  # Top 5 articles
        news_text += f"{i}. [{article['source']}] {article['title']}\n"
        if article['description']:
            news_text += f"   {article['description']}\n"
        news_text += "\n"
    
    prompt = f"""Analyze the following recent news about {ticker} and provide:

{news_text}

Please provide:
1. Overall Sentiment: (Bullish/Bearish/Neutral) with confidence level
2. Key Themes: 2-3 main themes emerging from the news
3. Market Impact: How this news might affect the stock in the short term

Keep your response concise and actionable for a financial analyst."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "sentiment_analysis": message.content[0].text,
            "articles_analyzed": len(news_articles[:5])
        }
    
    except Exception as e:
        return {"error": f"Error analyzing sentiment: {str(e)}"}


def analyze_price_action(ticker, stock_data, peer_data=None):
    """
    Use Claude to provide context on price movements
    """
    prompt = f"""Analyze the following stock performance for {ticker}:

Current Price: ${stock_data['current_price']}
30-Day Change: {stock_data['price_change_pct_30d']}%
30-Day High: ${stock_data['high_30d']}
30-Day Low: ${stock_data['low_30d']}
Average Volume: {stock_data['avg_volume_30d']:,.0f}
"""
    
    if peer_data and peer_data.get('comparison_data'):
        prompt += "\nPeer Comparison:\n"
        for comp in peer_data['comparison_data']:
            if not comp['is_primary']:
                prompt += f"- {comp['ticker']}: {comp['change_30d_pct']:+.2f}%\n"
    
    prompt += """
Provide a brief analysis:
1. Price Performance: How has the stock performed relative to its recent range?
2. Relative Strength: How does it compare to peers (if provided)?
3. Technical Observations: Any notable patterns or levels?

Keep response under 150 words."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "price_analysis": message.content[0].text
        }
    
    except Exception as e:
        return {"error": f"Error analyzing price action: {str(e)}"}


def identify_risks_catalysts(ticker, news_articles, stock_data):
    """
    Use Claude to identify key risks and potential catalysts
    """
    news_summary = "\n".join([f"- {article['title']}" for article in news_articles[:5]])
    
    prompt = f"""Based on recent news and price action for {ticker}:

Recent Headlines:
{news_summary}

Recent Performance: {stock_data['price_change_pct_30d']}% over 30 days

Identify:
1. Key Risks: 2-3 main risks facing the company
2. Potential Catalysts: 2-3 events or factors that could drive the stock higher

Be specific and concise. Focus on actionable insights for investors."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "risks_catalysts": message.content[0].text
        }
    
    except Exception as e:
        return {"error": f"Error identifying risks/catalysts: {str(e)}"}

def analyze_fundamentals(ticker, fundamental_data):
    """
    Use Claude to analyze valuation and financial health metrics
    """
    prompt = f"""Analyze the following fundamental metrics for {ticker}:

VALUATION METRICS:
- P/E Ratio: {fundamental_data.get('pe_ratio', 'N/A')}
- P/S Ratio: {fundamental_data.get('price_to_sales', 'N/A')}
- Price-to-Book: {fundamental_data.get('price_to_book', 'N/A')}
- Market Cap: {fundamental_data.get('market_cap_formatted', 'N/A')}

PROFITABILITY METRICS:
- Profit Margin: {fundamental_data.get('profit_margin', 0):.2f}%
- Operating Margin: {fundamental_data.get('operating_margin', 0):.2f}%
- Gross Margin: {fundamental_data.get('gross_margin', 0):.2f}%
- ROE (Return on Equity): {fundamental_data.get('roe', 0):.2f}%
- ROA (Return on Assets): {fundamental_data.get('roa', 0):.2f}%

GROWTH METRICS:
- Revenue Growth (YoY): {fundamental_data.get('revenue_growth_yoy', 0):.2f}%
- Earnings Growth (YoY): {fundamental_data.get('earnings_growth_yoy', 0):.2f}%

Provide concise analysis:
1. Valuation Assessment: Is the stock expensive, fairly valued, or cheap based on multiples?
2. Profitability Analysis: Comment on margin strength and efficiency (ROE/ROA)
3. Growth Profile: Assess revenue and earnings growth trajectory

Keep response under 200 words. Be specific and avoid generic statements."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "fundamental_analysis": message.content[0].text
        }
    
    except Exception as e:
        return {"error": f"Error analyzing fundamentals: {str(e)}"}

def generate_executive_summary(ticker, all_analyses):
    """
    Use Claude to create a concise executive summary
    """
    prompt = f"""Create a concise executive summary for {ticker} based on this analysis:

SENTIMENT ANALYSIS:
{all_analyses.get('sentiment', 'Not available')}

PRICE ACTION:
{all_analyses.get('price_action', 'Not available')}

RISKS & CATALYSTS:
{all_analyses.get('risks_catalysts', 'Not available')}

Provide a 3-4 sentence executive summary that captures the investment thesis and key takeaways. Write as if briefing a portfolio manager."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "executive_summary": message.content[0].text
        }
    
    except Exception as e:
        return {"error": f"Error generating summary: {str(e)}"}


# Test
if __name__ == "__main__":
    from data_fetchers import get_stock_data, get_company_news, get_fundamental_data
    
    print("Testing AI Analysis Layer...\n")
    
    # Get sample data
    print("Fetching NVDA data...")
    stock_data = get_stock_data("NVDA")
    news_data = get_company_news("NVDA", "NVIDIA")
    fundamental_data = get_fundamental_data("NVDA")
    
    print("\n[1/4] Analyzing news sentiment...")
    sentiment = analyze_news_sentiment("NVDA", news_data['articles'])
    if "error" not in sentiment:
        print("✅ Sentiment analysis complete")
        print(sentiment['sentiment_analysis'][:150] + "...\n")
    
    print("[2/4] Analyzing price action...")
    price_analysis = analyze_price_action("NVDA", stock_data)
    if "error" not in price_analysis:
        print("✅ Price analysis complete")
        print(price_analysis['price_analysis'][:150] + "...\n")
    
    print("[3/4] Identifying risks & catalysts...")
    risks = identify_risks_catalysts("NVDA", news_data['articles'], stock_data)
    if "error" not in risks:
        print("✅ Risks & catalysts identified")
        print(risks['risks_catalysts'][:150] + "...\n")
    
    print("[4/4] Analyzing fundamentals...")
    fundamental_analysis = analyze_fundamentals("NVDA", fundamental_data)
    if "error" not in fundamental_analysis:
        print("✅ Fundamental analysis complete")
        print(fundamental_analysis['fundamental_analysis'][:150] + "...\n")
    
    print("="*60)
    print("AI ANALYSIS LAYER COMPLETE ✅")
    print("="*60)