from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.texts import TYPES_DATA
import os

app = FastAPI()
router = APIRouter()

# API Endpoint to get types
@router.get("/api/types")
async def get_types():
    # Convert dataclasses to dicts
    return {k: v.__dict__ for k, v in TYPES_DATA.items()}

# Mount specific routes first
app.include_router(router)

# Serve static files
# We need to get absolute path to avoid issues
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))

# For detailed view if we want deep linking in future
@app.get("/type/{type_id}")
async def read_type_page(type_id: str):
    return FileResponse(os.path.join(static_path, "index.html"))
