# Real Estate Investment Analyzer — implementation notes

This bundle follows the repository's existing directories:
`agents/`, `nodes/`, `human_intervention/`, `services/`, `pytest/`, plus the
root Python modules.

## Important repository corrections

The public repository currently contains several malformed placeholder lines
in files that were described by the assignment as pre-loaded. Examples include
broken environment variable names, malformed Python syntax, malformed SQL,
and mismatched property keys. To make the project runnable, this solution
repairs those integration files as well as implementing the marked modules.

The assignment's data contract uses:
- `listing_price`, not `listing price`
- `square_footage`, not `square footage`
- `year_built`
- `interest_rate`
- `historical_prices`
- decision keys `STRONG_BUY`, `BUY`, `CONSIDER`, `PASS`

The `.env` file should contain:

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite

Run:

pip install -r requirements.txt
python3 -m streamlit run main.py

The provided live test needs a real Gemini API key.
