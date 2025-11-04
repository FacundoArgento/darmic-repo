import mariadb
import sys


config = {}

try:
    conn = mariadb.connect(**config)
    print("¡Conexión exitosa!")

    cur = conn.cursor()

    cur.execute("Select name, provincia from institution i order by provincia ASC;")

    for (columna1, columna2) in cur:
        print(f"Columna1: {columna1}, Columna2: {columna2}")

    # Ejemplo: Insertar datos usando parámetros (evita inyecciones SQL)
    #try:
    #    cur.execute(
    #        "INSERT INTO tu_tabla (columna1, columna2) VALUES (?, ?)",
    #        ("dato_ejemplo", 123)
    #    )
        # Confirmar la transacción
    #    conn.commit()
    #    print(f"ID del último registro insertado: {cur.lastrowid}")

    #except mariadb.Error as e:
    #    print(f"Error en la inserción: {e}")

# Manejar excepciones de conexión
except mariadb.Error as e:
    print(f"Error al conectarse a la plataforma MariaDB: {e}")
    sys.exit(1)

finally:
    # Cerrar la conexión siempre
    if conn:
        conn.close()
        print("Conexión cerrada.")