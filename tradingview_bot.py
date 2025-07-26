import os
from flask import Flask, jsonify, request
from datetime import datetime

try:
    from tradingview_ta import TA_Handler, Interval, Exchange
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False

app = Flask(__name__)

INTERVALS = {
    '1m': Interval.INTERVAL_1_MINUTE if TRADINGVIEW_AVAILABLE else None,
    '5m': Interval.INTERVAL_5_MINUTES if TRADINGVIEW_AVAILABLE else None,
    '15m': Interval.INTERVAL_15_MINUTES if TRADINGVIEW_AVAILABLE else None,
    '1h': Interval.INTERVAL_1_HOUR if TRADINGVIEW_AVAILABLE else None,
    '4h': Interval.INTERVAL_4_HOURS if TRADINGVIEW_AVAILABLE else None,
    '1d': Interval.INTERVAL_1_DAY if TRADINGVIEW_AVAILABLE else None
}

@app.route('/')
def home():
    return jsonify({
        "message": "TradingView Bot Running",
        "version": "2.0",
        "tradingview_enabled": TRADINGVIEW_AVAILABLE
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "tradingview": TRADINGVIEW_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    if request.method == 'GET':
        # Für Browser-Tests
        return jsonify({
            "info": "Use POST method with JSON body",
            "example": {"symbol": "BTCUSDT", "interval": "1h"}
        })
    
    data = request.json or {}
    symbol = data.get('symbol', 'BTCUSDT')
    interval = data.get('interval', '1h')
    exchange = data.get('exchange', 'BINANCE')
    
    if not TRADINGVIEW_AVAILABLE:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "signal": "HOLD",
            "mode": "demo",
            "error": "TradingView not available"
        })
    
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener="crypto",
            interval=INTERVALS.get(interval, Interval.INTERVAL_1_HOUR)
        )
        
        analysis = handler.get_analysis()
        summary = analysis.summary
        indicators = analysis.indicators
        
        recommendation = summary['RECOMMENDATION']
        buy_count = summary.get('BUY', 0)
        sell_count = summary.get('SELL', 0)
        neutral_count = summary.get('NEUTRAL', 0)
        total = buy_count + sell_count + neutral_count
        
        if 'BUY' in recommendation:
            signal = 'BUY'
            confidence = (buy_count / total * 100) if total > 0 else 0
        elif 'SELL' in recommendation:
            signal = 'SELL'
            confidence = (sell_count / total * 100) if total > 0 else 0
        else:
            signal = 'HOLD'
            confidence = (neutral_count / total * 100) if total > 0 else 50
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "signal": signal,
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
            "current_price": indicators.get('close'),
            "analysis": {
                "buy_signals": buy_count,
                "sell_signals": sell_count,
                "neutral_signals": neutral_count
            },
            "indicators": {
                "rsi": indicators.get('RSI'),
                "macd": indicators.get('MACD.macd'),
                "sma_20": indicators.get('SMA20'),
                "ema_20": indicators.get('EMA20')
            }
        })
        
    except Exception as e:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "error": str(e),
            "mode": "error"
        }), 500

@app.route('/supported')
def supported():
    return jsonify({
        "crypto": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"],
        "intervals": list(INTERVALS.keys()),
        "tradingview_enabled": TRADINGVIEW_AVAILABLE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
