# Setup & Running the App

## Requirements

- Python 3.10 or higher
- ~200 MB disk space (excluding background videos)

## First-Time Setup

```bash
# 1. Navigate to the project folder
cd "Food comparison by country"

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 4. Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Make sure the virtual environment is active
source .venv/bin/activate

# Start the app
python app.py
```

The app will open automatically in your browser at **http://127.0.0.1:8050**.

If it doesn't open automatically, navigate there manually.

## Stopping

Press `Ctrl + C` in the terminal.

## Troubleshooting

**Port already in use:**
```bash
# Find and kill the process on port 8050
kill $(lsof -ti:8050)
# Then run app.py again
```

**Missing packages:**
```bash
pip install -r requirements.txt --upgrade
```

**Slow startup:** The app pre-computes ~15 figures on startup. The message `⚡ Pre-computing figures…` followed by `✓ Done` is normal — it takes a few seconds.
