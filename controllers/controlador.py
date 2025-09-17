from conexion import obtener_conexion

def insertar_costo_produccion(materia_prima, mano_obra, costos_indirectos):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            INSERT INTO costoProduccion(materia_prima_directa, mano_obra_directa, costos_indirectos_fabricacion) 
            VALUES (%s, %s, %s)
        """, (materia_prima, mano_obra, costos_indirectos))
        conexion.commit()
    conexion.close()


def obtener_costos_produccion():
    conexion = obtener_conexion()
    producciones = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, materia_prima_directa, mano_obra_directa, costos_indirectos_fabricacion, 
                   costo_total, fecha_calculo
            FROM costoProduccion
        """)
        producciones = cursor.fetchall()
    conexion.close()
    return producciones


def eliminar_costo_produccion(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM costoProduccion WHERE id = %s", (id,))
        conexion.commit()
    conexion.close()


def obtener_costo_produccion_por_id(id):
    conexion = obtener_conexion()
    produccion = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, materia_prima_directa, mano_obra_directa, costos_indirectos_fabricacion
            FROM costoProduccion WHERE id = %s
        """, (id,))
        produccion = cursor.fetchone()
    conexion.close()
    return produccion


def actualizar_costo_produccion(materia_prima, mano_obra, costos_indirectos, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            UPDATE costoProduccion 
            SET materia_prima_directa = %s, mano_obra_directa = %s, costos_indirectos_fabricacion = %s
            WHERE id = %s
        """, (materia_prima, mano_obra, costos_indirectos, id))
        conexion.commit()
    conexion.close()


def insertar_costo_unitario(produccion_id, cantidad_productos):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT materia_prima_directa + mano_obra_directa + costos_indirectos_fabricacion AS costo_total FROM costoProduccion WHERE id = %s",
            (produccion_id,)
        )
        costo_total = cursor.fetchone()[0]

        costo_unitario = float(costo_total) / float(cantidad_productos)

        cursor.execute(
            "INSERT INTO costoUnitario(costo_produccion_id, cantidad_productos, costo_total_snapshot, costo_unitario) VALUES (%s, %s, %s, %s)",
            (produccion_id, cantidad_productos, costo_total, costo_unitario)
        )
        conexion.commit()
    conexion.close()


def obtener_costos_unitarios():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, costo_produccion_id, cantidad_productos, costo_total_snapshot, costo_unitario, fecha_calculo FROM costoUnitario ORDER BY fecha_calculo DESC"
        )
        resultados = cursor.fetchall()
    conexion.close()
    return resultados


def eliminar_costo_unitario(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM costoUnitario WHERE id = %s", (id,))
        conexion.commit()
    conexion.close()


def obtener_costo_unitario_por_id(id):
    conexion = obtener_conexion()
    unitario = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, costo_produccion_id, cantidad_productos
            FROM costoUnitario WHERE id = %s
        """, (id,))
        unitario = cursor.fetchone()
    conexion.close()
    return unitario


def actualizar_costo_unitario(id, costo_produccion_id, cantidad_productos):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT costo_total FROM costoProduccion WHERE id = %s", (costo_produccion_id,))
        resultado = cursor.fetchone()
        if resultado:
            costo_total = resultado[0]
            costo_unitario = costo_total / cantidad_productos if cantidad_productos > 0 else 0

            cursor.execute("""
                UPDATE costoUnitario
                SET costo_produccion_id = %s, cantidad_productos = %s, 
                    costo_total_snapshot = %s, costo_unitario = %s
                WHERE id = %s
            """, (costo_produccion_id, cantidad_productos, costo_total, costo_unitario, id))
            conexion.commit()
    conexion.close()

def obtener_costos_unitarios_con_info():
    conexion = obtener_conexion()
    resultados = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT cu.id, cp.materia_prima_directa, cp.mano_obra_directa,
                   cp.costos_indirectos_fabricacion, cp.materia_prima_directa + cp.mano_obra_directa + cp.costos_indirectos_fabricacion AS costo_total,
                   cu.cantidad_productos, cu.costo_total_snapshot, cu.costo_unitario, cu.fecha_calculo
            FROM costoUnitario cu
            LEFT JOIN costoProduccion cp ON cu.costo_produccion_id = cp.id
            ORDER BY cu.id ASC
        """)
        resultados = cursor.fetchall()
    conexion.close()
    return resultados