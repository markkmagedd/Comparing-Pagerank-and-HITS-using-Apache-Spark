import pytest
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer, get_available_leagues, run_hits

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

def test_run_hits_basic(spark):
    # Create a small network: A -> B, A -> C, B -> C
    # Expected: C has highest Authority, A has highest Hub
    edges_list = [
        ("Club A", ("Club B", 10.0)),
        ("Club A", ("Club C", 20.0)),
        ("Club B", ("Club C", 5.0))
    ]
    edges_rdd = spark.sparkContext.parallelize(edges_list)
    
    authorities, hubs = run_hits(edges_rdd, iterations=5)
    
    auth_scores = dict(authorities.collect())
    hub_scores = dict(hubs.collect())
    
    assert "Club C" in auth_scores
    assert "Club A" in hub_scores
    
    # Validate Authority: C should be highest as it has 2 incoming edges
    assert auth_scores["Club C"] > auth_scores["Club B"]
    
    # Validate Hub: A should be highest as it has 2 outgoing edges
    assert hub_scores["Club A"] > hub_scores["Club B"]
    
    # Validate L2 Normalization (Auth)
    a_sq_sum = sum(v**2 for v in auth_scores.values())
    assert pytest.approx(a_sq_sum, rel=1e-5) == 1.0
    
    # Validate L2 Normalization (Hub)
    h_sq_sum = sum(v**2 for v in hub_scores.values())
    assert pytest.approx(h_sq_sum, rel=1e-5) == 1.0

def test_hits_authority_vs_hub(spark):
    analyzer = TransferAnalyzer(spark, "transfers.csv")
    
    # Authority (Buyers)
    res_auth = analyzer.get_top_graph(direction='buyers', algorithm='hits', iterations=1, top_n=5)
    assert res_auth["meta"]["score_type"] == "authority"
    assert res_auth["meta"]["algorithm"] == "hits"
    assert len(res_auth["nodes"]) > 0
    
    # Hub (Sellers)
    res_hub = analyzer.get_top_graph(direction='sellers', algorithm='hits', iterations=1, top_n=5)
    assert res_hub["meta"]["score_type"] == "hub"
    assert res_hub["meta"]["algorithm"] == "hits"
    assert len(res_hub["nodes"]) > 0

def test_hits_vs_pagerank_differ(spark):
    analyzer = TransferAnalyzer(spark, "transfers.csv")
    
    # Run both on same data
    res_pagerank = analyzer.get_top_graph(algorithm='pagerank', top_n=10)
    res_hits = analyzer.get_top_graph(algorithm='hits', top_n=10)
    
    ids_pagerank = [n["id"] for n in res_pagerank["nodes"]]
    ids_hits = [n["id"] for n in res_hits["nodes"]]
    
    # Algorithms are different, rankings should likely vary at some positions
    # (Checking for exact Inequality might be risky on small data, but HITS and PR are very different)
    assert ids_pagerank != ids_hits

def test_hits_with_league_filter(spark):
    # Intra-league Premier League
    analyzer = TransferAnalyzer(spark, "transfers.csv", league="Premier League")
    res = analyzer.get_top_graph(algorithm='hits', direction='buyers', iterations=1, top_n=5)
    
    assert res["meta"]["league"] == "Premier League"
    assert res["meta"]["empty"] == False
    assert len(res["nodes"]) > 0

def test_hits_with_count_weight(spark):
    analyzer = TransferAnalyzer(spark, "transfers.csv", weight_mode="count")
    res = analyzer.get_top_graph(algorithm='hits', direction='buyers', iterations=1, top_n=5)
    
    assert res["meta"]["weight_mode"] == "count"
    for edge in res["edges"]:
        assert "deals" in edge["weight_label"]
