import os
import json
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.utils.dbConn import get_db_connection
from app.utils.PdfProcessor import process_pdf_with_metadata
from mysql.connector import MySQLConnection

router = APIRouter(tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===============================
#  DOCUMENTOS
# ===============================
@router.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    connection: MySQLConnection = Depends(get_db_connection)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        cursor = connection.cursor()

        # Procesar PDF -> texto + tablas con metadatos
        pdf_data = process_pdf_with_metadata(file_path)
        contenido = pdf_data.get("text", "")
        tablas = pdf_data.get("tables", [])

        # Guardar documento
        cursor.execute(
            "INSERT INTO documentos (nombre, contenido) VALUES (%s, %s)",
            (file.filename, contenido)
        )
        document_id = cursor.lastrowid

        # Guardar tablas
        for idx, t in enumerate(tablas, start=1):
            cursor.execute("""
                INSERT INTO document_tables
                (document_id, table_uid, page, bbox, n_rows, n_cols, detection, confidence, title_guess, headers, rows_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                document_id,
                f"t{idx}",
                int(t.get("page", 1)),
                json.dumps(t.get("bbox", [])),
                int(t.get("nRows", 0)),
                int(t.get("nCols", 0)),
                t.get("detection", "auto"),
                float(t.get("confidence", 0.0)),
                t.get("titleGuess", ""),
                json.dumps(t.get("headers", [])),
                json.dumps(t.get("rows", [])),
            ))

        connection.commit()

        return {
            "message": "Documento y tablas guardados correctamente",
            "document_id": document_id,
            "tables_count": len(tablas),
        }

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error guardando en DB: {e}")
    finally:
        cursor.close()
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/documents/")
def list_documents(connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nombre, fecha_subida
        FROM documentos
        ORDER BY fecha_subida DESC
    """)
    documentos = cursor.fetchall()
    cursor.close()
    return {"documentos": documentos}


@router.get("/documents/{document_id}")
def get_document(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nombre, contenido, fecha_subida
        FROM documentos
        WHERE id = %s
    """, (document_id,))
    documento = cursor.fetchone()
    cursor.close()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return documento


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM documentos WHERE id = %s", (document_id,))
    connection.commit()
    deleted = cursor.rowcount
    cursor.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {"message": f"Documento con ID {document_id} y sus tablas eliminados correctamente"}


# ===============================
#  TABLAS
# ===============================

@router.get("/tables/search")
def search_in_tables(
    q: str = Query(..., description="Texto a buscar dentro de las tablas"),
    connection: MySQLConnection = Depends(get_db_connection)
):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT document_id, table_uid, title_guess, headers, rows_data
        FROM document_tables
    """)
    tables = cursor.fetchall()
    cursor.close()

    resultados = []
    for t in tables:
        if q.lower() in str(t.get("rows_data", "")).lower():
            resultados.append({
                "document_id": t["document_id"],
                "table_uid": t["table_uid"],
                "title_guess": t["title_guess"],
                "headers": json.loads(t["headers"]) if t.get("headers") else [],
                "rows": json.loads(t["rows_data"]) if t.get("rows_data") else []
            })

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron coincidencias")

    return {"results": resultados}


# 2) Luego la lista por documento
@router.get("/tables/{document_id}")
def list_document_tables(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT table_uid, page, title_guess
        FROM document_tables
        WHERE document_id = %s
        ORDER BY page, table_uid
    """, (document_id,))
    items = cursor.fetchall()
    cursor.close()

    tables = [
        {"id": it["table_uid"], "name": it["title_guess"] or "", "page": it["page"]}
        for it in items
    ]
    return {"documentId": document_id, "count": len(tables), "items": tables}


# 3) Y por último la tabla específica
@router.get("/tables/{document_id}/{table_uid}")
def get_table_content(document_id: int, table_uid: str, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT table_uid, page, title_guess, headers, rows_data
        FROM document_tables
        WHERE document_id = %s AND table_uid = %s
    """, (document_id, table_uid))
    table = cursor.fetchone()
    cursor.close()

    if not table:
        raise HTTPException(status_code=404, detail="Tabla no encontrada")

    headers = json.loads(table["headers"]) if table.get("headers") else []
    rows = json.loads(table["rows_data"]) if table.get("rows_data") else []

    return {
        "table_uid": table["table_uid"],
        "page": table["page"],
        "title": table["title_guess"] or "",
        "headers": headers,
        "rows": rows,
    }