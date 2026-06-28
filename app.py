# =====================================================
# API BACKEND - SISTEMA RESTAURANTE
# Flask + PostgreSQL (SQL PURO)
# =====================================================

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import csv
from io import StringIO
from config import Config

# =====================================================
# INICIALIZAR FLASK
# =====================================================
app = Flask(__name__)
CORS(app)

# =====================================================
# CONEXIÓN A POSTGRESQL
# =====================================================
def get_db_connection():
    return psycopg2.connect(Config.get_db_url())

# =====================================================
# 1. CRUD - CREAR PEDIDO (POST /api/pedidos)
# =====================================================
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

# =====================================================
# 2. CRUD - LISTAR PEDIDOS (GET /api/pedidos)
# =====================================================
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

# =====================================================
# 3. CRUD - EDITAR PEDIDO (PUT /api/pedidos/<id>)
# =====================================================
@app.route('/api/pedidos/<int:id_pedido>', methods=['PUT'])
def editar_pedido(id_pedido):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE PEDIDO SET estado = %s, total = %s WHERE id_pedido = %s
        """, (data.get('estado'), data.get('total'), id_pedido))
        conn.commit()
        return jsonify({'mensaje': 'Pedido actualizado'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 4. CRUD - ELIMINAR PEDIDO (DELETE /api/pedidos/<id>)
# =====================================================
@app.route('/api/pedidos/<int:id_pedido>', methods=['DELETE'])
def eliminar_pedido(id_pedido):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("BEGIN;")
        cur.execute("DELETE FROM DETALLE_PEDIDO WHERE id_pedido = %s", (id_pedido,))
        cur.execute("DELETE FROM PEDIDO WHERE id_pedido = %s", (id_pedido,))
        cur.execute("COMMIT;")
        return jsonify({'mensaje': 'Pedido eliminado'})
    except Exception as e:
        cur.execute("ROLLBACK;")
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 5. REPORTE GROUP BY/HAVING (GET /api/reporte/ventas)
# =====================================================
@app.route('/api/reporte/ventas', methods=['GET'])
def reporte_ventas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("""
            SELECT 
                pr.nombre AS producto,
                SUM(dp.cantidad) AS unidades_vendidas,
                SUM(dp.subtotal) AS ingresos_totales
            FROM PRODUCTO pr
            JOIN DETALLE_PEDIDO dp ON pr.id_producto = dp.id_producto
            JOIN PEDIDO p ON dp.id_pedido = p.id_pedido
            WHERE p.estado = 'Entregado'
            GROUP BY pr.id_producto, pr.nombre
            HAVING SUM(dp.cantidad) > 0
            ORDER BY unidades_vendidas DESC
        """)
        return jsonify([dict(row) for row in cur.fetchall()])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 6. EXPORTAR A CSV (GET /api/reporte/exportar-csv)
# =====================================================
@app.route('/api/reporte/exportar-csv', methods=['GET'])
def exportar_csv():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                pr.nombre AS producto,
                SUM(dp.cantidad) AS unidades_vendidas,
                SUM(dp.subtotal) AS ingresos_totales
            FROM PRODUCTO pr
            JOIN DETALLE_PEDIDO dp ON pr.id_producto = dp.id_producto
            JOIN PEDIDO p ON dp.id_pedido = p.id_pedido
            WHERE p.estado = 'Entregado'
            GROUP BY pr.id_producto, pr.nombre
            HAVING SUM(dp.cantidad) > 0
            ORDER BY unidades_vendidas DESC
        """)
        rows = cur.fetchall()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['producto', 'unidades_vendidas', 'ingresos_totales'])
        for row in rows:
            writer.writerow(row)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='reporte_ventas.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 7. JSONB - GUARDAR (POST /api/pedidos/jsonb)
# =====================================================
@app.route('/api/pedidos/jsonb', methods=['POST'])
def insertar_jsonb():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO PEDIDO_JSONB (datos) VALUES (%s) RETURNING id_pedido",
                   (data['datos'],))
        id_pedido = cur.fetchone()[0]
        conn.commit()
        return jsonify({'mensaje': 'JSONB guardado', 'id_pedido': id_pedido}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 8. JSONB - CONSULTAR (GET /api/pedidos/jsonb)
# =====================================================
@app.route('/api/pedidos/jsonb', methods=['GET'])
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

# =====================================================
# INICIAR SERVIDOR
# =====================================================
if __name__ == '__main__':
    print("🚀 API RESTAURANTE")
    print("📍 http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
