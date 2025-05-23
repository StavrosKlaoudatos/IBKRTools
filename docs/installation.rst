Installation
============

Prerequisites
-------------

- Python 3.8 or higher
- Interactive Brokers TWS or IB Gateway installed and running
- Active IBKR account with market data subscriptions

Installing the Package
----------------------

You can install IBKRTools using pip:

.. code-block:: bash

    pip install ibkrtools

If you want to install the latest development version directly from GitHub:

.. code-block:: bash

    pip install git+https://github.com/StavrosKlaoudatos/IBKRTools.git

Development Installation
-----------------------

If you want to contribute to IBKRTools, you can install it in development mode:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/StavrosKlaoudatos/IBKRTools.git
    cd IBKRTools
    
    # Install in development mode
    pip install -e .
    
    # Install development dependencies
    pip install -r requirements-dev.txt

Verifying the Installation
--------------------------

After installation, you can verify that IBKRTools is properly installed:

.. code-block:: python

    import ibkrtools
    print(ibkrtools.__version__)

If this runs without errors, you're all set!
