from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import health, analyze, dashboard

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(dashboard.router, prefix="/dashboard")
