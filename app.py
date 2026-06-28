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

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(Config.get_db_url())

# =====================================================
# 1. CRUD - CREAR CLIENTE (POST /api/clientes)
# =====================================================
@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO CLIENTE (nombre, apellido, email, dni, telefono)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_cliente
        """, (data['nombre'], data['apellido'], data['email'], data['dni'], data['telefono']))
        id_cliente = cur.fetchone()[0]
        conn.commit()
        return jsonify({'mensaje': 'Cliente creado', 'id_cliente': id_cliente}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 2. CRUD - LISTAR CLIENTES (GET /api/clientes)
# =====================================================
@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("SELECT * FROM CLIENTE ORDER BY id_cliente DESC")
        clientes = [dict(row) for row in cur.fetchall()]
        return jsonify(clientes)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 3. CRUD - EDITAR CLIENTE (PUT /api/clientes/<id>)
# =====================================================
@app.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def editar_cliente(id_cliente):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE CLIENTE SET nombre=%s, apellido=%s, email=%s, telefono=%s
            WHERE id_cliente=%s
        """, (data['nombre'], data['apellido'], data['email'], data['telefono'], id_cliente))
        conn.commit()
        return jsonify({'mensaje': 'Cliente actualizado'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 4. CRUD - ELIMINAR CLIENTE (DELETE /api/clientes/<id>)
# =====================================================
@app.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def eliminar_cliente(id_cliente):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM CLIENTE WHERE id_cliente = %s", (id_cliente,))
        conn.commit()
        return jsonify({'mensaje': 'Cliente eliminado'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# =====================================================
# 5. CRUD - CREAR PEDIDO (POST /api/pedidos) - 3 TABLAS
# =====================================================
@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("BEGIN;")
        
        # Insertar pedido
        cur.execute("""
            INSERT INTO PEDIDO (id_cliente, id_empleado, id_mesa, estado, total)
            VALUES (%s, %s, %s, 'Pendiente', 0) RETURNING id_pedido
        """, (data['id_cliente'], data['id_empleado'], data['id_mesa']))
        id_pedido = cur.fetchone()[0]
        
        # Obtener precio del producto
        cur.execute("SELECT precio FROM PRODUCTO WHERE id_producto = %s", (data['id_producto'],))
        precio = cur.fetchone()[0]
        subtotal = precio * data['cantidad']
        
        # Insertar detalle
        cur.execute("""
            INSERT INTO DETALLE_PEDIDO (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_pedido, data['id_producto'], data['cantidad'], precio, subtotal))
        
        # Actualizar stock
        cur.execute("UPDATE PRODUCTO SET stock = stock - %s WHERE id_producto = %s",
                   (data['cantidad'], data['id_producto']))
        
        # Actualizar total del pedido
        cur.execute("UPDATE PEDIDO SET total = %s WHERE id_pedido = %s", (subtotal, id_pedido))
        
        # Cambiar estado de mesa
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
# 6. LISTAR PEDIDOS (GET /api/pedidos)
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
# 7. REPORTE GROUP BY/HAVING (GET /api/reporte/ventas)
# =====================================================
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

# =====================================================
# 8. EXPORTAR CSV (GET /api/reporte/exportar-csv)
# =====================================================
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
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['cliente', 'total_pedidos', 'total_gastado'])
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
# 9. JSONB - GUARDAR (POST /api/pedidos/jsonb)
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
# 10. JSONB - CONSULTAR (GET /api/pedidos/jsonb)
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
    print("🚀 API RESTAURANTE - http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
