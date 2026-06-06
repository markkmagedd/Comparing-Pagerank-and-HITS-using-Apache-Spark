import os
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer

def print_table(title, results):
    print(f"\n% {title}")
    print("\\begin{table}[H]")
    print("\\centering")
    print("\\begin{tabular}{|l|l|r|}")
    print("\\hline")
    print("\\textbf{Rank} & \\textbf{Club} & \\textbf{Score} \\\\")
    print("\\hline")
    for i, node in enumerate(results['nodes']):
        club = node['id']
        score = node['rank']
        print(f"{i+1} & {club} & {score:.4f} \\\\")
    print("\\hline")
    print("\\end{tabular}")
    print(f"\\caption{{{title}}}")
    print(f"\\label{{tab:{title.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}}}")
    print("\\end{table}")

spark = SparkSession.builder.appName("GenerateTables").master("local[*]").getOrCreate()
analyzer = TransferAnalyzer(spark, "transfers.csv")

# 1. PageRank Buyers (Fee)
pr_buyers = analyzer.get_top_graph(
    direction="buyers", top_n=10, algorithm="pagerank"
)
print_table("Top 10 Buyers PageRank - Fee Weighted", pr_buyers)

# 2. HITS Authority (Fee) - Equivalent to buyers
hits_auth = analyzer.get_top_graph(
    direction="buyers", top_n=10, algorithm="hits"
)
print_table("Top 10 Authority Buyers HITS - Fee Weighted", hits_auth)

# 3. PageRank Sellers (Fee)
pr_sellers = analyzer.get_top_graph(
    direction="sellers", top_n=10, algorithm="pagerank"
)
print_table("Top 10 Sellers PageRank - Fee Weighted", pr_sellers)

# 4. HITS Hubs (Fee) - Equivalent to sellers
hits_hubs = analyzer.get_top_graph(
    direction="sellers", top_n=10, algorithm="hits"
)
print_table("Top 10 Hubs Sellers HITS - Fee Weighted", hits_hubs)

# 5. PageRank Buyers (Count)
analyzer_count = TransferAnalyzer(spark, "transfers.csv", weight_mode="count")
pr_buyers_count = analyzer_count.get_top_graph(
    direction="buyers", top_n=10, algorithm="pagerank"
)
print_table("Top 10 Buyers PageRank - Count Weighted", pr_buyers_count)

# 6. HITS Authority (Count) - Equivalent to buyers
hits_auth_count = analyzer_count.get_top_graph(
    direction="buyers", top_n=10, algorithm="hits"
)
print_table("Top 10 Authority Buyers HITS - Count Weighted", hits_auth_count)

# 7. PageRank Sellers (Count)
pr_sellers_count = analyzer_count.get_top_graph(
    direction="sellers", top_n=10, algorithm="pagerank"
)
print_table("Top 10 Sellers PageRank - Count Weighted", pr_sellers_count)

# 8. HITS Hubs (Count) - Equivalent to sellers
hits_hubs_count = analyzer_count.get_top_graph(
    direction="sellers", top_n=10, algorithm="hits"
)
print_table("Top 10 Hubs Sellers HITS - Count Weighted", hits_hubs_count)

# Stop spark
spark.stop()
