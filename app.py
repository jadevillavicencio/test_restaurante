from flask import Flask, request, jsonify, send_file
from db import get_connection
import csv

app = Flask(__name__)

# =========================
# 🔹 CRUD CLIENTE
# =========================

@app.route('/clientes', methods=['POST'])
def crear_cliente():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO cliente (nombre, email)
            VALUES (%s, %s)
            RETURNING id_cliente;
        """, (data['nombre'], data['email']))

        conn.commit()
        return jsonify({"mensaje": "Cliente creado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route('/clientes', methods=['GET'])
def listar_clientes():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM cliente;")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(data)


@app.route('/clientes/<int:id>', methods=['PUT'])
def actualizar_cliente(id):
    data = request.json
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE cliente
            SET nombre = %s, email = %s
            WHERE id_cliente = %s;
        """, (data['nombre'], data['email'], id))

        conn.commit()
        return jsonify({"mensaje": "Actualizado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route('/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM cliente WHERE id_cliente = %s;", (id,))
        conn.commit()
        return jsonify({"mensaje": "Eliminado"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})
    finally:
        cur.close()
        conn.close()

# =========================
# 🔥 TRANSACCIÓN COMPLEJA (3 TABLAS)
# =========================

@app.route('/pedido-completo', methods=['POST'])
def pedido_completo():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")

        # 1. crear pedido
        cur.execute("""
            INSERT INTO pedido (id_cliente)
            VALUES (%s) RETURNING id_pedido;
        """, (data['id_cliente'],))

        id_pedido = cur.fetchone()[0]

        # 2. insertar detalle
        for item in data['productos']:
            cur.execute("""
                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad)
                VALUES (%s, %s, %s);
            """, (id_pedido, item['id_producto'], item['cantidad']))

            # 3. actualizar stock
            cur.execute("""
                UPDATE producto
                SET stock = stock - %s
                WHERE id_producto = %s;
            """, (item['cantidad'], item['id_producto']))

        conn.commit()
        return jsonify({"mensaje": "Pedido completo OK"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})

    finally:
        cur.close()
        conn.close()

# =========================
# 📊 REPORTE + CSV
# =========================

@app.route('/reporte', methods=['GET'])
def reporte():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.nombre, COUNT(p.id_pedido) as total
        FROM cliente c
        JOIN pedido p ON c.id_cliente = p.id_cliente
        GROUP BY c.nombre;
    """)

    rows = cur.fetchall()

    filename = "reporte.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Cliente", "Total pedidos"])
        writer.writerows(rows)

    cur.close()
    conn.close()

    return send_file(filename, as_attachment=True)

# =========================

if __name__ == '__main__':
    app.run(debug=True)
