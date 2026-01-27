// 1. Importaciones del Núcleo
import { verificarPermisos, logout } from "./auth.js";
import { loadView } from "./router.js";

// 2. Importaciones de Módulos (Lógica específica)
import { initHome } from "./modules/home.js";
import { initGenerator } from "./modules/generator.js";
import { initReports } from "./modules/reports.js";
import { initUsers } from "./modules/users.js";
import { initSettings } from "./modules/settings.js";

// 3. Exponer funciones GLOBALES para el HTML
// (Necesario porque los módulos son privados por defecto, pero el HTML usa onclick="...")
window.logout = logout;
window.loadView = loadView;

// 4. Inicializar Módulos
// Esto registra las funciones específicas de cada vista (ej: window.generarReporte)
initHome();
initGenerator();
initReports();
initUsers();
initSettings();

// 5. Lógica de Arranque
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 Sistema BIOLAB Iniciado");

  // Primero verificamos quién es el usuario (Admin u Operador)
  verificarPermisos().then((esAdmin) => {
    // Una vez sabemos quién es, cargamos la vista inicial
    loadView("home");
  });
});
