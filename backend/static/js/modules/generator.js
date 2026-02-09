import { API_URL, authHeaders, logout } from "../config.js";

let reportesCache = [];

// --- FUNCIÓN DE INICIALIZACIÓN (EXPORTADA) ---
export function initGenerator() {
  // Exponemos las funciones al ámbito global (window) para que el HTML pueda usarlas
  window.cargarModuloGenerator = cargarListaReportes;
  window.cargarFormularioDinamico = cargarFormularioDinamico;
  window.generarReporte = generarReporte;

  // Opcional: Si queremos exponer la función de cola también
  window.agregarFilaCola = agregarFilaCola;
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
    if (select) {
      select.innerHTML = '<option value="">-- Seleccione --</option>';
      reportesCache.forEach((r) => {
        const opt = document.createElement("option");
        opt.value = r.id;
        opt.innerText = r.title;
        select.appendChild(opt);
      });
    }
  } catch (e) {
    console.error(e);
  }
}

function cargarFormularioDinamico() {
  const id = document.getElementById("reportSelect").value;
  const container = document.getElementById("dynamicForm");

  if (!container) return;
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

// --- LÓGICA DE GENERACIÓN ---

async function generarReporte() {
  const reportSelect = document.getElementById("reportSelect");
  if (!reportSelect) return;

  const reportId = reportSelect.value;
  const reportTitle =
    reportSelect.options[reportSelect.selectedIndex]?.text || "Reporte";

  if (!reportId)
    return Swal.fire("Atención", "Seleccione un reporte primero", "warning");

  // 1. Parámetros
  const params = {};
  const inputs = document.querySelectorAll(".param-input");
  inputs.forEach((i) => {
    let val = i.value;
    if (i.name === "lista_pacientes" || val.includes(","))
      val = val.split(",").filter((x) => x.trim() !== "");
    params[i.name] = val;
  });

  // 2. Formato (PDF/CSV)
  const formatoRadio = document.querySelector('input[name="formato"]:checked');
  const formato = formatoRadio ? formatoRadio.value : "PDF";

  // 3. CAPTURA DE SEDE
  // Buscamos cuál radio button de 'sede' está seleccionado
  const sedeRadio = document.querySelector('input[name="sede"]:checked');
  const sede = sedeRadio ? sedeRadio.value : "BIOLAB"; // Valor por defecto

  console.log(`📡 Enviando reporte ID ${reportId} a sede: ${sede}`);

  try {
    const Toast = Swal.mixin({
      toast: true,
      position: "top-end",
      showConfirmButton: false,
      timer: 2000,
    });
    Toast.fire({ icon: "info", title: "Enviando solicitud..." });

    // Enviamos el JSON incluyendo la sede
    const res = await fetch(`${API_URL}/reports/generar-background`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        reporte_id: parseInt(reportId),
        params: params,
        formato: formato,
        sede: sede,
      }),
    });

    const data = await res.json();
    if (data.error) throw new Error(data.error);

    // Agregamos a la cola visual
    agregarFilaCola(data.task_id, reportTitle, formato, sede);
  } catch (e) {
    Swal.fire("Error", e.message, "error");
  }
}

// --- LÓGICA DE COLA VISUAL ---

function agregarFilaCola(taskId, titulo, formato, sede) {
  const tbody = document.getElementById("downloads-body");
  if (!tbody) return;

  const emptyMsg = document.getElementById("empty-queue-msg");
  if (emptyMsg) emptyMsg.classList.add("hidden");

  const tr = document.createElement("tr");
  tr.id = `row-${taskId}`;
  tr.className =
    "new-row bg-blue-50 border-b border-blue-100 transition-colors duration-500";

  // Color distintivo para la sede
  const sedeColor =
    sede === "BIOLAB"
      ? "bg-blue-100 text-blue-800"
      : "bg-purple-100 text-purple-800";

  tr.innerHTML = `
        <td class="px-4 py-3 font-medium text-gray-800">${titulo}</td>
        <td class="px-4 py-3">
             <div class="flex flex-col gap-1">
                <span class="text-xs uppercase font-bold text-gray-500">${formato}</span>
                <span class="inline-flex w-fit items-center px-2 py-0.5 rounded text-[10px] font-bold border border-transparent ${sedeColor}">
                    ${sede}
                </span>
             </div>
        </td>
        <td class="px-4 py-3">
            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-blue-200 text-blue-800 animate-pulse">
                <i class="fa-solid fa-circle-notch fa-spin"></i> Procesando
            </span>
        </td>
        <td class="px-4 py-3 text-right text-xs text-gray-400">Espere...</td>
    `;

  tbody.insertBefore(tr, tbody.firstChild);

  monitorFila(taskId, tr);
}

function monitorFila(taskId, rowElement) {
  let intentos = 0;
  const interval = setInterval(async () => {
    intentos++;
    if (intentos > 300) {
      clearInterval(interval);
      return;
    } // Timeout 10 min

    try {
      const res = await fetch(`${API_URL}/reports/task/${taskId}`, {
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.estado === "SUCCESS") {
        clearInterval(interval);

        if (rowElement) {
          rowElement.classList.remove("bg-blue-50");
          rowElement.classList.add("bg-white");

          const resultado = data.resultado;

          // CASO OFFLINE / VACÍO
          if (resultado.status === "skipped" || !resultado.url_descarga) {
            rowElement.classList.add("bg-yellow-50");
            const celdaEstado = rowElement.querySelector("td:nth-child(3)");
            const celdaAccion = rowElement.querySelector("td:nth-child(4)");

            if (celdaEstado)
              celdaEstado.innerHTML = `
                            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800 border border-yellow-200">
                                <i class="fa-solid fa-triangle-exclamation"></i> Offline/Vacío
                            </span>`;
            if (celdaAccion)
              celdaAccion.innerHTML = `<span class="text-yellow-600 text-xs truncate max-w-[150px] block" title="${resultado.mensaje}">${resultado.mensaje}</span>`;
          }
          // CASO ÉXITO
          else {
            const url = resultado.url_descarga;
            const isPdf = resultado.formato === "PDF";
            const btnClass = isPdf
              ? "text-red-600 border-red-200 hover:bg-red-50"
              : "text-green-600 border-green-200 hover:bg-green-50";
            const icon = isPdf ? "fa-file-pdf" : "fa-file-csv";

            const celdaEstado = rowElement.querySelector("td:nth-child(3)");
            const celdaAccion = rowElement.querySelector("td:nth-child(4)");

            if (celdaEstado)
              celdaEstado.innerHTML = `
                            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800 border border-green-200">
                                <i class="fa-solid fa-check"></i> Listo
                            </span>`;

            if (celdaAccion)
              celdaAccion.innerHTML = `
                            <a href="${url}" target="_blank" class="inline-flex items-center gap-1 border ${btnClass} border px-3 py-1 rounded transition font-bold text-xs shadow-sm">
                                <i class="fa-solid ${icon}"></i> Descargar
                            </a>`;
          }
        }
      } else if (data.estado === "FAILURE") {
        clearInterval(interval);
        if (rowElement) {
          rowElement.classList.add("bg-red-50");
          rowElement.querySelector("td:nth-child(3)").innerHTML =
            `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800"><i class="fa-solid fa-xmark"></i> Error</span>`;
          rowElement.querySelector("td:nth-child(4)").innerText =
            "Fallo en worker";
        }
      }
    } catch (e) {
      // Si falla la red, sigue intentando
    }
  }, 2000);
}
