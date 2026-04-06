import requests
import json

# Endpoint subgraph yang benar
SUBGRAPH_URL = "https://base-mainnet.subgraph.x.superfluid.dev/"

# Wallet InsightForge AI
WALLET = "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32"

# Query untuk mencari IDA subscriptions
query = """
{
  account(id: "%s") {
    id
    tokenBalances {
      token {
        symbol
      }
      balance
    }
    subscriptions {
      id
      approved
      units
      index {
        id
        indexId
        token {
          symbol
        }
      }
      totalAmountReceivedUntilUpdatedAt
    }
    indexSubscriptions {
      id
      approved
      units
      index {
        id
        indexId
      }
      totalAmountReceivedUntilUpdatedAt
    }
  }
}
""" % WALLET.lower()

print(f"Querying: {SUBGRAPH_URL}")
print(f"Wallet: {WALLET}")
print()

try:
    response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
        else:
            account = data.get("data", {}).get("account")
            if account:
                print("\n✅ ACCOUNT FOUND:")
                print(f"  ID: {account.get('id')}")
                
                # Token balances
                balances = account.get("tokenBalances", [])
                print(f"\n  Token Balances ({len(balances)}):")
                for b in balances:
                    token = b.get("token", {})
                    print(f"    - {token.get('symbol')}: {float(b.get('balance', 0)) / 1e18:.6f}")
                
                # Subscriptions (IDA)
                subs = account.get("subscriptions", [])
                print(f"\n  Subscriptions ({len(subs)}):")
                for s in subs:
                    idx = s.get("index", {})
                    amount = float(s.get("totalAmountReceivedUntilUpdatedAt", 0)) / 1e18
                    print(f"    - Pool: {idx.get('id')}")
                    print(f"      Amount Received: {amount:.4f} SUP")
                    print(f"      Approved: {s.get('approved')}")
                
                # Alternative: indexSubscriptions
                idx_subs = account.get("indexSubscriptions", [])
                print(f"\n  Index Subscriptions ({len(idx_subs)}):")
                for s in idx_subs:
                    idx = s.get("index", {})
                    amount = float(s.get("totalAmountReceivedUntilUpdatedAt", 0)) / 1e18
                    print(f"    - Pool: {idx.get('id')}")
                    print(f"      Amount Received: {amount:.4f} SUP")
            else:
                print("\n❌ No account found for this wallet")
    else:
        print(f"HTTP Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"Exception: {e}")
