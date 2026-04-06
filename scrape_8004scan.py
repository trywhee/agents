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
    """Query lengkap seperti yang digunakan dashboard Superfluid"""
    query = f"""
    {{
      account(id: "{wallet_address.lower()}") {{
        id
        subscriptions(where: {{approved: true}}) {{
          id
          approved
          units
          totalUnits
          totalAmountReceivedUntilUpdatedAt
          totalAmountReceived
          totalDistributionAmountReceived
          index {{
            id
            indexId
            totalUnits
            token {{
              id
              symbol
              name
              decimals
            }}
          }}
        }}
      }}
    }}
    """
    
    try:
        print(f"  Querying subgraph for {wallet_address[:10]}...")
        response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
        
        if response.status_code != 200:
            print(f"  HTTP Error: {response.status_code}")
            return []
        
        data = response.json()
        
        # Debug: print response structure
        if "errors" in data:
            print(f"  GraphQL Error: {data['errors']}")
            return []
        
        account_data = data.get("data", {}).get("account")
        if not account_data:
            print(f"  No account data found")
            return []
        
        subscriptions = account_data.get("subscriptions", [])
        print(f"  Found {len(subscriptions)} subscriptions")
        
        pools = []
        for sub in subscriptions:
            index_data = sub.get("index", {})
            if not index_data:
                continue
                
            raw_address = index_data.get("id", "")
            short_address = f"{raw_address[:6]}...{raw_address[-4:]}" if len(raw_address) > 10 else raw_address
            
            raw_amount = sub.get("totalAmountReceivedUntilUpdatedAt", "0")
            try:
                amount_received = float(raw_amount) / 1e18
                amount_formatted = f"{amount_received:.4f}"
            except:
                amount_formatted = "0"
            
            # Hitung flow rate per bulan (estimasi dari units)
            flow_rate = "+.../mo"
            
            pools.append({
                "poolAddress": short_address,
                "totalReceived": amount_formatted,
                "flowRate": flow_rate,
                "status": "Connected"
            })
            
        return pools
        
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return []

def main():
    print("Starting Superfluid data fetch...")
    print(f"Subgraph URL: {SUBGRAPH_URL}")
    print()
    
    results = {}
    for agent in AGENTS:
        print(f"Processing {agent['name']}...")
        balance = get_sup_balance(agent["wallet"])
        pools = get_pool_distributions(agent["wallet"])
        
        results[agent["name"]] = {
            "balance": balance,
            "pools": pools
        }
        print(f"  -> Balance: {balance} SUP, Pools: {len(pools)}\n")
    
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": results
    }
    
    with open("superfluid-data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Data saved to superfluid-data.json")

if __name__ == "__main__":
    main()
