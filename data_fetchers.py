import os
import requests
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def get_stock_data(ticker):
    """
    Get stock price data using yfinance
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_30d_ago = hist['Close'].iloc[0]
        price_change_30d = current_price - price_30d_ago
        price_change_pct_30d = (price_change_30d / price_30d_ago) * 100
        
        return {
            'current_price': round(current_price, 2),
            'price_change_30d': round(price_change_30d, 2),
            'price_change_pct_30d': round(price_change_pct_30d, 2),
            'high_30d': round(hist['High'].max(), 2),
            'low_30d': round(hist['Low'].min(), 2),
            'avg_volume_30d': int(hist['Volume'].mean()),
            'chart_data': hist[['Close']].reset_index().to_dict('records')
        }
        
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return None


def get_company_news(ticker, company_name=None):
    """
    Fetch recent news about a company
    Returns: list of news articles with title, source, date, url
    """
    api_key = os.getenv('NEWS_API_KEY')
    
    search_query = company_name if company_name else ticker
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q={search_query}&from={from_date}&sortBy=relevancy&language=en&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") != "ok":
            return []
        
        articles = data.get("articles", [])[:10]
        
        news_items = []
        for article in articles:
            news_items.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", "")[:10],
                "description": article.get("description", ""),
                "url": article.get("url", "")
            })
        
        return news_items
        
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []


def get_fundamental_data(ticker):
    """
    Get fundamental financial data using yfinance
    Returns dict with valuation metrics, profitability, growth
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key metrics
        fundamental_data = {
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'forward_pe': info.get('forwardPE', 'N/A'),
            'peg_ratio': info.get('pegRatio', 'N/A'),
            'price_to_book': info.get('priceToBook', 'N/A'),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
            'ev_to_ebitda': info.get('enterpriseToEbitda', 'N/A'),
            
            # Profitability
            'profit_margin': info.get('profitMargins', 'N/A'),
            'operating_margin': info.get('operatingMargins', 'N/A'),
            'gross_margin': info.get('grossMargins', 'N/A'),
            'roe': info.get('returnOnEquity', 'N/A'),
            'roa': info.get('returnOnAssets', 'N/A'),
            
            # Growth
            'revenue_growth_yoy': info.get('revenueGrowth', 'N/A'),
            'earnings_growth_yoy': info.get('earningsGrowth', 'N/A'),
            
            # Other
            'beta': info.get('beta', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
        }
        
        # Convert percentages to readable format
        if fundamental_data['profit_margin'] != 'N/A':
            fundamental_data['profit_margin'] = f"{fundamental_data['profit_margin']*100:.2f}%"
        if fundamental_data['roe'] != 'N/A':
            fundamental_data['roe'] = f"{fundamental_data['roe']*100:.2f}%"
        if fundamental_data['revenue_growth_yoy'] != 'N/A':
            fundamental_data['revenue_growth_yoy'] = f"{fundamental_data['revenue_growth_yoy']*100:.2f}%"
            
        return fundamental_data
        
    except Exception as e:
        print(f"Error fetching fundamental data: {str(e)}")
        return None


def format_market_cap(market_cap):
    """Helper function to format market cap in B/T"""
    if market_cap == 'N/A' or market_cap is None:
        return 'N/A'
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"


def get_comprehensive_peer_data(ticker, peers):
    """
    Get fundamental data for ticker + all peers for comparison
    Returns dict with all companies' key metrics
    """
    all_data = {}
    
    # Get primary company data
    print(f"Fetching data for {ticker}...")
    stock_data = get_stock_data(ticker)
    fundamental_data = get_fundamental_data(ticker)
    
    if stock_data and fundamental_data:
        all_data[ticker] = {
            'price': stock_data.get('current_price', 'N/A'),
            'change_30d': stock_data.get('price_change_pct_30d', 'N/A'),
            'pe_ratio': fundamental_data.get('pe_ratio', 'N/A'),
            'profit_margin': fundamental_data.get('profit_margin', 'N/A'),
            'market_cap': fundamental_data.get('market_cap', 'N/A'),
            'roe': fundamental_data.get('roe', 'N/A'),
            'ev_to_ebitda': fundamental_data.get('ev_to_ebitda', 'N/A'),
            'revenue_growth': fundamental_data.get('revenue_growth_yoy', 'N/A'),
        }
    
    # Get peer data
    for peer in peers:
        print(f"Fetching data for peer: {peer}...")
        peer_stock = get_stock_data(peer)
        peer_fund = get_fundamental_data(peer)
        
        if peer_stock and peer_fund:
            all_data[peer] = {
                'price': peer_stock.get('current_price', 'N/A'),
                'change_30d': peer_stock.get('price_change_pct_30d', 'N/A'),
                'pe_ratio': peer_fund.get('pe_ratio', 'N/A'),
                'profit_margin': peer_fund.get('profit_margin', 'N/A'),
                'market_cap': peer_fund.get('market_cap', 'N/A'),
                'roe': peer_fund.get('roe', 'N/A'),
                'ev_to_ebitda': peer_fund.get('ev_to_ebitda', 'N/A'),
                'revenue_growth': peer_fund.get('revenue_growth_yoy', 'N/A'),
            }
    
    return all_data


# Test functions
if __name__ == "__main__":
    print("Testing data fetchers...")
    print("="*60)
    
    # Test stock data
    print("\n[1/4] Testing stock data fetcher...")
    stock_result = get_stock_data("NVDA")
    if stock_result:
        print("✅ Stock data fetched successfully!")
        print(f"    Current Price: ${stock_result['current_price']}")
        print(f"    30-Day Change: {stock_result['price_change_pct_30d']}%")
        print(f"    30-Day High: ${stock_result['high_30d']}")
        print(f"    30-Day Low: ${stock_result['low_30d']}")
    else:
        print("❌ Error: Could not fetch stock data")
    
    # Test fundamental data
    print("\n[2/4] Testing fundamental data fetcher...")
    fund_result = get_fundamental_data("NVDA")
    if fund_result:
        print("✅ Fundamental data fetched successfully!")
        print(f"    Market Cap: {format_market_cap(fund_result['market_cap'])}")
        print(f"    P/E Ratio: {fund_result['pe_ratio']}")
        print(f"    Profit Margin: {fund_result['profit_margin']}")
        print(f"    ROE: {fund_result['roe']}")
    else:
        print("❌ Error: Could not fetch fundamental data")
    
    # Test news
    print("\n[3/4] Testing news fetcher...")
    news_result = get_company_news("NVDA", "NVIDIA")
    if news_result:
        print(f"✅ Found {len(news_result)} news articles")
        if news_result:
            print(f"    Latest: {news_result[0]['title'][:60]}...")
    else:
        print("❌ Error: Could not fetch news")
    
    # Test peer comparison
    print("\n[4/4] Testing peer comparison...")
    peer_result = get_comprehensive_peer_data("NVDA", ["AMD", "INTC"])
    if peer_result:
        print(f"✅ Peer data fetched for {len(peer_result)} companies")
        for ticker_sym, data in peer_result.items():
            print(f"    {ticker_sym}: P/E={data['pe_ratio']}, Margin={data['profit_margin']}")
    else:
        print("❌ Error: Could not fetch peer data")
    
    print("\n" + "="*60)
    print("DATA FETCHERS TEST COMPLETE ✅")
    print("="*60)