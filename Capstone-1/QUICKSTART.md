# Quick Start Guide

## Setup Steps

1. **Create and activate virtual environment** (if not already done):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Run the application**:
```bash
# Option 1: Use the run script
./run.sh

# Option 2: Run directly with .venv
.venv/bin/streamlit run app.py
```

**IMPORTANT**: Always use `.venv/bin/streamlit` or the `run.sh` script to ensure you're using the virtual environment's packages, not system-wide packages.

## Troubleshooting

### TypeError: __init__() got an unexpected keyword argument 'proxies'

If you encounter this error, reinstall OpenAI with compatible dependencies:

```bash
.venv/bin/pip uninstall -y openai httpx httpcore
.venv/bin/pip install openai==1.54.0
```

### GitHub Integration Warning

If you see "GitHub initialization failed: 401 Bad credentials", this is normal if you haven't configured GitHub support. The app will use mock mode for support tickets. To enable real GitHub integration:

1. Create a GitHub Personal Access Token at https://github.com/settings/tokens
2. Add to your `.env` file:
```
GITHUB_TOKEN=your_token_here
GITHUB_REPO=username/repo-name
```

## First Run

On first run, the app will:
1. Create SQLite database from `data/car_prices.csv` (takes ~10-20 seconds)
2. Load 558,837 car records
3. Create indexes for faster queries
4. Launch web interface at http://localhost:8501

## Sample Queries to Try

- "What's the average price of BMW cars?"
- "Show me the top 5 most expensive models"
- "How many cars were sold in California?"
- "What's the price difference between automatic and manual transmission?"

Enjoy exploring your car data! 🚗
