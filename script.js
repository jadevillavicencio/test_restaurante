const API = 'http://127.0.0.1:5000';

// =============================================
// TABS
// =============================================
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('tab-' + this.dataset.tab).classList.add('active');
    });
});

// =============================================
// UTILIDADES
// =============================================
function mostrarResultado(id, data, isError = false) {
    const el = document.getElementById(id);
    if (typeof data === 'object') {
        el.textContent = JSON.stringify(data, null, 2);
    } else {
        el.textContent = data;
    }
    el.className = 'resultado' + (isError ? ' error' : '');
}

// =============================================
// 1. CREAR PEDIDO
// =============================================
async function crearPedido() {
    const data = {
        id_cliente: parseInt(document.getElementById('cr_cliente').value),
        id_empleado: parseInt(document.getElementById('cr_empleado').value),
        id_mesa: parseInt(document.getElementById('cr_mesa').value),
        id_producto: parseInt(document.getElementById('cr_producto').value),
        cantidad: parseInt(document.getElementById('cr_cantidad').value)
    };
    try {
        const res = await fetch(API + '/api/pedidos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        mostrarResultado('resultado-crear', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-crear', 'Error: ' + e.message, true);
    }
}

// =============================================
// 2. LISTAR PEDIDOS
// =============================================
async function listarPedidos() {
    try {
        const res = await fetch(API + '/api/pedidos');
        const result = await res.json();
        mostrarResultado('resultado-listar', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-listar', 'Error: ' + e.message, true);
    }
}

// =============================================
// 3. EDITAR PEDIDO (CORREGIDO)
// =============================================
async function editarPedido() {
    const id = parseInt(document.getElementById('ed_id').value);
    const data = {
        estado: document.getElementById('ed_estado').value,
        total: parseFloat(document.getElementById('ed_total').value)
    };
    try {
        const res = await fetch(API + '/api/pedidos/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        mostrarResultado('resultado-editar', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-editar', 'Error: ' + e.message, true);
    }
}

// =============================================
// 4. ELIMINAR PEDIDO (CORREGIDO)
// =============================================
async function eliminarPedido() {
    const id = parseInt(document.getElementById('del_id').value);
    if (!confirm('Seguro que quieres eliminar el pedido ' + id + '?')) return;
    try {
        const res = await fetch(API + '/api/pedidos/' + id, {
            method: 'DELETE'
        });
        const result = await res.json();
        mostrarResultado('resultado-eliminar', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-eliminar', 'Error: ' + e.message, true);
    }
}

// =============================================
// 5. REPORTE VENTAS
// =============================================
async function reporteVentas() {
    try {
        const res = await fetch(API + '/api/reporte/ventas');
        const result = await res.json();
        mostrarResultado('resultado-reporte', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-reporte', 'Error: ' + e.message, true);
    }
}

function exportarCSV() {
    window.open(API + '/api/reporte/exportar-csv', '_blank');
}

// =============================================
// 6. REPORTE PRODUCTOS
// =============================================
async function reporteProductos() {
    try {
        const res = await fetch(API + '/api/reporte/productos');
        const result = await res.json();
        mostrarResultado('resultado-reporte-productos', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-reporte-productos', 'Error: ' + e.message, true);
    }
}

function exportarProductosCSV() {
    window.open(API + '/api/reporte/productos-csv', '_blank');
}

// =============================================
// 7. JSONB GUARDAR
// =============================================
async function guardarJSONB() {
    try {
        const datos = JSON.parse(document.getElementById('jsonb_datos').value);
        const res = await fetch(API + '/api/jsonb', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ datos })
        });
        const result = await res.json();
        mostrarResultado('resultado-jsonb-guardar', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-jsonb-guardar', 'Error: ' + e.message, true);
    }
}

// =============================================
// 8. JSONB CONSULTAR
// =============================================
async function consultarJSONB() {
    const nombre = document.getElementById('jsonb_nombre').value;
    try {
        const url = nombre ? API + '/api/jsonb?nombre=' + encodeURIComponent(nombre) : API + '/api/jsonb';
        const res = await fetch(url);
        const result = await res.json();
        mostrarResultado('resultado-jsonb-consultar', result, !res.ok);
    } catch (e) {
        mostrarResultado('resultado-jsonb-consultar', 'Error: ' + e.message, true);
    }
}

// =============================================
// CARGA INICIAL
// =============================================
document.addEventListener('DOMContentLoaded', listarPedidos);
