import { API_URL, authHeaders } from '../config.js';

let userChart = null;
let activityChart = null;

export function initHome() {
    // Exponer función de carga para el Router
    window.cargarModuloHome = () => {
        cargarDatosIniciales();
        cargarGraficas();
    };
}

async function cargarDatosIniciales() {
    // Cargar historial
    try {
        const res = await fetch(`http://127.0.0.1:8000/historial`, { headers: authHeaders() });
        const data = await res.json();
        const div = document.getElementById('dashboard-history');
        
        if (data.ultimos_eventos && data.ultimos_eventos.length > 0) {
            let html = '<ul class="divide-y divide-gray-200">';
            data.ultimos_eventos.forEach(ev => { 
                html += `<li class="py-2 flex justify-between">
                    <span class="font-medium text-blue-700">${ev.reporte || 'Reporte'}</span>
                    <span class="text-xs text-gray-400">${ev.hora}</span>
                </li>`; 
            });
            div.innerHTML = html + '</ul>';
        } else { 
            div.innerHTML = 'Sin actividad reciente.'; 
        }
    } catch (e) {}
}

function cargarGraficas() {
    fetch(`${API_URL}/stats/`, { headers: authHeaders() })
    .then(r => r.json())
    .then(data => {
        // Render Charts (Chart.js)
        const ctx1 = document.getElementById('chartUsers').getContext('2d');
        if (userChart) userChart.destroy();
        userChart = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Admin', 'Operador'],
                datasets: [{ data: [data.users.admins, data.users.operators], backgroundColor: ['#ef4444', '#3b82f6'] }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });

        const ctx2 = document.getElementById('chartActivity').getContext('2d');
        if (activityChart) activityChart.destroy();
        activityChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: data.activity.labels || ["Sin Datos"],
                datasets: [{ label: 'Generaciones', data: data.activity.data || [0], backgroundColor: '#10b981', borderRadius: 4 }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    });
}