from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from scripts.generate_data import SyntheticDataGenerator
from scripts.export_data import export_all

router = APIRouter(prefix="/data-generation", tags=["Data Generation"])

# Simple in-memory tracker for generation jobs
generation_state = {
    "status": "IDLE",  # IDLE, RUNNING, COMPLETED, FAILED
    "mode": None,
    "last_run": None,
    "message": "Ready"
}

class GenerationRequest(BaseModel):
    mode: str = "starter"  # starter or full
    seed: int = 20261022

def _run_generator_task(mode: str, seed: int):
    global generation_state
    try:
        generation_state["status"] = "RUNNING"
        generation_state["mode"] = mode
        generation_state["message"] = f"Generating dataset in {mode} mode..."
        
        gen = SyntheticDataGenerator(mode=mode, seed=seed)
        gen.run()
        export_all()

        generation_state["status"] = "COMPLETED"
        generation_state["message"] = f"Successfully generated and exported {mode} dataset."
    except Exception as e:
        generation_state["status"] = "FAILED"
        generation_state["message"] = f"Data generation error: {str(e)}"

@router.post("/run")
def trigger_data_generation(req: GenerationRequest, background_tasks: BackgroundTasks):
    global generation_state
    if generation_state["status"] == "RUNNING":
        raise HTTPException(status_code=409, detail="A data generation job is already in progress.")
    
    background_tasks.add_task(_run_generator_task, req.mode, req.seed)
    return {"message": f"Data generation initiated in {req.mode} mode", "seed": req.seed}

@router.get("/status")
def get_generation_status():
    return generation_state

@router.get("/report")
def get_generation_manifest() -> Dict[str, Any]:
    manifest_path = os.path.join("data", "manifests", "manifest.json")
    if not os.path.exists(manifest_path):
        return {"error": "Manifest file not found. Run data generation first."}
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)
