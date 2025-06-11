// static/js/event_form_dynamic.js

// Función principal que inicializa la lógica dinámica del formset
function initDynamicFormset(formsetPrefix, initialTotalForms, initialMinForms) {
    const addBoletoButton = document.getElementById('add-boleto-button');
    const boletoFormList = document.getElementById('boleto-form-list');
    
    // Obtener los inputs ocultos del formset de gestión
    const totalFormsInput = document.querySelector(`input[name="${formsetPrefix}-TOTAL_FORMS"]`);
    const minFormsInput = document.querySelector(`input[name="${formsetPrefix}-MIN_NUM_FORMS"]`);

    // Depuración: Verificar si los elementos se encuentran
    if (!totalFormsInput) {
        console.error(`ERROR JS: No se encontró el input oculto TOTAL_FORMS con nombre "${formsetPrefix}-TOTAL_FORMS". La funcionalidad dinámica puede fallar.`);
        return; // Salir si falta un elemento crítico
    }
    if (!minFormsInput) {
        console.error(`ERROR JS: No se encontró el input oculto MIN_NUM_FORMS con nombre "${formsetPrefix}-MIN_NUM_FORMS". La funcionalidad dinámica puede fallar.`);
        return; // Salir si falta un elemento crítico
    }

    let formCount = initialTotalForms;
    const minForms = initialMinForms;

    // Función para mostrar mensajes de Django (simulada aquí, en tu caso usaría el sistema real de Django)
    function displayMessage(messageText, type) {
        // En un entorno real, esto se manejaría a través del sistema de mensajes de Django
        // y la plantilla base. Aquí es solo para propósitos de la funcionalidad JS.
        // Podrías mostrar un div simple o usar una librería de notificaciones.
        console.warn(`Mensaje (desde JS): ${messageText} (${type})`);
        const messagesContainer = document.querySelector('.messages-list');
        if (messagesContainer) {
            const li = document.createElement('li');
            li.className = `message-item ${type || 'info'}`;
            li.textContent = messageText;
            messagesContainer.appendChild(li);
            // Simular la desaparición (ya que el JS de messages.js no lo controla desde aquí)
            setTimeout(() => {
                li.remove();
            }, 5000);
        }
    }


    // Función para actualizar el estado de los botones de eliminar
    function updateDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.delete-boleto-button');
        deleteButtons.forEach(button => {
            // Si el número de formularios es igual o menor al mínimo requerido, deshabilita el botón de eliminar
            button.disabled = (formCount <= minForms);
            button.style.opacity = (formCount <= minForms) ? '0.5' : '0.8';
            button.style.cursor = (formCount <= minForms) ? 'not-allowed' : 'pointer';
        });
    }

    // Llamar al inicio para configurar los botones iniciales
    updateDeleteButtons();

    addBoletoButton.addEventListener('click', function() {
        // Clonar el primer formulario existente para crear uno nuevo
        // Clonamos el primero (índice 0) porque es el que Django renderiza por defecto.
        const firstFormWrapper = boletoFormList.children[0];
        if (!firstFormWrapper) {
            console.error("ERROR JS: No se encontró un formulario base para clonar.");
            displayMessage("No se pudo añadir un nuevo tipo de boleto. Recargue la página.", "error");
            return;
        }

        const newForm = firstFormWrapper.cloneNode(true);
        
        // Reemplazar los índices de los nombres e IDs de los campos para el nuevo formulario
        // La expresión regular busca el prefijo del formset seguido de un guion y un número.
        const regex = new RegExp(`${formsetPrefix}-(\\d+)`, 'g');
        newForm.innerHTML = newForm.innerHTML.replace(regex, `${formsetPrefix}-${formCount}`);
        
        // Limpiar valores de los campos clonados y asegurar que el checkbox DELETE esté desmarcado
        newForm.querySelectorAll('input, select, textarea').forEach(input => {
            // Limpiar valores de los campos clonados, excepto los campos ocultos de gestión
            if (input.type !== 'hidden') {
                input.value = '';
            }
            // Desmarcar checkbox DELETE si existe (importante para boletos eliminados y luego añadidos)
            if (input.type === 'checkbox' && input.name.includes('-DELETE')) {
                input.checked = false;
            }
        });

        // Asegurarse de que el nuevo formulario no tenga la clase 'removing'
        newForm.classList.remove('removing');
        newForm.style.height = ''; // Remover estilos de altura que podrían quedar de 'removing'
        newForm.style.paddingTop = '';
        newForm.style.paddingBottom = '';
        newForm.style.marginTop = '';
        newForm.style.marginBottom = '';
        newForm.style.opacity = '1';
        newForm.style.transform = 'translateY(0)';


        // Re-adjuntar el listener para el botón de eliminar del nuevo formulario
        const newDeleteButton = newForm.querySelector('.delete-boleto-button');
        if (newDeleteButton) {
            newDeleteButton.dataset.formId = formCount; // Asigna el ID al nuevo botón
            newDeleteButton.addEventListener('click', handleDeleteButtonClick);
        }
        
        // Añadir el nuevo formulario al DOM
        boletoFormList.appendChild(newForm);
        
        // Actualizar el contador total de formularios en el input oculto
        formCount++;
        totalFormsInput.value = formCount; // Actualiza el valor del input oculto TOTAL_FORMS
        updateDeleteButtons(); // Actualizar botones después de añadir
    });

    // Función para manejar clics en botones de eliminar
    function handleDeleteButtonClick(event) {
        const button = event.target;
        // Solo permitir eliminar si no es el último formulario requerido
        if (formCount > minForms) {
            const formWrapper = button.closest('.boleto-form-wrapper');
            // Encontrar el checkbox DELETE asociado dentro del mismo wrapper de formulario
            const deleteCheckbox = formWrapper.querySelector('input[name$="-DELETE"]');

            if (deleteCheckbox) {
                deleteCheckbox.checked = true; // Marcar para eliminación lógica por Django
                formWrapper.classList.add('removing'); // Añadir clase para animación de salida
                
                // Retrasar la eliminación real del DOM para que la animación se vea
                setTimeout(() => {
                    formWrapper.remove();
                    formCount--; // Decrementar el contador DESPUÉS de la eliminación visual
                    totalFormsInput.value = formCount; // Actualiza el valor del input oculto TOTAL_FORMS
                    updateDeleteButtons(); // Actualizar botones después de eliminar
                }, 300); // Coincide con la duración de la transición CSS
            } else {
                console.warn("No se encontró el checkbox DELETE para el formulario. La eliminación lógica no será posible.");
                displayMessage("Hubo un problema al intentar eliminar el boleto. Contacte a soporte.", "error");
            }
        } else {
            displayMessage(`Debes tener al menos ${minForms} tipo(s) de boleto.`, "warning"); // Usar el valor dinámico de minForms
        }
    }

    // Adjuntar listeners a los botones de eliminar existentes (los que Django renderiza inicialmente)
    boletoFormList.querySelectorAll('.delete-boleto-button').forEach(button => {
        button.addEventListener('click', handleDeleteButtonClick);
    });

    // Asegurarse de que los campos iniciales estén visibles (si hidden al principio por alguna razón)
    boletoFormList.querySelectorAll('.boleto-form-wrapper').forEach(formWrapper => {
        formWrapper.classList.add('show');
    });
}
