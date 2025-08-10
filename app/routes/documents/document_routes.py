from fastapi import APIRouter, UploadFile, File, HTTPException
import os, shutil
from app.utils.pdf_processor import process_pdf
from app.utils.dbConn import get_connection
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/documents", tags=["Documents"])
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten PDFs")
    saved = os.path.join(TEMP_DIR, file.filename)
    with open(saved, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = process_pdf(saved)   # esto ddevuelve {'text': '...'}
    text = result["text"]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documentos (nombre, contenido) VALUES (%s, %s)",
                (file.filename, text)
            )
        conn.commit()
    finally:
        conn.close()

    os.remove(saved)
    return {"status": "ok", "text_preview": text[:800]}
