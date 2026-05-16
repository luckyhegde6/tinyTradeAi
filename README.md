# TinyTrade AI

TinyTrade AI is a lightweight Edge AI Market Intelligence Terminal built specifically for ultra-low-power ARM devices like the **Orange Pi 2G-IOT** (256MB RAM). It fetches live crypto and stock market data, performs sentiment analysis on financial news using lightweight NLP, detects volatility anomalies via Z-score analysis, and displays it all on a 0.96-inch OLED screen. It also serves a low-footprint Flask API.

## Features
- **Live Market OLED Ticker:** Displays BTC, ETH, and NIFTY 50 prices.
- **AI Sentiment Analysis:** Uses VADER and TextBlob to analyze financial RSS feeds without heavy ML models.
- **Volatility Engine:** Calculates Z-scores on rolling price windows to detect anomalies.
- **Lightweight API:** Exposes endpoints `/prices`, `/sentiment`, and `/alerts` via Flask.
- **Low Memory Footprint:** Specifically engineered to avoid Pandas, Transformers, and large databases. Uses raw `requests`, `sqlite3`, and minimal memory queues.

## Hardware Requirements
- **Board:** Orange Pi 2G-IOT (or any Raspberry Pi / Linux SBC).
- **Display:** 0.96-inch I2C OLED Display (SSD1306).
- **RAM:** Designed to run on as little as 256MB.

## Wiring Diagram (I2C OLED)
Connect the 4-pin SSD1306 OLED to the Orange Pi GPIO pins:

| OLED Pin | Orange Pi 2G-IOT Pin |
|----------|----------------------|
| **VCC**  | 3.3V (Pin 1 or 17)   |
| **GND**  | Ground (Pin 6 or 9)  |
| **SCL**  | I2C SCL (Pin 5)      |
| **SDA**  | I2C SDA (Pin 3)      |

*(Note: Verify pinouts with your specific OS image, usually I2C-0 is mapped to pins 3 and 5).*

## Setup Guide

### 1. Enable I2C on Orange Pi
Ensure I2C is enabled in your Armbian/Debian OS.
```bash
sudo apt-get update
sudo apt-get install i2c-tools python3-dev python3-pip libfreetype6-dev libjpeg-dev build-essential
```
Verify the display is detected (look for `3c` in the output):
```bash
sudo i2cdetect -y 0
```

### 2. Clone and Install
```bash
git clone https://github.com/luckyhegde6/TinyTradeAi.git
cd TinyTradeAi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

### 4. Setup as an Auto-start Service
We provide a systemd service file to automatically start TinyTrade on boot.
```bash
sudo cp scripts/tinytrade.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tinytrade.service
sudo systemctl start tinytrade.service
```

## API Endpoints
- `GET /status` : Check system status
- `GET /prices` : Get current prices of tracked assets
- `GET /price/<symbol>` : Get price for a specific asset
- `GET /sentiment` : Get recent AI sentiment analysis history
- `GET /alerts` : Get recent market anomaly alerts

## Architecture
See the source code for our highly modular architecture separated into `fetchers`, `ai`, `oled`, `database`, and `api` folders.

## License
MIT License
