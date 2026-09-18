# Polymarket Briefing Agent

A Python script that grabs the 5 biggest open markets on Polymarket and has Gemini write a short summary of each one.

Raw market data is hard to read. A market title next to a price like 0.003 doesn't tell you much at a glance. This script turns it into a few sentences per market so you can read the whole thing in about 30 seconds.

## How it works

1. Python calls the Polymarket API and gets the top 5 open markets by volume.
2. For each market it pulls out the question, the YES price, and the price change over the last 24 hours.
3. It puts those numbers into a prompt and asks Gemini for a 3 sentence summary.
4. It prints all 5 summaries.

The model doesn't look anything up. Python gets the data and the model only writes about what's in the prompt. If a number isn't in the prompt, the model can't use it.

## Setup

You need Python 3. On a Mac use `pip3` and `python3`.

```bash
pip3 install requests google-genai
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com). Then run:

```bash
export GEMINI_API_KEY="your-key-here"
python3 briefing.py
```

The export only works in the terminal window you typed it in. To keep it permanently, add that line to `~/.zshrc`. The key is never written in the code.

## Example output

```
============================================================
POLYMARKET DIGEST: top 5 markets by volume
============================================================

1. Will Adanech Abiebie be the next Prime Minister of Ethiopia?
   YES: 0.003 | 24h change: +0.1 pts
   This market is on whether Adanech Abiebie will be the next Prime Minister of Ethiopia. Over the last day, the price increased by 0.1 percentage points. The current price implies about a 0.3% probability of a YES outcome.

2. Will the U.S. invade Iran before 2027?
   YES: 0.165 | 24h change: +0.0 pts
   This prediction market focuses on whether the U.S. will invade Iran before 2027. Over the last 24 hours, the price was flat, changing by 0.0 percentage points. The current price implies about a 16.5% probability of a YES outcome.

3. Will Jesus Christ return before 2027?
   YES: 0.019 | 24h change: +0.1 pts
   This prediction market is about whether Jesus Christ will return before 2027. Over the last 24 hours, the price increased by 0.1 percentage points. The current price implies an approximate 1.9% probability of a YES outcome.

4. Will Gedion Timothewos be the next Prime Minister of Ethiopia?
   YES: 0.007 | 24h change: +0.1 pts
   This market is about whether Gedion Timothewos will be the next Prime Minister of Ethiopia. Over the last 24 hours, the price moved up by 0.1 percentage points. The current price implies about a 0.7% probability of a YES outcome.

5. Will LeBron James win the 2028 US Presidential Election?
   YES: 0.001 | 24h change: +0.0 pts
   This prediction market asks whether LeBron James will win the 2028 US Presidential Election. Over the last 24 hours, the price was flat with a change of +0.0 percentage points. The current YES price of 0.001 implies about a 0.1% probability of this outcome.

============================================================
```

## What I learned

- The API sends prices as a string that looks like a list, like `'["0.003","0.997"]'`. I had to use `json.loads()` to turn it into a real list and `float()` to get a number.
- Printing one full market first showed me every field I could use. That's how I found `oneDayPriceChange`, so I didn't need a second API call.
- The prompt controls accuracy. Telling the model to only use the numbers I gave it stopped it from making up reasons for price moves.
- One summary said 0.8% when the price was 0.007. The model wasn't the problem. My prompt rounded the price and the percentage separately, so it got two numbers that didn't match. Rounding once fixed it.
- APIs break. The model I started with got retired and Google's servers were sometimes busy, so I added retries and made sure one failed market doesn't stop the rest.
- API keys go in environment variables, not in the code, so the repo is safe to put on GitHub.