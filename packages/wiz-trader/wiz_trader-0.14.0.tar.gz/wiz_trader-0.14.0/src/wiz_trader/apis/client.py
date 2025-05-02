import os
import json
import logging
from typing import Dict, List, Optional, Union, Any

import requests

# Setup module-level logger with a default handler if none exists.
logger = logging.getLogger(__name__)
if not logger.handlers:
  handler = logging.StreamHandler()
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)

class WizzerClient:
  """
  A Python SDK for connecting to the Wizzer's REST API.

  Attributes:
    base_url (str): Base URL of the Wizzer's API server.
    token (str): JWT token for authentication.
    log_level (str): Logging level. Options: "error", "info", "debug".
    strategy_id (str): Default strategy ID to use if not provided in methods.
  """
  
  # Constants
  # Transaction types
  TRANSACTION_TYPE_BUY = "BUY"
  TRANSACTION_TYPE_SELL = "SELL"

  # Product types
  PRODUCT_CNC = "CNC"         # Cash and Carry
  PRODUCT_MIS = "MIS"         # Margin Intraday Square-off
  PRODUCT_NRML = "NRML"       # Normal / Overnight Futures and Options

  # Order types
  ORDER_TYPE_MARKET = "MARKET"
  ORDER_TYPE_LIMIT = "LIMIT"
  ORDER_TYPE_SL = "STOPLIMIT"        # Stop Loss
  ORDER_TYPE_SLM = "STOPMARKET"      # Stop Loss Market

  # Validity types
  VALIDITY_DAY = "DAY"
  VALIDITY_IOC = "IOC"        # Immediate or Cancel
  VALIDITY_GTT = "GTT"        # Good Till Triggered

  # Variety types
  VARIETY_REGULAR = "REGULAR"
  VARIETY_AMO = "AMO"         # After Market Order
  VARIETY_BO = "BO"           # Bracket Order
  VARIETY_CO = "CO"           # Cover Order

  # Exchanges
  EXCHANGE_NSE = "NSE"        # National Stock Exchange
  EXCHANGE_BSE = "BSE"        # Bombay Stock Exchange
  EXCHANGE_WZR = "WZR"        # Wizzer Exchange (for baskets)

  # Segments
  SEGMENT_NSE_CM = "NSECM"    # NSE Cash Market
  SEGMENT_BSE_CM = "BSECM"    # BSE Cash Market
  SEGMENT_NSE_FO = "NSEFO"    # NSE Futures and Options
  SEGMENT_WZREQ = "WZREQ"     # Wizzer Basket Segment
  
  # Order status constants
  ORDER_STATUS_OPEN = "OPEN"
  ORDER_STATUS_CANCELLED = "CANCELLED" 
  ORDER_STATUS_REJECTED = "REJECTED"
  ORDER_STATUS_PENDING = "PENDING"
  ORDER_STATUS_COMPLETED = "COMPLETED"

  # Trading mode constants
  TRADING_MODE_PAPER = "paper_trading"
  TRADING_MODE_ADVICES = "advices"
  TRADING_MODE_TRADING_AND_ADVICES = "trading_and_advices"
  
  # Rebalance execution policies
  REBALANCE_FULL = "full_rebalance"
  REBALANCE_ENTRY_ONLY = "entry_only"
  REBALANCE_EXIT_ONLY = "exit_only"

  # URIs to various API endpoints
  _routes = {
    # Order related endpoints
    "order.place": "/orders",
    "order.get": "/orders",
    "order.modify": "/orders/{order_id}",
    "order.cancel": "/orders/{order_id}",
    "order.info": "/orders/{order_id}",
    
    # Basket order endpoints
    "basket.order.place": "/orders/basket",
    "basket.order.exit": "/orders/basket/exit",
    "basket.order.modify": "/orders/basket/{order_id}",
    
    # Portfolio and position management
    "portfolio.positions": "/portfolios/positions",
    "portfolio.positions.exit.all": "/portfolios/positions/exit/all",
    "portfolio.positions.exit.strategy": "/portfolios/positions/exit/strategies/{strategy_id}",
    "portfolio.holdings": "/portfolios/holdings",
    
    # Basket management
    "basket.create": "/baskets",
    "basket.list": "/baskets",
    "basket.info": "/baskets/{basket_id}",
    "basket.instruments": "/baskets/{basket_id}/instruments",
    "basket.rebalance": "/baskets/rebalance",
    
    # Data hub endpoints
    "datahub.indices": "/datahub/indices",
    "datahub.index.components": "/datahub/index/components",
    "datahub.historical.ohlcv": "/datahub/historical/ohlcv",
  }
  
  def __init__(
    self,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    strategy_id: Optional[str] = None,
    log_level: str = "error"  # default only errors
  ):
    # Configure logger based on log_level.
    valid_levels = {"error": logging.ERROR, "info": logging.INFO, "debug": logging.DEBUG}
    if log_level not in valid_levels:
      raise ValueError(f"log_level must be one of {list(valid_levels.keys())}")
    logger.setLevel(valid_levels[log_level])

    self.log_level = log_level
    # System env vars take precedence over .env
    self.base_url = base_url or os.environ.get("WZ__API_BASE_URL")
    self.token = token or os.environ.get("WZ__TOKEN")
    self.strategy_id = strategy_id or os.environ.get("WZ__STRATEGY_ID")
    
    if not self.token:
      raise ValueError("JWT token must be provided as an argument or in .env (WZ__TOKEN)")
    if not self.base_url:
      raise ValueError("Base URL must be provided as an argument or in .env (WZ__API_BASE_URL)")

    # Prepare the authorization header
    self.headers = {
      "Authorization": f"Bearer {self.token}",
      "Content-Type": "application/json"
    }

    logger.debug("Initialized WizzerClient with URL: %s", self.base_url)

  def _get_strategy(self, strategy: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Get strategy information, either from the provided parameter or from the default.
    
    Args:
      strategy (Optional[Dict[str, str]]): Strategy object with id, identifier, and name.
    
    Returns:
      Dict[str, str]: A strategy object with at least the id field.
        
    Raises:
      ValueError: If no strategy is provided and no default is set.
    """
    if strategy and "id" in strategy:
      return strategy
    
    if not self.strategy_id:
      raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
    
    return {"id": self.strategy_id}

  # ===== DATA HUB METHODS =====

  def get_indices(self, trading_symbol: Optional[str] = None, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of indices available on the exchange.

    Args:
      trading_symbol (Optional[str]): Filter by specific index symbol.
      exchange (Optional[str]): Filter by specific exchange (NSE, BSE).

    Returns:
      List[Dict[str, Any]]: List of index information.
    """
    params = {}
    
    if trading_symbol:
      params["tradingSymbol"] = trading_symbol
    if exchange:
      params["exchange"] = exchange

    logger.debug("Fetching indices with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.indices"], params=params)
    return response

  def get_index_components(self, trading_symbol: str, exchange: str) -> List[Dict[str, Any]]:
    """
    Get list of components (stocks) for a specific index.

    Args:
      trading_symbol (str): Index symbol (e.g., "NIFTY 50").
      exchange (str): Exchange name (NSE, BSE).

    Returns:
       List[Dict[str, Any]]: List of component stocks in the index.
    """
    params = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange
    }

    logger.debug("Fetching index components with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.index.components"], params=params)
    return response

  def get_historical_ohlcv(
    self, 
    instruments: List[str], 
    start_date: str, 
    end_date: str, 
    ohlcv: List[str],
    interval: str = "1d"
  ) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for specified instruments.

    Args:
      instruments (List[str]): List of instrument identifiers (e.g., ["NSE:SBIN:3045"]).
      start_date (str): Start date in YYYY-MM-DD format.
      end_date (str): End date in YYYY-MM-DD format.
      ohlcv (List[str]): List of OHLCV fields to retrieve (open, high, low, close, volume).
      interval (str, optional): Data interval. Options: "1d" (daily, default), "1M" (monthly - last trading day of month).

    Returns:
      List[Dict[str, Any]]: Historical data for requested instruments.
    """
    data = {
      "instruments": instruments,
      "startDate": start_date,
      "endDate": end_date,
      "ohlcv": ohlcv,
      "interval": interval
    }

    logger.debug("Fetching historical OHLCV with data: %s", data)
    response = self._make_request("POST", self._routes["datahub.historical.ohlcv"], json=data)
    return response

  # ===== ORDER MANAGEMENT METHODS =====

  def place_order(
    self,
    exchange: str,
    trading_symbol: str,
    transaction_type: str,
    quantity: int,
    order_type: str = None,
    product: str = None,
    price: float = 0,
    trigger_price: float = 0,
    disclosed_qty: int = 0,
    validity: str = None,
    variety: str = None,
    stoploss: float = 0,
    target: float = 0,
    exchange_token: Optional[int] = None,
    broker: str = None,
    strategy: Optional[Dict[str, str]] = None
  ) -> Dict[str, Any]:
    """
    Place a regular order.
    
    Args:
      exchange (str): Exchange code (e.g., "NSE", "BSE").
      trading_symbol (str): Symbol of the instrument.
      transaction_type (str): "BUY" or "SELL".
      quantity (int): Number of shares to trade.
      order_type (str, optional): Order type (e.g., "MARKET", "LIMIT"). Defaults to MARKET.
      product (str, optional): Product code (e.g., "CNC" for delivery). Defaults to CNC.
      price (float, optional): Price for limit orders. Defaults to 0.
      trigger_price (float, optional): Trigger price for stop orders. Defaults to 0.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      validity (str, optional): Order validity (e.g., "DAY", "IOC"). Defaults to DAY.
      variety (str, optional): Order variety. Defaults to REGULAR.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      segment (Optional[str], optional): Market segment. If None, determined from exchange.
      exchange_token (Optional[int], optional): Exchange token for the instrument.
      broker (str, optional): Broker code.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "exchange": exchange,
      "tradingSymbol": trading_symbol,
      "transactionType": transaction_type,
      "qty": quantity,
      "orderType": order_type,
      "product": product,
      "price": price,
      "triggerPrice": trigger_price,
      "disclosedQty": disclosed_qty,
      "validity": validity,
      "variety": variety,
      "stoploss": stoploss,
      "target": target,
      "strategy": strategy_info
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    logger.debug("Placing order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def cancel_order(self, order_id: str) -> Dict[str, Any]:
    """
    Cancel an existing order.
    
    Args:
      order_id (str): Order ID to cancel.
        
    Returns:
      Dict[str, Any]: Response with the cancelled order ID.
    """
    endpoint = self._routes["order.cancel"].format(order_id=order_id)
    
    logger.debug("Cancelling order: %s", order_id)
    return self._make_request("DELETE", endpoint)

  def get_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      page_no: int = 1,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
              Valid values: "paper_trading", "advices", "trading_and_advices".
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
              Valid values: "OPEN", "CANCELLED", "REJECTED", "PENDING", "COMPLETED".
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format. Defaults to today.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format. Defaults to today.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          page_no (int, optional): Page number for pagination. Defaults to 1.
          paginate (bool, optional): Whether to automatically fetch all pages. Defaults to False.
              
      Returns:
          List[Dict[str, Any]]: List of orders matching the filter criteria.
      """
      endpoint = self._routes["order.get"]
      
      # Build the base parameters without list items
      params = {}
      
      # Handle single parameters
      if from_date:
          params["fromDateRange"] = from_date
      
      if to_date:
          params["toDateRange"] = to_date
      
      if not paginate:
          params["pageNo"] = page_no
      
      # Validate trading modes
      if trading_modes:
          for mode in trading_modes:
              if mode not in [self.TRADING_MODE_PAPER, self.TRADING_MODE_ADVICES, self.TRADING_MODE_TRADING_AND_ADVICES]:
                  raise ValueError(f"Invalid trading mode: {mode}")
      
      # Validate order statuses
      if order_statuses:
          for status in order_statuses:
              if status not in [self.ORDER_STATUS_OPEN, self.ORDER_STATUS_CANCELLED, 
                              self.ORDER_STATUS_REJECTED, self.ORDER_STATUS_PENDING, 
                              self.ORDER_STATUS_COMPLETED]:
                  raise ValueError(f"Invalid order status: {status}")
      
      # Handle pagination with properly formatted parameters
      if paginate:
          return self._paginate_orders(endpoint, params, trading_modes, order_statuses, trading_symbols)
      else:
          logger.debug("Fetching orders with params: %s", params)
          return self._make_request_with_multi_params(
              "GET", 
              endpoint, 
              params=params,
              trading_modes=trading_modes,
              order_statuses=order_statuses, 
              trading_symbols=trading_symbols
          )

  def _make_request_with_multi_params(
      self, 
      method: str, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> Any:
      """
      Make an HTTP request with multiple parameters having the same name.
      
      Args:
          method (str): HTTP method (GET, POST, etc.)
          endpoint (str): API endpoint path.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          Any: Parsed JSON response.
      """
      url = f"{self.base_url}{endpoint}"
      
      # Start with the base parameters
      all_params = params.copy()
      
      # Create a session to manually handle parameter encoding
      session = requests.Session()
      req = requests.Request(method, url, headers=self.headers, params=all_params)
      prepped = req.prepare()
      
      # Build the URL with additional repeated parameters
      query_parts = []
      if prepped.url.find('?') >= 0:
          query_parts.append(prepped.url.split('?', 1)[1])
      
      # Add repeated parameters
      if trading_modes:
          for mode in trading_modes:
              query_parts.append(f"tradingMode={mode}")
      
      if order_statuses:
          for status in order_statuses:
              query_parts.append(f"orderStatus={status}")
      
      if trading_symbols:
          for symbol in trading_symbols:
              query_parts.append(f"tradingSymbols={symbol}")
      
      # Build the final URL
      final_url = prepped.url.split('?')[0]
      if query_parts:
          final_url += '?' + '&'.join(query_parts)
      
      try:
          logger.debug("%s request to %s", method, final_url)
          response = session.send(prepped)
          response.url = final_url
          response.raise_for_status()
          return response.json()
      except requests.RequestException as e:
          logger.error("API request failed: %s", e, exc_info=True)
          if hasattr(e.response, 'text'):
              logger.error("Response content: %s", e.response.text)
          raise

  def _paginate_orders(
      self, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> List[Dict[str, Any]]:
      """
      Internal method to handle pagination for orders API with multi-value parameters.
      
      Args:
          endpoint (str): API endpoint.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          List[Dict[str, Any]]: Combined results from all pages.
      """
      all_orders = []
      page_no = 1
      total_count = None
      page_size = 50  # API returns 50 orders per page
      
      while True:
          current_params = params.copy()
          current_params["pageNo"] = page_no
          logger.debug("Fetching orders page %d", page_no)
          
          # Build the URL with the session to get the properly formatted parameters
          session = requests.Session()
          req = requests.Request("GET", f"{self.base_url}{endpoint}", headers=self.headers, params=current_params)
          prepped = req.prepare()
          
          # Build the URL with additional repeated parameters
          query_parts = []
          if prepped.url.find('?') >= 0:
              query_parts.append(prepped.url.split('?', 1)[1])
          
          # Add repeated parameters
          if trading_modes:
              for mode in trading_modes:
                  query_parts.append(f"tradingMode={mode}")
          
          if order_statuses:
              for status in order_statuses:
                  query_parts.append(f"orderStatus={status}")
          
          if trading_symbols:
              for symbol in trading_symbols:
                  query_parts.append(f"tradingSymbols={symbol}")
          
          # Build the final URL
          final_url = prepped.url.split('?')[0]
          if query_parts:
              final_url += '?' + '&'.join(query_parts)
          
          # Make the request
          try:
              logger.debug("GET request to %s", final_url)
              prepped.url = final_url
              response = session.send(prepped)
              response.raise_for_status()
              
              # Get orders from the current page
              orders = response.json()
              all_orders.extend(orders)
              
              # Check if we need to fetch more pages
              if total_count is None and "X-Total-Count" in response.headers:
                  try:
                      total_count = int(response.headers["X-Total-Count"])
                      logger.debug("Total orders count: %d", total_count)
                  except (ValueError, TypeError):
                      logger.warning("Could not parse X-Total-Count header")
                      break
              
              # If we've fetched all orders or there are no more pages, stop
              if not orders or len(all_orders) >= total_count or total_count is None:
                  break
              
              # Move to the next page
              page_no += 1
              
          except requests.RequestException as e:
              logger.error("API request failed during pagination: %s", e, exc_info=True)
              if hasattr(e.response, 'text'):
                  logger.error("Response content: %s", e.response.text)
              raise
      
      logger.info("Fetched %d orders in total", len(all_orders))
      return all_orders

  def get_open_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get open orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of open orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_OPEN],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_completed_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get completed orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of completed orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_COMPLETED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_pending_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get pending orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of pending orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_PENDING],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_cancelled_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get cancelled orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of cancelled orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_CANCELLED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_rejected_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get rejected orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of rejected orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_REJECTED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_paper_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get paper traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of paper traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_PAPER],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_advised_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get advised orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of advised orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_live_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get live traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of live traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_TRADING_AND_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )
  
  def get_order(self, order_id: str) -> Dict[str, Any]:
    """
    Get details of a specific order by ID.
    
    Args:
      order_id (str): ID of the order to retrieve.
        
    Returns:
      Dict[str, Any]: Order details.
    """
    endpoint = self._routes["order.info"].format(order_id=order_id)
    
    logger.debug("Fetching order: %s", order_id)
    return self._make_request("GET", endpoint)
    
  def get_positions(self, position_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get portfolio positions with optional filtering by status.
    
    Args:
      position_status (Optional[str], optional): Filter positions by status.
        Valid values: "open", "closed". If None, returns all positions.
        
    Returns:
      List[Dict[str, Any]]: List of positions matching the filter criteria.
    """
    endpoint = self._routes["portfolio.positions"]
    params = {}
    
    if position_status:
      if position_status not in ["open", "closed"]:
        raise ValueError("position_status must be either 'open', 'closed', or None")
      params["positionStatus"] = position_status
    
    logger.debug("Fetching positions with status: %s", position_status or "all")
    return self._make_request("GET", endpoint, params=params)
    
  def get_open_positions(self) -> List[Dict[str, Any]]:
    """
    Get all open positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of open positions.
    """
    return self.get_positions(position_status="open")
    
  def get_closed_positions(self) -> List[Dict[str, Any]]:
    """
    Get all closed positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of closed positions.
    """
    return self.get_positions(position_status="closed")
  
  def get_holdings(self, portfolios: Optional[str] = "default") -> List[Dict[str, Any]]:
    """
    Get current holdings.
    
    Args:
      portfolios (str, optional): Portfolio name. Defaults to "default".
        
    Returns:
      List[Dict[str, Any]]: List of holdings.
    """
    endpoint = self._routes["portfolio.holdings"]
    params = {"portfolios": portfolios}
    
    logger.debug("Fetching holdings for portfolio: %s", portfolios)
    return self._make_request("GET", endpoint, params=params)
    
  # ===== BASKET MANAGEMENT METHODS =====

  def create_basket(
    self,
    name: str,
    instruments: List[Dict[str, Any]],
    weightage_scheme: str = "equi_weighted",
    capital: Optional[Dict[str, float]] = None,
    instrument_types: Optional[List[str]] = None,
    trading_symbol: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Create a new basket.
    
    Args:
      name (str): Name of the basket.
      instruments (List[Dict[str, Any]]): List of instruments with weightage and shares.
      weightage_scheme (str, optional): Weightage scheme. Defaults to "equi_weighted".
      capital (Optional[Dict[str, float]], optional): Capital allocation. Defaults to {"minValue": 0, "actualValue": 0}.
      instrument_types (Optional[List[str]], optional): Types of instruments. Defaults to ["EQLC"].
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.create"]
    
    # Set defaults
    if capital is None:
      capital = {"minValue": 0, "actualValue": 0}
        
    data = {
      "name": name,
      "weightageScheme": weightage_scheme,
      "instruments": instruments,
      "capital": capital,
      "instrumentTypes": instrument_types
    }
    
    logger.debug("Creating basket: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def get_baskets(self) -> List[Dict[str, Any]]:
    """
    Get all baskets.
    
    Returns:
      List[Dict[str, Any]]: List of baskets.
    """
    endpoint = self._routes["basket.list"]
    
    logger.debug("Fetching baskets")
    return self._make_request("GET", endpoint)
    
  def get_basket(self, basket_id: str) -> Dict[str, Any]:
    """
    Get a specific basket by ID.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.info"].format(basket_id=basket_id)
    
    logger.debug("Fetching basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def get_basket_instruments(self, basket_id: str) -> List[Dict[str, Any]]:
    """
    Get instruments in a basket.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      List[Dict[str, Any]]: List of instruments in the basket.
    """
    endpoint = self._routes["basket.instruments"].format(basket_id=basket_id)
    
    logger.debug("Fetching instruments for basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def place_basket_order(
    self,
    trading_symbol: str,
    transaction_type: str,
    quantity: float,
    price: float = 0,
    order_type: str = None,
    product: str = None,
    validity: str = None,
    exchange_token: Optional[int] = None,
    trigger_price: float = 0,
    stoploss: float = 0,
    target: float = 0,
    broker: str = "wizzer",
    variety: str = None,
    strategy: Optional[Dict[str, str]] = None,
    disclosed_qty: int = 0,
    sl_applied_level: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Place a basket order.
    
    Args:
      trading_symbol (str): Basket trading symbol (e.g., "/BASKET_NAME").
      transaction_type (str): "BUY" or "SELL".
      quantity (float): Quantity/units of the basket.
      price (float, optional): Price for limit orders. Defaults to 0.
      order_type (str, optional): Order type. Defaults to MARKET.
      product (str, optional): Product code. Defaults to CNC.
      validity (str, optional): Order validity. Defaults to DAY.
      exchange_token (Optional[int], optional): Exchange token for the basket.
      trigger_price (float, optional): Trigger price. Defaults to 0.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      broker (str, optional): Broker code. Defaults to "wizzer".
      variety (str, optional): Order variety. Defaults to REGULAR.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      sl_applied_level (Optional[str], optional): Stop loss applied level (e.g., "basket").
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": self.EXCHANGE_WZR,
      "transactionType": transaction_type,
      "qty": quantity,
      "price": price,
      "orderType": order_type,
      "product": product,
      "validity": validity,
      "triggerPrice": trigger_price,
      "stoploss": stoploss,
      "target": target,
      "broker": broker,
      "variety": variety,
      "strategy": strategy_info,
      "segment": self.SEGMENT_WZREQ,
      "disclosedQty": disclosed_qty
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    # Add stop loss level if provided
    if sl_applied_level:
      data["slAppliedLevel"] = sl_applied_level
        
    logger.debug("Placing basket order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def place_basket_exit_order(
    self,
    trading_symbol: str,
    exchange: str,
    transaction_type: str,
    quantity: float,
    exchange_token: int,
    **kwargs
  ) -> Dict[str, Any]:
    """
    Place a basket exit order.
    
    Args:
      trading_symbol (str): Basket trading symbol.
      exchange (str): Exchange code (usually "WZR" for baskets).
      transaction_type (str): "BUY" or "SELL" (usually "SELL" for exit).
      quantity (float): Quantity/units of the basket.
      exchange_token (int): Exchange token for the basket.
      **kwargs: Additional parameters for the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.exit"]
    
    # Build base data
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange,
      "transactionType": transaction_type,
      "qty": quantity,
      "exchangeToken": exchange_token,
      **kwargs
    }
    
    # Set strategy if not in kwargs
    if "strategy" not in kwargs:
      data["strategy"] = self._get_strategy(None)
        
    # Set defaults if not in kwargs
    defaults = {
      "orderType": self.ORDER_TYPE_MARKET,
      "product": self.PRODUCT_CNC, 
      "validity": self.VALIDITY_DAY,
      "disclosedQty": 0,
      "price": 0,
      "variety": self.VARIETY_REGULAR,
      "stoploss": 0,
      "broker": "wizzer",
      "triggerPrice": 0,
      "target": 0,
      "segment": self.SEGMENT_WZREQ
    }
    
    for key, value in defaults.items():
      if key not in data:
        data[key] = value
    
    logger.debug("Placing basket exit order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_basket_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing basket order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying basket order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def rebalance_basket(
    self,
    trading_symbol: str,
    instruments: List[str],
    execution_policy: str
  ) -> Dict[str, Any]:
    """
    Rebalance a basket with new instruments.
    
    Args:
      trading_symbol (str): Basket trading symbol.
      instruments (List[str]): List of instrument identifiers for the new basket composition.
      execution_policy (str): Rebalance execution policy. 
          Options: "full_rebalance", "entry_only", "exit_only".
        
    Returns:
      Dict[str, Any]: Rebalance response.
    """
    endpoint = self._routes["basket.rebalance"]
    
    data = {
      "tradingSymbol": trading_symbol,
      "instruments": instruments,
      "policies": {
        "execution": execution_policy
      }
    }
    
    logger.debug("Rebalancing basket %s with instruments: %s, policy: %s", 
                 trading_symbol, instruments, execution_policy)
    return self._make_request("POST", endpoint, json=data)
    
  def exit_all_positions(self) -> Dict[str, Any]:
    """
    Exit all positions across all strategies.
    
    This method sends a request to close all open positions for the user.
    
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
    """
    endpoint = self._routes["portfolio.positions.exit.all"]
    
    data = {}
    
    logger.debug("Exiting all positions")
    return self._make_request("POST", endpoint, json=data)
    
  def exit_strategy_positions(self, strategy_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Exit all positions for a specific strategy.
    
    Args:
      strategy_id (Optional[str]): ID of the strategy to exit positions for.
        If None, uses the default strategy ID.
        
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
      
    Raises:
      ValueError: If no strategy_id is provided and no default is set.
    """
    # Get strategy ID (either from parameter or default)
    if not strategy_id:
      if not self.strategy_id:
        raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
      strategy_id = self.strategy_id
      
    endpoint = self._routes["portfolio.positions.exit.strategy"].format(strategy_id=strategy_id)
    
    data = {}
    
    logger.debug("Exiting all positions for strategy: %s", strategy_id)
    return self._make_request("POST", endpoint, json=data)

  def _make_request(
    self, 
    method: str, 
    endpoint: str, 
    params: Optional[Dict[str, str]] = None, 
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
  ) -> Any:
    """
    Make an HTTP request to the API.

    Args:
      method (str): HTTP method (GET, POST, etc.)
      endpoint (str): API endpoint path.
      params (Optional[Dict[str, str]]): Query parameters for GET requests.
      json (Optional[Dict[str, Any]]): JSON payload for POST requests.
      headers (Optional[Dict[str, str]]): Custom headers to override the defaults.

    Returns:
      Any: Parsed JSON response.

    Raises:
      requests.RequestException: If the request fails.
    """
    url = f"{self.base_url}{endpoint}"
    request_headers = headers if headers else self.headers
    
    try:
      logger.debug("%s request to %s", method, url)
      response = requests.request(
        method=method,
        url=url,
        headers=request_headers,
        params=params,
        json=json
      )
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
      logger.error("API request failed: %s", e, exc_info=True)
      if hasattr(e.response, 'text'):
        logger.error("Response content: %s", e.response.text)
      raise