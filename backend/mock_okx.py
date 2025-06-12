#!/usr/bin/env python3
"""
Mock OKX Exchange for testing when real OKX API is not accessible
"""
import json
from typing import Dict, Any
from datetime import datetime
import random

class MockOKXExchange:
    """Mock OKX exchange for testing purposes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.apiKey = config.get('apiKey')
        self.secret = config.get('secret') 
        self.passphrase = config.get('passphrase')
        self.sandbox = config.get('sandbox', False)
        self.id = 'okex'
        
        # Validate required credentials
        if not all([self.apiKey, self.secret, self.passphrase]):
            raise Exception("Missing required OKX credentials (apiKey, secret, passphrase)")
        
        print(f"✅ Mock OKX Exchange initialized (sandbox: {self.sandbox})")
        print(f"   API Key: {self.apiKey[:10]}...")
        print(f"   Has Secret: {bool(self.secret)}")
        print(f"   Has Passphrase: {bool(self.passphrase)}")
    
    async def fetch_balance(self) -> Dict:
        """Mock balance response"""
        print("🔄 Fetching mock balance...")
        
        # Simulate API authentication check
        if not self._validate_credentials():
            raise Exception("Invalid API credentials")
        
        # Mock balance data
        balance = {
            'info': {},
            'BTC': {'free': 0.001, 'used': 0.0, 'total': 0.001},
            'USDT': {'free': 100.0, 'used': 0.0, 'total': 100.0},
            'ETH': {'free': 0.05, 'used': 0.0, 'total': 0.05},
            'free': {'BTC': 0.001, 'USDT': 100.0, 'ETH': 0.05},
            'used': {'BTC': 0.0, 'USDT': 0.0, 'ETH': 0.0},
            'total': {'BTC': 0.001, 'USDT': 100.0, 'ETH': 0.05}
        }
        
        print("✅ Mock balance fetched successfully")
        return balance
    
    async def fetch_ticker(self, symbol: str) -> Dict:
        """Mock ticker response"""
        print(f"🔄 Fetching mock ticker for {symbol}...")
        
        # Simulate API authentication check
        if not self._validate_credentials():
            raise Exception("Invalid API credentials")
        
        # Mock ticker data with realistic prices
        prices = {
            'BTC/USDT': 45000.0,
            'BTCUSDT': 45000.0,
            'ETH/USDT': 3000.0,
            'ETHUSDT': 3000.0,
        }
        
        base_price = prices.get(symbol, 1000.0)
        # Add some random variation
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        
        ticker = {
            'symbol': symbol,
            'last': current_price,
            'high': current_price * 1.05,
            'low': current_price * 0.95,
            'bid': current_price * 0.999,
            'ask': current_price * 1.001,
            'volume': random.uniform(1000, 10000),
            'timestamp': int(datetime.now().timestamp() * 1000),
            'datetime': datetime.now().isoformat(),
        }
        
        print(f"✅ Mock ticker fetched: {symbol} = ${current_price:.2f}")
        return ticker
    
    def _validate_credentials(self) -> bool:
        """Validate mock credentials"""
        # Check if credentials match expected format
        if len(self.apiKey) < 10:
            return False
        if len(self.secret) < 10:
            return False
        if len(self.passphrase) < 5:
            return False
        return True
    
    async def close(self):
        """Mock close method"""
        print("📄 Mock OKX Exchange closed")

# Test the mock exchange
async def test_mock_okx():
    """Test the mock OKX exchange"""
    print("🧪 Testing Mock OKX Exchange...")
    
    config = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': False,
    }
    
    try:
        # Create mock exchange
        exchange = MockOKXExchange(config)
        
        # Test balance
        balance = await exchange.fetch_balance()
        print(f"Balance test: USDT = {balance['USDT']['free']}")
        
        # Test ticker
        ticker = await exchange.fetch_ticker('BTCUSDT')
        print(f"Ticker test: BTC = ${ticker['last']:.2f}")
        
        # Close exchange
        await exchange.close()
        
        print("✅ All mock tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Mock test failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mock_okx())
