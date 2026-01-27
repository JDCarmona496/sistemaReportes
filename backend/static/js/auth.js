import { API_URL, getToken, logout } from "./config.js";

// --- CORRECCIÓN CRÍTICA ---
// Re-exportamos 'logout' para que app.js pueda importarlo desde aquí.
export { logout };

export let esAdmin = false;

export async function verificarPermisos() {
  const token = getToken();
  if (!token) {
    window.location.href = "/";
    return;
  }

  try {
    const res = await fetch(`${API_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const user = await res.json();
    esAdmin = user.is_superuser;

    // UI Header
    const nameDisplay = document.getElementById("user-name-display");
    const roleDisplay = document.getElementById("user-role-display");

    if (nameDisplay) nameDisplay.innerText = user.full_name || user.email;
    if (roleDisplay) {
      roleDisplay.innerText = esAdmin ? "ADMINISTRADOR" : "OPERADOR";
      roleDisplay.className = esAdmin
        ? "text-xs text-red-600 font-bold"
        : "text-xs text-blue-500 font-bold";
    }

    // UI Sidebar
    const adminMenu = document.getElementById("admin-menu-section");
    if (adminMenu) {
      if (esAdmin) adminMenu.classList.remove("hidden");
      else adminMenu.classList.add("hidden");
    }

    return esAdmin;
  } catch (e) {
    console.error(e);
    logout();
  }
}
