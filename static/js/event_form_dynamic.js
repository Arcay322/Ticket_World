// static/js/event_form_dynamic.js

function manejarLogicaConadis(formWrapper) {
    const tipoSelect = formWrapper.querySelector('select[id$="-tipo"]');
    const precioInput = formWrapper.querySelector('input[id$="-precio"]');
    if (!tipoSelect || !precioInput) return;

    let helpText = formWrapper.querySelector('.conadis-help-text');
    if (!helpText) {
        helpText = document.createElement('small');
        helpText.className = 'conadis-help-text';
        precioInput.parentElement.append(helpText);
    }

    const actualizarCampoPrecio = () => {
        if (tipoSelect.value === 'conadis') {
            precioInput.value = '0.00';
            // === CAMBIO CLAVE AQUÍ ===
            precioInput.readOnly = true; // Usamos readOnly en lugar de disabled
            helpText.textContent = 'El precio se calculará automáticamente con el descuento de ley.';
        } else {
            // === Y AQUÍ ===
            precioInput.readOnly = false; // Lo volvemos editable
            helpText.textContent = '';
        }
    };

    tipoSelect.addEventListener('change', actualizarCampoPrecio);
    actualizarCampoPrecio();
}


function initDynamicFormset(prefix, addButtonSelector, containerSelector, emptyFormSelector) {
    const addButton = document.querySelector(addButtonSelector);
    const container = document.querySelector(containerSelector);
    const emptyFormTemplate = document.querySelector(emptyFormSelector);
    const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);
    
    if (!addButton || !container || !emptyFormTemplate || !totalFormsInput) {
        console.error("Error: Faltan elementos para inicializar el formset.");
        return;
    }

    let formCount = parseInt(totalFormsInput.value);

    // --- Lógica para AÑADIR ---
    addButton.addEventListener('click', () => {
        const newFormHtml = emptyFormTemplate.innerHTML.replace(/__prefix__/g, formCount);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormHtml;
        const newFormElement = tempDiv.firstElementChild;

        container.append(newFormElement);
        manejarLogicaConadis(newFormElement);
        formCount++;
        totalFormsInput.value = formCount;
    });

    // --- Lógica de ELIMINACIÓN ---
    container.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('delete-boleto-button')) {
            const formWrapper = e.target.closest('.boleto-form-wrapper');
            const deleteInput = formWrapper.querySelector('input[id$="-DELETE"]');
            
            if (deleteInput) {
                // Es un formulario existente: lo marcamos para borrar en el backend y lo ocultamos.
                deleteInput.checked = true;
                formWrapper.classList.add('removing');
                setTimeout(() => {
                    formWrapper.style.display = 'none';
                }, 500);

            } else {
                // Es un formulario nuevo: lo eliminamos de la página y actualizamos el contador.
                formWrapper.remove();
                formCount--;
                totalFormsInput.value = formCount;
            }
        }
    });

    // Aplicamos la lógica CONADIS a los formularios que ya existen al cargar la página.
    document.querySelectorAll('.boleto-form-wrapper').forEach(formWrapper => {
        manejarLogicaConadis(formWrapper);
    });
}