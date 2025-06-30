// static/js/event_map.js

let map;
let marker;
let geocoder; // Para convertir direcciones a coordenadas

// Esta función se llama automáticamente cuando la API de Google Maps se ha cargado
function initMap() {
    geocoder = new google.maps.Geocoder();

    // Obtener valores iniciales de los campos ocultos o usar un valor por defecto (Lima, Perú)
    const initialLatValue = document.getElementById('id_latitud').value;
    const initialLngValue = document.getElementById('id_longitud').value;
    
    // Si no hay valores guardados, usa las coordenadas de Lima
    const defaultLat = initialLatValue ? parseFloat(initialLatValue) : -12.046374; 
    const defaultLng = initialLngValue ? parseFloat(initialLngValue) : -77.042793; 

    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: defaultLat, lng: defaultLng },
        zoom: 12,
        mapTypeControl: false, // Opcional: ocultar controles de tipo de mapa
        streetViewControl: false // Opcional: ocultar Street View
    });

    marker = new google.maps.Marker({
        position: { lat: defaultLat, lng: defaultLng },
        map: map,
        draggable: true, // Permite arrastrar el marcador
        title: "Arrastra para seleccionar la ubicación exacta"
    });

    // Event listener para actualizar coordenadas al arrastrar el marcador
    marker.addListener("dragend", function() {
        updateCoordinates(marker.getPosition());
    });

    // Event listener para actualizar coordenadas al hacer clic en el mapa
    map.addListener("click", function(event) {
        marker.setPosition(event.latLng);
        updateCoordinates(event.latLng);
    });

    // Lógica para el botón de búsqueda de dirección
    const searchInput = document.getElementById('address-input');
    const searchButton = document.getElementById('search-map-btn');

    searchButton.addEventListener('click', function() {
        const address = searchInput.value;
        if (address) {
            geocoder.geocode({ 'address': address }, function(results, status) {
                if (status === 'OK' && results[0]) {
                    map.setCenter(results[0].geometry.location);
                    marker.setPosition(results[0].geometry.location);
                    updateCoordinates(results[0].geometry.location);
                } else {
                    alert('No se pudo encontrar la dirección: ' + status);
                    console.error('Geocoding error:', status, results);
                }
            });
        }
    });

    // Si el formulario ya tiene latitud/longitud (ej. al editar un evento),
    // asegúrate de que el mapa se centre y el marcador se coloque correctamente al cargar.
    if (initialLatValue && initialLngValue) {
        const initialPosition = { lat: defaultLat, lng: defaultLng };
        map.setCenter(initialPosition);
        marker.setPosition(initialPosition);
        updateCoordinates(initialPosition); // Para asegurar que los displays y el embed link estén correctos
    } else {
        // Si no hay coordenadas guardadas, intenta geocodificar la dirección, ciudad y país existentes del evento
        // para pre-rellenar el mapa con una estimación
        const existingDireccion = document.getElementById('id_direccion') ? document.getElementById('id_direccion').value : '';
        const existingCiudad = document.getElementById('id_ciudad') ? document.getElementById('id_ciudad').value : '';
        const existingPais = document.getElementById('id_pais') ? document.getElementById('id_pais').value : '';
        
        const existingAddress = `${existingDireccion}, ${existingCiudad}, ${existingPais}`.trim();
                                
        // Evita buscar si todos los campos están vacíos o solo contienen comas y espacios
        if (existingAddress && existingAddress !== ', ,') { 
            geocoder.geocode({ 'address': existingAddress }, function(results, status) {
                if (status === 'OK' && results[0]) {
                    map.setCenter(results[0].geometry.location);
                    marker.setPosition(results[0].geometry.location);
                    updateCoordinates(results[0].geometry.location);
                } else {
                    console.warn('Could not geocode existing address:', existingAddress, 'Status:', status);
                }
            });
        }
    }
}

/**
 * Actualiza los campos ocultos de latitud, longitud y el enlace embed del mapa.
 * También actualiza la visualización de coordenadas para el usuario.
 * @param {google.maps.LatLng} latLng - Objeto LatLng de Google Maps.
 */
function updateCoordinates(latLng) {
    const lat = latLng.lat();
    const lng = latLng.lng();

    // Actualiza los campos ocultos del formulario
    document.getElementById('id_latitud').value = lat.toFixed(6);
    document.getElementById('id_longitud').value = lng.toFixed(6);
    
    // Genera el enlace de Google Maps para incrustar (iframe)
    // Este es el formato de URL de la API de Embed para incrustar un mapa con un marcador.
    // ¡REEMPLAZA TU_API_KEY CON TU CLAVE REAL AQUÍ TAMBIÉN!
    const embedUrl = `https://www.google.com/maps/embed/v1/place?key=AIzaSyA4i1Hral8K2FIx0YU_QlbxIr4KD8xFEmM&q=${lat},${lng}`;
    document.getElementById('id_mapa_enlace_embed').value = embedUrl;

    // Actualiza la visualización para el usuario
    document.getElementById('lat-display').textContent = lat.toFixed(6);
    document.getElementById('lng-display').textContent = lng.toFixed(6);
}

// Puedes añadir esta línea si quieres forzar que initMap esté en el ámbito global antes de que la API la llame.
// Esto es una redundancia para asegurar, aunque el callback=initMap ya se encarga.
window.initMap = initMap;