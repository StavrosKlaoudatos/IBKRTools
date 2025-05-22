
global SCHEMA
global USE_RTH



USE_RTH       = 0

SCHEMA = {
    'TRADES'                   : ['First_Traded',                 'Highest_Traded',                 'Lowest_Traded',                 'Last_Traded',                 'Total_Traded_Volume'],
    'MIDPOINT'                 : ['First_Midpoint',               'Highest_Midpoint',               'Lowest_Midpoint',               'Last_Midpoint',               None],
    'BID'                      : ['First_Bid',                    'Highest_Bid',                    'Lowest_Bid',                    'Last_Bid',                    None],
    'ASK'                      : ['First_Ask',                    'Highest_Ask',                    'Lowest_Ask',                    'Last_Ask',                    None],
    'BID_ASK'                  : ['Time_Average_Bid',             'Highest_Ask',                    'Lowest_Bid',                    'Time_Average_Ask',            None],
    'ADJUSTED_LAST'            : ['Dividend_Adjusted_First_Traded','Dividend_Adjusted_Highest_Traded','Dividend_Adjusted_Lowest_Traded','Dividend_Adjusted_Last_Traded','Total_Traded_Volume'],
    'HISTORICAL_VOLATILITY'    : ['First_Volatility',             'Highest_Volatility',             'Lowest_Volatility',             'Last_Volatility',             None],
    'OPTION_IMPLIED_VOLATILITY': ['First_Implied_Volatility',     'Highest_Implied_Volatility',     'Lowest_Implied_Volatility',     'Last_Implied_Volatility',     None],
    'FEE_RATE'                 : ['First_Fee_Rate',               'Highest_Fee_Rate',               'Lowest_Fee_Rate',               'Last_Fee_Rate',               None],
    'YIELD_BID'                : ['First_Bid_Yield',              'Highest_Bid_Yield',              'Lowest_Bid_Yield',              'Last_Bid_Yield',              None],
    'YIELD_ASK'                : ['First_Ask_Yield',              'Highest_Ask_Yield',              'Lowest_Ask_Yield',              'Last_Ask_Yield',              None],
    'YIELD_BID_ASK'            : ['Time_Average_Bid_Yield',       'Highest_Ask_Yield',              'Lowest_Bid_Yield',              'Time_Average_Ask_Yield',      None],
    'YIELD_LAST'               : ['First_Last_Yield',             'Highest_Last_Yield',             'Lowest_Last_Yield',             'Last_Last_Yield',             None],
    'AGGTRADES'                : ['First_Agg_Traded',             'Highest_Agg_Traded',             'Lowest_Agg_Traded',             'Last_Agg_Traded',             'Total_Traded_Volume'],
}