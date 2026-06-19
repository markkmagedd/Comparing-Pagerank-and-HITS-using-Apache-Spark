import sys
import os

from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer

spark = SparkSession.builder.master("local[*]").appName("Test").getOrCreate()
analyzer = TransferAnalyzer(spark, "transfers.csv")

pr = analyzer.get_historical_timeline(algorithm="pagerank", top_n=5)
hits = analyzer.get_historical_timeline(algorithm="hits", top_n=5)

print("PageRank Season 1:")
for c in pr[0]["clubs"]:
    print(c["club_name"], c["score"])

print("HITS Season 1:")
for c in hits[0]["clubs"]:
    print(c["club_name"], c["score"])

spark.stop()
