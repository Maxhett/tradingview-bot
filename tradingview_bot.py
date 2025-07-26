import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "TradingView Bot Running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    return jsonify({
        "symbol": "BTCUSDT",
        "signal": "HOLD",
        "price": 42000,
        "recommendation": "NEUTRAL"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)