import csv
import math
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

# Global cache for the pre-loaded transfers RDD
_CACHED_DATA = None

def preload_data(sc, file_path="transfers.csv"):
    """
    Load data precisely once and store in memory.
    """
    global _CACHED_DATA
    if _CACHED_DATA is not None:
        return _CACHED_DATA

    with open(file_path, 'r', encoding='utf-8') as f:
        lines_list = f.readlines()
    
    lines = sc.parallelize(lines_list)
    header = lines.first()
    _CACHED_DATA = lines.filter(lambda row: row != header).map(parse_csv_line).cache()
    # Force evaluation to ensure it's in memory before any request
    _CACHED_DATA.count()
    return _CACHED_DATA

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

def run_hits(edges_rdd, iterations=10):
    """
    Executes the HITS algorithm on an RDD of (source, (destination, weight)).
    Returns a tuple of (authorities, hubs) RDDs.
    
    Uses a broadcast-based approach to avoid the shuffle explosion that
    occurs with repeated RDD joins in a loop.
    """
    sc = edges_rdd.context
    
    # Build adjacency lists once and cache them
    # forward_links: (source, [(dest, weight), ...])
    # reverse_links: (dest, [(source, weight), ...])
    forward_links = edges_rdd.groupByKey().mapValues(list).cache()
    reverse_links = edges_rdd.map(
        lambda x: (x[1][0], (x[0], x[1][1]))
    ).groupByKey().mapValues(list).cache()
    
    # Force materialization of cached adjacency lists
    forward_links.count()
    reverse_links.count()
    
    # Collect all node IDs
    all_nodes = edges_rdd.flatMap(lambda x: [x[0], x[1][0]]).distinct().collect()
    
    # Initialize scores as simple dicts
    hub_scores = {node: 1.0 for node in all_nodes}
    auth_scores = {node: 1.0 for node in all_nodes}
    
    for i in range(iterations):
        # --- Authority update: a(u) = sum(h(v) * w(v->u)) for all v pointing to u ---
        # Broadcast current hub scores
        hub_bc = sc.broadcast(hub_scores)
        
        # For each (dest, [(src, w), ...]) compute new authority score
        new_auth = reverse_links.mapValues(
            lambda neighbors: sum(hub_bc.value.get(src, 0.0) * w for src, w in neighbors)
        ).collect()
        
        hub_bc.destroy()
        
        # Normalize authorities (L2 norm)
        a_sq_sum = sum(score ** 2 for _, score in new_auth)
        a_norm = math.sqrt(a_sq_sum)
        if a_norm > 0:
            auth_scores = {node: score / a_norm for node, score in new_auth}
        else:
            auth_scores = {node: score for node, score in new_auth}
        
        # --- Hub update: h(u) = sum(a(v) * w(u->v)) for all v that u points to ---
        # Broadcast current authority scores
        auth_bc = sc.broadcast(auth_scores)
        
        # For each (source, [(dest, w), ...]) compute new hub score
        new_hubs = forward_links.mapValues(
            lambda neighbors: sum(auth_bc.value.get(dest, 0.0) * w for dest, w in neighbors)
        ).collect()
        
        auth_bc.destroy()
        
        # Normalize hubs (L2 norm)
        h_sq_sum = sum(score ** 2 for _, score in new_hubs)
        h_norm = math.sqrt(h_sq_sum)
        if h_norm > 0:
            hub_scores = {node: score / h_norm for node, score in new_hubs}
        else:
            hub_scores = {node: score for node, score in new_hubs}
    
    # Convert final dicts back to RDDs for compatibility with the rest of the code
    authorities = sc.parallelize(list(auth_scores.items()))
    hubs = sc.parallelize(list(hub_scores.items()))
    
    # Unpersist adjacency lists
    forward_links.unpersist()
    reverse_links.unpersist()
    
    return authorities, hubs

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
    def __init__(self, spark: SparkSession, file_path: str = "transfers.csv", 
                 league: str = "all", weight_mode: str = "fee",
                 start_season: str = "all", end_season: str = "all"):
        self.spark = spark
        self.sc = spark.sparkContext
        self.file_path = file_path
        self.league = league
        self.weight_mode = weight_mode
        self.start_season = start_season
        self.end_season = end_season
        self.transfers = None
        self._load_data()

    def _load_data(self):
        """
        Loads and parses the CSV data into an RDD of transfers.
        Uses cached data if available, otherwise performs lazy loading.
        """
        global _CACHED_DATA
        if _CACHED_DATA is not None:
            data = _CACHED_DATA
        else:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines_list = f.readlines()
            
            lines = self.sc.parallelize(lines_list)
            header = lines.first()
            data = lines.filter(lambda row: row != header).map(parse_csv_line)
        
        # Extract into local variables to avoid serializing 'self' (which contains SparkContext) 
        # in the lambda closures.
        active_league = self.league
        active_weight_mode = self.weight_mode
        s_start = self.start_season
        s_end = self.end_season

        # Apply Season Filter
        # Seasons are '2000-2001' format. They are chronological in alphabetical sort.
        if s_start != "all":
            data = data.filter(lambda x: x[7] >= s_start)
        if s_end != "all":
            data = data.filter(lambda x: x[7] <= s_end)

        # Apply League Filter (Intra-league)
        if active_league != "all":
            data = data.filter(lambda x: x[4].strip() == active_league and x[6].strip() == active_league)

        # Cache the filtered raw RDD for multi-purpose analysis (e.g. League Flow)
        self.data_rdd = data.cache()
        
        # Map to weight mode
        if active_weight_mode == "count":
            # Mapping format: ((Team_from, Team_to), 1.0)
            mapped_data = self.data_rdd.map(lambda x: ((x[3].strip(), x[5].strip()), 1.0))
        else:
            # Mapping format: ((Team_from, Team_to), Total_Fee)
            mapped_data = self.data_rdd.map(lambda x: ((x[3].strip(), x[5].strip()), parse_fee(x[9])))

        self.transfers = mapped_data.reduceByKey(add).cache()

    def get_rankings(self, direction='buyers', iterations=10, damping=0.85, algorithm="pagerank"):
        """
        Computes either Buyer or Seller rankings using specified algorithm.
        """
        # HITS uses the same edge list for both hubs and authorities (Seller -> Buyer)
        primary_edges = self.transfers.map(lambda x: (x[0][0], (x[0][1], x[1])))

        if algorithm == "hits":
            authorities, hubs = run_hits(primary_edges, iterations)
            return authorities if direction == 'buyers' else hubs
        else:
            if direction == 'buyers':
                # Seller -> Buyer
                edges = primary_edges
            else:
                # Buyer -> Seller (PageRank in reverse)
                edges = self.transfers.map(lambda x: (x[0][1], (x[0][0], x[1])))
                
            ranks = run_pagerank(edges, iterations, damping)
            return ranks

    def get_top_graph(self, direction='buyers', iterations=10, damping=0.85, top_n=10, algorithm="pagerank"):
        """
        Computes ranks and extracts the top N nodes + their edges for visualization.
        """
        ranks = self.get_rankings(direction, iterations, damping, algorithm)
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
        
        score_type = "pagerank"
        if algorithm == "hits":
            score_type = "authority" if direction == "buyers" else "hub"

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "meta": {
                "league": self.league,
                "weight_mode": self.weight_mode,
                "total_records": self.transfers.count(),
                "empty": len(nodes_list) == 0,
                "algorithm": algorithm,
                "score_type": score_type,
                "season_range": f"{self.start_season} to {self.end_season}" if self.start_season != "all" or self.end_season != "all" else "All Seasons"
            }
        }

    def get_league_flow(self):
        """
        Computes flow between leagues, grouping minor leagues into 'Other' for visual clarity.
        """
        active_weight_mode = self.weight_mode
        
        # 1. First, get all raw flows
        if active_weight_mode == "count":
            raw_flow_rdd = self.data_rdd.map(lambda x: ((x[4].strip(), x[6].strip()), 1.0))
        else:
            raw_flow_rdd = self.data_rdd.map(lambda x: ((x[4].strip(), x[6].strip()), parse_fee(x[9])))
            
        league_flows_raw = raw_flow_rdd.reduceByKey(add).collect()
        
        # 2. Identify "Top Leagues" to avoid the 'spaghetti' look
        # Calculate total volume per league (sum of in and out)
        league_totals = {}
        for (l_from, l_to), weight in league_flows_raw:
            league_totals[l_from] = league_totals.get(l_from, 0) + weight
            league_totals[l_to] = league_totals.get(l_to, 0) + weight
            
        # Keep top 15 leagues by volume
        top_leagues = sorted(league_totals.items(), key=lambda x: x[1], reverse=True)[:15]
        top_names = {name for name, total in top_leagues}
        
        # 3. Component-ize: Map small leagues to 'Other' and re-aggregate
        flow_map = {}
        for (l_from, l_to), weight in league_flows_raw:
            final_from = l_from if l_from in top_names else "Other"
            final_to = l_to if l_to in top_names else "Other"
            
            # Skip circular 'Other' to 'Other' flows to keep it clean
            if final_from == "Other" and final_to == "Other":
                continue
                
            key = (final_from, final_to)
            flow_map[key] = flow_map.get(key, 0) + weight
            
        flow_list = []
        for (f_f, f_t), weight in flow_map.items():
            if weight > 0:
                flow_list.append({
                    "from": f_f,
                    "to": f_t,
                    "flow": weight
                })
                
        return {
            "flows": flow_list,
            "meta": {
                "league": self.league,
                "weight_mode": self.weight_mode,
                "total_records": self.data_rdd.count(),
                "top_leagues_count": len(top_names),
                "season_range": f"{self.start_season} to {self.end_season}" if self.start_season != "all" or self.end_season != "all" else "All Seasons"
            }
        }

    def get_historical_timeline(self, direction='buyers', iterations=10, damping=0.85, algorithm="pagerank", top_n=10):
        """
        Computes rankings year-by-year and returns a timeline of top N clubs.
        """
        # 1. Identify all available years in the dataset (Filtered by current league/season settings)
        years_rdd = self.data_rdd.map(lambda x: x[7].split('-')[0]) \
                             .filter(lambda y: y.isdigit()) \
                             .distinct()
                             
        years = sorted([int(y) for y in years_rdd.collect()])
        
        timeline = []
        
        # 2. Sequential calculation for each year
        for year in years:
            season_prefix = str(year)
            # Filter specifically by the start year of the season
            year_rdd = self.data_rdd.filter(lambda x: x[7].startswith(season_prefix))
            
            if year_rdd.isEmpty():
                continue
            
            # Map weights based on mode
            if self.weight_mode == "count":
                mapped_data = year_rdd.map(lambda x: ((x[3].strip(), x[5].strip()), 1.0))
            else:
                mapped_data = year_rdd.map(lambda x: ((x[3].strip(), x[5].strip()), parse_fee(x[9])))
            
            consolidated_year = mapped_data.reduceByKey(add).cache()
            
            # Prepare edges for algorithm
            primary_edges = consolidated_year.map(lambda x: (x[0][0], (x[0][1], x[1])))
            
            if algorithm == "hits":
                authorities, hubs = run_hits(primary_edges, iterations)
                ranks = authorities if direction == 'buyers' else hubs
            else:
                if direction == 'buyers':
                    edges = primary_edges
                else:
                    edges = consolidated_year.map(lambda x: (x[0][1], (x[0][0], x[1])))
                ranks = run_pagerank(edges, iterations, damping)
            
            top_ranks = ranks.takeOrdered(top_n, key=lambda x: -x[1])
            
            timeline.append({
                "year": year,
                "season": f"{year}-{year+1}",
                "clubs": [
                    {
                        "club_id": club,
                        "club_name": club,
                        "score": round(rank, 6),
                        "rank": i + 1
                    } for i, (club, rank) in enumerate(top_ranks)
                ]
            })
            
            consolidated_year.unpersist()
            
        return timeline

    def get_top_transfers(self, club_name, top_n=10):
        """
        Returns the top_n most expensive transfers (bought or sold) for a specific club.
        It uses the already-filtered self.data_rdd (based on league/season range).
        """
        # Filter all transfers where the provided club is either buyer or seller
        # within the current active data set (league/season filter already applied)
        club_transfers = self.data_rdd.filter(lambda x: x[3].strip() == club_name or x[5].strip() == club_name)
        
        # Map to common structure for pop-up rendering
        def map_transfer_row(row):
            from src.core.processing import parse_fee # Needed for serializing correctly? 
            # Wait, parse_fee is a top level function, but in Spark lambdas sometimes we hit serialization issues.
            # But the other functions use it fine.
            player_name = row[0].strip()
            fee = parse_fee(row[9])
            if row[3].strip() == club_name:
                return (player_name, fee, row[5].strip(), 'out') # Sold
            else:
                return (player_name, fee, row[3].strip(), 'in')  # Bought

        mapped_transfers = club_transfers.map(map_transfer_row)
        
        # Sort by fee desc and take top N
        top_transfers_list = mapped_transfers.takeOrdered(top_n, key=lambda x: -x[1])
        
        return [
            {
                "player_name": t[0],
                "fee": t[1],
                "counterparty_club": t[2],
                "direction": t[3]
            } for t in top_transfers_list
        ]
