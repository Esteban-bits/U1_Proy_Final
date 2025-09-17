function validarMaximo(id, max) {
        const input = document.getElementById(id);
        input.addEventListener("input", () => {
            if (input.value.length > max) {
                alert(`Máximo ${max} caracteres permitidos`);
                input.value = input.value.slice(0, max);
            }
        });
    }

    validarMaximo("usuario", 20);     
    validarMaximo("contraseña", 15);   