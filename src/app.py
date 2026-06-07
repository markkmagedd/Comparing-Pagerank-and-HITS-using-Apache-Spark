from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer, get_available_leagues, preload_data
import os

# Initialize Spark once globally for the app lifespan
spark = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global spark
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("Transfer_Visualizer_API") \
        .config("spark.driver.memory", "4g") \
        .config("spark.driver.extraJavaOptions", "--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/javax.security.auth=ALL-UNNAMED") \
        .getOrCreate()
    
    # Warm up Spark cache by loading data once at startup
    preload_data(spark.sparkContext, "transfers.csv")
    
    yield
    import sys
    if spark and "pytest" not in sys.modules:
        spark.stop()

app = FastAPI(title="PageRank Transfer Visualizer", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

class CalculationRequest(BaseModel):
    direction: str = Field("buyers", pattern="^(buyers|sellers)$")
    iterations: int = Field(10, ge=1, le=50)
    damping_factor: float = Field(0.85, ge=0.0, le=1.0)
    top_n: int = Field(10, ge=1, le=50)
    league: str = Field("all", description="League name or 'all'")
    weight_mode: str = Field("fee", pattern="^(fee|count)$")
    algorithm: str = Field("pagerank", pattern="^(pagerank|hits)$")
    start_season: str = Field("all", description="Starting season or 'all'")
    end_season: str = Field("all", description="Ending season or 'all'")

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/analysis")
async def get_analysis(request: Request):
    return templates.TemplateResponse(request=request, name="analysis.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "spark_active": spark is not None}

import requests
from functools import lru_cache

# Top-tier mapping for instant high-quality logos
TOP_LOGOS = {
    "Man City": "https://www.thesportsdb.com/images/media/team/badge/8pt9i31548175510.png",
    "Paris SG": "https://www.thesportsdb.com/images/media/team/badge/7avf991515234503.png",
    "Barcelona": "https://www.thesportsdb.com/images/media/team/badge/v20p9p1512411984.png",
    "Real Madrid": "https://www.thesportsdb.com/images/media/team/badge/862p3h1515234254.png",
    "Liverpool": "https://www.thesportsdb.com/images/media/team/badge/098v681530725537.png",
    "Bayern": "https://www.thesportsdb.com/images/media/team/badge/7788v81515232759.png",
    "Juventus": "https://www.thesportsdb.com/images/media/team/badge/073t2a1534015697.png",
    "Atletico": "https://www.thesportsdb.com/images/media/team/badge/v77stf1515234283.png",
    "Man Utd": "https://www.thesportsdb.com/images/media/team/badge/9f4t051515233152.png",
    "Inter": "https://www.thesportsdb.com/images/media/team/badge/puyr6p1617462002.png",
    "Chelsea": "https://www.thesportsdb.com/images/media/team/badge/965f7i1560611413.png",
    "Dortmund": "https://www.thesportsdb.com/images/media/team/badge/0v8r081531086088.png",
    "Napoli": "https://www.thesportsdb.com/images/media/team/badge/qpwrxv1470404733.png",
    "Roma": "https://www.thesportsdb.com/images/media/team/badge/9d9ofn1515233216.png",
    "Arsenal": "https://www.thesportsdb.com/images/media/team/badge/909fyr1512409549.png",
    "Milan": "https://www.thesportsdb.com/images/media/team/badge/7fec2d1531088655.png",
    "Spurs": "https://www.thesportsdb.com/images/media/team/badge/099v3y1512409581.png",
    "Everton": "https://www.thesportsdb.com/images/media/team/badge/6v73v71550225139.png"
}

@lru_cache(maxsize=1000)
def search_club_logo_url(club_name: str):
    """
    Searches for a club logo URL using the public sports database API.
    """
    try:
        # Search API (API Key '3' is a public dev key)
        search_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={requests.utils.quote(club_name)}"
        resp = requests.get(search_url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            data = resp.json()
            if data.get('teams'):
                # Return the main badge URL
                return data['teams'][0].get('strTeamBadge')
    except Exception:
        pass
    return None

@lru_cache(maxsize=500)
def fetch_image_from_url(url: str):
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return resp.content, resp.headers.get('Content-Type', 'image/png')
    except Exception:
        pass
    return None, None

@app.get("/logo/{club_name}")
def get_club_logo(club_name: str):
    clean_name = club_name.strip()
    
    # 1. Try Hardcoded VIP First (Instant)
    VIP_LOGOS = {
        "Man City": "https://www.thesportsdb.com/images/media/team/badge/8pt9i31548175510.png",
        "Barcelona": "https://www.thesportsdb.com/images/media/team/badge/v20p9p1512411984.png",
        "Real Madrid": "https://www.thesportsdb.com/images/media/team/badge/862p3h1515234254.png",
        "Liverpool": "https://www.thesportsdb.com/images/media/team/badge/098v681530725537.png",
        "Bayern": "https://www.thesportsdb.com/images/media/team/badge/7788v81515232759.png",
        "Man Utd": "https://www.thesportsdb.com/images/media/team/badge/9f4t051515233152.png",
        "Arsenal": "https://www.thesportsdb.com/images/media/team/badge/909fyr1512409549.png",
        "Chelsea": "https://www.thesportsdb.com/images/media/team/badge/965f7i1560611413.png",
        "Spurs": "https://www.thesportsdb.com/images/media/team/badge/099v3y1512409581.png"
    }
    
    logo_url = None
    for key, url in VIP_LOGOS.items():
        if key.lower() in clean_name.lower():
            logo_url = url
            break
            
    # 2. Dynamic Search if not in VIP
    if not logo_url:
        logo_url = search_club_logo_url(clean_name)
        
    # 3. Proxy the result if found
    if logo_url:
        binary, content_type = fetch_image_from_url(logo_url)
        if binary:
            return Response(content=binary, media_type=content_type)
            
    # 4. Final Fallback: Styled SVG
    primary_color = "#3b82f6" # Default blue
    if any(k in clean_name.lower() for k in ["liverpool", "united", "milan", "madrid", "bayern"]):
        primary_color = "#ef4444" # Red
    elif any(k in clean_name.lower() for k in ["city", "napoli", "spurs", "inter"]):
        primary_color = "#38bdf8" # Sky blue
    
    initials = "".join([w[0] for w in clean_name.split()[:2]]).upper()
    svg = f"""<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="95" fill="#111827" stroke="{primary_color}" stroke-width="5"/>
        <text x="100" y="115" font-family="Arial, sans-serif" font-size="70" font-weight="bold" fill="{primary_color}" text-anchor="middle">{initials}</text>
    </svg>"""
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/league-flow")
async def process_league_flow(req: CalculationRequest):
    try:
        analyzer = TransferAnalyzer(
            spark, 
            "transfers.csv", 
            league=req.league, 
            weight_mode=req.weight_mode,
            start_season=req.start_season,
            end_season=req.end_season
        )
        result = analyzer.get_league_flow()
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/leagues")
def get_leagues():
    try:
        leagues = get_available_leagues(spark.sparkContext, "transfers.csv")
        return {"leagues": leagues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pagerank")
async def process_pagerank(req: CalculationRequest):
    try:
        analyzer = TransferAnalyzer(
            spark, 
            "transfers.csv", 
            league=req.league, 
            weight_mode=req.weight_mode,
            start_season=req.start_season,
            end_season=req.end_season
        )
        result = analyzer.get_top_graph(
            direction=req.direction,
            iterations=req.iterations,
            damping=req.damping_factor,
            top_n=req.top_n,
            algorithm=req.algorithm
        )
        
        # Format for Cytoscape.js and Chart.js
        cy_nodes = [{"data": {"id": n["id"], "label": n["id"], "rank": round(n["rank"], 4)}} for n in result["nodes"]]
        cy_edges = [{"data": e} for e in result["edges"]]

        return {
            "nodes": cy_nodes,
            "edges": cy_edges,
            "meta": result["meta"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transfers/{club_name}")
async def get_transfer_details(
    club_name: str, 
    top_n: int = 10,
    league: str = "all",
    weight_mode: str = "fee",
    start_season: str = "all",
    end_season: str = "all"
):
    try:
        analyzer = TransferAnalyzer(
            spark,
            "transfers.csv",
            league=league,
            weight_mode=weight_mode,
            start_season=start_season,
            end_season=end_season
        )
        transfers = analyzer.get_top_transfers(club_name, top_n)
        return {
            "club": club_name,
            "transfers": transfers
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rankings/historical")
async def get_historical_rankings(
    direction: str = "buyers",
    iterations: int = 10,
    damping_factor: float = 0.85,
    top_n: int = 10,
    league: str = "all",
    weight_mode: str = "fee",
    algorithm: str = "pagerank"
):
    try:
        analyzer = TransferAnalyzer(
            spark,
            "transfers.csv",
            league=league,
            weight_mode=weight_mode
        )
        timeline = analyzer.get_historical_timeline(
            direction=direction,
            iterations=iterations,
            damping=damping_factor,
            algorithm=algorithm,
            top_n=top_n
        )
        return {
            "status": "success",
            "data": {
                "algorithm": algorithm,
                "timeline": timeline
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
