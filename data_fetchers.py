import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# API Keys
FMP_API_KEY = os.getenv('FMP_API_KEY', 'nxio4zeKtGuItR5eXrw2pcGmqgQs3VlH')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '8I0IMPIUNWV89JF9')


# ============================================================
# STOCK PRICE DATA - Fallback Chain: FMP → Alpha Vantage → yfinance
# ============================================================

def get_stock_data_fmp(ticker):
    """Get stock price data from Financial Modeling Prep"""
    try:
        # Get current quote
        quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
        quote_resp = requests.get(quote_url, timeout=10)
        quote_data = quote_resp.json()
        
        if not quote_data or isinstance(quote_data, dict) and 'Error' in str(quote_data):
            return None
        
        quote = quote_data[0]
        
        # Get historical prices (30 days)
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        hist_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
        hist_resp = requests.get(hist_url, timeout=10)
        hist_data = hist_resp.json()
        
        if not hist_data or 'historical' not in hist_data:
            return None
        
        historical = hist_data['historical'][:30]  # Last 30 trading days
        
        if not historical:
            return None
        
        current_price = quote.get('price', historical[0]['close'])
        price_30d_ago = historical[-1]['close']
        price_change_30d = current_price - price_30d_ago
        price_change_pct_30d = (price_change_30d / price_30d_ago) * 100
        
        highs = [d['high'] for d in historical]
        lows = [d['low'] for d in historical]
        volumes = [d['volume'] for d in historical]
        
        chart_data = [{'Date': d['date'], 'Close': d['close']} for d in reversed(historical)]
        
        print(f"[FMP] Stock data fetched for {ticker}")
        return {
            'current_price': round(current_price, 2),
            'price_change_30d': round(price_change_30d, 2),
            'price_change_pct_30d': round(price_change_pct_30d, 2),
            'high_30d': round(max(highs), 2),
            'low_30d': round(min(lows), 2),
            'avg_volume_30d': int(sum(volumes) / len(volumes)),
            'chart_data': chart_data
        }
    except Exception as e:
        print(f"[FMP] Error fetching stock data for {ticker}: {e}")
        return None


def get_stock_data_alpha_vantage(ticker):
    """Get stock price data from Alpha Vantage"""
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=compact&apikey={ALPHA_VANTAGE_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if 'Time Series (Daily)' not in data:
            return None
        
        ts = data['Time Series (Daily)']
        dates = sorted(ts.keys(), reverse=True)[:30]
        
        if not dates:
            return None
        
        current_price = float(ts[dates[0]]['4. close'])
        price_30d_ago = float(ts[dates[-1]]['4. close'])
        price_change_30d = current_price - price_30d_ago
        price_change_pct_30d = (price_change_30d / price_30d_ago) * 100
        
        highs = [float(ts[d]['2. high']) for d in dates]
        lows = [float(ts[d]['3. low']) for d in dates]
        volumes = [int(ts[d]['5. volume']) for d in dates]
        
        chart_data = [{'Date': d, 'Close': float(ts[d]['4. close'])} for d in reversed(dates)]
        
        print(f"[Alpha Vantage] Stock data fetched for {ticker}")
        return {
            'current_price': round(current_price, 2),
            'price_change_30d': round(price_change_30d, 2),
            'price_change_pct_30d': round(price_change_pct_30d, 2),
            'high_30d': round(max(highs), 2),
            'low_30d': round(min(lows), 2),
            'avg_volume_30d': int(sum(volumes) / len(volumes)),
            'chart_data': chart_data
        }
    except Exception as e:
        print(f"[Alpha Vantage] Error fetching stock data for {ticker}: {e}")
        return None


def get_stock_data_yfinance(ticker):
    """Get stock price data from yfinance (last resort fallback)"""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        price_30d_ago = hist['Close'].iloc[0]
        price_change_30d = current_price - price_30d_ago
        price_change_pct_30d = (price_change_30d / price_30d_ago) * 100
        
        print(f"[yfinance] Stock data fetched for {ticker}")
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
        print(f"[yfinance] Error fetching stock data for {ticker}: {e}")
        return None


def get_stock_data(ticker):
    """
    Get stock price data with fallback chain: FMP → Alpha Vantage → yfinance
    """
    for fetcher, name in [
        (get_stock_data_fmp, "FMP"),
        (get_stock_data_alpha_vantage, "Alpha Vantage"),
        (get_stock_data_yfinance, "yfinance"),
    ]:
        result = fetcher(ticker)
        if result:
            return result
        print(f"[{name}] Failed for {ticker}, trying next...")
    
    print(f"All sources failed for {ticker}")
    return None


# ============================================================
# FUNDAMENTAL DATA - Fallback Chain: FMP → yfinance
# ============================================================

def get_fundamental_data_fmp(ticker):
    """Get fundamental data from FMP"""
    try:
        # Company profile
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_resp = requests.get(profile_url, timeout=10)
        profile_data = profile_resp.json()
        
        if not profile_data or isinstance(profile_data, dict) and 'Error' in str(profile_data):
            return None
        
        profile = profile_data[0]
        
        # Key metrics
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"
        ratios_resp = requests.get(ratios_url, timeout=10)
        ratios_data = ratios_resp.json()
        
        ratios = ratios_data[0] if ratios_data and isinstance(ratios_data, list) else {}
        
        # Growth
        growth_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?limit=1&apikey={FMP_API_KEY}"
        growth_resp = requests.get(growth_url, timeout=10)
        growth_data = growth_resp.json()
        growth = growth_data[0] if growth_data and isinstance(growth_data, list) else {}
        
        def safe_pct(val, label=""):
            if val is None or val == 'N/A':
                return 'N/A'
            try:
                return f"{float(val)*100:.2f}%"
            except:
                return 'N/A'
        
        fundamental_data = {
            'market_cap': profile.get('mktCap', 'N/A'),
            'pe_ratio': profile.get('peRatio') or ratios.get('peRatioTTM', 'N/A'),
            'forward_pe': ratios.get('priceEarningsToGrowthRatioTTM', 'N/A'),
            'peg_ratio': ratios.get('priceEarningsToGrowthRatioTTM', 'N/A'),
            'price_to_book': ratios.get('priceToBookRatioTTM', 'N/A'),
            'price_to_sales': ratios.get('priceToSalesRatioTTM', 'N/A'),
            'ev_to_ebitda': ratios.get('enterpriseValueOverEBITDATTM', 'N/A'),
            
            'profit_margin': safe_pct(ratios.get('netProfitMarginTTM')),
            'operating_margin': safe_pct(ratios.get('operatingProfitMarginTTM')),
            'gross_margin': safe_pct(ratios.get('grossProfitMarginTTM')),
            'roe': safe_pct(ratios.get('returnOnEquityTTM')),
            'roa': safe_pct(ratios.get('returnOnAssetsTTM')),
            
            'revenue_growth_yoy': safe_pct(growth.get('revenueGrowth')),
            'earnings_growth_yoy': safe_pct(growth.get('epsgrowth')),
            
            'beta': profile.get('beta', 'N/A'),
            'dividend_yield': safe_pct(ratios.get('dividendYieldTTM')),
            '52_week_high': profile.get('range', 'N/A').split('-')[-1].strip() if profile.get('range') else 'N/A',
            '52_week_low': profile.get('range', 'N/A').split('-')[0].strip() if profile.get('range') else 'N/A',
        }
        
        # Clean up None values
        for k, v in fundamental_data.items():
            if v is None:
                fundamental_data[k] = 'N/A'
        
        print(f"[FMP] Fundamental data fetched for {ticker}")
        return fundamental_data
        
    except Exception as e:
        print(f"[FMP] Error fetching fundamental data for {ticker}: {e}")
        return None


def get_fundamental_data_yfinance(ticker):
    """Get fundamental data from yfinance (fallback)"""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) < 5:
            return None
        
        fundamental_data = {
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'forward_pe': info.get('forwardPE', 'N/A'),
            'peg_ratio': info.get('pegRatio', 'N/A'),
            'price_to_book': info.get('priceToBook', 'N/A'),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
            'ev_to_ebitda': info.get('enterpriseToEbitda', 'N/A'),
            'profit_margin': info.get('profitMargins', 'N/A'),
            'operating_margin': info.get('operatingMargins', 'N/A'),
            'gross_margin': info.get('grossMargins', 'N/A'),
            'roe': info.get('returnOnEquity', 'N/A'),
            'roa': info.get('returnOnAssets', 'N/A'),
            'revenue_growth_yoy': info.get('revenueGrowth', 'N/A'),
            'earnings_growth_yoy': info.get('earningsGrowth', 'N/A'),
            'beta': info.get('beta', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
        }
        
        if fundamental_data['profit_margin'] != 'N/A' and isinstance(fundamental_data['profit_margin'], (int, float)):
            fundamental_data['profit_margin'] = f"{fundamental_data['profit_margin']*100:.2f}%"
        if fundamental_data['roe'] != 'N/A' and isinstance(fundamental_data['roe'], (int, float)):
            fundamental_data['roe'] = f"{fundamental_data['roe']*100:.2f}%"
        if fundamental_data['revenue_growth_yoy'] != 'N/A' and isinstance(fundamental_data['revenue_growth_yoy'], (int, float)):
            fundamental_data['revenue_growth_yoy'] = f"{fundamental_data['revenue_growth_yoy']*100:.2f}%"
        
        print(f"[yfinance] Fundamental data fetched for {ticker}")
        return fundamental_data
        
    except Exception as e:
        print(f"[yfinance] Error fetching fundamental data for {ticker}: {e}")
        return None


def get_fundamental_data(ticker):
    """
    Get fundamental data with fallback chain: FMP → yfinance
    """
    for fetcher, name in [
        (get_fundamental_data_fmp, "FMP"),
        (get_fundamental_data_yfinance, "yfinance"),
    ]:
        result = fetcher(ticker)
        if result:
            return result
        print(f"[{name}] Fundamentals failed for {ticker}, trying next...")
    
    print(f"All fundamental sources failed for {ticker}")
    return None


# ============================================================
# NEWS - Same as before
# ============================================================

def get_company_news(ticker, company_name=None):
    """Fetch recent news about a company"""
    api_key = os.getenv('NEWS_API_KEY')
    
    search_query = company_name if company_name else ticker
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q={search_query}&from={from_date}&sortBy=relevancy&language=en&apiKey={api_key}'
    
    try:
        response = requests.get(url, timeout=10)
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


# ============================================================
# HELPERS
# ============================================================

def format_market_cap(market_cap):
    """Helper function to format market cap in B/T"""
    if market_cap == 'N/A' or market_cap is None:
        return 'N/A'
    try:
        market_cap = float(market_cap)
    except:
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
    """Get fundamental data for ticker + all peers for comparison"""
    all_data = {}
    
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


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("Testing data fetchers with fallback chain...")
    print("=" * 60)
    
    print("\n[1/3] Testing stock data (FMP → Alpha Vantage → yfinance)...")
    stock_result = get_stock_data("AAPL")
    if stock_result:
        print(f"  Price: ${stock_result['current_price']}")
        print(f"  30D Change: {stock_result['price_change_pct_30d']}%")
    else:
        print("  FAILED - all sources")
    
    print("\n[2/3] Testing fundamental data (FMP → yfinance)...")
    fund_result = get_fundamental_data("AAPL")
    if fund_result:
        print(f"  Market Cap: {format_market_cap(fund_result['market_cap'])}")
        print(f"  P/E: {fund_result['pe_ratio']}")
        print(f"  Profit Margin: {fund_result['profit_margin']}")
    else:
        print("  FAILED - all sources")
    
    print("\n[3/3] Testing news...")
    news = get_company_news("AAPL", "Apple")
    print(f"  Found {len(news)} articles")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")