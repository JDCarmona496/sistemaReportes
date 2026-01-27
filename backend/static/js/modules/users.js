import { API_URL, authHeaders } from "../config.js";

export function initUsers() {
  window.cargarModuloUsers = cargarTablaUsuarios;
  window.abrirModalUsuario = abrirModalUsuario;
  window.cerrarModalUsuario = cerrarModalUsuario;
  window.guardarUsuario = guardarUsuario;
  window.editarUsuario = editarUsuario;
  window.eliminarUsuario = eliminarUsuario;
}

function cargarTablaUsuarios() {
  const tbody = document.getElementById("users-table-body");
  tbody.innerHTML =
    '<tr><td colspan="6" class="text-center py-4">Cargando...</td></tr>';

  fetch(`${API_URL}/users/`, { headers: authHeaders() })
    .then((res) => res.json())
    .then((users) => {
      tbody.innerHTML = "";
      users.forEach((u) => {
        const rolBadge = u.is_superuser
          ? '<span class="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-bold border border-red-200">Admin</span>'
          : '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full border border-blue-200">Operador</span>';
        const estadoBadge = u.is_active
          ? '<span class="text-green-600 font-bold text-xs flex items-center gap-1"><i class="fa-solid fa-check"></i> Activo</span>'
          : '<span class="text-gray-400 font-bold text-xs flex items-center gap-1"><i class="fa-solid fa-ban"></i> Inactivo</span>';

        const tr = document.createElement("tr");
        tr.className = "hover:bg-gray-50 border-b";
        tr.innerHTML = `
                <td class="px-6 py-4 text-gray-500 text-xs font-mono">${u.id}</td>
                <td class="px-6 py-4 font-medium text-gray-900">${u.full_name || "Sin nombre"}</td>
                <td class="px-6 py-4 text-gray-600">${u.email}</td>
                <td class="px-6 py-4">${rolBadge}</td>
                <td class="px-6 py-4">${estadoBadge}</td>
                <td class="px-6 py-4 text-right space-x-2">
                    <button onclick='editarUsuario(${JSON.stringify(u)})' class="text-indigo-600 hover:text-indigo-900 transition"><i class="fa-solid fa-pen"></i></button>
                    <button onclick="eliminarUsuario(${u.id})" class="text-red-600 hover:text-red-900 transition"><i class="fa-solid fa-trash"></i></button>
                </td>
            `;
        tbody.appendChild(tr);
      });
    });
}

function abrirModalUsuario(isEdit = false) {
  document.getElementById("modal-usuario").classList.remove("hidden");
  document.getElementById("modal-user-title").innerText = isEdit
    ? "Editar"
    : "Nuevo";
  if (!isEdit) {
    document.getElementById("user-id").value = "";
    document.getElementById("user-pass").value = "";
  }
}
function cerrarModalUsuario() {
  document.getElementById("modal-usuario").classList.add("hidden");
}

function editarUsuario(u) {
  abrirModalUsuario(true);
  document.getElementById("user-id").value = u.id;
  document.getElementById("user-name").value = u.full_name;
  document.getElementById("user-email").value = u.email;
  document.getElementById("user-pass").value = "";
  document.getElementById("user-active").checked = u.is_active;
  document.getElementById("user-superuser").checked = u.is_superuser;
}

async function guardarUsuario() {
  const id = document.getElementById("user-id").value;
  const payload = {
    email: document.getElementById("user-email").value,
    full_name: document.getElementById("user-name").value,
    is_active: document.getElementById("user-active").checked,
    is_superuser: document.getElementById("user-superuser").checked,
  };
  const pass = document.getElementById("user-pass").value;
  if (pass) payload.password = pass;

  if (!id && !pass)
    return Swal.fire("Error", "Contraseña requerida", "warning");

  const method = id ? "PUT" : "POST";
  const url = id ? `${API_URL}/users/${id}` : `${API_URL}/users/`;

  try {
    const res = await fetch(url, {
      method: method,
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Error al guardar");
    Swal.fire("Guardado", "", "success");
    cerrarModalUsuario();
    cargarTablaUsuarios();
  } catch (e) {
    Swal.fire("Error", e.message, "error");
  }
}

async function eliminarUsuario(id) {
  if (
    (await Swal.fire({ title: "¿Borrar?", showCancelButton: true })).isConfirmed
  ) {
    await fetch(`${API_URL}/users/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    cargarTablaUsuarios();
  }
}
