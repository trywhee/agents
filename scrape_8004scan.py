import json
import requests
from datetime import datetime

AGENTS = [
    {"name": "Quantiva Intelligence", "wallet": "0xb9868eb3bb740d4d61c0dc1feb4bed6fb58f76e7"},
    {"name": "Nexora Analytics AI", "wallet": "0xB9868eB3Bb740d4d61c0Dc1fEb4Bed6FB58f76E7"},
    {"name": "DataQuant Pro", "wallet": "0xC222Ce890859E07D8b31a3ccb8C186ebA9914948"},
    {"name": "DataAnalyst Pro", "wallet": "0xe16b3f9617aae564c7314bb555c052ce6524fd3f"},
    {"name": "InsightForge AI", "wallet": "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32"},
    {"name": "StoryWeaver AI", "wallet": "0x65f20d80f2817cb4524bfc0f3bc37173da6b1058"}
]

# ENDPOINT YANG BENAR (dari Inspect Element Anda)
RPC_URL = "https://rpc-endpoints.superfluid.dev/base-mainnet"

def get_sup_balance(wallet_address):
    """Mengambil balance SUP dari RPC Superfluid"""
    
    # Contract ABI untuk function balanceOf
    data = "0x70a08231000000000000000000000000" + wallet_address[2:].lower()
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": "0xa69f80524381275a7ffdb3ae01c54150644c8792",  # Token SUP
            "data": data
        }, "latest"],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            balance_hex = result.get("result", "0x0")
            balance = int(balance_hex, 16) / 1e18
            return f"{balance:.6f}"
        else:
            return "0"
    except Exception as e:
        print(f"Error: {e}")
        return "0"

def main():
    results = {}
    for agent in AGENTS:
        print(f"Fetching {agent['name']}...")
        balance = get_sup_balance(agent["wallet"])
        results[agent["name"]] = {
            "balance": balance,
            "inflowRate": "0",  # RPC call lebih kompleks untuk flow rate
            "pools": []
        }
    
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": results
    }
    
    with open("superfluid-data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Data saved to superfluid-data.json")

if __name__ == "__main__":
    main()
