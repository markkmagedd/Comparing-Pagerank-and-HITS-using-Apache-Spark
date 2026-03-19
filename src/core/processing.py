import csv
from operator import add
from pyspark.sql import SparkSession

def parse_csv_line(line):
    """
    Parses a single CSV line into a list of columns.
    """
    return next(csv.reader([line]))

def parse_fee(val):
    """
    Parses a fee string into a float, defaulting to 100k if invalid.
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return 100000.0

def compute_contributions(edges_with_weights, rank):
    """
    Computes PageRank contributions for edges from a node.
    """
    # Calculate the total mathematical weight leaving the node
    total_weight = sum([weight for dst, weight in edges_with_weights])
    
    # Distribute the rank proportionally based on the fee weight
    for dst, weight in edges_with_weights:
        if total_weight > 0:
            yield (dst, rank * (weight / total_weight))
        else:
            yield (dst, rank / len(edges_with_weights))

def run_pagerank(edges_rdd, iterations=10, damping=0.85):
    """
    Executes the PageRank algorithm on an RDD of (source, (destination, weight)).
    """
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
def get_available_leagues(sc, file_path="transfers.csv"):
    """
    Parses the CSV data and returns a sorted list of unique league names.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines_list = f.readlines()
    
    lines = sc.parallelize(lines_list)
    header = lines.first()
    data = lines.filter(lambda row: row != header).map(parse_csv_line)
    
    # Union of League_from (x[4]) and League_to (x[6])
    leagues_from = data.map(lambda x: x[4].strip())
    leagues_to = data.map(lambda x: x[6].strip())
    
    all_leagues = leagues_from.union(leagues_to).distinct().collect()
    return sorted([l for l in all_leagues if l])

class TransferAnalyzer:
    """
    Main class for loading transfer data and calculating rankings.
    """
    def __init__(self, spark: SparkSession, file_path: str = "transfers.csv", league: str = "all", weight_mode: str = "fee"):
        self.spark = spark
        self.sc = spark.sparkContext
        self.file_path = file_path
        self.league = league
        self.weight_mode = weight_mode
        self.transfers = None
        self._load_data()

    def _load_data(self):
        """
        Loads and parses the CSV data into an RDD of transfers.
        Using Python built-in to load small file (532K) to bypass Hadoop FileSystem getSubject compatibility issues on Java 25+.
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines_list = f.readlines()
        
        lines = self.sc.parallelize(lines_list)
        header = lines.first()
        data = lines.filter(lambda row: row != header).map(parse_csv_line)
        
        # Extract into local variables to avoid serializing 'self' (which contains SparkContext) 
        # in the lambda closures.
        active_league = self.league
        active_weight_mode = self.weight_mode

        # Apply League Filter (Intra-league)
        if active_league != "all":
            data = data.filter(lambda x: x[4].strip() == active_league and x[6].strip() == active_league)

        # Map to weight mode
        if active_weight_mode == "count":
            # Mapping format: ((Team_from, Team_to), 1.0)
            mapped_data = data.map(lambda x: ((x[3].strip(), x[5].strip()), 1.0))
        else:
            # Mapping format: ((Team_from, Team_to), Total_Fee)
            mapped_data = data.map(lambda x: ((x[3].strip(), x[5].strip()), parse_fee(x[9])))

        self.transfers = mapped_data.reduceByKey(add).cache()

    def get_rankings(self, direction='buyers', iterations=10, damping=0.85):
        """
        Computes either Buyer or Seller PageRank.
        """
        if direction == 'buyers':
            # Seller -> Buyer
            edges = self.transfers.map(lambda x: (x[0][0], (x[0][1], x[1])))
        else:
            # Buyer -> Seller
            edges = self.transfers.map(lambda x: (x[0][1], (x[0][0], x[1])))
            
        ranks = run_pagerank(edges, iterations, damping)
        return ranks

    def get_top_graph(self, direction='buyers', iterations=10, damping=0.85, top_n=10):
        """
        Computes ranks and extracts the top N nodes + their edges for visualization.
        """
        ranks = self.get_rankings(direction, iterations, damping)
        top_ranks = ranks.takeOrdered(top_n, key=lambda x: -x[1])
        top_node_ids = set([x[0] for x in top_ranks])
        
        # Extract into local variable to avoid serializing 'self'
        active_weight_mode = self.weight_mode

        # Filter transfers involving at least one of the top nodes
        # For simplicity in graph render, we'll only show edges between top nodes
        if direction == 'buyers':
            # Edge source is Team_from, target is Team_to
            filtered_edges = self.transfers.filter(lambda x: x[0][0] in top_node_ids and x[0][1] in top_node_ids)
            edges_list = filtered_edges.map(lambda x: {
                "source": x[0][0],
                "target": x[0][1],
                "weight": x[1],
                "weight_label": f"€{x[1]/1000000:.0f}M" if active_weight_mode == "fee" else f"{int(x[1])} deals"
            }).collect()
        else:
            # Direction is seller, so source is Team_to, target is Team_from in original data sense
            filtered_edges = self.transfers.filter(lambda x: x[0][1] in top_node_ids and x[0][0] in top_node_ids)
            edges_list = filtered_edges.map(lambda x: {
                "source": x[0][1],
                "target": x[0][0],
                "weight": x[1],
                "weight_label": f"€{x[1]/1000000:.0f}M" if active_weight_mode == "fee" else f"{int(x[1])} deals"
            }).collect()

        nodes_list = [{"id": club, "rank": rank} for club, rank in top_ranks]
        
        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "meta": {
                "league": self.league,
                "weight_mode": self.weight_mode,
                "total_records": self.transfers.count(),
                "empty": len(nodes_list) == 0
            }
        }
