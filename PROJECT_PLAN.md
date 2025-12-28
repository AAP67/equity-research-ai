# 10-K Analysis Tool - Project Plan

## What We're Building
AI-powered 10-K filing analysis tool that reads SEC filings and generates intelligent summaries.

## Completed
✅ Basic equity research tool with stock data, news, fundamentals
✅ Deployed to Streamlit Cloud
✅ Got feedback from DE Shaw analyst
✅ Decided to pivot to 10-K focus

## Current Status
🔄 Just updated requirements.txt with SEC parsing libraries
🔄 About to build sec_parser.py

## Next Steps (8-10 hours remaining)

### Phase 1: SEC Filing Parser (2-3 hours)
- [ ] Create sec_parser.py
- [ ] Build download_10k() function
- [ ] Build extract_risk_factors() function
- [ ] Build extract_mda() function
- [ ] Test with NVDA and Belden

### Phase 2: AI Analysis (2 hours)
- [ ] Update ai_analyzer.py with 10-K analysis functions
- [ ] Summarize Risk Factors
- [ ] Identify changes vs. prior year
- [ ] Generate executive summary

### Phase 3: UI Redesign (1.5 hours)
- [ ] Simplify app.py to focus on 10-K only
- [ ] Show filing metadata
- [ ] Display analysis in clean sections

### Phase 4: Year-over-Year Comparison (2 hours)
- [ ] Fetch current + prior year 10-K
- [ ] Compare risk factors
- [ ] Highlight changes

### Phase 5: Testing & Polish (1 hour)
- [ ] Test 5-10 companies
- [ ] Speed optimization
- [ ] Final deployment

## Key Files
- `app.py` - Main Streamlit UI
- `sec_parser.py` - NEW - SEC filing parser
- `ai_analyzer.py` - AI analysis functions
- `data_fetchers.py` - Data collection (may deprecate some)
- `requirements.txt` - Python dependencies

## GitHub Repo
https://github.com/AAP67/equity-research-ai

## Streamlit App
https://equity-research-ai-[your-url].streamlit.app

## API Keys (in .env locally, in Streamlit Secrets on cloud)
- ANTHROPIC_API_KEY
- ALPHA_VANTAGE_API_KEY (may not need anymore)
- NEWS_API_KEY (may not need anymore)

## Feedback from DE Shaw Analyst
1. Too slow (need to optimize)
2. Too broad (pivot to specific use case - 10-K analysis)
3. Missing 10-K data for smaller companies like Belden
