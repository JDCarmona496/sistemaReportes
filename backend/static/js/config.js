export const API_URL = "http://localhost:8000/api/v1";

export function getToken() {
  return localStorage.getItem("access_token");
}

export function authHeaders() {
  return {
    Authorization: `Bearer ${getToken()}`,
    "Content-Type": "application/json",
  };
}

export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/";
}
