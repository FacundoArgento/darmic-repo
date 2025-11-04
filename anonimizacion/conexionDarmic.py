import mariadb
import sys


config = {}

def addNRRD (study_name, nrrd_string):


    try:
        if (study_name == "") or (nrrd_string == ""):
            raise ValueError("El nombre del estudio y la cadena NRRD no pueden estar vacíos.")

        conn = mariadb.connect(**config)
        print("¡Conexión exitosa!")

        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id FROM sacunnoba.study AS s
            WHERE name = ?
            """, (study_name,)
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Estudio '{study_name}' no encontrado en la tabla 'study'.")
        study_id = row[0]

        cur.execute(
            "INSERT INTO study_nrrd_id (study_id, nrrd_id) VALUES (?, ?)",
            (study_id, nrrd_string)
        )
        # Confirmar la transacción
        conn.commit()
        print(f"ID del último registro insertado: {cur.lastrowid}")

    except mariadb.Error as e:
        print(f"Error al conectarse a la plataforma MariaDB: {e}")
        sys.exit(1)

    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")