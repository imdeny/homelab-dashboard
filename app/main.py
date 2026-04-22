from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import system, containers, stocks, deals
import json, os

app = FastAPI(title="Homelab Dashboard")

app.include_router(system.router, prefix="/api/system")
app.include_router(containers.router, prefix="/api/containers")
app.include_router(stocks.router, prefix="/api/stocks")
app.include_router(deals.router, prefix="/api/deals")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/api/config")
def get_config():
    with open("config.json") as f:
        return json.load(f)


@app.get("/")
def index():
    return FileResponse("app/static/index.html")
