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

RPC_URL = "https://rpc-endpoints.superfluid.dev/base-mainnet"
SUP_TOKEN = "0xa69f80524381275a7ffdb3ae01c54150644c8792"

# ENDPOINT YANG BENAR (dari Inspect Element Anda)
SUBGRAPH_URL = "https://base-mainnet.subgraph.x.superfluid.dev/"

def get_sup_balance(wallet_address):
    data = "0x70a08231000000000000000000000000" + wallet_address[2:].lower()
    payload = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": SUP_TOKEN, "data": data}, "latest"], "id": 1}
    try:
        response = requests.post(RPC_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            balance_hex = result.get("result", "0x0")
            return f"{int(balance_hex, 16) / 1e18:.6f}"
    except Exception as e:
        print(f"Balance error: {e}")
    return "0"

def get_pool_distributions(wallet_address):
    """Ambil daftar pool asli dari subgraph"""
    query = """
    {
      account(id: "%s") {
        subscriptions(where: {approved: true}) {
          index {
            id
          }
          totalAmountReceivedUntilUpdatedAt
        }
      }
    }
    """ % wallet_address.lower()
    
    try:
        response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            account_data = data.get("data", {}).get("account")
            pools = []
            
            if account_data and "subscriptions" in account_data:
                for sub in account_data["subscriptions"]:
                    raw_address = sub["index"]["id"]
                    short_address = f"{raw_address[:6]}...{raw_address[-4:]}"
                    raw_amount = sub.get("totalAmountReceivedUntilUpdatedAt", "0")
                    try:
                        amount_received = float(raw_amount) / 1e18
                        amount_formatted = f"{amount_received:.4f}"
                    except:
                        amount_formatted = "0"
                    
                    pools.append({
                        "poolAddress": short_address,
                        "totalReceived": amount_formatted,
                        "flowRate": "+.../mo",
                        "status": "Connected"
                    })
            return pools
        else:
            print(f"Subgraph Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Subgraph Exception: {e}")
        return []

def main():
    results = {}
    for agent in AGENTS:
        print(f"Fetching {agent['name']}...")
        balance = get_sup_balance(agent["wallet"])
        pools = get_pool_distributions(agent["wallet"])
        results[agent["name"]] = {
            "balance": balance,
            "pools": pools
        }
        print(f"  Balance: {balance} SUP, Pools: {len(pools)}")
    
    output = {"timestamp": datetime.utcnow().isoformat(), "agents": results}
    with open("superfluid-data.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\n✅ Data saved!")

if __name__ == "__main__":
    main()
