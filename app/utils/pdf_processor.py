import pdfplumber
import pandas as pd
from typing import Dict

def format_table_as_text(table):
    """
    aca convierte una lista de listas (tabla) en texto alineado por columnas
    """
    if not table:
        return ""
    df = pd.DataFrame(table).fillna("").astype(str)
    col_widths = [df[col].map(len).max() for col in df.columns]
    lines = []
    for _, row in df.iterrows():
        line = "  ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return "\n".join(lines)

def process_pdf(pdf_path: str) -> Dict[str, str]:
    """
    aca podemos pasar un PDF y devolveria un texto con:
     Titulo principal de la primera pagina
     Tablas con sus titulos
     Columnas alineadas
     Separacion por pagina
    Funcionaria con PDFs donde las tablas pueden estar separadas del titulo
    """
    result_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            # Extrae las lineas de texto
            lines = (page.extract_text() or "").split("\n")

            # Agrega titulo principal en la primera pagina
            if page_idx == 1 and lines:
                result_text += lines[0].strip() + "\n\n"

            # Extrae tablas detectadas por el pdfplumber
            tables = page.extract_tables()
            for table in tables:
                # Detecta el   titulo de la tabla (la linea que va antes de la cabecera)
                header_first_cell = str(table[0][0]).strip() if table and table[0] else ""
                title_line = None
                for i, line in enumerate(lines):
                    if header_first_cell and header_first_cell in line:
                        if i > 0:
                            title_line = lines[i - 1].strip()
                        break

                # Agrega un titulo si existe
                if title_line:
                    result_text += title_line + "\n"

                # Agrega la ya tabla formateada
                result_text += format_table_as_text(table) + "\n\n"

            # Marca un fin de la pagina
            result_text += f"--- Fin pagina {page_idx} ---\n\n"

    return {"text": result_text}
