"""
Diccionarios de Normalización
==============================
Mapas de estandarización para municipios del Valle de Aburrá y grupos de edad.

Relación con la metodología
---------------------------
Estos diccionarios resuelven una de las observaciones de los evaluadores:
"aclarar cómo se integran las estaciones con la información epidemiológica".

Los CSVs históricos contienen variantes ortográficas de los nombres de
municipios y grupos de edad. Sin normalización, un JOIN entre las tablas
de mediciones SIATA y los datos epidemiológicos fallaría porque 'medellin'
≠ 'Medellín'. Estos diccionarios garantizan la CONSISTENCIA de la integración.

Delimitación geográfica
-----------------------
El estudio se delimita a los 10 municipios del Área Metropolitana del
Valle de Aburrá (AMVA):
    1. Medellín       6. Caldas
    2. Bello          7. Copacabana
    3. Envigado       8. La Estrella
    4. Itagüí         9. Girardota
    5. Sabaneta      10. Barbosa
"""

# ─────────────────────────────────────────────────────────────────────────────
# NORMALIZACIÓN DE MUNICIPIOS
# ─────────────────────────────────────────────────────────────────────────────
# Mapea todas las variantes encontradas en los CSVs al nombre oficial con
# tildes correctas. Este mismo nombre se usa para vincular las estaciones
# SIATA con los datos epidemiológicos mediante:
#     estacion ILIKE '%' || municipio.nombre_normalizado || '%'

MUNICIPIOS_MAPA = {
    "medellin":    "Medellín",
    "medellín":    "Medellín",
    "envigado":    "Envigado",
    "itagui":      "Itagüí",
    "itagüí":      "Itagüí",
    "sabaneta":    "Sabaneta",
    "bello":       "Bello",
    "caldas":      "Caldas",
    "copacabana":  "Copacabana",
    "la estrella": "La Estrella",
    "laestrella":  "La Estrella",
    "girardota":   "Girardota",
    "barbosa":     "Barbosa",
}

# ─────────────────────────────────────────────────────────────────────────────
# NORMALIZACIÓN DE GRUPOS DE EDAD
# ─────────────────────────────────────────────────────────────────────────────
# Los CSVs usan múltiples formatos para los mismos rangos etarios.
# Se estandarizan a las 4 categorías epidemiológicas del estudio.

EDADES_MAPA = {
    "menores de 5 años": "Menores de 5 años",
    "menor de 5 años":   "Menores de 5 años",
    "menores de 5":      "Menores de 5 años",
    "5 a 14 años":       "5 a 14 años",
    "5 a 14":            "5 a 14 años",
    "15 a 64 años":      "15 a 64 años",
    "15 a 64":           "15 a 64 años",
    "65 años y más":     "65 años y más",
    "65 y más":          "65 años y más",
    "65+":               "65 años y más",
}
