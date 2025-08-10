import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils.dbConn import get_db_connection
from app.utils.pdf_processor import process_pdf
from mysql.connector import MySQLConnection

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    connection: MySQLConnection = Depends(get_db_connection)
):
    """
    esto hace que se sube un PDF lo procesa y guarda en la tabla `documentos`.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF...")

    # Guarda temporalmente el archivo
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Procesa el PDF
    extracted_data = process_pdf(file_path)
    contenido = extracted_data["text"]

    # Guarda en la base de datos
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO documentos (nombre, contenido) VALUES (%s, %s)",
            (file.filename, contenido)
        )
        connection.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando en DB: {e}")
    finally:
        cursor.close()
        if os.path.exists(file_path):
            os.remove(file_path)  # Limpia el archivo temporal

    return {"message": "Documento subido y procesado correctamente"}


@router.get("/")
def list_documents(connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, fecha_subida FROM documentos ORDER BY fecha_subida DESC")
    documentos = cursor.fetchall()
    cursor.close()
    return {"documentos": documentos}


@router.get("/{document_id}")
def get_document(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, contenido, fecha_subida FROM documentos WHERE id = %s", (document_id,))
    documento = cursor.fetchone()
    cursor.close()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado...")
    return documento
