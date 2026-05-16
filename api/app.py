from flask import Flask, jsonify
from database.db import get_market_data, get_recent_sentiment, get_recent_alerts

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "device": "TinyTrade AI"})

@app.route('/price/<symbol>', methods=['GET'])
def price(symbol):
    data = get_market_data(symbol.upper())
    if data:
        return jsonify(data)
    return jsonify({"error": "Symbol not found"}), 404

@app.route('/prices', methods=['GET'])
def all_prices():
    data = get_market_data()
    return jsonify(data)

@app.route('/sentiment', methods=['GET'])
def sentiment():
    data = get_recent_sentiment(10)
    return jsonify(data)

@app.route('/alerts', methods=['GET'])
def alerts():
    data = get_recent_alerts(10)
    return jsonify(data)

def start_flask(host='0.0.0.0', port=5000):
    # Running in threaded mode is important so we don't block
    app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
