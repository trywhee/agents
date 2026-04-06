import json
import requests
from datetime import datetime

# ========== KONFIGURASI AGENT ==========
AGENTS = [
    {"name": "Quantiva Intelligence", "wallet": "0xb9868eb3bb740d4d61c0dc1feb4bed6fb58f76e7", "score": "72.37"},
    {"name": "Nexora Analytics AI", "wallet": "0xB9868eB3Bb740d4d61c0Dc1fEb4Bed6FB58f76E7", "score": "68.50"},
    {"name": "DataQuant Pro", "wallet": "0xC222Ce890859E07D8b31a3ccb8C186ebA9914948", "score": "65.20"},
    {"name": "DataAnalyst Pro", "wallet": "0xe16b3f9617aae564c7314bb555c052ce6524fd3f", "score": "45.38"},
    {"name": "InsightForge AI", "wallet": "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32", "score": "58.90"},
    {"name": "StoryWeaver AI", "wallet": "0x65f20d80f2817cb4524bfc0f3bc37173da6b1058", "score": "0"}
]

# ========== 3 POOL ASLI ANDA ==========
POOLS_DATA = [
    {"address": "0xd0fd005048B759A3B97FB0797F83636F9Bf7632E", "short": "0xd0fd...632E"},
    {"address": "0xc5006EC21d3292D72e5fbdDA19cd90F48d9A15b2", "short": "0xc500...15b2"},
    {"address": "0x72AB3a3459599Bbd2ccdE2db742565f8C50a2Cf7", "short": "0x72AB...2Cf7"}
]

# ========== ENDPOINT ==========
RPC_URL = "https://rpc-endpoints.superfluid.dev/base-mainnet"
SUP_TOKEN = "0xa69f80524381275a7ffdb3ae01c54150644c8792"

def get_sup_balance(wallet_address):
    """Ambil balance SUP via RPC"""
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

def main():
    results = {}
    for agent in AGENTS:
        print(f"Memproses {agent['name']}...")
        balance = get_sup_balance(agent["wallet"])
        
        # Gunakan 3 pool asli Anda
        pools = []
        for pool in POOLS_DATA:
            pools.append({
                "poolAddress": pool["short"],  # Pakai format pendek untuk tampilan
                "fullAddress": pool["address"], # Simpan yang lengkap kalau perlu
                "totalReceived": "Active",      # Ganti dengan data riil jika ada
                "flowRate": "+.../mo",
                "status": "Connected"
            })
        
        results[agent["name"]] = {
            "balance": balance,
            "pools": pools
        }
        print(f"  -> Balance: {balance} SUP, Menampilkan {len(pools)} pool")

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": results
    }
    
    with open("superfluid-data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Data berhasil disimpan dengan 3 pool asli Anda!")

if __name__ == "__main__":
    main()
