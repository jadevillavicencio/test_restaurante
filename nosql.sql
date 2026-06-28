
-- PERSONA 1: 


CREATE TABLE PEDIDO_JSONB (
    id_pedido SERIAL PRIMARY KEY,
    datos JSONB
);

INSERT INTO PEDIDO_JSONB (datos)
VALUES ('{
    "id_pedido": 1,
    "fecha_hora": "2026-06-19 14:30:00",
    "total": 50.00,
    "cliente": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan.perez@email.com",
        "telefono": "999-111-111"
    },
    "productos": [
        {
            "id_producto": 10,
            "nombre": "Coca Cola 500ml",
            "cantidad": 2,
            "precio_unitario": 25.00,
            "subtotal": 50.00
        }
    ],
    "estado_pago": "pendiente"
}');

SELECT * FROM PEDIDO_JSONB
WHERE datos->'cliente'->>'nombre' = 'Juan';


-- PERSONA 2: COMPRAS (JSONB)

CREATE TABLE COMPRA_JSONB (
    id_compra SERIAL PRIMARY KEY,
    datos JSONB
);

INSERT INTO COMPRA_JSONB (datos)
VALUES ('{
    "id_compra": 1,
    "fecha": "2026-06-19",
    "total": 50000,
    "proveedor": {
        "id": 1,
        "nombre": "Brynja",
        "ruc": "20551234561"
    },
    "productos": [
        {
            "id_producto": 10,
            "nombre": "Coca Cola 500ml",
            "cantidad": 100,
            "precio_unitario": 500,
            "subtotal": 50000
        }
    ],
    "estado": "recibido"
}');

SELECT * FROM COMPRA_JSONB
WHERE datos->'proveedor'->>'nombre' = 'Brynja';


-- PERSONA 3: PAGOS Y FACTURAS (JSONB)

CREATE TABLE PAGO_JSONB (
    id_pago SERIAL PRIMARY KEY,
    datos JSONB
);

INSERT INTO PAGO_JSONB (datos)
VALUES ('{
    "id_pedido": 5,
    "total": 15000,
    "cliente": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Perez"
    },
    "pago": {
        "monto": 15000,
        "metodo": "tarjeta debito",
        "fecha": "2026-06-19",
        "estado": "completado"
    },
    "factura": {
        "numero": "FAC-001",
        "fecha_emision": "2026-06-19"
    }
}');

SELECT * FROM PAGO_JSONB
WHERE datos->'pago'->>'metodo' = 'tarjeta debito';


-- PERSONA 4: RESERVAS (JSONB)


CREATE TABLE RESERVA_JSONB (
    id_reserva SERIAL PRIMARY KEY,
    datos JSONB
);

INSERT INTO RESERVA_JSONB (datos)
VALUES ('{
    "id_reserva": 1,
    "fecha_reserva": "2026-06-19",
    "hora": "20:00",
    "num_personas": 4,
    "estado": "Confirmada",
    "cliente": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Perez"
    },
    "mesa": {
        "id": 3,
        "numero": 1,
        "capacidad": 2
    },
    "sucursal": {
        "id": 1,
        "nombre": "Sucursal Centro",
        "ciudad": "Lima"
    }
}');

SELECT * FROM RESERVA_JSONB
WHERE datos->'sucursal'->>'ciudad' = 'Lima';
