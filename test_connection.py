import requests
import json

SUBGRAPH_URL = "https://base-mainnet.subgraph.x.superfluid.dev/"
WALLET = "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32"  # InsightForge AI

print("=" * 60)
print(f"Testing Subgraph: {SUBGRAPH_URL}")
print(f"Wallet: {WALLET}")
print("=" * 60)

# ========== QUERY 1: poolMembers ==========
query1 = """
{
  pools(
    where: {poolMembers_: {account: "%s"}}
  ) {
    id
    totalUnits
    totalMembers
    flowRate
    token {
      symbol
    }
  }
}
""" % WALLET.lower()

# ========== QUERY 2: streams (incoming) ==========
query2 = """
{
  streams(where: {receiver: "%s"}) {
    currentFlowRate
    token {
      symbol
    }
    sender {
      id
    }
    createdAtTimestamp
  }
}
""" % WALLET.lower()

# ========== QUERY 3: account dengan inflows ==========
query3 = """
{
  account(id: "%s") {
    id
    inflows {
      currentFlowRate
      token {
        symbol
      }
      sender {
        id
      }
    }
    outflows {
      currentFlowRate
      token {
        symbol
      }
      receiver {
        id
      }
    }
  }
}
""" % WALLET.lower()

# ========== EKSEKUSI ==========

# Query 1: poolMembers
print("\n📡 QUERY 1: poolMembers")
try:
    r1 = requests.post(SUBGRAPH_URL, json={"query": query1}, timeout=30)
    if r1.status_code == 200:
        data1 = r1.json()
        pools = data1.get("data", {}).get("pools", [])
        print(f"✅ Found {len(pools)} pools:")
        for p in pools:
            print(f"   - {p['id']}")
    else:
        print(f"❌ Error: {r1.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Query 2: streams
print("\n📡 QUERY 2: streams (incoming)")
try:
    r2 = requests.post(SUBGRAPH_URL, json={"query": query2}, timeout=30)
    if r2.status_code == 200:
        data2 = r2.json()
        streams = data2.get("data", {}).get("streams", [])
        print(f"✅ Found {len(streams)} incoming streams:")
        for s in streams:
            print(f"   - From: {s['sender']['id'][:15]}... Flow: {s['currentFlowRate']}")
    else:
        print(f"❌ Error: {r2.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Query 3: account dengan inflows
print("\n📡 QUERY 3: account inflows/outflows")
try:
    r3 = requests.post(SUBGRAPH_URL, json={"query": query3}, timeout=30)
    if r3.status_code == 200:
        data3 = r3.json()
        account = data3.get("data", {}).get("account")
        if account:
            inflows = account.get("inflows", [])
            outflows = account.get("outflows", [])
            print(f"✅ Found {len(inflows)} inflows, {len(outflows)} outflows")
            for i in inflows:
                print(f"   - Inflow from: {i['sender']['id'][:15]}... Rate: {i['currentFlowRate']}")
        else:
            print("❌ No account found")
    else:
        print(f"❌ Error: {r3.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 60)
print("Selesai. Mana yang berhasil?")
