import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

# Daftar wallet agent
WALLETS = {
    "Quantiva Intelligence": "0xb9868eb3bb740d4d61c0dc1feb4bed6fb58f76e7",
    "Nexora Analytics AI": "0xB9868eB3Bb740d4d61c0Dc1fEb4Bed6FB58f76E7",
    "DataQuant Pro": "0xC222Ce890859E07D8b31a3ccb8C186ebA9914948",
    "DataAnalyst Pro": "0xe16b3f9617aae564c7314bb555c052ce6524fd3f",
    "InsightForge AI": "0x32D9b8E82aa07F77bcBB648Ccf534ED41A782b32",
    "StoryWeaver AI": "0x65f20d80f2817cb4524bfc0f3bc37173da6b1058"
}

def fetch_wallet_data(wallet_address, agent_name):
    """Ambil data balance dan stream dari halaman Superfluid"""
    url = f"https://app.superfluid.org/?view={wallet_address}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"📡 Fetching {agent_name}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # === AMBIL BALANCE SUP (BUKAN USD) ===
        balance = "0"
        
        # Method 1: Cari teks yang mengandung "SUP" dan ambil angka sebelumnya
        # Cari semua teks yang mengandung "SUP"
        sup_texts = soup.find_all(string=re.compile(r'\d+\.?\d*\s*SUP'))
        for text in sup_texts:
            match = re.search(r'([\d.]+)\s*SUP', text)
            if match:
                balance = match.group(1)
                print(f"   Found SUP balance via text: {balance}")
                break
        
        # Method 2: Jika Method 1 gagal, cari di sekitar elemen dengan data-cy="token-balance"
        if balance == "0":
            balance_container = soup.select_one('[data-cy="token-balance"]')
            if balance_container:
                # Cari teks yang mengandung "SUP" di dalam container ini
                container_text = balance_container.get_text()
                match = re.search(r'([\d.]+)\s*SUP', container_text)
                if match:
                    balance = match.group(1)
                    print(f"   Found SUP balance via container: {balance}")
        
        # Method 3: Cari berdasarkan struktur MUI typography
        if balance == "0":
            # Cari semua elemen dengan kelas yang mengandung "MuiTypography"
            typography_elements = soup.find_all(class_=re.compile(r'MuiTypography'))
            for elem in typography_elements:
                text = elem.get_text(strip=True)
                # Cari pola: angka + spasi + SUP
                match = re.search(r'^([\d.]+)\s+SUP$', text)
                if match:
                    balance = match.group(1)
                    print(f"   Found SUP balance via typography: {balance}")
                    break
        
        # Method 4: Cari berdasarkan posisi (angka setelah SUP atau sebelum SUP)
        if balance == "0":
            # Cari semua teks yang mengandung angka
            all_text = soup.get_text()
            # Cari pola "XXX SUP" atau "SUP XXX"
            patterns = [
                r'([\d.]+)\s*SUP',  # "123.45 SUP"
                r'SUP\s*([\d.]+)'   # "SUP 123.45"
            ]
            for pattern in patterns:
                matches = re.findall(pattern, all_text)
                if matches:
                    # Ambil yang pertama, asumsikan itu balance utama
                    balance = matches[0]
                    print(f"   Found SUP balance via pattern: {balance}")
                    break
        
        # Pastikan balance adalah angka valid
        try:
            float(balance)
        except ValueError:
            balance = "0"
            print(f"   WARNING: Could not parse balance, setting to 0")
        
        # === AMBIL STREAM DISTRIBUTIONS ===
        streams = []
        
        # Cari tabel Stream Distributions
        tables = soup.find_all('table')
        for table in tables:
            # Cek apakah ini tabel Stream Distributions (cari kolom Pool, Amount Received, Flow Rate)
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text().lower() for h in headers])
            if 'pool' in header_text and 'amount' in header_text and 'flow' in header_text:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # Pool address
                        pool_text = cols[0].get_text(strip=True)
                        address_match = re.search(r'0x[a-fA-F0-9]{40}', pool_text)
                        if address_match:
                            pool = f"{address_match.group(0)[:8]}...{address_match.group(0)[-6:]}"
                        else:
                            pool = pool_text[:20] if pool_text else "Unknown"
                        
                        # Amount received
                        amount_text = cols[1].get_text(strip=True)
                        amount_match = re.search(r'[\d.]+', amount_text)
                        amount = amount_match.group(0) if amount_match else "0"
                        
                        # Flow rate
                        flow = cols[2].get_text(strip=True)
                        
                        if amount != "0" and amount != "":
                            streams.append({
                                "pool": pool,
                                "amount": amount,
                                "flow": flow
                            })
                break  # Keluar setelah menemukan tabel yang benar
        
        print(f"   Balance: {balance} SUP, Streams: {len(streams)}")
        
        return {
            "success": True,
            "balance": balance,
            "streams": streams,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching {agent_name}: {str(e)}")
        return {
            "success": False,
            "balance": "0",
            "streams": [],
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }

def main():
    print("🚀 Starting Superfluid data fetch...")
    print("=" * 50)
    
    results = {}
    
    for name, wallet in WALLETS.items():
        data = fetch_wallet_data(wallet, name)
        results[name] = data
        time.sleep(2)  # Delay lebih lama untuk menghindari rate limit
    
    # Generate JSON output
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(WALLETS),
        "agents": results
    }
    
    with open("superfluid-data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print("✅ superfluid-data.json generated!")
    
    # Print summary
    print("\n📊 SUMMARY:")
    for name, data in results.items():
        if data['success'] and data['balance'] != "0":
            print(f"   ✅ {name}: {data['balance']} SUP, {len(data['streams'])} streams")
        elif data['success']:
            print(f"   ⚠️ {name}: Balance 0 SUP, {len(data['streams'])} streams")
        else:
            print(f"   ❌ {name}: Failed")

if __name__ == "__main__":
    main()
