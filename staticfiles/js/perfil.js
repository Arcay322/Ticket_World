// static/js/perfil.js

// Añade una variable global para asegurar que el script solo se ejecute una vez
if (typeof perfilScriptLoaded === 'undefined') {
    var perfilScriptLoaded = true; 
    console.log('perfil.js: script detectado e inicializado.');
    document.addEventListener('DOMContentLoaded', function() {
        console.log('perfil.js: DOMContentLoaded disparado.');

        // --- Validación de Formulario de Detalles de Cuenta ---
        const updateProfileForm = document.getElementById('update_profile_form');
        const btnUpdateProfile = document.getElementById('btn_update_profile');

        const changePasswordForm = document.getElementById('change_password_form');
        const btnChangePassword = document.getElementById('btn_change_password');

        function displayFieldError(fieldId, message) {
            const errorDiv = document.getElementById(`${fieldId}_error`);
            if (errorDiv) {
                errorDiv.textContent = message;
                errorDiv.style.display = message ? 'block' : 'none';
            }
        }

        function isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }

        function isValidPassword(password) {
            const minLength = 8;
            const hasLetter = /[a-zA-Z]/.test(password);
            const hasNumber = /[0-9]/.test(password);
            const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/.test(password);
            return password.length >= minLength && hasLetter && hasNumber && hasSpecialChar;
        }

        function clearDjangoErrorsOnInput(fieldElement) {
            fieldElement.addEventListener('input', () => {
                let djangoErrorDiv = fieldElement.nextElementSibling;
                while (djangoErrorDiv && !djangoErrorDiv.classList.contains('invalid-feedback')) {
                    djangoErrorDiv = djangoErrorDiv.nextElementSibling;
                }
                if (djangoErrorDiv) {
                    djangoErrorDiv.style.display = 'none';
                }
                displayFieldError(fieldElement.id, '');
            });
        }

        if (updateProfileForm) {
            const usernameField = updateProfileForm.querySelector('input[name="username"]');
            const emailField = updateProfileForm.querySelector('input[name="email"]');

            if (usernameField) {
                clearDjangoErrorsOnInput(usernameField);
                usernameField.addEventListener('input', () => {
                    if (usernameField.value.trim().length < 3) {
                        displayFieldError(usernameField.id, 'El nombre de usuario debe tener al menos 3 caracteres.');
                    } else {
                        displayFieldError(usernameField.id, '');
                    }
                });
            }
            if (emailField) {
                clearDjangoErrorsOnInput(emailField);
                emailField.addEventListener('input', () => {
                    if (!isValidEmail(emailField.value)) {
                        displayFieldError(emailField.id, 'Introduce un correo electrónico válido.');
                    } else {
                        displayFieldError(emailField.id, '');
                    }
                });
            }

            btnUpdateProfile.addEventListener('click', function(event) {
                event.preventDefault(); 
                
                let formIsValid = true;

                if (usernameField && usernameField.value.trim() === '') {
                    displayFieldError(usernameField.id, 'El nombre de usuario no puede estar vacío.');
                    formIsValid = false;
                } else if (usernameField && usernameField.value.trim().length < 3) {
                    displayFieldError(usernameField.id, 'El nombre de usuario debe tener al menos 3 caracteres.');
                    formIsValid = false;
                } else if (usernameField) {
                    displayFieldError(usernameField.id, '');
                }

                if (emailField && (emailField.value.trim() === '' || !isValidEmail(emailField.value))) {
                    displayFieldError(emailField.id, 'Introduce un correo electrónico válido.');
                    formIsValid = false;
                } else if (emailField) {
                    displayFieldError(emailField.id, '');
                }

                if (!formIsValid) {
                    console.log('perfil.js: Validación de perfil falló en frontend.');
                    this.disabled = false;
                    this.textContent = 'Guardar Cambios';
                    this.style.opacity = 1;
                } else {
                    this.disabled = true;
                    this.textContent = 'Guardando...';
                    this.style.opacity = 0.7;
                    updateProfileForm.submit();
                }
            });
        }

        // --- Validación de Formulario de Cambio de Contraseña ---
        if (changePasswordForm) {
            const oldPasswordField = document.getElementById('id_old_password');
            const newPassword1Field = document.getElementById('id_new_password1');
            const newPassword2Field = document.getElementById('id_new_password2');

            if (oldPasswordField) clearDjangoErrorsOnInput(oldPasswordField);
            if (newPassword1Field) clearDjangoErrorsOnInput(newPassword1Field);
            if (newPassword2Field) clearDjangoErrorsOnInput(newPassword2Field);

            if (newPassword1Field) {
                newPassword1Field.addEventListener('input', () => {
                    if (!isValidPassword(newPassword1Field.value)) {
                        displayFieldError(newPassword1Field.id, 'La contraseña debe tener al menos 8 caracteres, incluyendo letras, números y símbolos.');
                    } else {
                        displayFieldError(newPassword1Field.id, '');
                    }
                    if (newPassword2Field && newPassword1Field.value !== newPassword2Field.value) {
                        displayFieldError(newPassword2Field.id, 'Las contraseñas no coinciden.');
                    } else if (newPassword2Field) {
                        displayFieldError(newPassword2Field.id, '');
                    }
                });
            }
            if (newPassword2Field) {
                newPassword2Field.addEventListener('input', () => {
                    if (newPassword1Field && newPassword1Field.value !== newPassword2Field.value) {
                        displayFieldError(newPassword2Field.id, 'Las contraseñas no coinciden.');
                    } else {
                        displayFieldError(newPassword2Field.id, '');
                    }
                });
            }

            btnChangePassword.addEventListener('click', function(event) {
                event.preventDefault();
                
                let formIsValid = true;

                displayFieldError(oldPasswordField.id, '');
                displayFieldError(newPassword1Field.id, '');
                displayFieldError(newPassword2Field.id, '');

                if (oldPasswordField.value.trim() === '') {
                    displayFieldError(oldPasswordField.id, 'Por favor, introduce tu contraseña antigua.');
                    formIsValid = false;
                }

                if (!isValidPassword(newPassword1Field.value)) {
                    displayFieldError(newPassword1Field.id, 'La contraseña debe tener al menos 8 caracteres, incluyendo letras, números y símbolos.');
                    formIsValid = false;
                }

                if (newPassword1Field.value !== newPassword2Field.value) {
                    displayFieldError(newPassword2Field.id, 'Las contraseñas no coinciden.');
                    formIsValid = false;
                }

                if (!formIsValid) {
                    console.log('perfil.js: Validación de cambio de contraseña falló en frontend.');
                    this.disabled = false;
                    this.textContent = 'Cambiar Contraseña';
                    this.style.opacity = 1;
                } else {
                    this.disabled = true;
                    this.textContent = 'Cambiando...';
                    this.style.opacity = 0.7;
                    changePasswordForm.submit();
                }
            });
        }

        // Variable global para almacenar el temporizador de ocultación de contraseña
        let passwordHideTimeout; 

        // --- Lógica para Mostrar/Ocultar Contraseñas ---
        const togglePasswordButtons = document.querySelectorAll('.toggle-password');
        console.log(`perfil.js: Se encontraron ${togglePasswordButtons.length} botones de toggle de contraseña.`);

        togglePasswordButtons.forEach(button => {
            const targetInputId = button.dataset.target;
            const passwordInput = document.getElementById(targetInputId);
            const eyeIcon = button.querySelector('.feather-eye');

            if (passwordInput && eyeIcon) {
                console.log(`perfil.js: Adjuntando listener al botón de toggle para input: #${targetInputId}`);

                const hidePassword = () => {
                    if (passwordInput.type === 'text') {
                        passwordInput.type = 'password';
                        eyeIcon.setAttribute('stroke', 'currentColor'); 
                        console.log(`perfil.js: Contraseña #${targetInputId} oculta automáticamente.`);
                    }
                };

                button.addEventListener('click', function() {
                    clearTimeout(passwordHideTimeout); 

                    if (passwordInput.type === 'password') {
                        passwordInput.type = 'text';
                        eyeIcon.setAttribute('stroke', 'var(--color-primario)'); 
                        console.log(`perfil.js: Contraseña #${targetInputId} ahora visible.`);

                        passwordHideTimeout = setTimeout(hidePassword, 5000); 

                    } else {
                        hidePassword();
                    }
                });

            } else {
                console.error(`perfil.js: ERROR: No se encontró el input #${targetInputId} o el icono de ojo dentro del botón.`);
            }
        });

    }); // Cierre de DOMContentLoaded
} // Cierre del guard de perfilScriptLoaded
