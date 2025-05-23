Usage
=====

This section provides an overview of how to use IBKRTools to interact with Interactive Brokers TWS API.

Quick Start
-----------

Here's a quick example to get you started with IBKRTools:

.. code-block:: python

    from ibkrtools import RealTimeData, HistoricalData
    import pandas as pd

    # Initialize real-time data for multiple instruments
    rt = RealTimeData(
        stocks=["AAPL", "MSFT"],
        forex=["EUR/USD"],
        futures=["ES"]
    )

    # Start streaming data
    rt.run()

    # Fetch historical data
    hist = HistoricalData()
    df = hist.get_historical_data(
        symbol="AAPL",
        end_date="2023-01-01",
        duration_str="1 Y",
        bar_size_setting="1 day",
        what_to_show="TRADES"
    )
    print(df.head())

Real-time Data
--------------

The :class:`RealTimeData` class provides functionality to stream real-time market data.

.. autoclass:: ibkrtools.IBKR_Realitime_Data.RealTimeData
   :members:
   :inherited-members:

Historical Data
---------------

The :class:`HistoricalData` class allows you to fetch historical market data.

.. autoclass:: ibkrtools.IBKR_Hist.HistoricalData
   :members:
   :inherited-members:

Saving Data
-----------

The :class:`Save_Realtime_Data` class provides functionality to save real-time data to various formats.

.. autoclass:: ibkrtools.IBKR_Realitime_Data.Save_Realtime_Data
   :members:
   :inherited-members:

Examples
--------

Here are some additional examples of how to use IBKRTools:

Fetching Real-time Data
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ibkrtools import RealTimeData

    # Initialize with your symbols
    rt = RealTimeData(
        stocks=["AAPL", "GOOG"],
        forex=["EUR/USD", "GBP/USD"],
        futures=["ES", "NQ"]
    )

    # Start streaming data
    rt.run()

    # Access the latest data
    print(rt.get_latest_data("AAPL"))

Fetching Historical Data
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ibkrtools import HistoricalData
    import pandas as pd

    hist = HistoricalData()
    
    # Fetch 1 year of daily data for AAPL
    df = hist.get_historical_data(
        symbol="AAPL",
        end_date=pd.Timestamp.now().strftime("%Y%m%d %H:%M:%S"),
        duration_str="1 Y",
        bar_size_setting="1 day",
        what_to_show="TRADES"
    )
    
    print(df.head())

Saving Real-time Data
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ibkrtools import Save_Realtime_Data

    # Initialize with symbols and save options
    saver = Save_Realtime_Data(
        symbols=["AAPL", "MSFT"],
        save_dir="./market_data",
        save_format="parquet",
        timeframe="1T"  # 1-minute bars
    )
    
    # Start saving data
    saver.run()

For more detailed examples, check out the `examples <https://github.com/StavrosKlaoudatos/IBKRTools/tree/main/examples>`_ directory in the GitHub repository.
