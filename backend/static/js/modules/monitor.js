export function initMonitor() {
    // Registramos la función global para que el Router la llame al cambiar de pestaña
    window.cargarModuloMonitor = cargarMonitor;
}

function cargarMonitor() {
    const frame = document.getElementById('flower-frame');
    
    // Validación de seguridad: Si no existe el elemento, salir
    if (!frame) return;

    // Optimización: Si ya tiene la URL correcta cargada, no recargar (evita parpadeo)
    if (frame.getAttribute('data-loaded') === 'true') return;

    // --- LÓGICA DE IP DINÁMICA ---
    // Usamos el mismo protocolo (http/https) y el mismo hostname (IP/Dominio)
    // que tiene la página actual, pero cambiamos el puerto a 5556.
    const protocol = window.location.protocol; // ej: "http:"
    const hostname = window.location.hostname; // ej: "192.168.1.50"
    const flowerPort = "5556"; 
    
    const flowerUrl = `${protocol}//${hostname}:${flowerPort}`;
    
    console.log(`🌸 Cargando Flower en: ${flowerUrl}`);
    
    frame.src = flowerUrl;
    frame.setAttribute('data-loaded', 'true'); // Marcamos como cargado
}