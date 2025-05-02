# WizTrader SDK Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Authentication](#authentication)
4. [Quotes Client](#quotes-client)
    - [Initialization](#quotes-client-initialization)
    - [Connection Methods](#connection-methods)
    - [Callbacks](#callbacks)
    - [Subscribing to Instruments](#subscribing-to-instruments)
    - [Unsubscribing from Instruments](#unsubscribing-from-instruments)
    - [Handling WebSocket Connection](#handling-websocket-connection)
    - [Complete Examples](#quotes-client-examples)
5. [Wizzer Client](#wizzer-client)
    - [Initialization](#wizzer-client-initialization)
    - [Constants](#constants)
    - [Data Hub Methods](#data-hub-methods)
    - [Order Management](#order-management)
    - [Portfolio Management](#portfolio-management)
    - [Basket Management](#basket-management)
    - [Complete Examples](#wizzer-client-examples)
6. [Common Use Cases](#common-use-cases)
7. [Error Handling](#error-handling)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

## Introduction

WizTrader is a Python SDK for connecting to the Wizzer trading platform. It provides two main client classes:

- **QuotesClient**: For real-time market data streaming via WebSockets
- **WizzerClient**: For REST API access to trading, order management, and market data

This documentation covers all the ways to use the SDK, with examples for each endpoint and common use cases.

## Installation

You can install the package directly from PyPI:

```bash
pip install wiz_trader
```

To install the development version from GitHub:

```bash
pip install git+https://github.com/wizzer-tech/wiz_trader.git
```

## Authentication

There are two ways to provide authentication credentials to the SDK:

1. **Direct parameter passing** (Recommended for most use cases)
2. **Environment variables** (Recommended for production deployments)

### Direct Parameter Passing

Simply provide the required parameters directly when initializing the clients:

```python
from wiz_trader import QuotesClient, WizzerClient

quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    strategy_id="str_01hxgwgfxgfrxb48bzchnve7gm",  # Optional
    log_level="info"
)
```

### Environment Variables

Set the following environment variables:

```bash
export WZ__QUOTES_BASE_URL="wss://websocket-url/quotes"
export WZ__API_BASE_URL="https://api-url.in"
export WZ__TOKEN="your-jwt-token"
export WZ__STRATEGY_ID="str_01hxgwgfxgfrxb48bzchnve7gm"  # Optional
```

Then initialize the clients without parameters:

```python
from wiz_trader import QuotesClient, WizzerClient

quotes_client = QuotesClient(log_level="info")
wizzer_client = WizzerClient(log_level="info")
```

You can also use a hybrid approach, providing some parameters directly and letting others fall back to environment variables:

```python
quotes_client = QuotesClient(log_level="debug")  # Only override log level
```

## Quotes Client

The `QuotesClient` enables you to connect to Wizzer's WebSocket server for real‑time market data using **plain synchronous** callbacks—no `async def` required.

### Quotes Client Initialization

You can initialize the `QuotesClient` in several ways:

```python
from wiz_trader import QuotesClient

# Method 1: All parameters provided directly
client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info",         # Options: "error", "info", "debug"
    max_message_size=10 * 1024 * 1024,  # Optional: default 10MB
    batch_size=20             # Optional: default 20 instruments per batch
)

# Method 2: Using environment variables
# (Requires WZ__QUOTES_BASE_URL and WZ__TOKEN set)
client = QuotesClient(log_level="info")

# Method 3: Mixed approach
client = QuotesClient(
    base_url="wss://custom-url/quotes",
    log_level="debug"         # token from WZ__TOKEN env var
)
```

### Connection Methods

#### Blocking Connection

Blocks your main thread, similar to Zerodha’s KiteTicker:

```python
client.connect()
```

#### Non‑Blocking Connection

Run alongside your own `asyncio` code:

```python
client.connect_async()
# … do other work …
client.stop()
```

### Callbacks

All callbacks are **plain `def`** functions.  Inside them you can call `subscribe(...)`, which under the hood schedules the actual async work—so you never `await` in your callbacks.

```python
def on_tick(ws, tick):
    print("Tick:", tick)

def on_connect(ws):
    print("Connected!")
    # fire‑and‑forget subscribe—no await needed
    ws.subscribe([
        "NSE:SBIN:3045",
        "NSE:RELIANCE:2885"
    ])

def on_close(ws, code, reason):
    print(f"Connection closed [{code}]: {reason}")
    ws.stop()   # to prevent auto‑reconnect

def on_error(ws, error):
    print("Error:", error)

client.on_tick    = on_tick
client.on_connect = on_connect
client.on_close   = on_close
client.on_error   = on_error
```

### Subscribing to Instruments

Call `ws.subscribe([...])` directly; the SDK will batch large lists and send them over the socket:

```python
def on_connect(ws):
    # subscribe without await
    ws.subscribe([
        "NSE:SBIN:3045",
        "NSE:ICICIBANK:4963",
        "NSE:RELIANCE:2885",
    ])
```

### Unsubscribing from Instruments

Similarly, plain call to `unsubscribe`:

```python
ws.unsubscribe(["NSE:SBIN:3045", "NSE:ICICIBANK:4963"])
```

### Complete Examples

#### Blocking Example

```python
import logging
from wiz_trader import QuotesClient

logging.basicConfig(level=logging.INFO)

client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token"
)

def on_tick(ws, tick):
    logging.debug("Tick: %s", tick)

def on_connect(ws):
    logging.info("Connected.")
    ws.subscribe(["NSE:SBIN:3045", "NSE:RELIANCE:2885"])  # no await

def on_close(ws, code, reason):
    logging.warning("Closed: %s", reason)
    ws.stop()

def on_error(ws, error):
    logging.error("Error: %s", error)

client.on_tick    = on_tick
client.on_connect = on_connect
client.on_close   = on_close
client.on_error   = on_error

try:
    client.connect()
except KeyboardInterrupt:
    client.stop()
```

#### Non‑Blocking Example

```python
import asyncio
import logging
from wiz_trader import QuotesClient

async def main():
    logging.basicConfig(level=logging.INFO)
    client = QuotesClient(
        base_url="wss://websocket-url/quotes",
        token="your-jwt-token"
    )
    client.on_tick    = lambda ws, tick: logging.info(tick)
    client.on_connect = lambda ws: ws.subscribe(["NSE:SBIN:3045"])
    client.connect_async()

    # Your other async work here...
    await asyncio.sleep(60)
    client.stop()

asyncio.run(main())
```

#### Ticks structure
ts = tick timestamp
lastTradedTs = timestamp of the last executed trade in this instrument

```
{'identifier': 'NSE:RELIANCE:2885', 'tradingSymbol': 'RELIANCE', 'exchange': 'NSE', 'segment': 'NSECM', 'exchangeToken': 2885, 'bids': [{'volume': 1722, 'price': 1295.5, 'orders': 43}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}], 'offers': [{'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}, {'volume': 0, 'price': 0, 'orders': 0}], 'ltp': 1295.5, 'lastTradedQty': 10, 'buyQty': 1722, 'sellQty': 0, 'volume': 10429964, 'avgPrice': 1291.46, 'netChange': 0, 'ohlc': {'open': 1270, 'high': 1300.9, 'low': 1267, 'close': 1295.5}, 'lastTradedTs': '2025-04-21T10:29:33Z', 'ts': '2025-04-21T10:29:46Z'}
```

## Wizzer Client

The `WizzerClient` provides access to Wizzer's REST APIs for trading, portfolio management, and market data.

### Wizzer Client Initialization

Initialize the client with your authentication details:

```python
from wiz_trader import WizzerClient

# Method 1: All parameters provided directly
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    strategy_id="str_01hxgwgfxgfrxb48bzchnve7gm",  # Optional: Default strategy ID
    log_level="info"  # Options: "error", "info", "debug"
)

# Method 2: Using environment variables
# (Requires WZ__API_BASE_URL and WZ__TOKEN to be set)
client = WizzerClient(log_level="info")
```

### Constants

The `WizzerClient` provides constants for various parameter values, making your code more readable and type-safe:

```python
from wiz_trader import WizzerClient

client = WizzerClient(...)

# Use constants for transaction types
client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_MARKET,
    product=client.PRODUCT_CNC
)
```

Available constants:

- Transaction types: `TRANSACTION_TYPE_BUY`, `TRANSACTION_TYPE_SELL`
- Product types: `PRODUCT_CNC`, `PRODUCT_MIS`, `PRODUCT_NRML`
- Order types: `ORDER_TYPE_MARKET`, `ORDER_TYPE_LIMIT`, `ORDER_TYPE_SL`, `ORDER_TYPE_SLM`
- Validity types: `VALIDITY_DAY`, `VALIDITY_IOC`, `VALIDITY_GTT`
- Variety types: `VARIETY_REGULAR`, `VARIETY_AMO`, `VARIETY_BO`, `VARIETY_CO`
- Exchanges: `EXCHANGE_NSE`, `EXCHANGE_BSE`, `EXCHANGE_WZR`
- Segments: `SEGMENT_NSE_CM`, `SEGMENT_BSE_CM`, `SEGMENT_NSE_FO`, `SEGMENT_WZREQ`
- Instrument types: `INSTRUMENT_TYPE_EQ`, `INSTRUMENT_TYPE_EQLC`, `INSTRUMENT_TYPE_EQMCC`, `INSTRUMENT_TYPE_EQSCC`, `INSTRUMENT_TYPE_BASKET`

### Data Hub Methods

#### Get Indices

Fetch available indices from an exchange:

```python
# Get all indices from NSE
indices = client.get_indices(exchange="NSE")
print(f"Found {len(indices)} indices")

# Get a specific index by trading symbol
nifty_50 = client.get_indices(trading_symbol="NIFTY 50", exchange="NSE")
```

#### Get Index Components

Fetch components (stocks) in a specific index:

```python
# Get components of NIFTY 50
components = client.get_index_components(trading_symbol="NIFTY 50", exchange="NSE")
print(f"Found {len(components)} components in NIFTY 50")
for component in components[:5]:
    print(f"{component['tradingSymbol']} - {component.get('weightage', 'N/A')}%")
```

#### Get Historical OHLCV Data

Fetch historical price data for instruments:

```python
# Get daily data
daily_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN:3045"],
    start_date="2024-01-01",
    end_date="2024-01-31",
    ohlcv=["open", "high", "low", "close", "volume"],
    interval="1d"  # Daily data (default)
)

# Get monthly data
monthly_data = client.get_historical_ohlcv(
    instruments=["NSE:SBIN:3045", "NSE:ICICIBANK:4963"],
    start_date="2023-01-01",
    end_date="2024-01-01",
    ohlcv=["close", "volume"],
    interval="1M"  # Monthly data
)
```

### Order Management

#### Place Regular Order

Place a regular order for a single instrument:

```python
# Simple market order
order_response = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_MARKET,
    product=client.PRODUCT_CNC
)
print(f"Order placed successfully: {order_response.get('orderId')}")

# Limit order with price
limit_order = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    order_type=client.ORDER_TYPE_LIMIT,
    product=client.PRODUCT_CNC,
    price=650.00
)

# Order with stop loss and target
sl_order = client.place_order(
    exchange=client.EXCHANGE_NSE,
    trading_symbol="SBIN",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=10,
    product=client.PRODUCT_CNC,
    stoploss=640.00,
    target=670.00
)
```

#### Modify Order

Modify an existing order:

```python
# Modify an order's price
modified_order = client.modify_order(
    order_id="order_01jpeyxtr4fb69fx740my3115c",
    price=655.00
)

# Modify an order's quantity
modified_order = client.modify_order(
    order_id="order_01jpeyxtr4fb69fx740my3115c",
    qty=15
)
```

#### Cancel Order

Cancel an existing order:

```python
# Cancel an order
cancelled_order = client.cancel_order(order_id="order_01jpeyxtr4fb69fx740my3115c")
```

#### Get Order Details

Fetch details of a specific order:

```python
# Get order details
order_details = client.get_order(order_id="order_01jpeyxtr4fb69fx740my3115c")
print(f"Order status: {order_details.get('status')}")
```

### Portfolio Management

#### Get Positions

Fetch your current positions:

```python
# Get all positions
all_positions = client.get_positions()
print(f"Found {len(all_positions)} positions")

# Get only open positions
open_positions = client.get_open_positions()
print(f"Found {len(open_positions)} open positions")

# Get only closed positions
closed_positions = client.get_closed_positions()
print(f"Found {len(closed_positions)} closed positions")
```

#### Get Holdings

Fetch your holdings:

```python
# Get holdings
holdings = client.get_holdings()
print(f"Found {len(holdings)} holdings")

# Get holdings for a specific portfolio
portfolio_holdings = client.get_holdings(portfolios="my_portfolio")
```

#### Exit Positions

Exit all positions or positions for a specific strategy:

```python
# Exit all positions
exit_response = client.exit_all_positions()
print(f"Successfully exited {exit_response.get('success', 0)} positions")

# Exit positions for a specific strategy
strategy_exit = client.exit_strategy_positions(strategy_id="str_01jbxszcjdegz8zt3h95g8c1d9")
```

### Basket Management

#### Create Basket

Create a new basket of instruments:

```python
# Create a basic basket with two stocks
basket_response = client.create_basket(
    name="My Basket",
    instruments=[
        {
            "shares": 10,
            "weightage": 50,
            "instrument": {
                "exchange": "NSE",
                "identifier": "NSE:SBIN:3045",
                "orderIndex": 1,
                "exchangeToken": 3045,
                "tradingSymbol": "SBIN"
            }
        },
        {
            "shares": 15,
            "weightage": 50,
            "instrument": {
                "exchange": "NSE",
                "identifier": "NSE:ICICIBANK:4963",
                "orderIndex": 2,
                "exchangeToken": 4963,
                "tradingSymbol": "ICICIBANK"
            }
        }
    ],
    weightage_scheme="equi_weighted",
    capital={"minValue": 50000, "actualValue": 50000},
    instrument_types=["EQLC"]
)
basket_id = basket_response.get('id')
```

#### Get Baskets

Fetch existing baskets:

```python
# Get all baskets
baskets = client.get_baskets()
print(f"Found {len(baskets)} baskets")

# Get a specific basket by ID
basket = client.get_basket(basket_id="bk_01jpf2d57ae96bez63me7p6g9k")

# Get instruments in a basket
basket_instruments = client.get_basket_instruments(basket_id="bk_01jpf2d57ae96bez63me7p6g9k")
```

#### Place Basket Order

Place an order for an entire basket:

```python
# Place a basket order
basket_order = client.place_basket_order(
    trading_symbol="/MY_BASKET",
    transaction_type=client.TRANSACTION_TYPE_BUY,
    quantity=1,
    price=50000.00,
    product=client.PRODUCT_CNC
)
```

#### Exit Basket Order

Exit a basket position:

```python
# Exit a basket position
exit_order = client.place_basket_exit_order(
    trading_symbol="/MY_BASKET",
    exchange=client.EXCHANGE_WZR,
    transaction_type=client.TRANSACTION_TYPE_SELL,
    quantity=1,
    exchange_token=1741872632
)
```

#### Rebalance Basket

Rebalance a basket with new instruments:

```python
# Rebalance a basket
rebalance_response = client.rebalance_basket(
    trading_symbol="/MY_BASKET",
    instruments=["NSE:SBIN:3045", "NSE:HDFCBANK:1333", "NSE:TCS:2953"]
)
```

### Wizzer Client Examples

#### Market Data and Analysis Example

```python
from wiz_trader import WizzerClient
import pandas as pd
import matplotlib.pyplot as plt

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def analyze_index_performance(index_symbol, exchange, start_date, end_date):
    # Get index components
    components = client.get_index_components(
        trading_symbol=index_symbol,
        exchange=exchange
    )
    print(f"Found {len(components)} components in {index_symbol}")
    
    # Get the identifiers for the top 5 weighted components
    top_components = sorted(components, key=lambda x: x.get('weightage', 0), reverse=True)[:5]
    instrument_ids = [comp['identifier'] for comp in top_components]
    
    # Fetch historical data
    historical_data = client.get_historical_ohlcv(
        instruments=instrument_ids,
        start_date=start_date,
        end_date=end_date,
        ohlcv=["close"],
        interval="1d"
    )
    
    # Process and plot the data
    for instrument_data in historical_data:
        symbol = instrument_data['instrument'].split(':')[1]
        df = pd.DataFrame(instrument_data['data'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Calculate percentage change from first day
        first_close = df['close'].iloc[0]
        df['pct_change'] = ((df['close'] - first_close) / first_close) * 100
        
        plt.plot(df.index, df['pct_change'], label=symbol)
    
    plt.title(f"Performance of Top {index_symbol} Components")
    plt.xlabel("Date")
    plt.ylabel("% Change")
    plt.legend()
    plt.grid(True)
    plt.show()

# Analyze NIFTY 50 performance for Jan 2024
analyze_index_performance(
    index_symbol="NIFTY 50",
    exchange="NSE",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

#### Algorithmic Trading Example

```python
from wiz_trader import QuotesClient, WizzerClient
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMovingAverageCrossover:
    def __init__(self, symbol, exchange, token, fast_period=5, slow_period=20):
        # Trading parameters
        self.symbol = symbol
        self.exchange = exchange
        self.token = token
        self.instrument_id = f"{exchange}:{symbol}:{token}"
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        # State variables
        self.prices = []
        self.position = None
        self.order_id = None
        
        # Clients
        self.quotes_client = QuotesClient(
            base_url="wss://websocket-url/quotes",
            token="your-jwt-token"
        )
        self.wizzer_client = WizzerClient(
            base_url="https://api-url.in",
            token="your-jwt-token"
        )
        
        # Set up quotes client callbacks
        self.quotes_client.on_tick = self.on_tick
        self.quotes_client.on_connect = self.on_connect
        self.quotes_client.on_error = lambda ws, error: logger.error(f"Error: {error}")
    
    def on_connect(self, ws):
        logger.info(f"Connected to quotes server")
        ws.subscribe([self.instrument_id])
    
    def on_tick(self, ws, tick):
        if "ltp" in tick:
            price = tick["ltp"]
            self.prices.append(price)
            
            # Keep only the required number of prices
            if len(self.prices) > self.slow_period:
                self.prices.pop(0)
            
            # Once we have enough data, check for signals
            if len(self.prices) >= self.slow_period:
                self.check_for_signals()
    
    def check_for_signals(self):
        # Calculate moving averages
        fast_ma = sum(self.prices[-self.fast_period:]) / self.fast_period
        slow_ma = sum(self.prices) / self.slow_period
        
        current_price = self.prices[-1]
        
        logger.info(f"Price: {current_price}, Fast MA: {fast_ma:.2f}, Slow MA: {slow_ma:.2f}")
        
        # Generate signals
        if fast_ma > slow_ma and self.position != "long":
            # Buy signal
            logger.info("BUY SIGNAL")
            self.enter_position("long", current_price)
        
        elif fast_ma < slow_ma and self.position == "long":
            # Sell signal
            logger.info("SELL SIGNAL")
            self.exit_position(current_price)
    
    def enter_position(self, position_type, price):
        if position_type == "long":
            # Place a buy order
            try:
                order_response = self.wizzer_client.place_order(
                    exchange=self.exchange,
                    trading_symbol=self.symbol,
                    transaction_type=self.wizzer_client.TRANSACTION_TYPE_BUY,
                    quantity=10,  # Fixed quantity for simplicity
                    order_type=self.wizzer_client.ORDER_TYPE_MARKET,
                    product=self.wizzer_client.PRODUCT_CNC
                )
                self.order_id = order_response.get("orderId")
                self.position = "long"
                logger.info(f"Entered LONG position at {price}, Order ID: {self.order_id}")
            except Exception as e:
                logger.error(f"Error entering position: {e}")
    
    def exit_position(self, price):
        if self.position == "long":
            # Place a sell order
            try:
                order_response = self.wizzer_client.place_order(
                    exchange=self.exchange,
                    trading_symbol=self.symbol,
                    transaction_type=self.wizzer_client.TRANSACTION_TYPE_SELL,
                    quantity=10,  # Fixed quantity for simplicity
                    order_type=self.wizzer_client.ORDER_TYPE_MARKET,
                    product=self.wizzer_client.PRODUCT_CNC
                )
                logger.info(f"Exited LONG position at {price}, Order ID: {order_response.get('orderId')}")
                self.position = None
                self.order_id = None
            except Exception as e:
                logger.error(f"Error exiting position: {e}")
    
    def run(self):
        try:
            logger.info("Starting the strategy...")
            self.quotes_client.connect()
        except KeyboardInterrupt:
            logger.info("Strategy interrupted by user")
            if self.position:
                logger.info("Closing position before exit")
                self.exit_position(self.prices[-1] if self.prices else 0)
            self.quotes_client.stop()

# Run the strategy
strategy = SimpleMovingAverageCrossover(
    symbol="SBIN",
    exchange="NSE",
    token=3045,
    fast_period=5,
    slow_period=20
)
strategy.run()
```

#### Basket Management Example

```python
from wiz_trader import WizzerClient
import json

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def create_and_trade_basket():
    # Create a sector-based basket
    banking_basket = client.create_basket(
        name="Banking Basket",
        instruments=[
            {
                "shares": 20,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:SBIN:3045",
                    "orderIndex": 1,
                    "exchangeToken": 3045,
                    "tradingSymbol": "SBIN"
                }
            },
            {
                "shares": 15,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:ICICIBANK:4963",
                    "orderIndex": 2,
                    "exchangeToken": 4963,
                    "tradingSymbol": "ICICIBANK"
                }
            },
            {
                "shares": 15,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:HDFCBANK:1333",
                    "orderIndex": 3,
                    "exchangeToken": 1333,
                    "tradingSymbol": "HDFCBANK"
                }
            },
            {
                "shares": 30,
                "weightage": 25,
                "instrument": {
                    "exchange": "NSE",
                    "identifier": "NSE:BANKBARODA:2263",
                    "orderIndex": 4,
                    "exchangeToken": 2263,
                    "tradingSymbol": "BANKBARODA"
                }
            }
        ],
        weightage_scheme="equi_weighted",
        capital={"minValue": 100000, "actualValue": 100000},
        instrument_types=["EQLC"]
    )
    
    basket_id = banking_basket.get('id')
    basket_symbol = banking_basket.get('tradingSymbol')
    exchange_token = banking_basket.get('basketInstrument', {}).get('exchangeToken')
    
    print(f"Created basket: {basket_symbol} (ID: {basket_id})")
    
    # Place a buy order for the basket
    try:
        order_response = client.place_basket_order(
            trading_symbol=basket_symbol,
            transaction_type=client.TRANSACTION_TYPE_BUY,
            quantity=1,  # Buy one unit of the basket
            price=100000.00,
            product=client.PRODUCT_CNC
        )
        print(f"Placed basket buy order: {order_response.get('orderId')}")
        
        # After some time, exit the basket
        # (This would normally be based on some strategy or time delay)
        exit_response = client.place_basket_exit_order(
            trading_symbol=basket_symbol,
            exchange=client.EXCHANGE_WZR,
            transaction_type=client.TRANSACTION_TYPE_SELL,
            quantity=1,
            exchange_token=exchange_token
        )
        print(f"Placed basket exit order: {exit_response.get('orderId')}")
        
    except Exception as e:
        print(f"Error during basket trading: {e}")

# Rebalance the basket (e.g., to adjust weightages or change stocks)
    try:
        rebalance_response = client.rebalance_basket(
            trading_symbol=basket_symbol,
            instruments=[
                "NSE:SBIN:3045",
                "NSE:HDFCBANK:1333",
                "NSE:ICICIBANK:4963",
                "NSE:AXISBANK:5900"  # Replacing BANKBARODA with AXISBANK
            ]
        )
        print(f"Rebalanced basket successfully")
    except Exception as e:
        print(f"Error during basket rebalancing: {e}")

# Run the basket trading example
create_and_trade_basket()
```

## Common Use Cases

### Backtesting with Historical Data

```python
from wiz_trader import WizzerClient
import pandas as pd
import numpy as np
from datetime import datetime

# Initialize client
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token"
)

def backtest_simple_strategy(symbol, exchange, token, start_date, end_date, 
                             fast_period=10, slow_period=30):
    # Get historical data
    instrument_id = f"{exchange}:{symbol}:{token}"
    data = client.get_historical_ohlcv(
        instruments=[instrument_id],
        start_date=start_date,
        end_date=end_date,
        ohlcv=["open", "high", "low", "close", "volume"],
        interval="1d"
    )
    
    if not data or not data[0].get('data'):
        print("No data available for the specified period")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data[0]['data'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Calculate moving averages
    df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_period).mean()
    
    # Generate signals
    df['signal'] = 0
    df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1  # Buy signal
    df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1  # Sell signal
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    # Calculate cumulative returns
    df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
    df['strategy_cumulative_returns'] = (1 + df['strategy_returns']).cumprod() - 1
    
    # Calculate statistics
    total_days = len(df)
    winning_days = len(df[df['strategy_returns'] > 0])
    win_rate = winning_days / total_days if total_days > 0 else 0
    
    strategy_return = df['strategy_cumulative_returns'].iloc[-1]
    buy_hold_return = df['cumulative_returns'].iloc[-1]
    
    print(f"Backtest Results for {symbol} ({start_date} to {end_date}):")
    print(f"Strategy Return: {strategy_return:.2%}")
    print(f"Buy & Hold Return: {buy_hold_return:.2%}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Total Trades: {df['signal'].diff().abs().sum() / 2:.0f}")
    
    return df

# Run a backtest
result_df = backtest_simple_strategy(
    symbol="SBIN",
    exchange="NSE",
    token=3045,
    start_date="2023-01-01",
    end_date="2023-12-31",
    fast_period=10,
    slow_period=30
)

# Plot the results 
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))

# Plot prices and moving averages
plt.subplot(2, 1, 1)
plt.plot(result_df.index, result_df['close'], label='Close Price')
plt.plot(result_df.index, result_df['fast_ma'], label=f'Fast MA ({10} days)')
plt.plot(result_df.index, result_df['slow_ma'], label=f'Slow MA ({30} days)')
plt.title('Price and Moving Averages')
plt.legend()
plt.grid(True)

# Plot cumulative returns
plt.subplot(2, 1, 2)
plt.plot(result_df.index, result_df['cumulative_returns'], label='Buy & Hold')
plt.plot(result_df.index, result_df['strategy_cumulative_returns'], label='Strategy')
plt.title('Cumulative Returns')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
```

### Real-time Portfolio Monitoring

```python
from wiz_trader import QuotesClient, WizzerClient
import pandas as pd
import time
from datetime import datetime

# Initialize clients
quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="info"
)

class PortfolioMonitor:
    def __init__(self):
        self.portfolio = {}
        self.last_update_time = None
        self.update_interval = 60  # seconds
        
    def on_tick(self, ws, tick):
        """Process incoming market data"""
        if 'instrument' in tick and 'ltp' in tick:
            instrument = tick['instrument']
            ltp = tick['ltp']
            
            if instrument in self.portfolio:
                # Update the current price
                self.portfolio[instrument]['current_price'] = ltp
                
                # Calculate P&L
                avg_price = self.portfolio[instrument]['avg_price']
                qty = self.portfolio[instrument]['qty']
                
                if qty > 0:  # Long position
                    pnl = (ltp - avg_price) * qty
                    pnl_percent = ((ltp / avg_price) - 1) * 100
                else:  # Short position
                    pnl = (avg_price - ltp) * abs(qty)
                    pnl_percent = ((avg_price / ltp) - 1) * 100
                
                self.portfolio[instrument]['pnl'] = pnl
                self.portfolio[instrument]['pnl_percent'] = pnl_percent
                
                # Display portfolio if update interval has passed
                current_time = time.time()
                if (self.last_update_time is None or 
                    current_time - self.last_update_time > self.update_interval):
                    self.display_portfolio()
                    self.last_update_time = current_time
    
    def on_connect(self, ws):
        """Handle connection to quotes server"""
        print(f"Connected to quotes server at {datetime.now()}")
        # Fetch holdings and subscribe to them
        self.fetch_holdings()
    
    def fetch_holdings(self):
        """Fetch holdings from the API and update portfolio"""
        try:
            holdings = wizzer_client.get_holdings()
            
            # Extract holding information and update portfolio
            instruments_to_subscribe = []
            for holding in holdings:
                if holding.get('qty', 0) > 0:
                    instrument = holding.get('identifier', '')
                    if instrument:
                        self.portfolio[instrument] = {
                            'symbol': holding.get('tradingSymbol', ''),
                            'exchange': holding.get('exchange', ''),
                            'qty': holding.get('qty', 0),
                            'avg_price': holding.get('avgPrice', 0),
                            'invested_value': holding.get('investedValue', 0),
                            'current_price': 0,
                            'pnl': 0,
                            'pnl_percent': 0
                        }
                        instruments_to_subscribe.append(instrument)
            
            # Subscribe to these instruments for real-time updates
            if instruments_to_subscribe:
                quotes_client.subscribe(instruments_to_subscribe)
                print(f"Subscribed to {len(instruments_to_subscribe)} instruments")
            else:
                print("No holdings found to monitor")
        
        except Exception as e:
            print(f"Error fetching holdings: {e}")
    
    def display_portfolio(self):
        """Display the current portfolio status"""
        if not self.portfolio:
            print("Portfolio is empty")
            return
        
        print("\n" + "="*80)
        print(f"Portfolio Status as of {datetime.now()}")
        print("="*80)
        
        # Create a pandas DataFrame for nicer display
        df = pd.DataFrame.from_dict(self.portfolio, orient='index')
        df['pnl'] = df['pnl'].round(2)
        df['pnl_percent'] = df['pnl_percent'].round(2)
        
        # Sort by P&L
        df = df.sort_values('pnl', ascending=False)
        
        print(df[['symbol', 'qty', 'avg_price', 'current_price', 'pnl', 'pnl_percent']])
        
        # Calculate total values
        total_invested = df['invested_value'].sum()
        total_current = (df['current_price'] * df['qty']).sum()
        total_pnl = df['pnl'].sum()
        total_pnl_percent = ((total_current / total_invested) - 1) * 100 if total_invested > 0 else 0
        
        print("-"*80)
        print(f"Total Invested: ₹{total_invested:.2f}")
        print(f"Total Current Value: ₹{total_current:.2f}")
        print(f"Total P&L: ₹{total_pnl:.2f} ({total_pnl_percent:.2f}%)")
        print("="*80 + "\n")

# Create and run the portfolio monitor
monitor = PortfolioMonitor()

# Set up callbacks
quotes_client.on_tick = monitor.on_tick
quotes_client.on_connect = monitor.on_connect
quotes_client.on_error = lambda ws, error: print(f"Error: {error}")

# Start monitoring (blocking call)
try:
    quotes_client.connect()
except KeyboardInterrupt:
    print("\nPortfolio monitoring stopped by user")
    quotes_client.stop()
```

### Multi-Strategy Trading

```python
from wiz_trader import QuotesClient, WizzerClient
import pandas as pd
import threading
import time
from datetime import datetime
import numpy as np

# Initialize API clients
quotes_client = QuotesClient(
    base_url="wss://websocket-url/quotes",
    token="your-jwt-token",
    log_level="info"
)

wizzer_client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="info"
)

class TradingStrategy:
    """Base class for trading strategies"""
    def __init__(self, name, symbols):
        self.name = name
        self.symbols = symbols
        self.active = False
        self.positions = {}
        self.prices = {}
        
    def on_tick(self, tick):
        """Process tick data - should be implemented by subclasses"""
        pass
    
    def start(self):
        """Start the strategy"""
        self.active = True
        print(f"Strategy {self.name} started at {datetime.now()}")
    
    def stop(self):
        """Stop the strategy"""
        self.active = False
        print(f"Strategy {self.name} stopped at {datetime.now()}")
        
        # Close any open positions
        self.close_all_positions()
    
    def close_all_positions(self):
        """Close all open positions"""
        for symbol, position in list(self.positions.items()):
            if position != 0:
                try:
                    self.execute_order(
                        symbol=symbol.split(':')[1],
                        exchange=symbol.split(':')[0],
                        transaction_type="SELL" if position > 0 else "BUY",
                        quantity=abs(position)
                    )
                    print(f"Closed position for {symbol}: {position} units")
                    self.positions[symbol] = 0
                except Exception as e:
                    print(f"Error closing position for {symbol}: {e}")
    
    def execute_order(self, symbol, exchange, transaction_type, quantity):
        """Execute an order through the API"""
        try:
            response = wizzer_client.place_order(
                exchange=exchange,
                trading_symbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                order_type=wizzer_client.ORDER_TYPE_MARKET,
                product=wizzer_client.PRODUCT_CNC
            )
            print(f"Order executed: {exchange}:{symbol} {transaction_type} {quantity} units")
            return response.get('orderId')
        except Exception as e:
            print(f"Order execution error: {e}")
            return None

class MovingAverageCrossover(TradingStrategy):
    """Moving Average Crossover Strategy"""
    def __init__(self, name, symbols, fast_period=10, slow_period=30):
        super().__init__(name, symbols)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.price_history = {s: [] for s in symbols}
    
    def on_tick(self, tick):
        if not self.active:
            return
            
        instrument = tick.get('instrument')
        ltp = tick.get('ltp')
        
        if instrument in self.symbols and ltp is not None:
            # Store the current price
            self.prices[instrument] = ltp
            
            # Add to price history
            self.price_history[instrument].append(ltp)
            
            # Keep only enough prices for the slow MA
            if len(self.price_history[instrument]) > self.slow_period:
                self.price_history[instrument].pop(0)
            
            # Check for trading signals if we have enough data
            if len(self.price_history[instrument]) >= self.slow_period:
                self.check_signals(instrument)
    
    def check_signals(self, instrument):
        prices = self.price_history[instrument]
        
        # Calculate moving averages
        fast_ma = sum(prices[-self.fast_period:]) / self.fast_period
        slow_ma = sum(prices) / self.slow_period
        
        # Get current position and price
        current_position = self.positions.get(instrument, 0)
        current_price = self.prices[instrument]
        
        # Generate signals
        if fast_ma > slow_ma and current_position <= 0:
            # Buy signal
            quantity = 10  # Fixed quantity for simplicity
            
            # Close any short position first
            if current_position < 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="BUY",
                    quantity=abs(current_position)
                )
                self.positions[instrument] = 0
            
            # Enter long position
            self.execute_order(
                symbol=instrument.split(':')[1],
                exchange=instrument.split(':')[0],
                transaction_type="BUY",
                quantity=quantity
            )
            self.positions[instrument] = quantity
            
            print(f"{self.name}: BUY {quantity} units of {instrument} at {current_price}")
            
        elif fast_ma < slow_ma and current_position >= 0:
            # Sell signal
            
            # Close any long position
            if current_position > 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="SELL",
                    quantity=current_position
                )
                self.positions[instrument] = 0
                
                print(f"{self.name}: SELL {current_position} units of {instrument} at {current_price}")
            
            # Option: Enter short position (if allowed)
            # quantity = 10  # Fixed quantity for simplicity
            # self.execute_order(
            #     symbol=instrument.split(':')[1],
            #     exchange=instrument.split(':')[0],
            #     transaction_type="SELL",
            #     quantity=quantity
            # )
            # self.positions[instrument] = -quantity
            # print(f"{self.name}: SHORT {quantity} units of {instrument} at {current_price}")

class BollingerBands(TradingStrategy):
    """Bollinger Bands Strategy"""
    def __init__(self, name, symbols, period=20, std_dev=2):
        super().__init__(name, symbols)
        self.period = period
        self.std_dev = std_dev
        self.price_history = {s: [] for s in symbols}
    
    def on_tick(self, tick):
        if not self.active:
            return
            
        instrument = tick.get('instrument')
        ltp = tick.get('ltp')
        
        if instrument in self.symbols and ltp is not None:
            # Store the current price
            self.prices[instrument] = ltp
            
            # Add to price history
            self.price_history[instrument].append(ltp)
            
            # Keep only enough prices for the calculation
            if len(self.price_history[instrument]) > self.period:
                self.price_history[instrument].pop(0)
            
            # Check for trading signals if we have enough data
            if len(self.price_history[instrument]) >= self.period:
                self.check_signals(instrument)
    
    def check_signals(self, instrument):
        prices = self.price_history[instrument]
        
        # Calculate Bollinger Bands
        sma = sum(prices) / len(prices)
        std = np.std(prices)
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        # Get current position and price
        current_position = self.positions.get(instrument, 0)
        current_price = self.prices[instrument]
        
        # Generate signals
        if current_price < lower_band and current_position <= 0:
            # Buy signal (price below lower band)
            quantity = 10  # Fixed quantity for simplicity
            
            # Close any short position first
            if current_position < 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="BUY",
                    quantity=abs(current_position)
                )
                self.positions[instrument] = 0
            
            # Enter long position
            self.execute_order(
                symbol=instrument.split(':')[1],
                exchange=instrument.split(':')[0],
                transaction_type="BUY",
                quantity=quantity
            )
            self.positions[instrument] = quantity
            
            print(f"{self.name}: BUY {quantity} units of {instrument} at {current_price} (below lower band {lower_band:.2f})")
            
        elif current_price > upper_band and current_position >= 0:
            # Sell signal (price above upper band)
            
            # Close any long position
            if current_position > 0:
                self.execute_order(
                    symbol=instrument.split(':')[1],
                    exchange=instrument.split(':')[0],
                    transaction_type="SELL",
                    quantity=current_position
                )
                self.positions[instrument] = 0
                
                print(f"{self.name}: SELL {current_position} units of {instrument} at {current_price} (above upper band {upper_band:.2f})")

class MultiStrategyManager:
    """Manages multiple trading strategies"""
    def __init__(self, quotes_client):
        self.quotes_client = quotes_client
        self.strategies = {}
        
    def add_strategy(self, strategy):
        """Add a strategy to the manager"""
        self.strategies[strategy.name] = strategy
        
        # Subscribe to all strategy symbols
        for symbol in strategy.symbols:
            if not symbol.startswith('NSE:') and not symbol.startswith('BSE:'):
                print(f"Warning: Symbol {symbol} does not include exchange prefix")
        
    def on_tick(self, ws, tick):
        """Process ticks and distribute to strategies"""
        for strategy in self.strategies.values():
            strategy.on_tick(tick)
    
    def on_connect(self, ws):
        """Handle connection to quotes server"""
        print(f"Connected to quotes server at {datetime.now()}")
        
        # Collect all symbols from all strategies
        all_symbols = set()
        for strategy in self.strategies.values():
            all_symbols.update(strategy.symbols)
        
        # Subscribe to all symbols
        if all_symbols:
            ws.subscribe(list(all_symbols))
            print(f"Subscribed to {len(all_symbols)} symbols")
    
    def start_all(self):
        """Start all strategies"""
        for strategy in self.strategies.values():
            strategy.start()
    
    def stop_all(self):
        """Stop all strategies"""
        for strategy in self.strategies.values():
            strategy.stop()
    
    def start_strategy(self, name):
        """Start a specific strategy"""
        if name in self.strategies:
            self.strategies[name].start()
        else:
            print(f"Strategy {name} not found")
    
    def stop_strategy(self, name):
        """Stop a specific strategy"""
        if name in self.strategies:
            self.strategies[name].stop()
        else:
            print(f"Strategy {name} not found")
    
    def run(self):
        """Run the strategy manager"""
        # Set up callbacks
        self.quotes_client.on_tick = self.on_tick
        self.quotes_client.on_connect = self.on_connect
        self.quotes_client.on_error = lambda ws, error: print(f"Error: {error}")
        
        # Start all strategies
        self.start_all()
        
        # Start the quotes client (blocking call)
        try:
            self.quotes_client.connect()
        except KeyboardInterrupt:
            print("\nMulti-strategy manager stopped by user")
            self.stop_all()
            self.quotes_client.stop()

# Create strategies
ma_strategy = MovingAverageCrossover(
    name="MA Crossover",
    symbols=["NSE:SBIN:3045", "NSE:ICICIBANK:4963"],
    fast_period=10,
    slow_period=30
)

bb_strategy = BollingerBands(
    name="Bollinger Bands",
    symbols=["NSE:RELIANCE:2885", "NSE:TCS:2953"],
    period=20,
    std_dev=2
)

# Create and run the multi-strategy manager
manager = MultiStrategyManager(quotes_client)
manager.add_strategy(ma_strategy)
manager.add_strategy(bb_strategy)
manager.run()
```

## Error Handling

The SDK provides several mechanisms for handling errors:

### Exception Handling

All API calls can throw exceptions, which should be caught and handled:

```python
try:
    order_response = client.place_order(
        exchange=client.EXCHANGE_NSE,
        trading_symbol="SBIN",
        transaction_type=client.TRANSACTION_TYPE_BUY,
        quantity=10,
        order_type=client.ORDER_TYPE_MARKET,
        product=client.PRODUCT_CNC
    )
    print(f"Order placed successfully: {order_response.get('orderId')}")
except Exception as e:
    print(f"Error placing order: {e}")
```

### Callback Error Handling

For the WebSocket client, errors are also sent via the `on_error` callback:

```python
def on_error(ws, error):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {error}")
    
    # You could implement reconnection logic or alerting here
    if isinstance(error, ConnectionRefusedError):
        print("Connection refused. Check server status.")
    elif isinstance(error, TimeoutError):
        print("Connection timed out. Check network.")

quotes_client.on_error = on_error
```

### Logging

Both clients support different log levels:

```python
client = WizzerClient(
    base_url="https://api-url.in",
    token="your-jwt-token",
    log_level="debug"  # Options: "error", "info", "debug"
)
```

The logs can help diagnose issues during development and production.

## Troubleshooting

### Common Issues

#### Authentication Issues

If you're facing authentication errors:

1. Check that your token is valid and not expired
2. Ensure you're using the correct base_url for production or development
3. Verify environment variables if you're using them

Example of token validation:
```python
def is_token_valid(token):
    """Basic validation of JWT token format"""
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    # Check if the token is expired
    import base64
    import json
    import time
    
    try:
        # Decode the payload
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
        decoded = base64.b64decode(payload)
        data = json.loads(decoded)
        
        # Check expiration
        if 'exp' in data:
            return data['exp'] > time.time()
        return True
    except Exception:
        return False

# Check if token is valid
if not is_token_valid(token):
    print("Token is invalid or expired. Please get a new token.")
```

#### WebSocket Connection Issues

If you're having trouble connecting to the WebSocket server:

1. Check network connectivity and firewall settings
2. Verify the WebSocket URL is correct
3. Check if the server supports SSL/TLS if using 'wss://' protocol
4. Try with a smaller `max_message_size` to rule out size limitations

#### Order Placement Failures

If orders are not being placed successfully:

1. Check the error message from the API response
2. Verify that you're using the correct exchange, symbol, and token
3. Ensure you have sufficient funds/holdings for the trade
4. Check that market hours are active for the segment you're trading

## API Reference

For a complete list of all available methods and parameters, refer to the class docstrings within the SDK.

```python
# Example of getting detailed help on a method
help(WizzerClient.place_order)
```

### Environment Variables

All supported environment variables:

- `WZ__QUOTES_BASE_URL`: WebSocket URL for the quotes server
- `WZ__API_BASE_URL`: Base URL for the Wizzer's REST API
- `WZ__TOKEN`: JWT token for authentication
- `WZ__STRATEGY_ID`: Default strategy ID to use if not provided in methods

### Full Method List

#### QuotesClient
- `__init__(base_url, token, log_level, max_message_size, batch_size)`
- `connect()` - Connect in blocking mode
- `connect_async()` - Connect in non-blocking mode
- `stop()` - Stop the WebSocket connection
- `subscribe(instruments)` - Subscribe to instruments
- `unsubscribe(instruments)` - Unsubscribe from instruments

#### WizzerClient
- `__init__(base_url, token, strategy_id, log_level)`
- `get_indices(trading_symbol, exchange)`
- `get_index_components(trading_symbol, exchange)`
- `get_historical_ohlcv(instruments, start_date, end_date, ohlcv, interval)`
- `place_order(exchange, trading_symbol, transaction_type, quantity, ...)`
- `modify_order(order_id, **params)`
- `cancel_order(order_id)`
- `get_order(order_id)`
- `get_positions(position_status)`
- `get_open_positions()`
- `get_closed_positions()`
- `get_holdings(portfolios)`
- `create_basket(name, instruments, weightage_scheme, capital, instrument_types)`
- `get_baskets()`
- `get_basket(basket_id)`
- `get_basket_instruments(basket_id)`
- `place_basket_order(trading_symbol, transaction_type, quantity, ...)`
- `place_basket_exit_order(trading_symbol, exchange, transaction_type, quantity, exchange_token, **kwargs)`
- `modify_basket_order(order_id, **params)`
- `rebalance_basket(trading_symbol, instruments)`
- `exit_all_positions()`
- `exit_strategy_positions(strategy_id)`