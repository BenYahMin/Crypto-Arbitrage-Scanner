import requests
import time
import pandas as pd
from typing import Dict, List, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor

class CryptoArbitrageScanner:
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3/ticker/bookTicker',
            'kraken': 'https://api.kraken.com/0/public/Ticker',
            'coinbase': 'https://api.exchange.coinbase.com/products',
        }
        
        self.common_pairs = [
            'BTC-USDT', 'ETH-USDT', 'ADA-USDT', 'DOT-USDT', 'LINK-USDT',
            'BTC-USD', 'ETH-USD'
        ]
        
    def get_binance_prices(self) -> Dict:
        """Fetch prices from Binance"""
        try:
            response = requests.get(self.exchanges['binance'], timeout=5)
            data = response.json()
            prices = {}
            for item in data:
                symbol = item['symbol']
                if symbol.endswith('USDT'):
                    # Convert BTCUSDT to BTC-USDT format
                    base_currency = symbol.replace('USDT', '')
                    normalized_symbol = f"{base_currency}-USDT"
                    prices[normalized_symbol] = {
                        'bid': float(item['bidPrice']),
                        'ask': float(item['askPrice'])
                    }
            return prices
        except Exception as e:
            print(f"Binance error: {e}")
            return {}
    
    def get_kraken_prices(self) -> Dict:
        """Fetch prices from Kraken"""
        try:
            response = requests.get(self.exchanges['kraken'], timeout=5)
            data = response.json()['result']
            prices = {}
            for pair, info in data.items():
                # Normalize Kraken pairs (XBT = BTC)
                normalized_pair = pair.replace('XBT', 'BTC').replace('XXBT', 'BTC')
                if 'USDT' in normalized_pair or 'USD' in normalized_pair:
                    # Format as BTC-USDT
                    base_currency = normalized_pair.replace('USDT', '').replace('USD', '')
                    final_symbol = f"{base_currency}-USDT" if 'USDT' in normalized_pair else f"{base_currency}-USD"
                    prices[final_symbol] = {
                        'bid': float(info['b'][0]),
                        'ask': float(info['a'][0])
                    }
            return prices
        except Exception as e:
            print(f"Kraken error: {e}")
            return {}
    
    def get_coinbase_prices(self) -> Dict:
        """Fetch prices from Coinbase"""
        try:
            response = requests.get(self.exchanges['coinbase'], timeout=10)
            products = response.json()
            prices = {}
            
            for product in products[:50]:  # Limit to first 50 products
                if product['quote_currency'] in ['USDT', 'USD']:
                    symbol = f"{product['base_currency']}-{product['quote_currency']}"
                    # Get ticker data for this product
                    ticker_url = f"https://api.exchange.coinbase.com/products/{product['id']}/ticker"
                    try:
                        ticker_response = requests.get(ticker_url, timeout=5)
                        ticker_data = ticker_response.json()
                        prices[symbol] = {
                            'bid': float(ticker_data.get('bid', 0)),
                            'ask': float(ticker_data.get('ask', 0))
                        }
                    except Exception as e:
                        continue  # Skip if we can't get ticker data
            return prices
        except Exception as e:
            print(f"Coinbase error: {e}")
            return {}
    
    def calculate_arbitrage_opportunity(self, exchange1_bid: float, exchange2_ask: float) -> float:
        """Calculate arbitrage percentage"""
        if exchange2_ask == 0:
            return 0
        return ((exchange1_bid - exchange2_ask) / exchange2_ask) * 100
    
    def scan_arbitrage(self):
        """Main arbitrage scanning function"""
        print("Scanning for arbitrage opportunities...")
        print("-" * 80)
        
        # Get prices from all exchanges
        with ThreadPoolExecutor(max_workers=3) as executor:
            binance_future = executor.submit(self.get_binance_prices)
            kraken_future = executor.submit(self.get_kraken_prices)
            coinbase_future = executor.submit(self.get_coinbase_prices)
            
            binance_prices = binance_future.result()
            kraken_prices = kraken_future.result()
            coinbase_prices = coinbase_future.result()
        
        opportunities = []
        
        # Check arbitrage between exchanges
        exchanges_data = {
            'binance': binance_prices,
            'kraken': kraken_prices,
            'coinbase': coinbase_prices
        }
        
        exchange_names = list(exchanges_data.keys())
        
        for i in range(len(exchange_names)):
            for j in range(i + 1, len(exchange_names)):
                exch1 = exchange_names[i]
                exch2 = exchange_names[j]
                
                prices1 = exchanges_data[exch1]
                prices2 = exchanges_data[exch2]
                
                # Find common pairs between exchanges
                common_pairs = set(prices1.keys()) & set(prices2.keys())
                
                for pair in common_pairs:
                    if pair in prices1 and pair in prices2:
                        # Buy on exchange2, sell on exchange1
                        arb_percent1 = self.calculate_arbitrage_opportunity(
                            prices1[pair]['bid'], prices2[pair]['ask']
                        )
                        
                        # Buy on exchange1, sell on exchange2
                        arb_percent2 = self.calculate_arbitrage_opportunity(
                            prices2[pair]['bid'], prices1[pair]['ask']
                        )
                        
                        # Consider fees (approximately 0.2% per trade = 0.4% round trip)
                        effective_threshold = 0.5  # 0.5% after fees
                        
                        if arb_percent1 > effective_threshold:
                            opportunities.append({
                                'pair': pair,
                                'action': f"Buy on {exch2.upper()}, Sell on {exch1.upper()}",
                                'profit_percent': round(arb_percent1, 2),
                                'buy_price': prices2[pair]['ask'],
                                'sell_price': prices1[pair]['bid'],
                                'exchanges': f"{exch2} → {exch1}"
                            })
                        
                        if arb_percent2 > effective_threshold:
                            opportunities.append({
                                'pair': pair,
                                'action': f"Buy on {exch1.upper()}, Sell on {exch2.upper()}",
                                'profit_percent': round(arb_percent2, 2),
                                'buy_price': prices1[pair]['ask'],
                                'sell_price': prices2[pair]['bid'],
                                'exchanges': f"{exch1} → {exch2}"
                            })
        
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        
        # Display results
        if opportunities:
            print(f"\n🚀 Found {len(opportunities)} arbitrage opportunities:")
            print("=" * 80)
            for opp in opportunities[:10]:  # Show top 10
                print(f"💰 {opp['pair']}")
                print(f"   Action: {opp['action']}")
                print(f"   Profit: {opp['profit_percent']}%")
                print(f"   Buy at: ${opp['buy_price']:.4f} | Sell at: ${opp['sell_price']:.4f}")
                print(f"   Route: {opp['exchanges']}")
                print("-" * 50)
        else:
            print("❌ No significant arbitrage opportunities found.")
    
    def continuous_scan(self, interval: int = 30):
        """Run continuous arbitrage scanning"""
        print(f"Starting continuous arbitrage scanning (interval: {interval}s)")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                self.scan_arbitrage()
                print(f"\n⏰ Next scan in {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Scanner stopped by user.")

# Advanced version with more features
class AdvancedArbitrageScanner(CryptoArbitrageScanner):
    def __init__(self):
        super().__init__()
        self.opportunity_history = []
        self.min_profit_threshold = 0.5  # Minimum profit percentage
    
    def calculate_trading_fees(self, exchange: str, volume: float = 1000) -> float:
        """Estimate trading fees for different exchanges"""
        fee_rates = {
            'binance': 0.001,  # 0.1%
            'kraken': 0.0026,  # 0.26%
            'coinbase': 0.005,  # 0.5%
        }
        return fee_rates.get(exchange, 0.002) * volume
    
    def save_opportunities_to_csv(self, filename: str = 'arbitrage_opportunities.csv'):
        """Save found opportunities to CSV file"""
        if self.opportunity_history:
            df = pd.DataFrame(self.opportunity_history)
            df.to_csv(filename, index=False)
            print(f"💾 Opportunities saved to {filename}")

# Real-time scanner (now defined AFTER AdvancedArbitrageScanner)
class RealTimeArbitrageScanner(AdvancedArbitrageScanner):
    def __init__(self):
        super().__init__()
        self.realtime_prices = {}
        
    def start_real_time_monitoring(self):
        """Placeholder for real-time monitoring"""
        print("Real-time monitoring would be implemented with WebSockets")
        print("This requires more complex setup with exchange-specific WebSocket APIs")

# Simple usage function
def main():
    """Main function to run the scanner"""
    print("🚀 Crypto Arbitrage Scanner Starting...")
    print("Initializing scanner...")
    
    # Use the basic scanner for simplicity
    scanner = CryptoArbitrageScanner()
    
    while True:
        try:
            print("\n" + "="*50)
            print("CRYPTO ARBITRAGE SCANNER")
            print("="*50)
            print("1. Single Scan")
            print("2. Continuous Scan (30s intervals)")
            print("3. Exit")
            print("-"*50)
            
            choice = input("Choose option (1-3): ").strip()
            
            if choice == '1':
                print("\nRunning single scan...")
                scanner.scan_arbitrage()
                
            elif choice == '2':
                try:
                    interval = int(input("Enter scan interval in seconds (default 30): ") or "30")
                    scanner.continuous_scan(interval)
                except ValueError:
                    print("Invalid interval. Using default 30 seconds.")
                    scanner.continuous_scan(30)
                    
            elif choice == '3':
                print("👋 Thank you for using Crypto Arbitrage Scanner!")
                break
                
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Scanner stopped by user.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Trying again...")

if __name__ == "__main__":
    main()