"""Quick debug script to test HITS vs PageRank backend directly."""
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("Debug_HITS") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

analyzer = TransferAnalyzer(spark, "transfers.csv", league="all", weight_mode="fee")

print("=" * 60)
print("PAGERANK - Buyers (Fee) - Top 10")
print("=" * 60)
pr_ranks = analyzer.get_rankings(direction='buyers', iterations=10, damping=0.85, algorithm="pagerank")
pr_top = pr_ranks.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(pr_top, 1):
    print(f"  {i}. {club}: {score:.6f}")

print()
print("=" * 60)
print("HITS - Authority (Buyers) (Fee) - Top 10")
print("=" * 60)
hits_ranks = analyzer.get_rankings(direction='buyers', iterations=10, damping=0.85, algorithm="hits")
hits_top = hits_ranks.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(hits_top, 1):
    print(f"  {i}. {club}: {score:.6f}")

print()
print("=" * 60)
print("PAGERANK - Sellers (Fee) - Top 10")
print("=" * 60)
pr_ranks_s = analyzer.get_rankings(direction='sellers', iterations=10, damping=0.85, algorithm="pagerank")
pr_top_s = pr_ranks_s.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(pr_top_s, 1):
    print(f"  {i}. {club}: {score:.6f}")

print()
print("=" * 60)
print("HITS - Hub (Sellers) (Fee) - Top 10")
print("=" * 60)
hits_ranks_s = analyzer.get_rankings(direction='sellers', iterations=10, damping=0.85, algorithm="hits")
hits_top_s = hits_ranks_s.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(hits_top_s, 1):
    print(f"  {i}. {club}: {score:.6f}")

# Also test count mode
print()
print("=" * 60)
print("PAGERANK - Buyers (Count) - Top 10")
print("=" * 60)
analyzer2 = TransferAnalyzer(spark, "transfers.csv", league="all", weight_mode="count")
pr_ranks_c = analyzer2.get_rankings(direction='buyers', iterations=10, damping=0.85, algorithm="pagerank")
pr_top_c = pr_ranks_c.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(pr_top_c, 1):
    print(f"  {i}. {club}: {score:.6f}")

print()
print("=" * 60)
print("HITS - Authority (Buyers) (Count) - Top 10")
print("=" * 60)
hits_ranks_c = analyzer2.get_rankings(direction='buyers', iterations=10, damping=0.85, algorithm="hits")
hits_top_c = hits_ranks_c.takeOrdered(10, key=lambda x: -x[1])
for i, (club, score) in enumerate(hits_top_c, 1):
    print(f"  {i}. {club}: {score:.6f}")

spark.stop()
print("\nDone!")
