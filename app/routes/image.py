import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
import aiofiles
from pathlib import Path
import uuid
from fastapi.responses import StreamingResponse
from app.services.image_processing import remove_background, enhance_image
from app.services.progress_manager import progress_manager
from app.services.celery_worker import remove_background_task
from fastapi import BackgroundTasks
from fastapi_cache.decorator import cache

router = APIRouter()

UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure upload directory exists
PROCESSED_DIR = Path("app/static/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure processed directory exists

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validate file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPG, and WEBP are allowed.")

    file_path = UPLOAD_DIR / file.filename

    # Async save file
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    return {"filename": file.filename, "path": str(file_path)}

@router.post("/process")
@cache(expire=60 * 60)  # Cache result for 1 hour
async def process_image(filename: str, action: str):
    """
    Processes an image with AI-based background removal or enhancement.
    Returns a task ID for real-time progress updates.
    """
    input_path = UPLOAD_DIR / filename
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    output_path = PROCESSED_DIR / f"processed_{filename}"

    if action == "remove_bg":
        task = remove_background_task.apply_async(args=[str(input_path), str(output_path)])
    else:
        raise HTTPException(status_code=400, detail="Invalid action.")

    return {"task_id": task.id, "message": "Processing started in background."}


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Streams real-time progress updates for an image processing task.
    """
    async def event_generator():
        async for progress in progress_manager.get_progress_stream(task_id):
            yield f"data: {progress}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")