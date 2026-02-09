import { esAdmin } from "./auth.js";

// Mapeo de vistas a sus módulos de carga
const viewLoaders = {
  home: () => window.cargarModuloHome && window.cargarModuloHome(),
  generator: () =>
    window.cargarModuloGenerator && window.cargarModuloGenerator(),
  "admin-reports": () =>
    window.cargarModuloReports && window.cargarModuloReports(),
  users: () => window.cargarModuloUsers && window.cargarModuloUsers(),
  settings: () => window.cargarModuloSettings && window.cargarModuloSettings(),
  monitor: () => window.cargarModuloMonitor && window.cargarModuloMonitor(),
  scheduler: () => window.cargarModuloScheduler && window.cargarModuloScheduler(),
};

export function loadView(viewName) {
  // Protección de rutas
  const vistasAdmin = ["admin-reports", "users", "monitor", "settings"];
  if (vistasAdmin.includes(viewName) && !esAdmin) {
    Swal.fire(
      "Acceso Denegado",
      "No tienes permisos de administrador.",
      "error",
    );
    return;
  }

  // UI Updates
  document
    .querySelectorAll(".view-section")
    .forEach((el) => el.classList.add("hidden"));
  document
    .querySelectorAll(".nav-item")
    .forEach((el) => el.classList.remove("active"));

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.remove("hidden");

  const nav = document.getElementById(`nav-${viewName}`);
  if (nav) nav.classList.add("active");

  // Títulos
  const titulos = {
    home: "Resumen General",
    generator: "Generador de Reportes",
    "admin-reports": "Configuración de Reportes",
    monitor: "Monitor del Sistema",
    users: "Gestión de Usuarios",
    settings: "Configuración del Sistema",
  };
  document.getElementById("page-title").innerText =
    titulos[viewName] || "Dashboard";

  // Ejecutar cargador del módulo específico
  if (viewLoaders[viewName]) viewLoaders[viewName]();
}
