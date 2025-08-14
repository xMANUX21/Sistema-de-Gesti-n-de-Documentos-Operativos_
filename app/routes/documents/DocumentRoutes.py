import os
import json
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.utils.dbConn import get_db_connection
from app.utils.PdfProcessor import process_pdf_with_metadata
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

    try:
        cursor = connection.cursor()

        # Procesa el  PDF
        pdf_data = process_pdf_with_metadata(file_path)
        contenido = pdf_data.get("text", "")
        tablas = pdf_data.get("tables", [])

        # Guarda el documento
        cursor.execute(
            "INSERT INTO documentos (nombre, contenido) VALUES (%s, %s)",
            (file.filename, contenido)
        )
        document_id = cursor.lastrowid

        # Guarda tablas (headers/rows como JSON)
        for idx, t in enumerate(tablas, start=1):
            title = t.get("titleGuess", "").strip()
            if not title:
                title = f"Tabla #{idx}"
            else:
                title = f"{title} #{idx}"

            cursor.execute("""
                INSERT INTO document_tables
                (document_id, table_uid, page, bbox, n_rows, n_cols, detection, confidence, title_guess, `headers`, `rows_data`)
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
                title,
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


@router.get("/")
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


@router.get("/{document_id}")
def get_document_with_tables(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    
    # Se traen las tablas del documento
    cursor.execute("""
        SELECT id, page, title_guess, headers, rows_data
        FROM document_tables
        WHERE document_id = %s
        ORDER BY id
    """, (document_id,))
    tables = cursor.fetchall()
    cursor.close()

    if not tables:
        raise HTTPException(status_code=404, detail="Documento o tablas no encontradas...")

    result = {
        "document_id": document_id,
        "tables": []
    }

    for t in tables:
        headers = json.loads(t["headers"]) if t["headers"] else []
        rows = json.loads(t["rows_data"]) if t["rows_data"] else []
        table_data = [headers] + rows 

        result["tables"].append({
            "id": t["id"],
            "page_number": t["page"],
            "description": t["title_guess"] or "",
            "table_data": table_data
        })

    return result


@router.get("/{document_id}/tables")
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

    tables = []
    for it in items:
        name = it["title_guess"] or ""
        parts = name.split()
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            name = " ".join(parts[:-1])
        
        tables.append({
            "id": it["table_uid"],
            "name": name,
            "page": it["page"],
        })

    return {"documentId": document_id, "count": len(tables), "items": tables}



@router.get("/{document_id}/tables/{table_uid}")
def get_table_content(document_id: int, table_uid: str, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT table_uid, page, title_guess, `headers`, `rows_data`
        FROM document_tables
        WHERE document_id = %s AND table_uid = %s
    """, (document_id, table_uid))
    table = cursor.fetchone()
    cursor.close()

    if not table:
        raise HTTPException(status_code=404, detail="Tabla no encontrada...")

    headers = json.loads(table["headers"]) if table.get("headers") else []
    rows = json.loads(table["rows_data"]) if table.get("rows_data") else []

    return {
        "table_uid": table["table_uid"],
        "page": table["page"],
        "title": table["title_guess"] or "",
        "headers": headers,
        "rows": rows,
    }


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
                "title": t["title_guess"],
                "headers": json.loads(t["headers"]) if t.get("headers") else [],
                "rows": json.loads(t["rows_data"]) if t.get("rows_data") else []
            })

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron coincidencias...")

    return {"results": resultados}


@router.delete("/{document_id}")
def delete_document(document_id: int, connection: MySQLConnection = Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM documentos WHERE id = %s", (document_id,))
    connection.commit()
    deleted = cursor.rowcount
    cursor.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado....")
    return {"message": f"Documento con ID {document_id} eliminado correctamente"}
