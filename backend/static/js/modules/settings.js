import { API_URL, authHeaders } from "../config.js";

let systemConfig = {};

export function initSettings() {
  window.cargarModuloSettings = cargarConfiguracion;
  window.guardarConfiguracion = guardarConfiguracion;

  // Cargar config visual al inicio (sin necesidad de entrar al módulo)
  obtenerConfiguracionGlobal();
}

async function obtenerConfiguracionGlobal() {
  try {
    const res = await fetch(`${API_URL}/config/`, { headers: authHeaders() });
    const data = await res.json();
    data.forEach((item) => {
      systemConfig[item.key] = item.value;
    });
    aplicarTemaVisual();
  } catch (e) {}
}

function aplicarTemaVisual() {
  if (systemConfig.app_title) document.title = systemConfig.app_title;
  if (systemConfig.navbar_title)
    document.getElementById("page-title").innerText = systemConfig.navbar_title;
  if (systemConfig.company_name) {
    const brand = document.querySelector("aside div i + span");
    if (brand) brand.innerText = " " + systemConfig.company_name;
  }
  if (systemConfig.sidebar_color) {
    const sidebar = document.getElementById("main-sidebar");
    if (sidebar) {
      sidebar.style.backgroundColor = systemConfig.sidebar_color;
      sidebar.querySelector("div").style.backgroundColor =
        systemConfig.sidebar_color;
    }
  }
}

function cargarConfiguracion() {
  const container = document.getElementById("settings-container");
  container.innerHTML = "Cargando...";
  fetch(`${API_URL}/config/`, { headers: authHeaders() })
    .then((r) => r.json())
    .then((data) => {
      container.innerHTML = "";
      const categories = {};
      data.forEach((item) => {
        if (!categories[item.category]) categories[item.category] = [];
        categories[item.category].push(item);
      });
      for (const [cat, items] of Object.entries(categories)) {
        let html = `<div class="col-span-1 md:col-span-2 mt-4"><h4 class="font-bold text-gray-400 uppercase text-xs border-b mb-3">${cat}</h4></div>`;
        items.forEach((item) => {
          let inputType = item.key.includes("color") ? "color" : "text";
          let inputClass = item.key.includes("color")
            ? "w-16 h-10 p-1"
            : "w-full";
          html += `<div class="bg-gray-50 p-4 rounded border border-gray-200"><label class="block text-sm font-bold text-gray-700">${item.key.replace(/_/g, " ").toUpperCase()}</label><p class="text-xs text-gray-400 mb-2">${item.description || ""}</p><div class="flex items-center gap-2"><input type="${inputType}" data-key="${item.key}" value="${item.value}" class="setting-input ${inputClass} border rounded focus:ring-2 focus:ring-blue-500"></div></div>`;
        });
        container.innerHTML += html;
      }
    });
}

async function guardarConfiguracion() {
  const settings = {};
  document
    .querySelectorAll(".setting-input")
    .forEach((i) => (settings[i.dataset.key] = i.value));
  await fetch(`${API_URL}/config/`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify({ settings: settings }),
  });
  Swal.fire("Guardado", "", "success");
  obtenerConfiguracionGlobal();
}
