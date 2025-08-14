import pdfplumber
import pandas as pd
from typing import Dict
import json

def normalize_number(val: str) -> str:
    """Limpia valores numericos ($400,000 → 400000)"""
    if not val:
        return ""
    return val.replace("$", "").replace(",", "").strip()

def format_bbox(bbox):
    """Convierte bbox a lista de floats"""
    return [float(x) for x in bbox]

def process_pdf_with_metadata(pdf_path: str) -> Dict:
    """
    Procesa un PDF y devuelve:
    - text: Texto extraido
    - tables: Una lista de tablas con headers y rows
    """
    result = {
        "text": "",
        "tables": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            # Texto
            text_lines = (page.extract_text() or "").split("\n")
            if page_idx == 1 and text_lines:
                result["text"] += text_lines[0].strip() + "\n\n"

            # Extraemos tablas
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables, start=1):
                bbox = format_bbox(page.bbox)
                n_rows = len(table)
                n_cols = len(table[0]) if table else 0

                # Titulo 
                base_title = text_lines[0].strip() if text_lines else f"Tabla {t_idx}"
                title_guess = f"{base_title} #{t_idx}"

                # Pasar a DataFrame
                df = pd.DataFrame(table).fillna("").astype(str)
                headers = df.iloc[0].tolist() if not df.empty else []
                rows = df.iloc[1:].values.tolist() if len(df) > 1 else []

                # Normalizamo
                norm_headers = [h.strip() for h in headers]
                norm_rows = [[normalize_number(c) for c in r] for r in rows]

                result["tables"].append({
                    "tableId": f"t{t_idx}",
                    "page": page_idx,
                    "bbox": bbox,
                    "nRows": n_rows,
                    "nCols": n_cols,
                    "detection": "auto",
                    "confidence": 0.9,
                    "titleGuess": title_guess,
                    "headers": norm_headers,
                    "rows": norm_rows
                })

            result["text"] += f"--- Fin página {page_idx} ---\n\n"

    return result
