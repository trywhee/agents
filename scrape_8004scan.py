import json
import requests
from datetime import datetime

# Daftar agent (wallet address)
AGENTS = [
    {"name": "Quantiva Intelligence", "wallet": "0xb9868eb3bb740d4d61c0dc1feb4bed6fb58f76e7"},
    {"name": "Nexora Analytics AI", "wallet": "0xB9868eB3Bb740d4d61c0Dc1fEb4Bed6FB58f76E7"},
    {"name": "DataQuant Pro", "wallet": "0xC222Ce890859E07D8b31a3ccb8C186ebA9914948"},
    {"name": "DataAnalyst Pro", "wallet": "0xe16b3f9617aae564c7314bb555c052ce6524fd3f"},
    {"name": "InsightForge AI", "wallet": "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32"},
    {"name": "StoryWeaver AI", "wallet": "0x65f20d80f2817cb4524bfc0f3bc37173da6b1058"}
]

SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/superfluid-finance/protocol-v1-base-mainnet"

def query_subgraph(wallet_address):
    query = f"""
    {{
        account(id: "{wallet_address.lower()}") {{
            tokenBalances(where: {{ token_: {{ symbol: "SUPx" }} }}) {{
                balance
                totalInflowRate
            }}
            subscriptions {{
                index {{ id }}
                totalAmountReceivedUntilUpdatedAt
                approved
            }}
        }}
    }}
    """
    try:
        print(f"Querying {wallet_address}...")
        response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
        
        if response.status_code != 200:
            print(f"Error HTTP {response.status_code}: {response.text}")
            return None
            
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Error: {data['errors']}")
            return None
            
        account = data.get("data", {}).get("account")
        
        if not account:
            print(f"No account found for {wallet_address}")
            return None
        
        # Parse balance
        balance = "0"
        inflow_rate = "0"
        if account.get("tokenBalances") and len(account["tokenBalances"]) > 0:
            raw_balance = account["tokenBalances"][0]["balance"]
            raw_inflow = account["tokenBalances"][0]["totalInflowRate"]
            balance = f"{float(raw_balance) / 1e18:.6f}"
            monthly_rate = (float(raw_inflow) / 1e18) * 30 * 24 * 3600
            inflow_rate = f"{monthly_rate:.2f}"
            print(f"Balance: {balance} SUP, Inflow: {inflow_rate}/month")
        
        # Parse pools
        pools = []
        for sub in account.get("subscriptions", []):
            if sub.get("approved") and float(sub.get("totalAmountReceivedUntilUpdatedAt", 0)) > 0:
                amount = float(sub['totalAmountReceivedUntilUpdatedAt']) / 1e18
                pools.append({
                    "poolAddress": sub["index"]["id"],
                    "totalReceived": f"{amount:.4f}"
                })
                print(f"Pool {sub['index']['id'][:10]}...: {amount:.4f} SUP")
        
        return {
            "balance": balance,
            "inflowRate": inflow_rate,
            "pools": pools
        }
    except requests.exceptions.Timeout:
        print(f"Timeout for {wallet_address}")
        return None
    except Exception as e:
        print(f"Exception for {wallet_address}: {str(e)}")
        return None

def main():
    print("Starting Superfluid data fetch...")
    results = {}
    
    for agent in AGENTS:
        print(f"\n--- Fetching {agent['name']} ---")
        data = query_subgraph(agent["wallet"])
        if data:
            results[agent["name"]] = data
        else:
            results[agent["name"]] = {"error": "Failed to fetch"}
    
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": results
    }
    
    with open("superfluid-data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Data saved to superfluid-data.json")
    
    # Print summary
    print("\n=== SUMMARY ===")
    for name, data in results.items():
        if "error" not in data:
            print(f"✅ {name}: {data['balance']} SUP")
        else:
            print(f"❌ {name}: {data['error']}")

if __name__ == "__main__":
    main()
