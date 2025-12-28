# Equity Analyst Assistant

AI-powered equity research tool that provides institutional-grade stock analysis in 3 minutes.

**Live Demo:** [Your Streamlit URL here]

## Features
- 📊 Real-time financial metrics (P/E, margins, ROE, growth)
- 🔄 Peer comparison with AI analysis
- 📈 30-day price trends and momentum
- 📰 News sentiment analysis
- 🎯 AI-powered investment summary

## Tech Stack
- **Frontend:** Streamlit
- **Data:** yfinance, News API
- **AI:** Claude Sonnet 4 (Anthropic)
- **Deployment:** Streamlit Cloud

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/AAP67/equity-research-ai.git
cd equity-research-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys
Create a `.env` file:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
NEWS_API_KEY=your_news_api_key_here
```

### 5. Run locally
```bash
streamlit run app.py
```

## Usage
1. Enter stock ticker (e.g., NVDA)
2. Optionally add peer tickers (e.g., AMD, INTC)
3. Click "Analyze"
4. Get comprehensive analysis in ~30 seconds

## Project Documentation
See [PROJECT_PLAN.md](PROJECT_PLAN.md) for complete technical documentation and development decisions.

## Built By
**Karan Rajpal**  
Model Validation Expert @ Handshake AI  
Former 5th Hire @ Borderless Capital | UC Berkeley Haas MBA '25

Built in 16 hours as a portfolio project demonstrating product thinking and technical execution.
