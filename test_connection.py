import requests
import json

print("Test 1: Mencoba mengakses subgraph Superfluid...")

SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/superfluid-finance/protocol-v1-base-mainnet"

# Query sederhana untuk test
test_query = """
{
  _meta {
    block {
      number
    }
  }
}
"""

try:
    response = requests.post(SUBGRAPH_URL, json={"query": test_query}, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            print("✅ SUCCESS: Bisa mengakses subgraph!")
            print(f"Block number: {data['data']['_meta']['block']['number']}")
        else:
            print("❌ Response tidak sesuai format")
    else:
        print(f"❌ Gagal: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
