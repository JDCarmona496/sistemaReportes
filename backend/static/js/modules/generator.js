import { API_URL, authHeaders, logout } from "../config.js";

let reportesCache = [];

export function initGenerator() {
  window.cargarModuloGenerator = cargarListaReportes;
  window.cargarFormularioDinamico = cargarFormularioDinamico;
  window.generarReporte = generarReporte;
}

// --- CARGA DE DATOS ---
async function cargarListaReportes() {
  try {
    const res = await fetch(`${API_URL}/reports/?skip=0&limit=100`, {
      headers: authHeaders(),
    });
    if (res.status === 401) logout();
    reportesCache = await res.json();

    // Actualizar contador en Home si existe
    const statEl = document.getElementById("stat-total-reports");
    if (statEl) statEl.innerText = reportesCache.length;

    const select = document.getElementById("reportSelect");
    select.innerHTML = '<option value="">-- Seleccione --</option>';
    reportesCache.forEach((r) => {
      select.innerHTML += `<option value="${r.id}">${r.title}</option>`;
    });
  } catch (e) {
    console.error(e);
  }
}

function cargarFormularioDinamico() {
  const id = document.getElementById("reportSelect").value;
  const container = document.getElementById("dynamicForm");
  container.innerHTML = "";

  if (!id) return;
  const reporte = reportesCache.find((r) => r.id == id);

  if (!reporte.params_config || reporte.params_config.length === 0) {
    container.innerHTML =
      '<p class="text-gray-400 text-sm italic p-2 bg-blue-50 rounded">Este reporte no requiere parámetros.</p>';
    return;
  }

  reporte.params_config.forEach((p) => {
    let html = `<div><label class="block text-xs font-bold text-gray-500 uppercase mb-1">${p.label}</label>`;
    html += `<input type="${p.type}" name="${p.name}" class="param-input w-full border border-gray-300 p-2 rounded outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500">`;
    if (p.name === "lista_pacientes")
      html += `<span class="text-xs text-blue-400">Separe IDs con comas (Ej: 101, 102)</span>`;
    html += `</div>`;
    container.innerHTML += html;
  });
}

// --- LÓGICA DE GENERACIÓN Y COLA ---

async function generarReporte() {
  const reportSelect = document.getElementById("reportSelect");
  const reportId = reportSelect.value;
  const reportTitle = reportSelect.options[reportSelect.selectedIndex]?.text;

  if (!reportId)
    return Swal.fire("Atención", "Seleccione un reporte primero", "warning");

  const params = {};
  document.querySelectorAll(".param-input").forEach((i) => {
    let val = i.value;
    if (i.name === "lista_pacientes" || val.includes(","))
      val = val.split(",").filter((x) => x.trim() !== "");
    params[i.name] = val;
  });

  const formato = document.querySelector('input[name="formato"]:checked').value;

  try {
    // Feedback Toast
    const Toast = Swal.mixin({
      toast: true,
      position: "top-end",
      showConfirmButton: false,
      timer: 2000,
    });
    Toast.fire({ icon: "info", title: "Enviando solicitud..." });

    const res = await fetch(`${API_URL}/reports/generar-background`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        reporte_id: parseInt(reportId),
        params: params,
        formato: formato,
      }),
    });

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    // AGREGAR A LA COLA VISUAL
    agregarFilaCola(data.task_id, reportTitle, formato);
  } catch (e) {
    Swal.fire("Error", e.message, "error");
  }
}

function agregarFilaCola(taskId, titulo, formato) {
  const tbody = document.getElementById("downloads-body");
  const emptyMsg = document.getElementById("empty-queue-msg");
  if (emptyMsg) emptyMsg.classList.add("hidden");

  const tr = document.createElement("tr");
  tr.id = `row-${taskId}`;
  tr.className =
    "new-row bg-blue-50 border-b border-blue-100 transition-colors duration-500";
  tr.innerHTML = `
        <td class="px-4 py-3 font-medium text-gray-800">${titulo}</td>
        <td class="px-4 py-3 text-xs uppercase text-gray-500">${formato}</td>
        <td class="px-4 py-3">
            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-blue-200 text-blue-800">
                <i class="fa-solid fa-circle-notch fa-spin"></i> Procesando
            </span>
        </td>
        <td class="px-4 py-3 text-right text-xs text-gray-400">Espere...</td>
    `;
  // Insertar al inicio de la tabla
  tbody.insertBefore(tr, tbody.firstChild);

  // Iniciar monitoreo individual
  monitorFila(taskId, tr);
}

function monitorFila(taskId, rowElement) {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`${API_URL}/reports/task/${taskId}`, {
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.estado === "SUCCESS") {
        clearInterval(interval);

        // Actualizar Fila a Éxito
        rowElement.classList.remove("bg-blue-50");
        rowElement.classList.add("bg-white");

        const url = data.resultado.url_descarga;
        const isPdf = data.resultado.formato === "PDF";
        const btnClass = isPdf
          ? "text-red-600 border-red-200 hover:bg-red-50"
          : "text-green-600 border-green-200 hover:bg-green-50";
        const icon = isPdf ? "fa-file-pdf" : "fa-file-csv";

        rowElement.querySelector("td:nth-child(3)").innerHTML = `
                    <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                        <i class="fa-solid fa-check"></i> Listo
                    </span>`;

        rowElement.querySelector("td:nth-child(4)").innerHTML = `
                    <a href="${url}" target="_blank" class="inline-flex items-center gap-1 border ${btnClass} border px-3 py-1 rounded transition font-bold text-xs">
                        <i class="fa-solid ${icon}"></i> Descargar
                    </a>`;
      } else if (data.estado === "FAILURE") {
        clearInterval(interval);
        rowElement.classList.add("bg-red-50");
        rowElement.querySelector("td:nth-child(3)").innerHTML =
          `<span class="text-red-600 font-bold text-xs">Error</span>`;
        rowElement.querySelector("td:nth-child(4)").innerText =
          "Fallo en worker";
      }
    } catch (e) {
      // Si falla la red, sigue intentando en el próximo intervalo
      clearInterval(interval);
    }
  }, 2000);
}
