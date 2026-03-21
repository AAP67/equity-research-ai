import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# API Keys — must be set in .env or Streamlit secrets, never hardcoded
FMP_API_KEY = os.getenv('FMP_API_KEY')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')


# ============================================================
# STOCK PRICE DATA - Fallback Chain: FMP → Alpha Vantage → yfinance
# ============================================================

def get_stock_data_fmp(ticker):
    """Get stock price data from Financial Modeling Prep"""
    if not FMP_API_KEY:
        return None
    try:
        # Get current quote
        quote_url = f"https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={FMP_API_KEY}"
        quote_resp = requests.get(quote_url, timeout=10)
        quote_data = quote_resp.json()
        
        if not quote_data or isinstance(quote_data, dict) and 'Error' in str(quote_data):
            return None
        
        quote = quote_data[0]
        
        # Get historical prices (30 days)
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        hist_url = f"https://financialmodelingprep.com/stable/historical-price-eod/full?symbol={ticker}&from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
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
    if not ALPHA_VANTAGE_KEY:
        return None
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
    if not FMP_API_KEY:
        return None
    try:
        # Company profile
        profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={FMP_API_KEY}"
        profile_resp = requests.get(profile_url, timeout=10)
        profile_data = profile_resp.json()
        
        if not profile_data or isinstance(profile_data, dict) and 'Error' in str(profile_data):
            return None
        
        profile = profile_data[0]
        
        # Key metrics
        ratios_url = f"https://financialmodelingprep.com/stable/ratios-ttm?symbol={ticker}&apikey={FMP_API_KEY}"
        ratios_resp = requests.get(ratios_url, timeout=10)
        ratios_data = ratios_resp.json()
        
        ratios = ratios_data[0] if ratios_data and isinstance(ratios_data, list) else {}
        
        # Growth
        growth_url = f"https://financialmodelingprep.com/stable/financial-growth?symbol={ticker}&limit=1&apikey={FMP_API_KEY}"
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
# REVENUE SEGMENTATION - FMP
# ============================================================

def get_revenue_segmentation(ticker):
    """
    Fetch revenue breakdown by product line and geography.
    Returns: dict with 'by_product' and 'by_geography' keys,
    each containing a list of {segment, revenue, percentage} dicts.
    """
    if not FMP_API_KEY:
        return None
    result = {'by_product': [], 'by_geography': []}
    
    # Product segmentation
    try:
        url = f"https://financialmodelingprep.com/stable/revenue-product-segmentation?symbol={ticker}&structure=flat&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            # Get most recent period
            latest = data[0]
            # latest is a dict like {"2024-01-28": {"Gaming": 123, "Datacenter": 456, ...}}
            if isinstance(latest, dict):
                for period, segments in latest.items():
                    if isinstance(segments, dict):
                        total = sum(v for v in segments.values() if isinstance(v, (int, float)))
                        for segment, revenue in segments.items():
                            if isinstance(revenue, (int, float)) and total > 0:
                                result['by_product'].append({
                                    'segment': segment,
                                    'revenue': revenue,
                                    'percentage': round((revenue / total) * 100, 1)
                                })
                        # Sort by revenue descending
                        result['by_product'].sort(key=lambda x: x['revenue'], reverse=True)
                        break  # Only need most recent period
            
            print(f"[FMP] Product segmentation fetched for {ticker}: {len(result['by_product'])} segments")
    except Exception as e:
        print(f"[FMP] Error fetching product segmentation for {ticker}: {e}")
    
    # Geographic segmentation
    try:
        url = f"https://financialmodelingprep.com/stable/revenue-geographic-segmentation?symbol={ticker}&structure=flat&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            if isinstance(latest, dict):
                for period, segments in latest.items():
                    if isinstance(segments, dict):
                        total = sum(v for v in segments.values() if isinstance(v, (int, float)))
                        for segment, revenue in segments.items():
                            if isinstance(revenue, (int, float)) and total > 0:
                                result['by_geography'].append({
                                    'segment': segment,
                                    'revenue': revenue,
                                    'percentage': round((revenue / total) * 100, 1)
                                })
                        result['by_geography'].sort(key=lambda x: x['revenue'], reverse=True)
                        break
            
            print(f"[FMP] Geographic segmentation fetched for {ticker}: {len(result['by_geography'])} regions")
    except Exception as e:
        print(f"[FMP] Error fetching geographic segmentation for {ticker}: {e}")
    
    return result if (result['by_product'] or result['by_geography']) else None


# ============================================================
# EARNINGS CALL TRANSCRIPTS - FMP
# ============================================================

def get_earnings_transcript(ticker, num_quarters=2):
    """
    Fetch recent earnings call transcripts.
    Returns: list of dicts with 'quarter', 'year', 'content' keys.
    """
    if not FMP_API_KEY:
        return None
    transcripts = []
    
    try:
        # First get available transcript dates
        dates_url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={ticker}&apikey={FMP_API_KEY}"
        dates_resp = requests.get(dates_url, timeout=10)
        dates_data = dates_resp.json()
        
        if not dates_data or not isinstance(dates_data, list):
            print(f"[FMP] No transcript dates found for {ticker}")
            return None
        
        # Get the most recent quarters
        recent = dates_data[:num_quarters]
        
        for entry in recent:
            quarter = entry.get('quarter', 0)
            year = entry.get('year', 0)
            
            if not quarter or not year:
                continue
            
            # Fetch the actual transcript
            transcript_url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={ticker}&quarter={quarter}&year={year}&apikey={FMP_API_KEY}"
            transcript_resp = requests.get(transcript_url, timeout=15)
            transcript_data = transcript_resp.json()
            
            if transcript_data and isinstance(transcript_data, list) and len(transcript_data) > 0:
                content = transcript_data[0].get('content', '')
                
                if content:
                    # Transcripts can be very long — cap at 15K chars per transcript
                    transcripts.append({
                        'quarter': f"Q{quarter}",
                        'year': year,
                        'content': content[:15000],
                        'full_length': len(content)
                    })
                    print(f"[FMP] Transcript fetched for {ticker} Q{quarter} {year}: {len(content)} chars")
        
        return transcripts if transcripts else None
        
    except Exception as e:
        print(f"[FMP] Error fetching transcripts for {ticker}: {e}")
        return None


# ============================================================
# PHASE 3: HISTORICAL FINANCIALS (5-Year Trends)
# ============================================================

def get_historical_financials(ticker, years=5):
    """
    Fetch 5 years of income statements, cash flows, and ratios.
    Returns: dict with 'income', 'cashflow', 'ratios' keys, each a list of annual dicts.
    Sorted oldest-to-newest for trend analysis.
    """
    if not FMP_API_KEY:
        return None
    
    result = {}
    
    try:
        # Income statements
        url = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&limit={years}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data and isinstance(data, list):
            result['income'] = sorted(data, key=lambda x: x.get('date', ''))
            print(f"[FMP] Historical income statements fetched for {ticker}: {len(result['income'])} years")
        else:
            result['income'] = []
    except Exception as e:
        print(f"[FMP] Error fetching historical income for {ticker}: {e}")
        result['income'] = []
    
    try:
        # Cash flow statements
        url = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&limit={years}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data and isinstance(data, list):
            result['cashflow'] = sorted(data, key=lambda x: x.get('date', ''))
            print(f"[FMP] Historical cash flows fetched for {ticker}: {len(result['cashflow'])} years")
        else:
            result['cashflow'] = []
    except Exception as e:
        print(f"[FMP] Error fetching historical cash flow for {ticker}: {e}")
        result['cashflow'] = []
    
    try:
        # Financial ratios
        url = f"https://financialmodelingprep.com/stable/ratios?symbol={ticker}&limit={years}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data and isinstance(data, list):
            result['ratios'] = sorted(data, key=lambda x: x.get('date', ''))
            print(f"[FMP] Historical ratios fetched for {ticker}: {len(result['ratios'])} years")
        else:
            result['ratios'] = []
    except Exception as e:
        print(f"[FMP] Error fetching historical ratios for {ticker}: {e}")
        result['ratios'] = []
    
    return result if any(result.values()) else None


def compute_financial_trends(historical_data):
    """
    Pure Python — no API calls. Computes trend metrics from historical financials.
    Returns: dict with computed trends, CAGRs, and direction indicators.
    """
    if not historical_data:
        return None
    
    income = historical_data.get('income', [])
    cashflow = historical_data.get('cashflow', [])
    ratios = historical_data.get('ratios', [])
    
    trends = {
        'years': [],
        'revenue': [],
        'net_income': [],
        'gross_margin': [],
        'operating_margin': [],
        'net_margin': [],
        'roe': [],
        'fcf': [],
        'capex': [],
        'capex_pct_revenue': [],
        'cash_conversion': [],
    }
    
    # Build year-by-year data (oldest to newest)
    for i, inc in enumerate(income):
        year = inc.get('fiscalYear') or inc.get('date', '?')[:4]
        revenue = inc.get('revenue', 0)
        net_income = inc.get('netIncome', 0)
        
        trends['years'].append(str(year))
        trends['revenue'].append(revenue)
        trends['net_income'].append(net_income)
        
        # Capex and FCF from cashflow (matched by index)
        if i < len(cashflow):
            fcf = cashflow[i].get('freeCashFlow', 0)
            capex = abs(cashflow[i].get('capitalExpenditure', 0))
            trends['fcf'].append(fcf)
            trends['capex'].append(capex)
            trends['capex_pct_revenue'].append(round(capex / revenue * 100, 1) if revenue else 0)
            trends['cash_conversion'].append(round(fcf / net_income * 100, 1) if net_income and net_income > 0 else 0)
        
        # Margins and ROE from ratios (matched by index)
        if i < len(ratios):
            r = ratios[i]
            trends['gross_margin'].append(round((r.get('grossProfitMargin') or 0) * 100, 1))
            trends['operating_margin'].append(round((r.get('operatingProfitMargin') or 0) * 100, 1))
            trends['net_margin'].append(round((r.get('netProfitMargin') or 0) * 100, 1))
            trends['roe'].append(round((r.get('returnOnEquity') or 0) * 100, 1))
    
    # Computed summary metrics
    def _cagr(start, end, years):
        if not start or start <= 0 or not end or end <= 0 or years <= 0:
            return None
        return round(((end / start) ** (1 / years) - 1) * 100, 1)
    
    def _trend_direction(values):
        """Returns 'expanding', 'compressing', or 'stable' based on first vs last half"""
        if len(values) < 3:
            return 'insufficient data'
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        diff_pct = ((second_half_avg - first_half_avg) / abs(first_half_avg) * 100) if first_half_avg else 0
        if diff_pct > 5:
            return 'expanding'
        elif diff_pct < -5:
            return 'compressing'
        else:
            return 'stable'
    
    rev = trends['revenue']
    summary = {}
    
    # Revenue CAGRs
    if len(rev) >= 4:
        summary['revenue_cagr_3yr'] = _cagr(rev[-4], rev[-1], 3)
    if len(rev) >= 5:
        summary['revenue_cagr_5yr'] = _cagr(rev[0], rev[-1], len(rev) - 1)
    
    # Latest year metrics
    if rev:
        summary['latest_revenue'] = rev[-1]
        summary['latest_net_income'] = trends['net_income'][-1] if trends['net_income'] else None
    
    # Trend directions
    if trends['gross_margin']:
        summary['gross_margin_trend'] = _trend_direction(trends['gross_margin'])
    if trends['operating_margin']:
        summary['operating_margin_trend'] = _trend_direction(trends['operating_margin'])
    if trends['net_margin']:
        summary['net_margin_trend'] = _trend_direction(trends['net_margin'])
    if trends['roe']:
        summary['roe_trend'] = _trend_direction(trends['roe'])
    
    # Cash conversion average
    if trends['cash_conversion']:
        valid_cc = [c for c in trends['cash_conversion'] if c > 0]
        summary['avg_cash_conversion'] = round(sum(valid_cc) / len(valid_cc), 1) if valid_cc else 0
    
    # Capex intensity trend
    if trends['capex_pct_revenue']:
        summary['capex_intensity_trend'] = _trend_direction(trends['capex_pct_revenue'])
        summary['latest_capex_pct'] = trends['capex_pct_revenue'][-1]
    
    trends['summary'] = summary
    return trends


# ============================================================
# PHASE 4: ANALYST ESTIMATES (Forward Consensus)
# ============================================================

def get_analyst_estimates(ticker, years=3):
    """
    Fetch consensus analyst estimates (revenue, EPS, net income) for next 2-3 years.
    Returns: list of dicts sorted nearest-to-farthest, with low/avg/high for each metric.
    """
    if not FMP_API_KEY:
        return None
    
    try:
        url = f"https://financialmodelingprep.com/stable/analyst-estimates?symbol={ticker}&period=annual&limit={years}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if not data or not isinstance(data, list):
            print(f"[FMP] No analyst estimates found for {ticker}")
            return None
        
        # Sort nearest first
        estimates = sorted(data, key=lambda x: x.get('date', ''))
        
        result = []
        for est in estimates:
            result.append({
                'date': est.get('date', '?'),
                'revenue_low': est.get('revenueLow', 0),
                'revenue_avg': est.get('revenueAvg', 0),
                'revenue_high': est.get('revenueHigh', 0),
                'eps_low': est.get('epsLow', 0),
                'eps_avg': est.get('epsAvg', 0),
                'eps_high': est.get('epsHigh', 0),
                'net_income_low': est.get('netIncomeLow', 0),
                'net_income_avg': est.get('netIncomeAvg', 0),
                'net_income_high': est.get('netIncomeHigh', 0),
                'ebitda_avg': est.get('ebitdaAvg', 0),
                'num_analysts_revenue': est.get('numAnalystsRevenue', 0),
                'num_analysts_eps': est.get('numAnalystsEps', 0),
            })
        
        print(f"[FMP] Analyst estimates fetched for {ticker}: {len(result)} periods")
        return result
    
    except Exception as e:
        print(f"[FMP] Error fetching analyst estimates for {ticker}: {e}")
        return None


# ============================================================
# PHASE 5: HISTORICAL VALUATION CONTEXT
# ============================================================

def compute_valuation_context(historical_data):
    """
    Extract valuation multiples from the 5-year ratios data (already fetched in Phase 3).
    Computes current vs. historical average to show premium/discount to self.
    No new API calls needed.
    """
    if not historical_data or not historical_data.get('ratios'):
        return None
    
    ratios = historical_data['ratios']  # Already sorted oldest-to-newest
    
    metrics = {
        'pe': {'key': 'priceToEarningsRatio', 'label': 'P/E Ratio'},
        'ps': {'key': 'priceToSalesRatio', 'label': 'P/S Ratio'},
        'pfcf': {'key': 'priceToFreeCashFlowRatio', 'label': 'P/FCF Ratio'},
        'ev_ebitda': {'key': 'enterpriseValueMultiple', 'label': 'EV/EBITDA'},
        'peg': {'key': 'priceEarningsToGrowthRatio', 'label': 'PEG Ratio'},
    }
    
    result = {'years': [], 'multiples': {}}
    
    for m_key, m_info in metrics.items():
        values = []
        for r in ratios:
            val = r.get(m_info['key'])
            if val is not None and isinstance(val, (int, float)) and val > 0 and val < 1000:
                values.append(round(val, 2))
            else:
                values.append(None)
        result['multiples'][m_key] = {
            'label': m_info['label'],
            'values': values,
        }
    
    # Extract years
    for r in ratios:
        year = r.get('fiscalYear') or r.get('date', '?')[:4]
        result['years'].append(str(year))
    
    # Compute summary for each multiple
    for m_key, m_data in result['multiples'].items():
        valid = [v for v in m_data['values'] if v is not None]
        if valid:
            m_data['current'] = valid[-1]
            m_data['avg_5yr'] = round(sum(valid) / len(valid), 2)
            m_data['high_5yr'] = max(valid)
            m_data['low_5yr'] = min(valid)
            # Premium/discount to own average
            if m_data['avg_5yr'] > 0:
                m_data['vs_avg_pct'] = round(((m_data['current'] / m_data['avg_5yr']) - 1) * 100, 1)
            else:
                m_data['vs_avg_pct'] = None
        else:
            m_data['current'] = None
            m_data['avg_5yr'] = None
            m_data['high_5yr'] = None
            m_data['low_5yr'] = None
            m_data['vs_avg_pct'] = None
    
    return result


# ============================================================
# PHASE 7: CATALYST EVENTS
# ============================================================

def get_catalyst_events(ticker):
    """
    Fetch upcoming/recent catalyst events: earnings dates, dividends.
    Returns: dict with 'earnings' and 'dividends' keys.
    """
    if not FMP_API_KEY:
        return None
    
    result = {'earnings': [], 'dividends': []}
    
    # Earnings calendar — returns all stocks, filter to our ticker
    try:
        url = f"https://financialmodelingprep.com/stable/earnings-calendar?symbol={ticker}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data and isinstance(data, list):
            for entry in data:
                if entry.get('symbol', '').upper() == ticker.upper():
                    result['earnings'].append({
                        'date': entry.get('date', ''),
                        'eps_estimated': entry.get('epsEstimated'),
                        'eps_actual': entry.get('epsActual'),
                        'revenue_estimated': entry.get('revenueEstimated'),
                        'revenue_actual': entry.get('revenueActual'),
                    })
            # Sort by date, most recent first
            result['earnings'].sort(key=lambda x: x['date'], reverse=True)
            print(f"[FMP] Earnings events fetched for {ticker}: {len(result['earnings'])} events")
    except Exception as e:
        print(f"[FMP] Error fetching earnings calendar for {ticker}: {e}")
    
    # Dividends
    try:
        url = f"https://financialmodelingprep.com/stable/dividends?symbol={ticker}&apikey={FMP_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data and isinstance(data, list):
            for entry in data[:4]:  # Last 4 dividends
                result['dividends'].append({
                    'date': entry.get('date', ''),
                    'payment_date': entry.get('paymentDate', ''),
                    'dividend': entry.get('dividend', 0),
                    'frequency': entry.get('frequency', ''),
                })
            print(f"[FMP] Dividend events fetched for {ticker}: {len(result['dividends'])} events")
    except Exception as e:
        print(f"[FMP] Error fetching dividends for {ticker}: {e}")
    
    return result if (result['earnings'] or result['dividends']) else None


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