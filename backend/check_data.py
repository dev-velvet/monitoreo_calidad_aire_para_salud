import sys
sys.path.insert(0, 'etl')
from db_postgres import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT periodo, COUNT(*), SUM(casos) 
    FROM enfermedades 
    GROUP BY periodo 
    ORDER BY periodo;
""")
print("ENFERMEDADES por periodo:")
for r in cur.fetchall():
    print(f"  Año: {r[0]} | Filas: {r[1]} | Casos totales: {r[2]}")

cur.execute("""
    SELECT periodo, COUNT(*), SUM(muertes) 
    FROM defunciones 
    GROUP BY periodo 
    ORDER BY periodo;
""")
print("\nDEFUNCIONES por periodo:")
for r in cur.fetchall():
    print(f"  Año: {r[0]} | Filas: {r[1]} | Muertes totales: {r[2]}")

cur.close()
conn.close()
sys.exit(0)


cur.close()
conn.close()


