document.addEventListener("DOMContentLoaded", function() {
    const cantidadInput = document.getElementById("cantidad_productos");
    if (cantidadInput) {
        cantidadInput.addEventListener("input", () => {
            if (cantidadInput.value.length > 10) {
                alert("Máximo 10 dígitos permitidos");
                cantidadInput.value = cantidadInput.value.slice(0, 10);
            }
        });
    }
});