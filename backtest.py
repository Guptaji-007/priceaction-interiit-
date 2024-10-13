import yfinance as yf
import pandas as pd
# this code is for the backtesting of the intraday(pat).py 
# there are few changes made in this file the timeframe for the candlestick is now set for 15min
# the previous code was meant to detect the live data during the traing day of candle duration of 2 min 
# however the motive was to detect the candlestick pattern which can even be detected here.


# Function to calculate Support and Resistance levels
def supp_resis(data, lookback=20):
    data['Support'] = data['Low'].rolling(window=lookback).min()
    data['Resistance'] = data['High'].rolling(window=lookback).max()
    return data

# Functions to detect candlestick patterns
def bullish_engulfing(candle, prev_candle, sma):
    return (prev_candle['Close'] < prev_candle['Open'] and
            candle['Close'] > candle['Open'] and
            candle['Open'] < prev_candle['Close'] and
            candle['Close'] > prev_candle['Open'] and
            candle['Close'] > sma)

def bearish_engulfing(candle, prev_candle, sma):
    return (prev_candle['Close'] > prev_candle['Open'] and
            candle['Close'] < candle['Open'] and
            candle['Open'] > prev_candle['Close'] and
            candle['Close'] < prev_candle['Open'] and
            candle['Close'] < sma)

def hammer(candle, support, resistance):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    return (lower_shadow > 2 * body and 
            upper_shadow < 0.2 * body and 
            candle['Close'] > support and 
            candle['Close'] < resistance)

def inverted_hammer(candle, support, resistance):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
    return (upper_shadow > 2 * body and 
            lower_shadow < 0.1 * body and 
            candle['Close'] > support and 
            candle['Close'] < resistance)

def shooting_star(candle):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
    return upper_shadow > 2 * body and lower_shadow < 0.1 * body

def dragonfly_doji(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    return body <= 0.01 * candle['Close'] and lower_shadow > 2 * body and upper_shadow < body

def gravestone_doji(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Low'] - min(candle['Open'], candle['Close'])
    upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
    return body <= 0.01 * candle['Close'] and upper_shadow > 2 * body and lower_shadow < body

# Function to calculate SMA
def sma(data, period):
    return data['Close'].rolling(window=period).mean()

# Function to analyze stock data and detect patterns
def analyze_stock(symbol):
    stock_data = yf.download(tickers=symbol, start="2024-10-09", end="2024-10-10", interval='15m')
    stock_data['SMA'] = sma(stock_data, period=5)
    stock_data = supp_resis(stock_data)  # Calculate support and resistance levels

    results = []

    for i in range(1, len(stock_data)):
        current_candle = stock_data.iloc[i]
        previous_candle = stock_data.iloc[i - 1]

        patterns_detected = []

        # Check for various patterns
        if hammer(current_candle, stock_data['Support'].iloc[i], stock_data['Resistance'].iloc[i]):
            patterns_detected.append('Hammer')

        if inverted_hammer(current_candle, stock_data['Support'].iloc[i], stock_data['Resistance'].iloc[i]):
            patterns_detected.append('Inverted Hammer')

        if shooting_star(current_candle):
            patterns_detected.append('Shooting Star')

        if dragonfly_doji(current_candle):
            patterns_detected.append('Dragonfly Doji')

        if gravestone_doji(current_candle):
            patterns_detected.append('Gravestone Doji')

        if bullish_engulfing(current_candle, previous_candle, previous_candle['SMA']):
            patterns_detected.append('Bullish Engulfing')

        if bearish_engulfing(current_candle, previous_candle, previous_candle['SMA']):
            patterns_detected.append('Bearish Engulfing')

        if patterns_detected:
            # Track next 10 candles, if available
            next_candles = stock_data.iloc[i+1:i+11]  # Get the next 10 candles if they exist
            
            # If fewer than 10 candlesticks exist, take what is available
            if len(next_candles) > 0:
                next_close_value = next_candles['Close'].iloc[-1]  # Get the last close value of the available next candles
            else:
                next_close_value = None  # No further data available
            
            results.append({
                'Date': current_candle.name.date(),
                'Patterns Detected': ', '.join(patterns_detected),
                'Open': current_candle['Open'],
                'Close': current_candle['Close'],
                'Next Close Value after 10 candlesticks': next_close_value
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    return results_df


symbol = "MARUTI.NS"  
pattern_results = analyze_stock(symbol)

print(pattern_results)
