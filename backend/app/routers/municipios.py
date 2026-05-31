from fastapi import APIRouter, HTTPException, Query
from app.database import get_db

router = APIRouter(prefix="/api/municipios", tags=["catálogos"])

@router.get("")
def list_municipios():
    """
    Obtiene la lista de municipios registrados.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, nombre_normalizado FROM municipios ORDER BY nombre_normalizado;")
            return cur.fetchall()

@router.get("/grupos-diagnosticos")
def list_grupos_diagnosticos():
    """
    Obtiene la lista de grupos diagnósticos CIE-10.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, codigo_cie10, nombre, capitulo FROM grupos_diagnosticos ORDER BY nombre;")
            return cur.fetchall()

@router.get("/contaminantes")
def list_contaminantes():
    """
    Obtiene la lista de contaminantes registrados.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, nombre_display FROM contaminantes ORDER BY nombre;")
            return cur.fetchall()
