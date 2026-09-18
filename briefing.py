"""
Polymarket Briefing Agent

Pulls the top active prediction markets from Polymarket, then asks an LLM
(Gemini) to write a short plain-English brief for each one.

Key idea: the LLM fetches nothing. Python gets the data; the model only
writes about what's handed to it in the prompt.

Run:
    export GEMINI_API_KEY="your-key-here"
    python3 briefing.py
"""

import json
import os
import time

import requests
from google import genai

POLYMARKET_URL = "https://gamma-api.polymarket.com/markets"
MODEL = "gemini-3.6-flash"
NUM_MARKETS = 5



def fetch_markets(limit=NUM_MARKETS):
    """Return a list of the biggest open markets by volume."""
    params = {
        "limit": limit,
        "closed": "false",       # open markets only
        "order": "volumeNum",    # sort by trading volume
        "ascending": "false",    # biggest first
    }
    response = requests.get(POLYMARKET_URL, params=params, timeout=15)
    response.raise_for_status()  # crash loudly if the API returns an error
    return response.json()



def summarize_market(market):
    """Turn a raw market dict into a small dict with question, price, change."""
    question = market["question"]
    prices_string = market["outcomePrices"]      # e.g. '["0.003","0.997"]'
    prices_list = json.loads(prices_string)      # -> ["0.003", "0.997"]
    price = float(prices_list[0])                # YES price
    change = market.get("oneDayPriceChange") or 0.0  # missing/None -> 0
    return {"question": question, "price": price, "change": float(change)}



def build_prompt(summary):
    """Build the prompt string. Everything the model may mention is in here."""
    price = round(summary["price"], 3)
    price_pct = price * 100
    change_pts = summary["change"] * 100
    return f"""You are writing a short briefing on a prediction market for a busy reader.

Market question: {summary['question']}
Current YES price: {summary['price']:.3f} (about {price_pct:.1f}% implied probability)
Price change over the last 24 hours: {change_pts:+.1f} percentage points

Write exactly 3 sentences in plain English:
1. What this market is about.
2. Which way the price moved in the last day and by how much (if the change is 0, say it was flat).
3. What the current price implies as a probability of YES.

Use only the information above. Do not invent news, reasons for the move, or other numbers."""


def generate_brief(client, prompt, retries=3):
    """Send the prompt to Gemini and return the text reply, retrying if busy."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text.strip()
        except Exception as e:
            if "503" in str(e) and attempt < retries - 1:
                wait = 2 ** attempt * 3  # 3s, then 6s
                print(f"   (model busy, retrying in {wait}s...)")
                time.sleep(wait)
            else:
                raise


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    markets = fetch_markets()

    print("=" * 60)
    print(f"POLYMARKET DIGEST — top {len(markets)} markets by volume")
    print("=" * 60)

    for i, market in enumerate(markets, start=1):
        try:
            summary = summarize_market(market)
        except (KeyError, ValueError, IndexError) as e:
            print(f"\n{i}. Skipped a market with unexpected data ({e})")
            continue

        print(f"\n{i}. {summary['question']}")
        print(f"   YES: {summary['price']:.3f} | 24h change: {summary['change'] * 100:+.1f} pts")

        try:
            brief = generate_brief(client, build_prompt(summary))
            print(f"   {brief}")
        except Exception as e:
            print(f"   (LLM call failed: {e})")

        time.sleep(1)  
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()