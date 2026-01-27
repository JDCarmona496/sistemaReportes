import { API_URL, authHeaders } from "../config.js";

let reportesCache = [];

export function initReports() {
  window.cargarModuloReports = cargarTablaAdmin;
  window.abrirModalReporte = abrirModalReporte;
  window.cerrarModal = cerrarModal;
  window.editarReporte = editarReporte;
  window.guardarReporte = guardarReporte;
  window.eliminarReporte = eliminarReporte;
}

function cargarTablaAdmin() {
  const tbody = document.getElementById("admin-reports-table");
  tbody.innerHTML = "";
  fetch(`${API_URL}/reports/?skip=0&limit=100`, { headers: authHeaders() })
    .then((r) => r.json())
    .then((res) => {
      reportesCache = res;
      res.forEach((r) => {
        const layoutBadge =
          r.layout === "ficha"
            ? `<span class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full font-bold border border-purple-200">Ficha</span>`
            : `<span class="bg-teal-100 text-teal-800 text-xs px-2 py-1 rounded-full font-bold border border-teal-200">Tabla</span>`;

        tbody.innerHTML += `<tr><td class="p-3">${r.id}</td><td class="p-3 font-bold">${r.title}</td><td class="p-3">${layoutBadge}</td><td class="p-3">${r.params_config.length}</td><td class="p-3 text-right"><button onclick='editarReporte(${r.id})' class="text-blue-600 mr-2"><i class="fa-solid fa-pen"></i></button><button onclick="eliminarReporte(${r.id})" class="text-red-600"><i class="fa-solid fa-trash"></i></button></td></tr>`;
      });
    });
}

function abrirModalReporte(isEdit = false) {
  document.getElementById("modal-reporte").classList.remove("hidden");
  document.getElementById("modal-title").innerText = isEdit
    ? "Editar"
    : "Nuevo";
  if (!isEdit) {
    document.getElementById("edit-report-id").value = "";
    document.getElementById("edit-title").value = "";
    document.getElementById("edit-query").value = "";
    document.getElementById("edit-params").value = "[]";
  }
}
function cerrarModal() {
  document.getElementById("modal-reporte").classList.add("hidden");
}

function editarReporte(id) {
  const r = reportesCache.find((x) => x.id === id);
  if (r) {
    abrirModalReporte(true);
    document.getElementById("edit-report-id").value = r.id;
    document.getElementById("edit-title").value = r.title;
    document.getElementById("edit-query").value = r.sql_query;
    document.getElementById("edit-params").value = JSON.stringify(
      r.params_config,
      null,
      4,
    );
    document.getElementById("edit-layout").value = r.layout || "tabla";
  }
}

async function guardarReporte() {
  const id = document.getElementById("edit-report-id").value;
  try {
    const payload = {
      title: document.getElementById("edit-title").value,
      sql_query: document.getElementById("edit-query").value,
      params_config: JSON.parse(document.getElementById("edit-params").value),
      layout: document.getElementById("edit-layout").value,
    };
    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/reports/${id}` : `${API_URL}/reports/`;
    await fetch(url, {
      method: method,
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    cerrarModal();
    cargarTablaAdmin();
    Swal.fire("Guardado", "", "success");
  } catch (e) {
    Swal.fire("Error", e.message, "error");
  }
}

async function eliminarReporte(id) {
  if (
    (await Swal.fire({ title: "¿Borrar?", showCancelButton: true })).isConfirmed
  ) {
    await fetch(`${API_URL}/reports/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    cargarTablaAdmin();
  }
}
