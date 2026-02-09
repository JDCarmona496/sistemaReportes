import { API_URL, authHeaders } from "../config.js";

let tasksCache = [];

export function initScheduler() {
  window.cargarModuloScheduler = cargarTablaScheduler;
  window.abrirModalScheduler = abrirModalScheduler;
  window.cerrarModalScheduler = cerrarModalScheduler;
  window.guardarScheduler = guardarScheduler;
  window.editarScheduler = editarScheduler;
  window.eliminarScheduler = eliminarScheduler;
}

// --- 1. CARGAR Y RENDERIZAR TABLA ---
function cargarTablaScheduler() {
  const tbody = document.getElementById("scheduler-table-body");
  if (!tbody) return; // Si no estamos en la vista correcta, salir

  tbody.innerHTML =
    '<tr><td colspan="6" class="text-center py-4 text-gray-500"><i class="fa-solid fa-circle-notch fa-spin mr-2"></i>Cargando programación...</td></tr>';

  fetch(`${API_URL}/scheduler/`, { headers: authHeaders() })
    .then((res) => {
      if (res.status === 403) throw new Error("Acceso denegado");
      if (!res.ok) throw new Error("Error al cargar tareas");
      return res.json();
    })
    .then((tasks) => {
      tasksCache = tasks; // Guardar en caché para edición
      tbody.innerHTML = "";

      if (tasks.length === 0) {
        tbody.innerHTML =
          '<tr><td colspan="6" class="text-center py-8 text-gray-400 italic">No hay tareas programadas.</td></tr>';
        return;
      }

      tasks.forEach((t) => {
        // --- CORRECCIÓN VISUAL: Formatear CRON ---
        // Evita que '*' se muestre como '0*'
        const formatTime = (val) =>
          val === "*" ? "*" : val.toString().padStart(2, "0");

        const hour = formatTime(t.crontab_hour);
        const min = formatTime(t.crontab_minute);
        const cronText = `${hour}:${min}`;

        const dias =
          t.crontab_day_of_week === "*"
            ? "Todos los días"
            : t.crontab_day_of_week;

        // Formato de última ejecución
        let lastRun = "Nunca";
        let lastRunClass = "text-gray-400";
        if (t.last_run_at) {
          const date = new Date(t.last_run_at);
          lastRun = date.toLocaleString("es-CO");
          lastRunClass = "text-gray-700 font-mono text-xs";
        }

        const estadoBadge = t.enabled
          ? '<span class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold border border-green-200">Activa</span>'
          : '<span class="bg-gray-100 text-gray-500 text-xs px-2 py-1 rounded-full font-bold border border-gray-200">Pausada</span>';

        const tr = document.createElement("tr");
        tr.className =
          "hover:bg-gray-50 border-b last:border-0 transition-colors";
        tr.innerHTML = `
                    <td class="px-6 py-4 font-medium text-gray-900">
                        ${t.name}
                        <div class="text-xs text-gray-400 font-mono mt-1">${t.task.split(".").pop()}</div>
                    </td>
                    <td class="px-6 py-4 text-blue-600 font-bold font-mono">
                        <i class="fa-regular fa-clock mr-1"></i> ${cronText}
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600">${dias}</td>
                    <td class="px-6 py-4 text-center text-xs font-mono bg-gray-50 rounded">${t.total_run_count}</td>
                    <td class="px-6 py-4 text-center ${lastRunClass}">${lastRun}</td>
                    <td class="px-6 py-4 text-center">${estadoBadge}</td>
                    <td class="px-6 py-4 text-right space-x-2">
                        <button onclick='editarScheduler(${t.id})' class="text-indigo-600 hover:text-indigo-900 transition p-2 rounded hover:bg-indigo-50" title="Editar">
                            <i class="fa-solid fa-pen-to-square text-lg"></i>
                        </button>
                        <button onclick="eliminarScheduler(${t.id})" class="text-red-600 hover:text-red-900 transition p-2 rounded hover:bg-red-50" title="Eliminar">
                            <i class="fa-solid fa-trash text-lg"></i>
                        </button>
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch((err) => {
      console.error(err);
      tbody.innerHTML = `<tr><td colspan="6" class="text-center text-red-500 py-4"><i class="fa-solid fa-triangle-exclamation mr-2"></i>${err.message}</td></tr>`;
    });
}

// --- 2. GESTIÓN DEL MODAL ---
function abrirModalScheduler(isEdit = false) {
  const modal = document.getElementById("modal-scheduler");
  modal.classList.remove("hidden");
  document.getElementById("modal-scheduler-title").innerText = isEdit
    ? "Editar Tarea Programada"
    : "Nueva Tarea Programada";

  if (!isEdit) {
    // Limpiar formulario para crear
    document.getElementById("sch-id").value = "";
    document.getElementById("sch-name").value = "";
    document.getElementById("sch-task").value =
      "app.worker.generar_reporte_pesado_task"; // Default común
    document.getElementById("sch-args").value = "[]";
    document.getElementById("sch-kwargs").value = "{}";
    document.getElementById("sch-enabled").checked = true;

    // Reset Cron (Por defecto a las 00:00)
    document.getElementById("sch-hour").value = "0";
    document.getElementById("sch-minute").value = "0";
    document.getElementById("sch-days").value = "*";
  }
}

function cerrarModalScheduler() {
  document.getElementById("modal-scheduler").classList.add("hidden");
}

function editarScheduler(id) {
  const t = tasksCache.find((x) => x.id === id);
  if (!t) return;

  abrirModalScheduler(true);

  document.getElementById("sch-id").value = t.id;
  document.getElementById("sch-name").value = t.name;
  document.getElementById("sch-task").value = t.task;
  document.getElementById("sch-args").value = JSON.stringify(t.args);
  document.getElementById("sch-kwargs").value = JSON.stringify(t.kwargs);
  document.getElementById("sch-enabled").checked = t.enabled;

  // Cargar CRON
  document.getElementById("sch-hour").value = t.crontab_hour;
  document.getElementById("sch-minute").value = t.crontab_minute;
  document.getElementById("sch-days").value = t.crontab_day_of_week;
}

// --- 3. GUARDAR (CREAR / EDITAR) ---
async function guardarScheduler() {
  const id = document.getElementById("sch-id").value;
  const name = document.getElementById("sch-name").value;
  const taskName = document.getElementById("sch-task").value;
  const enabled = document.getElementById("sch-enabled").checked;

  // Recolectar CRON
  const hour = document.getElementById("sch-hour").value;
  const minute = document.getElementById("sch-minute").value;
  const days = document.getElementById("sch-days").value;

  try {
    // Validar JSON de argumentos
    const args = JSON.parse(document.getElementById("sch-args").value || "[]");
    const kwargs = JSON.parse(
      document.getElementById("sch-kwargs").value || "{}",
    );

    if (!name || !taskName) throw new Error("Nombre y Tarea son obligatorios");

    const payload = {
      name: name,
      task: taskName,
      args: args,
      kwargs: kwargs,
      enabled: enabled,
      // Mapeo al Schema del Backend
      crontab_hour: hour,
      crontab_minute: minute,
      crontab_day_of_week: days,
      crontab_day_of_month: "*",
      crontab_month_of_year: "*",
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/scheduler/${id}` : `${API_URL}/scheduler/`;

    const res = await fetch(url, {
      method: method,
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Error al guardar");
    }

    Swal.fire({
      icon: "success",
      title: "Guardado",
      text: "La tarea ha sido programada correctamente.",
      timer: 1500,
      showConfirmButton: false,
    });

    cerrarModalScheduler();
    cargarTablaScheduler();
  } catch (e) {
    Swal.fire("Error", e.message, "error");
  }
}

// --- 4. ELIMINAR ---
async function eliminarScheduler(id) {
  const result = await Swal.fire({
    title: "¿Detener y Eliminar?",
    text: "Esta tarea dejará de ejecutarse permanentemente.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  });

  if (result.isConfirmed) {
    try {
      const res = await fetch(`${API_URL}/scheduler/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });

      if (!res.ok) throw new Error("Error al eliminar");

      Swal.fire("Eliminado", "La tarea ha sido eliminada.", "success");
      cargarTablaScheduler();
    } catch (e) {
      Swal.fire("Error", e.message, "error");
    }
  }
}
