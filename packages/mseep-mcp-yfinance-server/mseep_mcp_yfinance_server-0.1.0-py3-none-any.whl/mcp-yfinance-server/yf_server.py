import yfinance as yf
from technical_indicators import TechnicalIndicators
from mcp.server.fastmcp import FastMCP
import threading
import time
import asyncio
from typing import Dict, List, Union, Optional, Tuple
import matplotlib.pyplot as plt


# Create the MCP server instance
mcp = FastMCP("Stock Price Server")

# In-memory watchlist and real-time price cache
watchlist = set()
watchlist_prices = {}

# --- Utility Functions ---
def fetch_ticker(symbol: str):
    """Helper to safely fetch a yfinance Ticker."""
    return yf.Ticker(symbol.upper())

def safe_get_price(ticker) -> float:
    """Attempt to retrieve the current price of a stock."""
    try:
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
        price = ticker.info.get('regularMarketPrice')
        if price is not None:
            return float(price)
        raise ValueError("Price data not available.")
    except Exception as e:
        raise ValueError(f"Error retrieving stock price: {e}")



ti = TechnicalIndicators()

@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """
    Retrieve the current stock price for the given ticker symbol.
    Returns the latest closing price as a float.
    """
    symbol = symbol.upper()
    ticker = fetch_ticker(symbol)
    return safe_get_price(ticker)


    
@mcp.tool()
def get_moving_averages(symbol: str, period: str = "6mo", interval: str = "1d", 
                        windows: List[int] = [20, 50, 200]) -> Dict[str, List[float]]:
    """
    Calculate multiple moving averages for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period (e.g., "6mo", "1y", "max")
        interval: Data interval (e.g., "1d", "1wk")
        windows: List of MA periods to calculate
        
    Returns:
        Dictionary with moving average values
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        result = {}
        
        for window in windows:
            ma = ti.calculate_moving_average(data, window)
            ema = ti.calculate_exponential_moving_average(data, window)
            
            result[f'SMA_{window}'] = ma.dropna().tolist()
            result[f'EMA_{window}'] = ema.dropna().tolist()
            
        # Also include dates for reference
        result['dates'] = data.index.strftime('%Y-%m-%d').tolist()
        result['close'] = data['Close'].tolist()
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_rsi(symbol: str, period: str = "6mo", interval: str = "1d", 
            window: int = 14) -> Dict[str, List[float]]:
    """
    Calculate RSI for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        window: RSI period
        
    Returns:
        Dictionary with RSI values and dates
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        rsi = ti.calculate_rsi(data, window)
        
        return {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'rsi': rsi.dropna().tolist(),
            'close': data['Close'].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_macd(symbol: str, period: str = "6mo", interval: str = "1d", 
            fast_period: int = 12, slow_period: int = 26, 
            signal_period: int = 9) -> Dict[str, List[float]]:
    """
    Calculate MACD for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
        
    Returns:
        Dictionary with MACD values and dates
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        macd_data = ti.calculate_macd(data, fast_period, slow_period, signal_period)
        
        return {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'macd': macd_data['macd'].dropna().tolist(),
            'signal': macd_data['signal'].dropna().tolist(),
            'histogram': macd_data['histogram'].dropna().tolist(),
            'close': data['Close'].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_bollinger_bands(symbol: str, period: str = "6mo", interval: str = "1d",
                        window: int = 20, num_std: float = 2.0) -> Dict[str, List[float]]:
    """
    Calculate Bollinger Bands for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        window: Moving average period
        num_std: Number of standard deviations
        
    Returns:
        Dictionary with Bollinger Bands values and dates
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        bb_data = ti.calculate_bollinger_bands(data, window, num_std)
        
        return {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'upper': bb_data['upper'].dropna().tolist(),
            'middle': bb_data['middle'].dropna().tolist(),
            'lower': bb_data['lower'].dropna().tolist(),
            'close': data['Close'].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_volatility_analysis(symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, List[float]]:
    """
    Calculate volatility metrics for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        
    Returns:
        Dictionary with volatility metrics and dates
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        
        # Calculate various volatility metrics
        vol_20d = ti.calculate_volatility(data, window=20)
        vol_50d = ti.calculate_volatility(data, window=50)
        atr = ti.calculate_atr(data)
        
        # Calculate daily returns
        data['Returns'] = data['Close'].pct_change()
        
        return {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'volatility_20d': vol_20d.dropna().tolist(),
            'volatility_50d': vol_50d.dropna().tolist(),
            'atr': atr.dropna().tolist(),
            'daily_returns': data['Returns'].dropna().tolist(),
            'close': data['Close'].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_support_resistance(symbol: str, period: str = "1y", interval: str = "1d",
                            window: int = 20) -> Dict[str, List[float]]:
    """
    Find support and resistance levels for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        window: Lookback period for pivot points
        
    Returns:
        Dictionary with support and resistance levels
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        levels = ti.detect_support_resistance(data, window)
        
        
        latest_close = data['Close'].iloc[-1]
        
        return {
            'support_levels': levels['support'],
            'resistance_levels': levels['resistance'],
            'latest_close': float(latest_close)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_trend_analysis(symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, any]:
    """
    Complete trend analysis for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Data period
        interval: Data interval
        
    Returns:
        Dictionary with trend analysis results
    """
    try:
        data = ti.get_stock_data(symbol, period, interval)
        
        # Calculate various trend indicators
        trends = ti.detect_trends(data)
        patterns = ti.calculate_pattern_recognition(data)
        rsi = ti.calculate_rsi(data)
        
        # Detect divergence between price and RSI
        divergences = ti.detect_divergence(data, rsi)
        
        # Filter signals to the last 10 days
        last_10_days = -10
        
        # Compile signals
        signals = []
        dates = data.index[last_10_days:].strftime('%Y-%m-%d').tolist()
        
        for i, date in enumerate(dates):
            idx = i + len(data) + last_10_days
            if idx >= len(data):
                continue
                
            day_signals = []
            
            # Check for trend changes
            if trends['signal'].iloc[idx] == 1:
                day_signals.append("Bullish trend change")
            elif trends['signal'].iloc[idx] == -1:
                day_signals.append("Bearish trend change")
            
            # Check for patterns
            for pattern, signal in patterns.items():
                if signal.iloc[idx] == 1:
                    day_signals.append(f"{pattern.replace('_', ' ').title()} pattern")
            
            # Check for divergences
            if divergences['bullish_divergence'].iloc[idx] == 1:
                day_signals.append("Bullish divergence")
            elif divergences['bearish_divergence'].iloc[idx] == 1:
                day_signals.append("Bearish divergence")
            
            if day_signals:
                signals.append({
                    'date': date,
                    'signals': day_signals
                })
        
        # Determine overall trend
        latest_trend = trends['trend'].iloc[-1]
        if latest_trend > 0:
            overall_trend = "Bullish"
        elif latest_trend < 0:
            overall_trend = "Bearish"
        else:
            overall_trend = "Neutral"
        
        return {
            'overall_trend': overall_trend,
            'signals': signals,
            'trends': trends['trend'].iloc[last_10_days:].tolist(),
            'close': data['Close'].iloc[last_10_days:].tolist(),
            'dates': dates
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_technical_summary(symbol: str) -> Dict[str, any]:
    """
    Generate a complete technical analysis summary for a stock.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with technical analysis summary
    """
    try:
        # Get data with different timeframes
        data_daily = ti.get_stock_data(symbol, period="6mo", interval="1d")
        data_weekly = ti.get_stock_data(symbol, period="2y", interval="1wk")
        latest_price = data_daily['Close'].iloc[-1]
        
        # Calculate indicators
        sma_20 = ti.calculate_moving_average(data_daily, 20).iloc[-1]
        sma_50 = ti.calculate_moving_average(data_daily, 50).iloc[-1]
        sma_200 = ti.calculate_moving_average(data_daily, 200).iloc[-1]
        
        ema_12 = ti.calculate_exponential_moving_average(data_daily, 12).iloc[-1]
        ema_26 = ti.calculate_exponential_moving_average(data_daily, 26).iloc[-1]
        
        rsi_14 = ti.calculate_rsi(data_daily).iloc[-1]
        
        macd_data = ti.calculate_macd(data_daily)
        macd = macd_data['macd'].iloc[-1]
        macd_signal = macd_data['signal'].iloc[-1]
        
        bb_data = ti.calculate_bollinger_bands(data_daily)
        bb_upper = bb_data['upper'].iloc[-1]
        bb_lower = bb_data['lower'].iloc[-1]
        
        volatility = ti.calculate_volatility(data_daily).iloc[-1]
        
        # Support and resistance
        levels = ti.detect_support_resistance(data_daily)
        supports = [level for level in levels['support'] if level < latest_price]
        resistances = [level for level in levels['resistance'] if level > latest_price]
        nearest_support = max(supports) if supports else None
        nearest_resistance = min(resistances) if resistances else None
        
        # Trend analysis
        daily_trend = ti.detect_trends(data_daily)['trend'].iloc[-1]
        weekly_trend = ti.detect_trends(data_weekly)['trend'].iloc[-1]
        
        # Generate signals
        signals = []
        
        # Moving average signals
        if latest_price > sma_20:
            signals.append("Price above SMA(20) - short-term bullish")
        else:
            signals.append("Price below SMA(20) - short-term bearish")
            
        if latest_price > sma_50:
            signals.append("Price above SMA(50) - medium-term bullish")
        else:
            signals.append("Price below SMA(50) - medium-term bearish")
            
        if latest_price > sma_200:
            signals.append("Price above SMA(200) - long-term bullish")
        else:
            signals.append("Price below SMA(200) - long-term bearish")
            
        # Golden/Death cross
        if sma_50 > sma_200 and sma_50.shift(1) <= sma_200.shift(1):
            signals.append("Recent Golden Cross (SMA50 crossed above SMA200) - major bullish signal")
        if sma_50 < sma_200 and sma_50.shift(1) >= sma_200.shift(1):
            signals.append("Recent Death Cross (SMA50 crossed below SMA200) - major bearish signal")
            
            # RSI signals
        if rsi_14 > 70:
            signals.append("RSI above 70 - overbought condition")
        elif rsi_14 < 30:
            signals.append("RSI below 30 - oversold condition")
            
        # MACD signals
        if macd > macd_signal and macd_data['macd'].iloc[-2] <= macd_data['signal'].iloc[-2]:
            signals.append("MACD bullish crossover - buy signal")
        elif macd < macd_signal and macd_data['macd'].iloc[-2] >= macd_data['signal'].iloc[-2]:
            signals.append("MACD bearish crossover - sell signal")
            
        # Bollinger Bands signals
        if latest_price > bb_upper:
            signals.append("Price above upper Bollinger Band - overbought/strong trend")
        elif latest_price < bb_lower:
            signals.append("Price below lower Bollinger Band - oversold/strong trend")
            
        # Bollinger Band squeeze (low volatility, potential breakout)
        band_width = (bb_upper - bb_lower) / bb_middle
        avg_band_width = ((data_daily['High'] - data_daily['Low']) / data_daily['Close']).rolling(20).mean().iloc[-1]
        
        if band_width < 0.7 * avg_band_width:
            signals.append("Bollinger Band squeeze - low volatility, potential breakout")
            
        # Determine overall bias based on multiple timeframes
        if daily_trend > 0 and weekly_trend > 0:
            overall_bias = "Strong Bullish"
        elif daily_trend > 0 and weekly_trend <= 0:
            overall_bias = "Moderately Bullish"
        elif daily_trend <= 0 and weekly_trend > 0:
            overall_bias = "Neutral with Bullish Bias"
        else:
            overall_bias = "Bearish"
            
        # Format results for return
        return {
            'symbol': symbol,
            'last_price': float(latest_price),
            'overall_bias': overall_bias,
            'signals': signals,
            'indicators': {
                'sma_20': float(sma_20),
                'sma_50': float(sma_50), 
                'sma_200': float(sma_200),
                'ema_12': float(ema_12),
                'ema_26': float(ema_26),
                'rsi_14': float(rsi_14),
                'macd': float(macd),
                'macd_signal': float(macd_signal),
                'bb_upper': float(bb_upper),
                'bb_middle': float(bb_middle),
                'bb_lower': float(bb_lower),
                'volatility_annualized': float(volatility * 100)  # Convert to percentage
            },
            'support_resistance': {
                'nearest_support': float(nearest_support) if nearest_support else None,
                'nearest_resistance': float(nearest_resistance) if nearest_resistance else None
            }
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.resource("stock://{symbol}")
def stock_resource(symbol: str) -> str:
    """
    Expose stock price data as a resource.
    Returns a formatted string with the current stock price.
    """
    try:
        price = get_stock_price(symbol)
        return f"The current price of {symbol.upper()} is ${price:.2f}"
    except ValueError as e:
        return f"[{symbol.upper()}] Error: {e}"

@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """
    Retrieve historical stock data in CSV format.
    """
    symbol = symbol.upper()
    try:
        ticker = fetch_ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            return f"[{symbol}] No historical data found for period '{period}'."
        return data.to_csv()
    except Exception as e:
        return f"[{symbol}] Error fetching historical data: {e}"

@mcp.tool()
def compare_stocks(symbol1: str, symbol2: str) -> str:
    """
    Compare two stock prices.
    """
    symbol1, symbol2 = symbol1.upper(), symbol2.upper()
    try:
        price1 = get_stock_price(symbol1)
        price2 = get_stock_price(symbol2)
        if price1 > price2:
            return f"{symbol1} (${price1:.2f}) is higher than {symbol2} (${price2:.2f})."
        elif price1 < price2:
            return f"{symbol1} (${price1:.2f}) is lower than {symbol2} (${price2:.2f})."
        else:
            return f"{symbol1} and {symbol2} have the same price (${price1:.2f})."
    except Exception as e:
        return f"Error comparing stocks: {e}"
    

# --- Watchlist Management ---
@mcp.tool()
def add_to_watchlist(symbol: str) -> str:
    symbol = symbol.upper()
    watchlist.add(symbol)
    return f"[Watchlist] Added {symbol}."

@mcp.tool()
def remove_from_watchlist(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol in watchlist:
        watchlist.remove(symbol)
        return f"[Watchlist] Removed {symbol}."
    return f"[Watchlist] {symbol} was not in the list."

@mcp.tool()
def get_watchlist() -> list:
    return sorted(watchlist)

@mcp.tool()
def get_watchlist_prices() -> dict:
    """
    Get the most recent prices for all stocks in the watchlist.
    """
    prices = {}
    for symbol in sorted(watchlist):
        try:
            prices[symbol] = round(get_stock_price(symbol), 2)
        except Exception as e:
            prices[symbol] = f"Error: {e}"
    return prices


# --- Simulated Real-Time Updates ---
def update_prices():
    """
    Background thread to update watchlist prices every 30 seconds.
    """
    while True:
        for symbol in list(watchlist):  # Use list to avoid set size change errors
            try:
                ticker = fetch_ticker(symbol)
                watchlist_prices[symbol] = round(safe_get_price(ticker), 2)
            except Exception as e:
                watchlist_prices[symbol] = f"Error: {e}"
        time.sleep(30)

@mcp.tool()
def get_realtime_watchlist_prices() -> dict:
    """
    Get real-time cached prices from the background updater.
    """
    return dict(sorted(watchlist_prices.items()))



@mcp.tool()
def analyze_stock(ticker):
    """
    Perform 1-month trend analysis for any stock ticker.
    
    Parameters:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    """
    # Download 1-month daily stock data
    df = yf.download(ticker, period='1mo', interval='1d')
    df.dropna(inplace=True)

    # Moving Averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (Moving Average Convergence Divergence)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Get latest values
    latest = df.iloc[-1]
    summary = {
        "Latest Close": latest['Close'],
        "20-Day MA": latest['MA20'],
        "50-Day MA": latest['MA50'],
        "RSI": latest['RSI'],
        "MACD": latest['MACD'],
        "Signal Line": latest['Signal']
    }

    # Print summary
    print(f"\n📊 Trend Analysis for {ticker.upper()} (Past 1 Month):")
    for key, value in summary.items():
        print(f"{key}: {value:.2f}")

    # Plot charts
    plt.figure(figsize=(14, 8))

    # Close Price & MAs
    plt.subplot(3, 1, 1)
    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['MA20'], label='20-Day MA')
    plt.plot(df['MA50'], label='50-Day MA', linestyle='--')
    plt.title(f"{ticker.upper()} - Price & Moving Averages")
    plt.legend()

    # RSI
    plt.subplot(3, 1, 2)
    plt.plot(df['RSI'], label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--', label='Overbought')
    plt.axhline(30, color='green', linestyle='--', label='Oversold')
    plt.title("Relative Strength Index (RSI)")
    plt.legend()

    # MACD
    plt.subplot(3, 1, 3)
    plt.plot(df['MACD'], label='MACD', color='blue')
    plt.plot(df['Signal'], label='Signal Line', color='orange')
    plt.title("MACD & Signal Line")
    plt.legend()

    plt.tight_layout()
    plt.show()


# --- Start the background price update thread ---
price_update_thread = threading.Thread(target=update_prices, daemon=True)
price_update_thread.start()

# Run the server
if __name__ == "__main__":
    mcp.run()
