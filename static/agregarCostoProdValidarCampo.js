document.addEventListener("DOMContentLoaded", function() {
    function validarCampo(id) {
        const input = document.getElementById(id);
        if (!input) return;
        input.addEventListener("input", () => {
            if (input.value.length > 10) {
                alert("Máximo 10 dígitos permitidos");
                input.value = input.value.slice(0, 10);
            }
            input.value = input.value.replace(/[^0-9.]/g, ''); 
        });
    }

    validarCampo("materia_prima_directa");
    validarCampo("mano_obra_directa");
    validarCampo("costos_indirectos");
});