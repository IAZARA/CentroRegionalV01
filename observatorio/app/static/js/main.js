// Funciones principales de JavaScript para la aplicación

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap si existen
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Manejar el cierre de alertas
    var alertList = document.querySelectorAll('.alert')
    alertList.forEach(function (alert) {
        new bootstrap.Alert(alert)
    });

    // Language selector logic
    var langSelectors = document.querySelectorAll('.dropdown-menu a[data-lang]');
    langSelectors.forEach(function(selector) {
        selector.addEventListener('click', function(event) {
            event.preventDefault();
            var lang = this.getAttribute('data-lang');
            // Construct the URL for setting language.
            // Assumes the Flask app is running at the root.
            window.location.href = '/set_language/' + lang;
        });
    });
});
