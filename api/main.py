from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Serve static assets
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Serve HTML pages directly as files
@app.get("/")
def index():
    return FileResponse("dashboard/templates/index.html")

@app.get("/transaction")
def transaction():
    return FileResponse("dashboard/templates/transaction.html")

@app.get("/user")
def user():
    return FileResponse("dashboard/templates/user.html")

@app.get("/health")
def health():
    return {"status": "ok", "agents": {
        "detector": "online",
        "investigator": "online",
        "decision": "online"
    }}
