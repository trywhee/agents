import requests

# ENDPOINT BARU YANG BENAR (SUDAH AKTIF)
SUBGRAPH_URL = "https://subgraph.satsuma-prod.com/3b5f1e47e3f6/superfluid-base-mainnet/api"

# Query sederhana untuk test koneksi
query = """
{
  _meta {
    block {
      number
    }
  }
}
"""

print(f"Testing connection to: {SUBGRAPH_URL}")
print("")

try:
    response = requests.post(SUBGRAPH_URL, json={"query": query}, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            block_number = data["data"]["_meta"]["block"]["number"]
            print(f"✅ SUCCESS! Block number: {block_number}")
            print("Koneksi ke subgraph Superfluid BERHASIL!")
        else:
            print("❌ Response tidak sesuai format")
            print(f"Response: {response.text[:200]}")
    else:
        print(f"❌ Gagal: HTTP {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print("❌ ERROR: Timeout - Server tidak merespon")
except requests.exceptions.ConnectionError as e:
    print(f"❌ ERROR: Gagal konek - {str(e)}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
