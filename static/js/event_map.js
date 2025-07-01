// static/js/event_map.js

let map;
let marker;
let geocoder;

function initMap() {
    geocoder = new google.maps.Geocoder();

    const initialLatValue = document.getElementById('id_latitud').value;
    const initialLngValue = document.getElementById('id_longitud').value;
    
    const defaultLat = initialLatValue ? parseFloat(initialLatValue) : -12.046374; 
    const defaultLng = initialLngValue ? parseFloat(initialLngValue) : -77.042793; 

    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: defaultLat, lng: defaultLng },
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false
    });

    marker = new google.maps.Marker({
        position: { lat: defaultLat, lng: defaultLng },
        map: map,
        draggable: true,
        title: "Arrastra para seleccionar la ubicación exacta"
    });

    marker.addListener("dragend", () => updateCoordinates(marker.getPosition()));
    map.addListener("click", (event) => {
        marker.setPosition(event.latLng);
        updateCoordinates(event.latLng);
    });

    const searchInput = document.getElementById('address-input');
    const searchButton = document.getElementById('search-map-btn');

    searchButton.addEventListener('click', () => {
        const address = searchInput.value;
        if (address) {
            geocoder.geocode({ 'address': address }, (results, status) => {
                if (status === 'OK' && results[0]) {
                    map.setCenter(results[0].geometry.location);
                    marker.setPosition(results[0].geometry.location);
                    updateCoordinates(results[0].geometry.location);
                } else {
                    alert('No se pudo encontrar la dirección: ' + status);
                }
            });
        }
    });

    if (initialLatValue && initialLngValue) {
        const initialPosition = { lat: defaultLat, lng: defaultLng };
        map.setCenter(initialPosition);
        marker.setPosition(initialPosition);
        updateCoordinates(initialPosition);
    }
}

/**
 * Actualiza los campos del formulario con las nuevas coordenadas y la URL de embed.
 * @param {google.maps.LatLng} latLng - Objeto LatLng con la nueva ubicación.
 */
function updateCoordinates(latLng) {
    const lat = latLng.lat();
    const lng = latLng.lng();

    // Actualiza los campos ocultos del formulario
    document.getElementById('id_latitud').value = lat.toFixed(6);
    document.getElementById('id_longitud').value = lng.toFixed(6);
    
    // --- CORRECCIÓN CRÍTICA AQUÍ ---
    // 1. Obtiene la API key del atributo data-api-key que pusimos en el HTML.
    const mapDiv = document.getElementById('map');
    const apiKey = mapDiv.dataset.apiKey;

    if (!apiKey) {
        console.error("Error: API Key de Google Maps no encontrada.");
        return;
    }

    // 2. Construye la URL para el iframe usando el formato correcto de la API Embed.
    const embedUrl = `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${lat},${lng}`;
    
    // 3. Asigna la URL correcta al campo oculto del formulario.
    document.getElementById('id_mapa_enlace_embed').value = embedUrl;
    // --- FIN DE LA CORRECCIÓN ---

    // Actualiza la visualización para el usuario
    document.getElementById('lat-display').textContent = lat.toFixed(6);
    document.getElementById('lng-display').textContent = lng.toFixed(6);
}

// Asegura que la función esté disponible globalmente para el callback de la API
window.initMap = initMap;