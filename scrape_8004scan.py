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

def get_agent_flow_rates(wallet_address):
    """
    Ambil flow rate SPESIFIK agent dari indexSubscriptions.
    Query ini sudah terbukti berhasil di test_connection.
    """
    query = f"""
    {{
      account(id: "{wallet_address.lower()}") {{
        id
        indexSubscriptions(where: {{approved: true}}) {{
          approved
          units
          index {{
            id
            totalUnits
            indexId
          }}
          totalAmountReceivedUntilUpdatedAt
        }}
      }}
    }}
    """
    
    try:
        response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
        if response.status_code != 200:
            print(f"  HTTP Error: {response.status_code}")
            return []
        
        data = response.json()
        
        if "errors" in data:
            print(f"  GraphQL Error: {data['errors']}")
            return []
        
        account = data.get("data", {}).get("account")
        if not account:
            print(f"  No account found")
            return []
        
        subscriptions = account.get("indexSubscriptions", [])
        print(f"  Found {len(subscriptions)} index subscriptions")
        
        results = []
        for sub in subscriptions:
            index_data = sub.get("index", {})
            if not index_data:
                continue
            
            pool_address = index_data.get("id", "")
            total_units = float(index_data.get("totalUnits", 1))
            agent_units = float(sub.get("units", 0))
            
            # Hitung flow rate agent berdasarkan porsi
            # Flow rate agent = (units_agent / total_units) * (total flow rate pool)
            # Karena total flow rate pool tidak tersedia langsung, kita gunakan units sebagai proksi
            # Semakin besar units, semakin besar porsi
            
            short_address = f"{pool_address[:6]}...{pool_address[-4:]}" if len(pool_address) > 10 else pool_address
            
            # Estimasi flow rate (dalam SUP/bulan) berdasarkan units
            # Ini akan update otomatis ketika total_units pool berubah
            if total_units > 0 and agent_units > 0:
                pct = (agent_units / total_units) * 100
                flow_rate_display = f"{pct:.1f}% of pool"
            else:
                flow_rate_display = "Active"
            
            # Ambil amount received jika ada
            raw_amount = sub.get("totalAmountReceivedUntilUpdatedAt", "0")
            try:
                amount_received = float(raw_amount) / 1e18
                amount_display = f"{amount_received:.4f} SUP"
            except:
                amount_display = "0 SUP"
            
            results.append({
                "poolAddress": short_address,
                "fullAddress": pool_address,
                "flowRate": flow_rate_display,
                "totalReceived": amount_display,
                "status": "Connected"
            })
        
        return results
        
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return []

def main():
    print("Starting Superfluid data fetch (indexSubscriptions)...")
    print(f"Subgraph URL: {SUBGRAPH_URL}\n")
    
    results = {}
    for agent in AGENTS:
        print(f"Processing {agent['name']}...")
        balance = get_sup_balance(agent["wallet"])
        pools = get_agent_flow_rates(agent["wallet"])
        
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
