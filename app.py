from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import csv
import json
from io import StringIO, BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'restaurante'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'comida'),
        port=os.getenv('DB_PORT', '5432')
    )

@app.route('/')
def home():
    return jsonify({
        'mensaje': 'Restaurante - Sistema de Gestion',
        'endpoints': {
            'GET /': 'Bienvenida',
            'GET /api/pedidos': 'Listar pedidos',
            'POST /api/pedidos': 'Crear pedido',
            'GET /api/reporte/ventas': 'Reporte GROUP BY/HAVING',
            'GET /api/reporte/exportar-csv': 'Exportar a CSV',
            'GET /api/reporte/productos': 'Reporte productos por categoria',
            'GET /api/reporte/productos-csv': 'Exportar CSV productos',
            'GET /api/jsonb': 'Consultar JSONB',
            'POST /api/jsonb': 'Guardar JSONB'
        }
    })

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT p.id_pedido, c.nombre AS cliente, p.total, p.estado, p.fecha_hora
            FROM PEDIDO p
            JOIN CLIENTE c ON p.id_cliente = c.id_cliente
            ORDER BY p.id_pedido DESC
        """)
        return jsonify([dict(row) for row in cur.fetchall()])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN;")
        cur.execute("""
            INSERT INTO PEDIDO (id_cliente, id_empleado, id_mesa, estado, total)
            VALUES (%s, %s, %s, 'Pendiente', 0) RETURNING id_pedido
        """, (data['id_cliente'], data['id_empleado'], data['id_mesa']))
        id_pedido = cur.fetchone()[0]
        cur.execute("SELECT precio FROM PRODUCTO WHERE id_producto = %s", (data['id_producto'],))
        precio = cur.fetchone()[0]
        subtotal = precio * data['cantidad']
        cur.execute("""
            INSERT INTO DETALLE_PEDIDO (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_pedido, data['id_producto'], data['cantidad'], precio, subtotal))
        cur.execute("UPDATE PRODUCTO SET stock = stock - %s WHERE id_producto = %s",
                   (data['cantidad'], data['id_producto']))
        cur.execute("UPDATE PEDIDO SET total = %s WHERE id_pedido = %s", (subtotal, id_pedido))
        cur.execute("UPDATE MESA SET estado = 'Ocupada' WHERE id_mesa = %s", (data['id_mesa'],))
        cur.execute("COMMIT;")
        return jsonify({'mensaje': 'Pedido registrado', 'id_pedido': id_pedido}), 201
    except Exception as e:
        cur.execute("ROLLBACK;")
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/reporte/ventas', methods=['GET'])
def reporte_ventas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT 
                c.nombre AS cliente,
                COUNT(p.id_pedido) AS total_pedidos,
                COALESCE(SUM(p.total), 0) AS total_gastado
            FROM CLIENTE c
            LEFT JOIN PEDIDO p ON c.id_cliente = p.id_cliente
            WHERE p.estado = 'Entregado' OR p.estado IS NULL
            GROUP BY c.id_cliente, c.nombre
            HAVING COALESCE(SUM(p.total), 0) > 0
            ORDER BY total_gastado DESC
        """)
        return jsonify([dict(row) for row in cur.fetchall()])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/reporte/exportar-csv', methods=['GET'])
def exportar_csv():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                c.nombre AS cliente,
                COUNT(p.id_pedido) AS total_pedidos,
                COALESCE(SUM(p.total), 0) AS total_gastado
            FROM CLIENTE c
            LEFT JOIN PEDIDO p ON c.id_cliente = p.id_cliente
            WHERE p.estado = 'Entregado' OR p.estado IS NULL
            GROUP BY c.id_cliente, c.nombre
            HAVING COALESCE(SUM(p.total), 0) > 0
            ORDER BY total_gastado DESC
        """)
        rows = cur.fetchall()
        csv_text = 'cliente,total_pedidos,total_gastado\n'
        for row in rows:
            csv_text += f"{row[0]},{row[1]},{row[2]}\n"
        return send_file(
            BytesIO(csv_text.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='reporte_ventas.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/reporte/productos', methods=['GET'])
def reporte_productos():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT 
                c.nombre AS categoria, 
                p.nombre AS producto,
                SUM(dp.cantidad) AS total_vendido, 
                SUM(dp.subtotal) AS ingreso_total
            FROM DETALLE_PEDIDO dp
            JOIN PRODUCTO p ON dp.id_producto = p.id_producto
            JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
            GROUP BY c.nombre, p.nombre
            HAVING SUM(dp.cantidad) > 2
            ORDER BY total_vendido DESC
        """)
        return jsonify([dict(row) for row in cur.fetchall()])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/reporte/productos-csv', methods=['GET'])
def exportar_productos_csv():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                c.nombre AS categoria, 
                p.nombre AS producto,
                SUM(dp.cantidad) AS total_vendido, 
                SUM(dp.subtotal) AS ingreso_total
            FROM DETALLE_PEDIDO dp
            JOIN PRODUCTO p ON dp.id_producto = p.id_producto
            JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
            GROUP BY c.nombre, p.nombre
            HAVING SUM(dp.cantidad) > 2
            ORDER BY total_vendido DESC
        """)
        rows = cur.fetchall()
        csv_text = 'categoria,producto,total_vendido,ingreso_total\n'
        for row in rows:
            csv_text += f"{row[0]},{row[1]},{row[2]},{row[3]}\n"
        return send_file(
            BytesIO(csv_text.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='reporte_productos.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/jsonb', methods=['POST'])
def guardar_jsonb():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        json_data = json.dumps(data['datos'])
        cur.execute(
            "INSERT INTO PEDIDO_JSONB (datos) VALUES (%s) RETURNING id_pedido",
            (json_data,)
        )
        id_pedido = cur.fetchone()[0]
        conn.commit()
        return jsonify({'mensaje': 'JSONB guardado', 'id_pedido': id_pedido}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/jsonb', methods=['GET'])
def consultar_jsonb():
    nombre = request.args.get('nombre')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if nombre:
            cur.execute("""
                SELECT * FROM PEDIDO_JSONB
                WHERE datos->'cliente'->>'nombre' = %s
            """, (nombre,))
        else:
            cur.execute("SELECT * FROM PEDIDO_JSONB")
        return jsonify([dict(row) for row in cur.fetchall()])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("🚀 API RESTAURANTE")
    print("📍 http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
