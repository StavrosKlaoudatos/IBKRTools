# IBKRTools

[![PyPI version](https://badge.fury.io/py/ibkrtools.svg)](https://pypi.org/project/ibkrtools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/ibkrtools.svg)](https://pypi.org/project/ibkrtools/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, user-friendly Python wrapper for Interactive Brokers TWS API, making it easier to download and manage market data.

## v1 Features

- **Simple Interface**: Intuitive Pythonic interface for interacting with IBKR TWS API
- **Real-time Data**: Stream and save real-time market data for stocks, forex, and futures
- **Historical Data**: Fetch historical market data with flexible timeframes and bar sizes
- **Thread-Safe**: Built with thread safety in mind for concurrent operations
- **Comprehensive**: Supports multiple asset classes and data types

## Upcoming Features

- **Foreign Equities**: Fetch data for non-US equities
- **Options Data**: Fetch data for options
- **Data Feeding**: Feed incoming data into your own strategy
- **Order Placement**: Place orders (OCA, Multileg, etc.)

## Installation

```bash
pip install ibkrtools
```

## Prerequisites

- Python 3.8+
- Interactive Brokers TWS installed and running
- Enabling Ibapi use on TWS
- Active IBKR account with market data subscriptions



## Documentation

### RealTimeData

```python
RealTimeData(
    stocks: List[str] = [],
    forex: List[str] = [],
    futures: List[str] = []
)
```


#### Return

Fetches and saves in real time, bid, ask, bidsize, and asksize to "RealTimeData/Stocks(Futures, or Forex)"


### HistoricalData

```python
HistoricalData(
    stock_symbols: List[str] = [],
    forex_pairs: List[str] = [],
    future_symbols: List[str] = [],
    what_to_show: str = "TRADES",
    duration: str = "1 D",
    bar_size: str = "1 hour",
    path: str = "Historical_Data",
    save: bool = True,
    verbose: bool = False
) -> pd.DataFrame
```

#### Parameters
- `what_to_show`: Type of market data (see https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#historical-whattoshow)
- `duration`: Amount of historical data to fetch (see https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#requesting-historical-bars)
- `bar_size`: Bar size (see https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#requesting-historical-bars)
- `path`: Directory to save the data
- `save`: Whether to save the data to disk
- `verbose`: Enable verbose output

## Examples

### Real-time Data

```python
from ibkrtools import RealTimeData

# Initialize with your symbols
rt = RealTimeData(
    stocks=["AAPL", "MSFT"],
    forex=["EUR/USD"],
    futures=["ES"]
)

# Start streaming data
rt.run()
```

### Historical Data

```python
from ibkrtools import HistoricalData

# Fetch historical data
df = HistoricalData(
    stock_symbols=["AAPL"],
    forex_pairs=["EUR/USD"],
    future_symbols=["ES"],
    what_to_show="TRADES",
    duration="1 D",
    bar_size="1 hour",
    save=True,
    path="historical_data"
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project, except ibapi is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The ibapi is 100% developed & owned by Interactive Brokers LLC ("IB"). By using this package (ibpy-native), you are assumed that you agreed the TWS API Non-Commercial License.

## Disclaimer

This software is for educational purposes only. Use it at your own risk. The author is not responsible for any financial losses incurred while using this software. Always test with paper trading before using real money.
