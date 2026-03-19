from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pyspark.sql import SparkSession
from src.core.processing import TransferAnalyzer, get_available_leagues
import os

# Initialize Spark once globally for the app lifespan
spark = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global spark
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("Transfer_Visualizer_API") \
        .config("spark.driver.memory", "2g") \
        .config("spark.driver.extraJavaOptions", "--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/javax.security.auth=ALL-UNNAMED") \
        .getOrCreate()
    yield
    if spark:
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

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    return {"status": "ok", "spark_active": spark is not None}

@app.get("/api/leagues")
def get_leagues():
    try:
        leagues = get_available_leagues(spark.sparkContext, "transfers.csv")
        return {"leagues": leagues}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pagerank")
async def process_pagerank(req: CalculationRequest):
    try:
        analyzer = TransferAnalyzer(spark, "transfers.csv", league=req.league, weight_mode=req.weight_mode)
        result = analyzer.get_top_graph(
            direction=req.direction,
            iterations=req.iterations,
            damping=req.damping_factor,
            top_n=req.top_n
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
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
