import mariadb
import sys
import re


config = {}

'''
Extrae el nombre del estudio con el cual está guardado en 
la base de datos, para reconocerlo y obtenerlo por su ID posteriormente.

Cuenta los guiones (ya que tiene mas de 4) y se fija que termine exclusivamente en hh:mm:ss 
(como se encuentra en la base), ya que las carpetas pueden tener sub-carpetas con nombres similares.
'''
def extract_study_name(path): 
    parts = path.split('/')
    for part in parts:
        if part.count('-') >= 5 and re.search(r'_\d{2}:?\d{2}:?\d{2}$', part):
            return part
    return None

'''
Obtiene el ID del estudio a partir del nombre del mismo.
'''
def get_study_id_by_name(study_name):
    if not study_name:
        raise ValueError("El nombre del estudio no puede estar vacío.")

    conn = None
    try:
        conn = mariadb.connect(**config)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.id FROM sacunnoba.study AS s
            WHERE name = ?
            """, ([study_name])
        )
        row = cur.fetchone()
        if row is None:
            return None
        return row[0]

    except mariadb.Error as e:
        print(f"Error al conectarse a la plataforma MariaDB: {e}")
        raise

    finally:
        if conn:
            conn.close()

'''
Agrega el NRRD en la nueva tabla 'study_nrrd_id' con el id del studio.
'''
def add_NRRD_to_study_in_darmic(study_id, nrrd_string):
    try:
        if (study_id is None) or (nrrd_string == ""):
            raise ValueError("El ID del estudio y la cadena NRRD no pueden estar vacíos.")

        conn = mariadb.connect(**config)
        print("¡Conexión exitosa!")

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO study_nrrd_id (study_id, nrrd_id) VALUES (?, ?)",
            ([study_id, nrrd_string])
        )
        conn.commit()

    except mariadb.Error as e:
        print(f"Error al conectarse a la plataforma MariaDB: {e}")
        sys.exit(1)

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Conexión cerrada.")