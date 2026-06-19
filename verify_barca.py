import urllib.request
import json
import time
import subprocess

# Start server
server = subprocess.Popen(["uvicorn", "src.app:app", "--host", "127.0.0.1", "--port", "8002"])
time.sleep(5) # Wait for startup

try:
    def get_data(algo, weight):
        url = f"http://127.0.0.1:8002/api/rankings/historical?algorithm={algo}&weight_mode={weight}&direction=buyers"
        req = urllib.request.urlopen(url)
        return json.loads(req.read())["timeline"]

    def analyze_barca(timeline):
        top10 = 0
        top5 = 0
        best_rank = 999
        best_years = []
        ranks = {}
        for f in timeline:
            season = f["season"]
            rank = next((i+1 for i, c in enumerate(f["clubs"]) if c["club_name"] == "FC Barcelona"), 999)
            ranks[season] = rank
            if rank <= 10:
                top10 += 1
            if rank <= 5:
                top5 += 1
            if rank < best_rank:
                best_rank = rank
                best_years = [season]
            elif rank == best_rank:
                best_years.append(season)
        return top10, top5, best_rank, best_years, ranks

    print("PR Fee:")
    pr_fee = analyze_barca(get_data("pagerank", "fee"))
    print(pr_fee[:4])
    print("PR Fee Ranks:", {k:v for k,v in pr_fee[4].items() if v <= 10})
    print("PR Fee Bad Ranks (2002, 2013, 2015, 2018):", pr_fee[4].get("2002-2003"), pr_fee[4].get("2013-2014"), pr_fee[4].get("2015-2016"), pr_fee[4].get("2018-2019"))

    print("\nHITS Fee:")
    hits_fee = analyze_barca(get_data("hits", "fee"))
    print(hits_fee[:4])
    print("HITS Fee Ranks:", {k:v for k,v in hits_fee[4].items() if v <= 10})

    print("\nPR Count:")
    pr_count = analyze_barca(get_data("pagerank", "count"))
    print(pr_count[:4])

    print("\nHITS Count:")
    hits_count = analyze_barca(get_data("hits", "count"))
    print(hits_count[:4])

finally:
    server.terminate()
