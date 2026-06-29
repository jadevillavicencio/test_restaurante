const API = 'http://127.0.0.1:5000';

function mostrarTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    event.target.classList.add('active');
}

function mostrarResultado(id, data) {
    document.getElementById(id).textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
}

async function crearPedido() {
    const data = {
        id_cliente: parseInt(document.getElementById('cr_cliente').value),
        id_empleado: parseInt(document.getElementById('cr_empleado').value),
        id_mesa: parseInt(document.getElementById('cr_mesa').value),
        id_producto: parseInt(document.getElementById('cr_producto').value),
        cantidad: parseInt(document.getElementById('cr_cantidad').value)
    };
    try {
        const res = await fetch(API + '/api/pedidos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        mostrarResultado('resultado-crear', await res.json());
    } catch (e) { mostrarResultado('resultado-crear', 'Error: ' + e.message); }
}

async function listarPedidos() {
    try {
        const res = await fetch(API + '/api/pedidos');
        mostrarResultado('resultado-listar', await res.json());
    } catch (e) { mostrarResultado('resultado-listar', 'Error: ' + e.message); }
}

async function editarPedido() {
    const id = parseInt(document.getElementById('ed_id').value);
    const data = { estado: document.getElementById('ed_estado').value, total: parseFloat(document.getElementById('ed_total').value) };
    try {
        const res = await fetch(API + '/api/pedidos/' + id, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        mostrarResultado('resultado-editar', await res.json());
    } catch (e) { mostrarResultado('resultado-editar', 'Error: ' + e.message); }
}

async function eliminarPedido() {
    const id = parseInt(document.getElementById('del_id').value);
    if (!confirm('Eliminar pedido ' + id + '?')) return;
    try {
        const res = await fetch(API + '/api/pedidos/' + id, { method: 'DELETE' });
        mostrarResultado('resultado-eliminar', await res.json());
    } catch (e) { mostrarResultado('resultado-eliminar', 'Error: ' + e.message); }
}

async function reporteVentas() {
    try {
        const res = await fetch(API + '/api/reporte/ventas');
        mostrarResultado('resultado-reporte', await res.json());
    } catch (e) { mostrarResultado('resultado-reporte', 'Error: ' + e.message); }
}

function exportarCSV() { window.open(API + '/api/reporte/exportar-csv', '_blank'); }

async function reporteProductos() {
    try {
        const res = await fetch(API + '/api/reporte/productos');
        mostrarResultado('resultado-reporte-productos', await res.json());
    } catch (e) { mostrarResultado('resultado-reporte-productos', 'Error: ' + e.message); }
}

function exportarProductosCSV() { window.open(API + '/api/reporte/productos-csv', '_blank'); }

async function guardarJSONB() {
    try {
        const datos = JSON.parse(document.getElementById('jsonb_datos').value);
        const res = await fetch(API + '/api/jsonb', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ datos }) });
        mostrarResultado('resultado-jsonb-guardar', await res.json());
    } catch (e) { mostrarResultado('resultado-jsonb-guardar', 'Error: ' + e.message); }
}

async function consultarJSONB() {
    const nombre = document.getElementById('jsonb_nombre').value;
    try {
        const url = nombre ? API + '/api/jsonb?nombre=' + encodeURIComponent(nombre) : API + '/api/jsonb';
        const res = await fetch(url);
        mostrarResultado('resultado-jsonb-consultar', await res.json());
    } catch (e) { mostrarResultado('resultado-jsonb-consultar', 'Error: ' + e.message); }
}

document.addEventListener('DOMContentLoaded', listarPedidos);
