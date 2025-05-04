# Stock Sentiment

Stock Sentiment is a modern Python package and MCP server that delivers real-time stock news sentiment and market movers using Alpha Vantage. Stay ahead of the market by tracking the latest news, trends, and sentiment for your favorite stocks, and discover the top gainers and losers with ease.

## Features

- **News Sentiment**: Instantly retrieve the latest news headlines and sentiment analysis for any stock ticker.
- **Top Movers**: Access real-time lists of the top gainers and losers in the stock market.
- **Seamless Integration**: Simple command-line interface and MCP server for easy integration into your data workflows.

## Installation

Install Stock Sentiment from PyPI:

```sh
pip install stock-sentiment
```

## Getting Started

1. **Obtain an Alpha Vantage API Key**  
   Sign up at [Alpha Vantage](https://www.alphavantage.co/support/#api-key) to get your free API key.

2. **Configure your API key**  
   Create a `.env` file in your project directory and add:
   ```env
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

3. **Run the MCP server**
   ```sh
   stock-sentiment
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
