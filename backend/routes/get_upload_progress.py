import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.utiles.upload_process_track import get_progress

from fastapi import APIRouter

router = APIRouter()

@router.get("/progress/{job_id}")
async def get_progress_endpoint(job_id: str):
    print("get_progress:", get_progress(job_id))
    return {"progress": get_progress(job_id)}