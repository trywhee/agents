import requests
import re
import json
import time
from datetime import datetime

# Daftar agent
AGENTS = [
    {"id": 22524, "name": "Quantiva Intelligence"},
    {"id": 22497, "name": "Nexora Analytics AI"},
    {"id": 22455, "name": "DataQuant Pro"},
    {"id": 22300, "name": "DataAnalyst Pro"},
    {"id": 22398, "name": "InsightForge AI"},
    {"id": 30502, "name": "StoryWeaver AI"}
]

def fetch_agent_scores(agent_id, agent_name):
    """Ambil Total Score, Average Score, Total Feedbacks dari 8004scan"""
    url = f"https://8004scan.io/agents/base/{agent_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        html = response.text
        
        # Ekstrak data dengan regex
        total_score_match = re.search(r'total_score[^0-9]*([0-9.]+)', html)
        avg_score_match = re.search(r'average_score[^0-9]*([0-9.]+)', html)
        feedbacks_match = re.search(r'total_feedbacks[^0-9]*([0-9]+)', html)
        
        return {
            "success": True,
            "name": agent_name,
            "agent_id": agent_id,
            "total_score": float(total_score_match.group(1)) if total_score_match else 0,
            "average_score": float(avg_score_match.group(1)) if avg_score_match else 0,
            "total_feedbacks": int(feedbacks_match.group(1)) if feedbacks_match else 0,
        }
        
    except Exception as e:
        print(f"Error fetching {agent_name}: {e}")
        return {
            "success": False,
            "name": agent_name,
            "agent_id": agent_id,
            "total_score": 0,
            "average_score": 0,
            "total_feedbacks": 0,
            "error": str(e)
        }

def main():
    print("🚀 Scraping 8004scan scores...")
    print("=" * 50)
    
    results = []
    for agent in AGENTS:
        print(f"📡 Fetching {agent['name']} (ID: {agent['id']})...")
        data = fetch_agent_scores(agent['id'], agent['name'])
        results.append(data)
        time.sleep(1)  # Delay to avoid rate limit
    
    # Prepare output
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(AGENTS),
        "agents": results
    }
    
    # Save to file
    with open("8004scan_scores.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print("✅ 8004scan_scores.json generated!")
    print(f"📊 Total agents: {len(results)}")
    
    # Print summary
    for agent in results:
        if agent['success']:
            print(f"   ✅ {agent['name']}: {agent['total_score']} | Avg: {agent['average_score']} | Feedback: {agent['total_feedbacks']}")
        else:
            print(f"   ❌ {agent['name']}: Failed")

if __name__ == "__main__":
    main()
