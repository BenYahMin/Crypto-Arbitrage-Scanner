# 🚀 Crypto Arbitrage Scanner

A sophisticated Python-based cryptocurrency arbitrage scanner that identifies profitable trading opportunities across multiple exchanges with real-time liquidity analysis.
Still working on the liquidity though

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

## 📋 Table of Contents
- [Features](#features)
- [Supported Exchanges](#supported-exchanges)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Output Example](#output-example)
- [Risk Disclaimer](#risk-disclaimer)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔍 Arbitrage Detection
- **Multi-exchange scanning** across Binance, Kraken, and Coinbase
- **Real-time price comparison** with sub-second updates
- **Profit calculation** including fees and slippage
- **Customizable thresholds** for minimum profit percentages

### 💧 Liquidity Analysis
- **Order book depth analysis** at multiple levels
- **Slippage estimation** for different trade sizes
- **Liquidity scoring** (0-100%) for each opportunity
- **Volume validation** with minimum thresholds

### ⚡ Performance
- **Concurrent API calls** using ThreadPoolExecutor
- **Configurable scan intervals** for continuous monitoring
- **Error resilience** with robust exception handling
- **Memory efficient** with optimized data structures

## 🏪 Supported Exchanges

| Exchange | Status | Pairs | API Rate Limit |
|----------|--------|-------|----------------|
| Binance | ✅ Active | USDT pairs | 1200 requests/min |
| Kraken | ✅ Active | USD/USDT pairs | 180 requests/min |
| Coinbase | ✅ Active | USD/USDT pairs | 300 requests/min |

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/BenYahMin/crypto-arbitrage-scanner.git
   cd crypto-arbitrage-scanner
   Still working on the code dropping soon
