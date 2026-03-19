import pytest
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer, get_available_leagues

@pytest.fixture(scope="session")
def spark():
    yield SparkSession.builder \
        .master("local[1]") \
        .appName("pytest-pyspark-local") \
        .config("spark.driver.extraJavaOptions", "--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED --add-opens=java.base/javax.security.auth=ALL-UNNAMED") \
        .getOrCreate()

def test_pyspark_setup(spark):
    assert spark is not None
    rdd = spark.sparkContext.parallelize([1, 2, 3])
    assert rdd.count() == 3

def test_get_available_leagues(spark):
    leagues = get_available_leagues(spark.sparkContext, "transfers.csv")
    assert isinstance(leagues, list)
    assert len(leagues) > 0
    assert "Premier League" in leagues
    assert "LaLiga" in leagues
    # Check sorting
    assert leagues == sorted(leagues)

def test_transfer_analyzer_league_filter(spark):
    analyzer = TransferAnalyzer(spark, "transfers.csv", league="Premier League")
    result = analyzer.get_top_graph(direction='buyers', iterations=1, top_n=5)
    
    assert result["meta"]["league"] == "Premier League"
    assert result["meta"]["empty"] == False
    assert result["meta"]["total_records"] > 0
    # In Premier League intra-league filter, all nodes should be PL clubs (this depends on data, but generally holds)
    assert len(result["nodes"]) > 0

def test_transfer_analyzer_weight_mode_count(spark):
    analyzer = TransferAnalyzer(spark, "transfers.csv", weight_mode="count")
    result = analyzer.get_top_graph(direction='buyers', iterations=1, top_n=5)
    
    assert result["meta"]["weight_mode"] == "count"
    for edge in result["edges"]:
        assert "deals" in edge["weight_label"]
        # Weight should be an integer in count mode (represented as float 1.0, 2.0 etc)
        assert float(edge["weight"]).is_integer()

def test_weight_mode_comparison(spark):
    # Fee mode
    analyzer_fee = TransferAnalyzer(spark, "transfers.csv", weight_mode="fee")
    res_fee = analyzer_fee.get_top_graph(top_n=10)
    
    # Count mode
    analyzer_count = TransferAnalyzer(spark, "transfers.csv", weight_mode="count")
    res_count = analyzer_count.get_top_graph(top_n=10)
    
    # Rankings should likely differ, or at least the weights definitely do
    ids_fee = [n["id"] for n in res_fee["nodes"]]
    ids_count = [n["id"] for n in res_count["nodes"]]
    
    # They don't HAVE to be different but usually are for top 10
    # At minimum, verify weight labels are different
    assert "M" in res_fee["edges"][0]["weight_label"]
    assert "deals" in res_count["edges"][0]["weight_label"]
