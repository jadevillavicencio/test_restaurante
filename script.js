const API = 'http://localhost:5000';

// =============================================
// TABS
// =============================================
function mostrarTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    event.target.classList.add('active');
}

function mostrarResultado(id, data) {
    const el = document.getElementById(id);
    el.textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
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
        mostrarResultado('resultado-crear', result);
    } catch (e) {
        mostrarResultado('resultado-crear', 'Error: ' + e.message);
    }
}

// =============================================
// 2. LISTAR PEDIDOS
// =============================================
async function listarPedidos() {
    try {
        const res = await fetch(API + '/api/pedidos');
        const result = await res.json();
        mostrarResultado('resultado-listar', result);
    } catch (e) {
        mostrarResultado('resultado-listar', 'Error: ' + e.message);
    }
}

// =============================================
// 3. EDITAR PEDIDO
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
        mostrarResultado('resultado-editar', result);
    } catch (e) {
        mostrarResultado('resultado-editar', 'Error: ' + e.message);
    }
}

// =============================================
// 4. ELIMINAR PEDIDO
// =============================================
async function eliminarPedido() {
    const id = parseInt(document.getElementById('del_id').value);
    if (!confirm('Eliminar pedido ' + id + '?')) return;
    try {
        const res = await fetch(API + '/api/pedidos/' + id, { method: 'DELETE' });
        const result = await res.json();
        mostrarResultado('resultado-eliminar', result);
    } catch (e) {
        mostrarResultado('resultado-eliminar', 'Error: ' + e.message);
    }
}

// =============================================
// 5. REPORTE VENTAS
// =============================================
async function reporteVentas() {
    try {
        const res = await fetch(API + '/api/reporte/ventas');
        const result = await res.json();
        mostrarResultado('resultado-reporte', result);
    } catch (e) {
        mostrarResultado('resultado-reporte', 'Error: ' + e.message);
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
        mostrarResultado('resultado-reporte-productos', result);
    } catch (e) {
        mostrarResultado('resultado-reporte-productos', 'Error: ' + e.message);
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
        mostrarResultado('resultado-jsonb-guardar', result);
    } catch (e) {
        mostrarResultado('resultado-jsonb-guardar', 'Error: ' + e.message);
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
        mostrarResultado('resultado-jsonb-consultar', result);
    } catch (e) {
        mostrarResultado('resultado-jsonb-consultar', 'Error: ' + e.message);
    }
}

// =============================================
// AL CARGAR: listar pedidos automaticamente
// =============================================
document.addEventListener('DOMContentLoaded', listarPedidos);
