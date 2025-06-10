#!/usr/bin/env python3
import asyncio
import aiohttp
import sys

async def test_health():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend healthy: {data}")
                    return True
                else:
                    print(f"❌ Backend error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    print("🧪 Simple health check test")
    success = await test_health()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
