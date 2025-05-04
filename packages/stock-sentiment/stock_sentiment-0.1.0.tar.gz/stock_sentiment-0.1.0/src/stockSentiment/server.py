from typing import Any
import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv


# Load .env variables
load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Initialize FastMCP server
mcp = FastMCP("alpha-finance")

# Constants
BASE_URL = "https://www.alphavantage.co/query"

async def call_alpha_vantage(endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Generic async caller to Alpha Vantage."""
    params["apikey"] = API_KEY
    params["function"] = endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_news_sentiment(ticker: str) -> str:
    """Get news sentiment data for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., MSFT, AAPL)
    """
    data = await call_alpha_vantage("NEWS_SENTIMENT", {"tickers": ticker.upper()})
    if not data or "feed" not in data:
        return "Couldn't retrieve news sentiment."

    articles = data["feed"][:3]
    result = []
    for item in articles:
        result.append(f"""
📰 {item['title']}
Summary: {item['summary']}
Source: {item['source']} | Published: {item['time_published']}
""")
    return "\n---\n".join(result)

@mcp.tool()
async def get_top_movers() -> str:
    """Get top gainers and losers from the stock market.

    No arguments required.
    """
    data = await call_alpha_vantage("TOP_GAINERS_LOSERS", {})
    if not data:
        return "Couldn't retrieve top movers."

    gainers = data.get("top_gainers", [])[:3]
    losers = data.get("top_losers", [])[:3]

    result = "**Top Gainers**\n"
    result += "\n".join([
        f"{g['ticker']} ({g.get('change_percentage', 'N/A')})"
        for g in gainers
    ])

    result += "\n\n**Top Losers**\n"
    result += "\n".join([
        f"{l['ticker']} ({l.get('change_percentage', 'N/A')})"
        for l in losers
    ])

    return result

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

