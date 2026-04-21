from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .design_md import generate_design_md
from .extractor import extract_pptx
from .models import (
    BatchExtractResponse,
    BatchItemResponse,
    ExtractResponse,
    SaveEditedDesignRequest,
    SaveEditedDesignResponse,
)
from .storage import save_edited_design, save_run

app = FastAPI(title="pptx-design-md", version="0.1.0")
MAX_UPLOAD_BYTES = int(os.getenv("PPTX_MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))
MAX_BATCH_FILES = int(os.getenv("PPTX_MAX_BATCH_FILES", "10"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("PPTX_ALLOWED_ORIGINS", "http://127.0.0.1:4173,http://localhost:4173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' http://127.0.0.1:8000 http://localhost:8000; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com;"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):  # pragma: no cover
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract(file: UploadFile = File(...)) -> ExtractResponse:
    suffix = Path(file.filename or "upload").suffix.lower()
    if suffix != ".pptx":
        raise HTTPException(status_code=400, detail="Only .pptx files are supported")
    if file.content_type and file.content_type not in {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/octet-stream",
    }:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds size limit")
    if not data.startswith(b"PK"):
        raise HTTPException(status_code=400, detail="Invalid PPTX file content")

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=True) as tmp:
        tmp.write(data)
        tmp.flush()
        try:
            analysis = extract_pptx(tmp.name)
            design_md = generate_design_md(analysis)
            run_id = save_run(file.filename or "upload.pptx", design_md, analysis)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Could not parse PPTX file") from exc

    return ExtractResponse(design_md=design_md, analysis=analysis, run_id=run_id)


@app.post("/extract/batch", response_model=BatchExtractResponse)
async def extract_batch(files: list[UploadFile] = File(...)) -> BatchExtractResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(status_code=400, detail=f"Batch limit exceeded (max {MAX_BATCH_FILES})")

    results: list[BatchItemResponse] = []
    for file in files:
        suffix = Path(file.filename or "upload").suffix.lower()
        if suffix != ".pptx":
            raise HTTPException(status_code=400, detail=f"Only .pptx files are supported: {file.filename}")
        if file.content_type and file.content_type not in {
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/octet-stream",
        }:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.filename}")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail=f"Uploaded file is empty: {file.filename}")
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Uploaded file exceeds size limit: {file.filename}")
        if not data.startswith(b"PK"):
            raise HTTPException(status_code=400, detail=f"Invalid PPTX file content: {file.filename}")
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            try:
                analysis = extract_pptx(tmp.name)
                design_md = generate_design_md(analysis)
                run_id = save_run(file.filename or "upload.pptx", design_md, analysis)
            except Exception as exc:
                raise HTTPException(status_code=422, detail=f"Could not parse file: {file.filename}") from exc
        results.append(
            BatchItemResponse(
                filename=file.filename or "upload.pptx",
                design_md=design_md,
                analysis=analysis,
                run_id=run_id,
            )
        )

    return BatchExtractResponse(results=results)


@app.post("/design/save", response_model=SaveEditedDesignResponse)
def save_design(request: SaveEditedDesignRequest) -> SaveEditedDesignResponse:
    if not request.design_md.strip():
        raise HTTPException(status_code=400, detail="design_md cannot be empty")
    try:
        saved = save_edited_design(request.run_id, request.design_md)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SaveEditedDesignResponse(run_id=request.run_id, saved_path=str(saved))
