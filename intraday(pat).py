import yfinance as yf
import time
import pandas as pd

# DataFrame to stire the results
result = pd.DataFrame(columns=['Symbol', 'Date', 'Pattern', 'Open', 'Close', 'Price Movement', 'Profit/Loss'])


# calculate Support and Resistance 
# looks at last 20 candle sticks and get min for support and max for resistance
def supp_resis(data, lookback=20):
    data['Support'] = data['Low'].rolling(window=lookback).min()
    data['Resistance'] = data['High'].rolling(window=lookback).max()
    return data


# detect Hammer pattern with support and volume confirmation
# A hammer is a price pattern in candlestick charting that occurs when a security trades significantly lower than its opening, but rallies within the period to close near the opening price.

def hammer(candle, avg_volume, support):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    
    # Volume confirmation: volume > average volume
    # Support confirmation: Close price is near the support level
    return (lower_shadow > 2 * body and upper_shadow < 0.2 * body and body < 0.15 * (candle['High'] - candle['Low']) 
            and candle['Volume'] > avg_volume and candle['Close'] <= support * 1.02)

# detect Inverted Hammer pattern with resistance and volume confirmation
# The Inverted Hammer candlestick formation occurs mainly at the bottom of downtrends and can act as a warning of a potential bullish reversal pattern.
def inverted_hammer(candle, avg_volume, resistance):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
    
    # Volume confirmation: volume > average volume
    # Resistance confirmation: Close price is near the resistance level
    return (upper_shadow > 2 * body and lower_shadow < 0.1 * body and body < 0.15 * (candle['High'] - candle['Low']) 
            and candle['Volume'] > avg_volume and candle['Close'] >= resistance * 0.98)

# detect Shooting Star pattern:A shooting star is a reversal candlestick pattern that forms after an uptrend. 
def shooting_star(candle):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
    
    return upper_shadow > 2 * body and lower_shadow < 0.1 * body and body < 0.15 * (candle['High'] - candle['Low'])


# detect Dragonfly Doji pattern:A Dragonfly Doji is a type of candlestick pattern that can signal a potential price reversal, either to the downside or upside, depending on past price action.
def dragonfly_doji(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    
    return body <= 0.01 * candle['Close'] and lower_shadow > 2 * body and upper_shadow < body

# Function to detect Gravestone Doji pattern:A gravestone doji is a bearish reversal candlestick pattern formed when the open, low, and closing prices are all near each other with a long upper shadow.
def gravestone_doji(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    
    return body <= 0.01 * candle['Close'] and upper_shadow > 2 * body and lower_shadow < body

# Bullish Engulfing pattern with SMA confirmation
def bullish_engulfing(candle, prev_candle, sma):
    return prev_candle['Close'] < prev_candle['Open'] and candle['Close'] > candle['Open'] and candle['Open'] < prev_candle['Close'] and candle['Close'] > prev_candle['Open'] and candle['Close'] > sma

# Bearish Engulfing pattern with SMA confirmation
def bearish_engulfing(candle, prev_candle, sma):
    return prev_candle['Close'] > prev_candle['Open'] and candle['Close'] < candle['Open'] and candle['Open'] > prev_candle['Close'] and candle['Close'] < prev_candle['Open'] and candle['Close'] < sma



# Function to log detected patterns
def log_pattern(symbol, candle, pattern_name):
    global result
    result = result.append({
        'Symbol': symbol,
        'Date': candle.name,
        'Pattern': pattern_name,
        'Open': candle['Open'],
        'Close': candle['Close'],
        'Price Movement': None, 
        'Profit/Loss': None  
    }, ignore_index=True)

# evaluate price movement after pattern detection
def evaluate_price_movement(symbol, latest_candle):
    # Fetch the price data for the next specified intervals (e.g., 5 minutes)
    future_data = yf.download(tickers=symbol, period='1d', interval='2m')

    # price movement for the next 5 intervals (10 minutes)
    last_price = latest_candle['Close']
    future_prices = future_data['Close'].iloc[-5:]  # Get the next 5 intervals

    price_change = future_prices.values - last_price
    avg_movement = price_change.mean()
    result.loc[result['Date'] == latest_candle.name, 'Price Movement'] = avg_movement

    # calculate Profit/Loss based on average movement
    result.loc[result['Date'] == latest_candle.name, 'Profit/Loss'] = "Profit" if avg_movement > 0 else "Loss"

    print(f"Price Movement for {symbol} after pattern detection: {avg_movement}, Result: {result.loc[result['Date'] == latest_candle.name, 'Profit/Loss'].values[0]}")

# Function to detect patterns with indicators
def detect_patterns(symbol):
    while True:
        stock_data = yf.download(tickers=symbol, period='1d', interval='2m')
        stock_data = supp_resis(stock_data) # calculate Support and Resistance levels
        stock_data['SMA'] = stock_data['Close'].rolling(window=20).mean()   # calculate SMA (20-period) for trend confirmation

        latest_candle = stock_data.iloc[-1]  # Get the latest candle
        prev_candle = stock_data.iloc[-2]  # Get the previous candle        
        avg_volume = stock_data['Volume'].rolling(window=10).mean().iloc[-1] # Calculate the average volume over the last 10 periods
        support = latest_candle['Support']
        resistance = latest_candle['Resistance']

        print(latest_candle) # Print the latest candle data 
        # Check for candlestick patterns
        
        pattern_found = False
        if hammer(latest_candle, avg_volume, support):
            print(f"Hammer detected for {symbol} at {latest_candle.name} near support level {support}")
            log_pattern(symbol, latest_candle, 'Hammer')
            pattern_found = True

        if inverted_hammer(latest_candle, avg_volume, resistance):
            print(f"Inverted Hammer detected for {symbol} at {latest_candle.name} near resistance level {resistance}")
            log_pattern(symbol, latest_candle, 'Inverted Hammer')
            pattern_found = True
            
        if shooting_star(latest_candle):
            print(f"Shooting Star detected for {symbol} at {latest_candle.name}")
            log_pattern(symbol, latest_candle, 'Shooting Star')
            pattern_found = True
            
        if dragonfly_doji(latest_candle):
            print(f"Dragonfly Doji detected for {symbol} at {latest_candle.name}")
            log_pattern(symbol, latest_candle, 'Dragonfly Doji')
            pattern_found = True
            
        if gravestone_doji(latest_candle):
            print(f"Gravestone Doji detected for {symbol} at {latest_candle.name}")
            log_pattern(symbol, latest_candle, 'Gravestone Doji')
            pattern_found = True
            
        if bullish_engulfing(latest_candle, prev_candle, latest_candle['SMA']):
            print(f"Bullish Engulfing detected for {symbol} at {latest_candle.name}")
            log_pattern(symbol, latest_candle, 'Bullish Engulfing')
            pattern_found = True
            
        if bearish_engulfing(latest_candle, prev_candle, latest_candle['SMA']):
            print(f"Bearish Engulfing detected for {symbol} at {latest_candle.name}")
            log_pattern(symbol, latest_candle, 'Bearish Engulfing')
            pattern_found = True

        print(f"Support Level: {latest_candle['Support']}, Resistance Level: {latest_candle['Resistance']}")
        if pattern_found:
            evaluate_price_movement(symbol, latest_candle)

        if not pattern_found:
            print(f"No significant candlestick pattern detected for {symbol} at {latest_candle.name}")

        print("Wait for next candle stick--->")
        time.sleep(120)

# Test the function
detect_patterns("RELIANCE.NS")
# write the name of the company you need to test for.
