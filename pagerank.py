from operator import add
import csv
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt

def plot_top_ranks(data, title, filename):
    """
    Saves a bar chart of the top ranked clubs.
    """
    # Reverse the data so the highest rank shows at the top of the bar chart
    clubs = [x[0] for x in data][::-1]
    ranks = [x[1] for x in data][::-1]

    plt.figure(figsize=(10, 6))
    bars = plt.barh(clubs, ranks, color='royalblue')
    
    # Add the exact value text next to each bar
    for i, v in enumerate(ranks):
        plt.text(v + 0.05, i, f"{v:.4f}", va='center', fontweight='bold')
        
    # Extend the x-axis slightly so the text doesn't get cut off
    plt.xlim(0, max(ranks) * 1.15)
    
    plt.xlabel('PageRank Score')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"--> Saved chart to {filename}")

def compute_contributions(edges_with_weights, rank):
    # Calculate the total mathematical weight leaving the node
    total_weight = sum([weight for dst, weight in edges_with_weights])
    
    # Distribute the rank proportionally based on the fee weight!
    for dst, weight in edges_with_weights:
        if total_weight > 0:
            yield (dst, rank * (weight / total_weight))
        else:
            yield (dst, rank / len(edges_with_weights))


def run_pagerank(edges_rdd, iterations=10, damping=0.85):
    # Group edges and turn them into a list of (destination, weight) tuples
    links = edges_rdd.groupByKey().mapValues(list).cache()
    ranks = links.mapValues(lambda x: 1.0)

    for i in range(iterations):
        contributions = links.join(ranks).flatMap(
            lambda x: compute_contributions(x[1][0], x[1][1])
        )

        ranks = contributions.reduceByKey(add) \
            .mapValues(lambda rank: (1 - damping) + damping * rank)

    return ranks


if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName("Transfer_Network_PageRank") \
        .getOrCreate()

    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # -----------------------------
    # 1. Load CSV file
    # -----------------------------
    file_path = "transfers.csv"

    lines = sc.textFile(file_path)

    header = lines.first()
    data = lines.filter(lambda row: row != header)
    
    def parse_csv_line(line):
        return next(csv.reader([line]))
        
    def parse_fee(val):
        try:
            return float(val)
        except ValueError:
            return 100000.0  # Nominal €100k fee for free transfers or missing data

    # Using index 3 (Team_from), index 5 (Team_to), and index 9 (Transfer_fee)
    # We group by the specific transfer combination and sum up the total fees
    transfers = data.map(parse_csv_line) \
                    .map(lambda x: ((x[3].strip(), x[5].strip()), parse_fee(x[9]))) \
                    .reduceByKey(add)

    # -----------------------------
    # 2️⃣ Attractor Ranking
    # (Seller → Buyer)
    # -----------------------------
    print("\n========== ATTRACTOR RANKING ==========")
    # Format: (Seller, (Buyer, Total_Fee))
    attractor_edges = transfers.map(lambda x: (x[0][0], (x[0][1], x[1])))
    attractor_ranks = run_pagerank(attractor_edges)

    top_attractors = attractor_ranks.takeOrdered(
        10, key=lambda x: -x[1]
    )

    for club, rank in top_attractors:
        print(f"{club}: {rank:.4f}")
        
    plot_top_ranks(top_attractors, 'Top 10 Buyer Clubs (Attractors)', 'top_attractors.png')

    # -----------------------------
    # 3️⃣ Supplier Ranking
    # (Reverse edges)
    # -----------------------------
    print("\n========== SUPPLIER RANKING ==========")
    # Format: (Buyer, (Seller, Total_Fee))
    supplier_edges = transfers.map(lambda x: (x[0][1], (x[0][0], x[1])))
    supplier_ranks = run_pagerank(supplier_edges)

    top_suppliers = supplier_ranks.takeOrdered(
        10, key=lambda x: -x[1]
    )

    for club, rank in top_suppliers:
        print(f"{club}: {rank:.4f}")
        
    plot_top_ranks(top_suppliers, 'Top 10 Seller Clubs (Suppliers)', 'top_suppliers.png')

    spark.stop()