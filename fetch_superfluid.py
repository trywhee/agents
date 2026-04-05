import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

# Daftar wallet agent
WALLETS = {
    "Quantiva Intelligence": "0xb9868eb3bb740d4d61c0dc1feb4bed6fb58f76e7",
    "Nexora Analytics AI": "0xB9868eB3Bb740d4d61c0Dc1fEb4Bed6FB58f76E7",
    "DataQuant Pro": "0xC222Ce890859E07D8b31a3ccb8C186ebA9914948",
    "DataAnalyst Pro": "0xe16b3f9617aae564c7314bb555c052ce6524fd3f",
    "InsightForge AI": "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32",
    "StoryWeaver AI": "0x65f20d80f2817cb4524bfc0f3bc37173da6b1058"
}

def fetch_wallet_data(wallet_address, agent_name):
    """Ambil data balance dan stream dari halaman Superfluid"""
    url = f"https://app.superfluid.org/?view={wallet_address}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"📡 Fetching {agent_name}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # === Ambil Balance SUP ===
        balance = "0"
        # Coba beberapa selector
        balance_selectors = [
            '[data-cy="token-balance"] [data-cy="token-amount"]',
            '.MuiTypography-h3mono [data-cy="token-amount"]',
            '[data-cy="balance"] [data-cy="token-amount"]'
        ]
        
        for selector in balance_selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                balance = elem.text.strip()
                break
        
        # Clean balance (hapus koma, spasi)
        balance = re.sub(r'[^\d.]', '', balance)
        if not balance or balance == '':
            balance = "0"
        
        # === Ambil Stream Distributions ===
        streams = []
        rows = soup.select('tbody tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # Pool address
                pool_text = cols[0].get_text(strip=True)
                address_match = re.search(r'0x[a-fA-F0-9]{40}', pool_text)
                if address_match:
                    pool = f"{address_match.group(0)[:8]}...{address_match.group(0)[-6:]}"
                else:
                    pool = pool_text[:20] if pool_text else "Unknown"
                
                # Amount received
                amount = cols[1].get_text(strip=True)
                amount = re.sub(r'[^\d.]', '', amount)
                
                # Flow rate
                flow = cols[2].get_text(strip=True)
                
                if amount and amount != '' and amount != '0':
                    streams.append({
                        "pool": pool,
                        "amount": amount,
                        "flow": flow
                    })
        
        return {
            "success": True,
            "balance": balance,
            "streams": streams,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching {agent_name}: {str(e)}")
        return {
            "success": False,
            "balance": "0",
            "streams": [],
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }

def main():
    print("🚀 Starting Superfluid data fetch...")
    print("=" * 50)
    
    results = {}
    
    for name, wallet in WALLETS.items():
        data = fetch_wallet_data(wallet, name)
        results[name] = data
        time.sleep(1)  # Delay untuk menghindari rate limit
    
    # Generate JSON output
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(WALLETS),
        "agents": results
    }
    
    with open("superfluid-data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print("✅ superfluid-data.json generated successfully!")
    print(f"📊 Total agents: {len(WALLETS)}")
    
    # Print summary
    for name, data in results.items():
        if data['success']:
            print(f"   ✅ {name}: {data['balance']} SUP, {len(data['streams'])} streams")
        else:
            print(f"   ❌ {name}: Failed - {data.get('error', 'Unknown')}")

if __name__ == "__main__":
    main()
