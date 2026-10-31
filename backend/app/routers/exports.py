from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List
import os
import json

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get("/csv")
def download_csv(table_name: str = "skus"):
    """
    Downloads CSV export for a specific table.
    """
    file_path = os.path.join("data", "exports", f"{table_name}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Export for {table_name}.csv not found.")
    return FileResponse(file_path, media_type="text/csv", filename=f"{table_name}.csv")

@router.get("/json")
def download_json(table_name: str = "skus"):
    file_path = os.path.join("data", "exports", f"{table_name}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Export for {table_name}.json not found.")
    return FileResponse(file_path, media_type="application/json", filename=f"{table_name}.json")

@router.get("/ground-truth")
def get_ground_truth_json() -> List[Dict[str, Any]]:
    path = os.path.join("data", "ground_truth", "ground_truth.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Ground truth file not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
