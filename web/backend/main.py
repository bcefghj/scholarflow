"""ScholarFlow Web Backend - FastAPI application."""

from __future__ import annotations

import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="ScholarFlow",
    description="The ultimate academic paper processing tool",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
OUTPUT_DIR = Path("data/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tasks_status: dict[str, dict] = {}


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/process")
async def process_paper(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    arxiv: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    lang: str = Form("zh"),
    verbosity: str = Form("normal"),
    notes_mode: str = Form("deep"),
    outputs: str = Form("summary,slides,script,notes"),
):
    """Submit a paper for processing. Returns a task ID."""
    task_id = str(uuid.uuid4())[:8]
    task_output = OUTPUT_DIR / task_id
    task_output.mkdir(parents=True, exist_ok=True)

    pdf_path = None
    if file:
        pdf_path = str(UPLOAD_DIR / f"{task_id}_{file.filename}")
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)

    tasks_status[task_id] = {"status": "processing", "outputs": {}}
    generate_list = [o.strip() for o in outputs.split(",") if o.strip()]

    background_tasks.add_task(
        _run_pipeline,
        task_id=task_id,
        pdf_path=pdf_path,
        title=title,
        arxiv=arxiv,
        doi=doi,
        output_dir=str(task_output),
        model=model,
        lang=lang,
        verbosity=verbosity,
        notes_mode=notes_mode,
        generate=generate_list,
    )

    return {"task_id": task_id, "status": "processing"}


def _run_pipeline(task_id: str, **kwargs):
    try:
        from scholarflow.pipeline import run_full_pipeline
        results = run_full_pipeline(**kwargs)
        tasks_status[task_id] = {
            "status": "completed",
            "outputs": {k: str(v) for k, v in results.items()},
        }
    except Exception as e:
        tasks_status[task_id] = {"status": "error", "error": str(e)}


@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    if task_id not in tasks_status:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return tasks_status[task_id]


@app.get("/api/download/{task_id}")
def download_all(task_id: str):
    """Download all outputs as a ZIP file."""
    task_output = OUTPUT_DIR / task_id
    if not task_output.exists():
        return JSONResponse(status_code=404, content={"error": "Output not found"})

    zip_path = OUTPUT_DIR / f"{task_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in task_output.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(task_output))

    return FileResponse(zip_path, filename=f"scholarflow_{task_id}.zip")


@app.get("/api/download/{task_id}/{filename}")
def download_file(task_id: str, filename: str):
    """Download a specific output file."""
    fpath = OUTPUT_DIR / task_id / filename
    if not fpath.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(fpath, filename=filename)
