import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import init_db, save_inspection, get_all_inspections, get_inspection_by_id
from detection import run_detection
from report_generator import generate_word_report, generate_pdf_report
from llm_client import generate_llm_report

app = FastAPI(title="Civil AI Inspection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
REPORT_DIR = Path("reports")

for d in [UPLOAD_DIR, OUTPUT_DIR, REPORT_DIR]:
    d.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.on_event("startup")
async def startup():
    init_db()

class DetectionRequest(BaseModel):
    image_id: str
    model_name: str
    asset_type: str

class ReportRequest(BaseModel):
    inspection_id: str
    engineer_notes: Optional[str] = ""

@app.get("/")
def root():
    return {"message": "Civil AI Inspection API", "version": "1.0.0"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    allowed = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".mp4", ".avi", ".mov"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    image_id = str(uuid.uuid4())
    filename = f"{image_id}{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "image_id": image_id,
        "filename": file.filename,
        "saved_as": filename,
        "url": f"/uploads/{filename}",
        "size": os.path.getsize(filepath)
    }

@app.post("/detect")
async def detect(request: DetectionRequest):
    ext_map = {}
    for f in UPLOAD_DIR.iterdir():
        if f.stem == request.image_id:
            ext_map[request.image_id] = f
            break

    if request.image_id not in ext_map:
        raise HTTPException(404, "Image not found")

    image_path = ext_map[request.image_id]

    try:
        results = run_detection(
            image_path=str(image_path),
            model_name=request.model_name,
            output_dir=str(OUTPUT_DIR),
            image_id=request.image_id
        )
    except Exception as e:
        raise HTTPException(500, f"Detection failed: {str(e)}")

    inspection_id = str(uuid.uuid4())
    inspection_data = {
        "id": inspection_id,
        "image_id": request.image_id,
        "original_filename": str(image_path.name),
        "model_name": request.model_name,
        "asset_type": request.asset_type,
        "detections": results["detections"],
        "annotated_image": results.get("annotated_image", ""),
        "total_defects": results["total_defects"],
        "severity_summary": results["severity_summary"],
        "created_at": datetime.utcnow().isoformat(),
        "engineer_notes": "",
        "report_docx": "",
        "report_pdf": ""
    }
    save_inspection(inspection_data)

    return {"inspection_id": inspection_id, **results}

@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    inspection = get_inspection_by_id(request.inspection_id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")

    inspection["engineer_notes"] = request.engineer_notes or ""

    try:
        ai_report = generate_llm_report(
            asset_type=inspection["asset_type"],
            model_name=inspection["model_name"],
            detections=inspection["detections"],
            engineer_notes=inspection["engineer_notes"]
        )
    except Exception as e:
        ai_report = {
            "executive_summary": f"AI report generation unavailable: {str(e)}",
            "defect_descriptions": "Manual review required.",
            "possible_causes": "To be determined.",
            "severity_assessment": "To be assessed.",
            "risk_explanation": "To be evaluated.",
            "recommended_actions": "Consult a qualified civil engineer.",
            "priority_level": "Medium",
            "final_conclusion": "Manual inspection required."
        }

    docx_path = REPORT_DIR / f"{request.inspection_id}.docx"
    pdf_path = REPORT_DIR / f"{request.inspection_id}.pdf"

    generate_word_report(inspection, ai_report, str(docx_path))
    generate_pdf_report(inspection, ai_report, str(pdf_path))

    inspection["engineer_notes"] = request.engineer_notes or ""
    inspection["report_docx"] = str(docx_path)
    inspection["report_pdf"] = str(pdf_path)
    inspection["ai_report"] = ai_report
    save_inspection(inspection)

    return {
        "inspection_id": request.inspection_id,
        "ai_report": ai_report,
        "docx_url": f"/download/docx/{request.inspection_id}",
        "pdf_url": f"/download/pdf/{request.inspection_id}"
    }

@app.get("/download/docx/{report_id}")
async def download_docx(report_id: str):
    path = REPORT_DIR / f"{report_id}.docx"
    if not path.exists():
        raise HTTPException(404, "Report not found")
    return FileResponse(str(path), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        filename=f"inspection_report_{report_id[:8]}.docx")

@app.get("/download/pdf/{report_id}")
async def download_pdf(report_id: str):
    path = REPORT_DIR / f"{report_id}.pdf"
    if not path.exists():
        raise HTTPException(404, "Report not found")
    return FileResponse(str(path), media_type="application/pdf",
                        filename=f"inspection_report_{report_id[:8]}.pdf")

@app.get("/inspections")
async def list_inspections():
    return get_all_inspections()

@app.get("/inspection/{id}")
async def get_inspection(id: str):
    inspection = get_inspection_by_id(id)
    if not inspection:
        raise HTTPException(404, "Inspection not found")
    return inspection

@app.get("/models")
async def list_models():
    from model_loader import get_available_models
    return get_available_models()
