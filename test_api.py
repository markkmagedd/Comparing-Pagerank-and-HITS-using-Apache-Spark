import requests
import json

try:
    r1 = requests.get("http://127.0.0.1:8000/api/rankings/historical?algorithm=pagerank&top_n=10", timeout=60)
    d1 = r1.json()["data"]["timeline"][-1]["clubs"]
    print("PageRank top 5:", [(x["club_name"], x["score"]) for x in d1[:5]])
except Exception as e:
    print("PageRank failed:", e)

try:
    r2 = requests.get("http://127.0.0.1:8000/api/rankings/historical?algorithm=hits&top_n=10", timeout=60)
    d2 = r2.json()["data"]["timeline"][-1]["clubs"]
    print("HITS top 5:", [(x["club_name"], x["score"]) for x in d2[:5]])
except Exception as e:
    print("HITS failed:", e)
