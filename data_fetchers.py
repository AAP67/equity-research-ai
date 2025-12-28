import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def get_stock_data(ticker):
    """
    Fetch stock price data and key metrics from Alpha Vantage
    Returns: dict with price data, metrics, and chart data
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    # Get daily time series data
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check if we got valid data
        if "Time Series (Daily)" not in data:
            return {"error": f"Could not fetch data for {ticker}. Check ticker symbol."}
        
        # Extract time series
        time_series = data["Time Series (Daily)"]
        
        # Get last 30 days of data
        dates = sorted(time_series.keys(), reverse=True)[:30]
        
        # Current price (most recent)
        current_date = dates[0]
        current_price = float(time_series[current_date]["4. close"])
        
        # Price 30 days ago
        old_date = dates[-1]
        old_price = float(time_series[old_date]["4. close"])
        
        # Calculate metrics
        price_change = current_price - old_price
        price_change_pct = (price_change / old_price) * 100
        
        # Get high/low for the period
        highs = [float(time_series[d]["2. high"]) for d in dates]
        lows = [float(time_series[d]["3. low"]) for d in dates]
        volumes = [int(time_series[d]["5. volume"]) for d in dates]
        
        # Prepare chart data
        chart_data = {
            "dates": dates,
            "prices": [float(time_series[d]["4. close"]) for d in dates],
            "volumes": volumes
        }
        
        result = {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "price_change_30d": round(price_change, 2),
            "price_change_pct_30d": round(price_change_pct, 2),
            "high_30d": round(max(highs), 2),
            "low_30d": round(min(lows), 2),
            "avg_volume_30d": round(sum(volumes) / len(volumes), 0),
            "chart_data": chart_data,
            "last_updated": current_date
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}

def get_company_news(ticker, company_name=None):
    """
    Fetch recent news about a company
    Returns: list of news articles with title, source, date, url
    """
    api_key = os.getenv('NEWS_API_KEY')
    
    # If company name not provided, use ticker
    search_query = company_name if company_name else ticker
    
    # Get news from last 7 days
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q={search_query}&from={from_date}&sortBy=relevancy&language=en&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") != "ok":
            return {"error": "Could not fetch news data"}
        
        articles = data.get("articles", [])[:10]  # Get top 10 most relevant
        
        news_items = []
        for article in articles:
            news_items.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", "")[:10],  # Just date
                "description": article.get("description", ""),
                "url": article.get("url", "")
            })
        
        return {
            "ticker": ticker.upper(),
            "news_count": len(news_items),
            "articles": news_items
        }
        
    except Exception as e:
        return {"error": f"Error fetching news: {str(e)}"}

def get_sec_filings(ticker):
    """
    Fetch recent SEC filings (10-K, 10-Q) for a company
    Returns: list of recent filings with links and filing dates
    """
    # SEC EDGAR API endpoint
    headers = {'User-Agent': 'equity-research-tool contact@example.com'}
    
    try:
        # Get company CIK (Central Index Key) first
        cik_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&ticker={ticker}&count=10&output=atom'
        
        response = requests.get(cik_url, headers=headers)
        
        if response.status_code != 200:
            return {"error": f"Could not fetch SEC data for {ticker}"}
        
        # Parse the response to extract filing information
        # The SEC returns an Atom feed which we'll parse simply
        content = response.text
        
        # Extract recent filings - look for 10-K and 10-Q
        filings = []
        
        # Simple parsing - look for filing entries
        if '10-K' in content or '10-Q' in content:
            lines = content.split('\n')
            current_filing = {}
            
            for i, line in enumerate(lines):
                if '<filing-type>' in line:
                    filing_type = line.split('>')[1].split('<')[0].strip()
                    if filing_type in ['10-K', '10-Q', '10-K/A', '10-Q/A']:
                        current_filing['type'] = filing_type
                
                if '<filing-date>' in line and current_filing:
                    filing_date = line.split('>')[1].split('<')[0].strip()
                    current_filing['date'] = filing_date
                
                if '<filing-href>' in line and current_filing:
                    filing_url = line.split('>')[1].split('<')[0].strip()
                    current_filing['url'] = filing_url
                    filings.append(current_filing.copy())
                    current_filing = {}
                
                # Limit to 5 most recent relevant filings
                if len(filings) >= 5:
                    break
        
        if not filings:
            # Fallback: provide a search link
            filings = [{
                'type': 'Search Required',
                'date': 'N/A',
                'url': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-&dateb=&owner=exclude&count=40'
            }]
        
        return {
            "ticker": ticker.upper(),
            "filings_count": len(filings),
            "filings": filings[:5]  # Return max 5 most recent
        }
        
    except Exception as e:
        return {"error": f"Error fetching SEC filings: {str(e)}"}

def get_peer_comparison(ticker, peers):
    """
    Fetch stock data for peer companies for comparison
    ticker: main company ticker
    peers: list of peer ticker symbols
    Returns: comparison data across all companies
    """
    results = []
    
    # Get data for the main company first
    main_data = get_stock_data(ticker)
    if "error" not in main_data:
        results.append({
            "ticker": main_data["ticker"],
            "price": main_data["current_price"],
            "change_30d_pct": main_data["price_change_pct_30d"],
            "is_primary": True
        })
    
    # Get data for peers
    for peer in peers:
        peer_data = get_stock_data(peer)
        if "error" not in peer_data:
            results.append({
                "ticker": peer_data["ticker"],
                "price": peer_data["current_price"],
                "change_30d_pct": peer_data["price_change_pct_30d"],
                "is_primary": False
            })
    
    return {
        "primary_ticker": ticker.upper(),
        "comparison_count": len(results),
        "comparison_data": results
    }

def get_fundamental_data(ticker):
    """
    Fetch fundamental metrics: valuation ratios, profitability metrics, financial health
    Returns: dict with P/E, P/S, margins, ROE, etc.
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    # Company Overview endpoint has all fundamental data
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data or 'Symbol' not in data:
            return {"error": f"Could not fetch fundamental data for {ticker}"}
        
        # Extract key metrics with safe fallbacks
        def safe_float(value, default=0):
            try:
                return float(value) if value and value != 'None' else default
            except (ValueError, TypeError):
                return default
        
        fundamentals = {
            "ticker": ticker.upper(),
            "company_name": data.get('Name', ticker),
            "sector": data.get('Sector', 'N/A'),
            "industry": data.get('Industry', 'N/A'),
            
            # Valuation Metrics
            "market_cap": safe_float(data.get('MarketCapitalization', 0)),
            "pe_ratio": safe_float(data.get('PERatio', 0)),
            "peg_ratio": safe_float(data.get('PEGRatio', 0)),
            "price_to_book": safe_float(data.get('PriceToBookRatio', 0)),
            "price_to_sales": safe_float(data.get('PriceToSalesRatioTTM', 0)),
            "ev_to_ebitda": safe_float(data.get('EVToEBITDA', 0)),
            
            # Profitability Metrics
            "profit_margin": safe_float(data.get('ProfitMargin', 0)) * 100,  # Convert to %
            "operating_margin": safe_float(data.get('OperatingMarginTTM', 0)) * 100,
            "gross_margin": safe_float(data.get('GrossMarginTTM', 0)) * 100,  # Added this
            "roe": safe_float(data.get('ReturnOnEquityTTM', 0)) * 100,
            "roa": safe_float(data.get('ReturnOnAssetsTTM', 0)) * 100,
            
            # Per Share Metrics
            "eps": safe_float(data.get('EPS', 0)),
            "dividend_yield": safe_float(data.get('DividendYield', 0)) * 100,
            
            # Growth Metrics
            "revenue_ttm": safe_float(data.get('RevenueTTM', 0)),
            "revenue_growth_yoy": safe_float(data.get('QuarterlyRevenueGrowthYOY', 0)) * 100,
            "earnings_growth_yoy": safe_float(data.get('QuarterlyEarningsGrowthYOY', 0)) * 100,
            
            # Financial Health
            "beta": safe_float(data.get('Beta', 0)),
            "52_week_high": safe_float(data.get('52WeekHigh', 0)),
            "52_week_low": safe_float(data.get('52WeekLow', 0)),
        }
        
        # Format market cap for readability
        if fundamentals['market_cap'] > 0:
            fundamentals['market_cap_formatted'] = format_market_cap(fundamentals['market_cap'])
        else:
            fundamentals['market_cap_formatted'] = 'N/A'
        
        return fundamentals
        
    except Exception as e:
        return {"error": f"Error fetching fundamentals: {str(e)}"}


def format_market_cap(market_cap):
    """Helper function to format market cap in B/T"""
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"

# Test functions
if __name__ == "__main__":
    print("="*60)
    print("TESTING DATA FETCHERS")
    print("="*60)
    
    # Test 1: Stock Data
    print("\n[1/5] Testing stock data fetcher...")
    stock_result = get_stock_data("NVDA")
    
    if "error" in stock_result:
        print(f"❌ Error: {stock_result['error']}")
    else:
        print(f"✅ Stock data fetched successfully!")
        print(f"    Ticker: {stock_result['ticker']}")
        print(f"    Current Price: ${stock_result['current_price']}")
        print(f"    30-Day Change: {stock_result['price_change_pct_30d']}%")
    
    # Test 2: News Data
    print("\n[2/5] Testing news fetcher...")
    news_result = get_company_news("NVDA", "NVIDIA")
    
    if "error" in news_result:
        print(f"❌ Error: {news_result['error']}")
    else:
        print(f"✅ News fetched successfully!")
        print(f"    Found {news_result['news_count']} articles")
        if news_result['articles']:
            print(f"    Latest: {news_result['articles'][0]['title'][:70]}...")
    
    # Test 3: SEC Filings
    print("\n[3/5] Testing SEC filings fetcher...")
    sec_result = get_sec_filings("NVDA")
    
    if "error" in sec_result:
        print(f"❌ Error: {sec_result['error']}")
    else:
        print(f"✅ SEC filings fetched successfully!")
        print(f"    Found {sec_result['filings_count']} recent filings")
    
    # Test 4: Peer Comparison
    print("\n[4/5] Testing peer comparison...")
    peer_result = get_peer_comparison("NVDA", ["AMD", "INTC"])
    
    print(f"✅ Peer comparison fetched!")
    print(f"    Comparing {peer_result['comparison_count']} companies:")
    for comp in peer_result['comparison_data']:
        symbol = "→" if comp['is_primary'] else " "
        print(f"    {symbol} {comp['ticker']}: ${comp['price']} ({comp['change_30d_pct']:+.2f}%)")
    
    # Test 5: Fundamental Data (NEW!)
    print("\n[5/5] Testing fundamental data fetcher...")
    fundamental_result = get_fundamental_data("NVDA")
    
    if "error" in fundamental_result:
        print(f"❌ Error: {fundamental_result['error']}")
    else:
        print(f"✅ Fundamental data fetched successfully!")
        print(f"    Company: {fundamental_result['company_name']}")
        print(f"    Market Cap: {fundamental_result['market_cap_formatted']}")
        print(f"    P/E Ratio: {fundamental_result['pe_ratio']:.2f}")
        print(f"    Profit Margin: {fundamental_result['profit_margin']:.2f}%")
        print(f"    ROE: {fundamental_result['roe']:.2f}%")
    
    print("\n" + "="*60)
    print("ALL DATA FETCHERS COMPLETE ✅")
    print("="*60)