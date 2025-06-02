/**
 * Sistema de traducción del navegador para el Observatorio de Drogas Sintéticas
 * Este script proporciona una solución alternativa para traducir la página usando 
 * las capacidades nativas del navegador
 */

document.addEventListener('DOMContentLoaded', function() {
    // Comprobamos si el navegador soporta la API de traducción
    const supportsTranslation = 
        window.navigator && 
        window.navigator.languages && 
        typeof window.navigator.language === 'string';
    
    console.log("Navegador soporta traducción:", supportsTranslation);
    
    // Función simplificada para almacenar preferencia de idioma
    function setLanguagePreference(targetLang) {
        console.log("Estableciendo preferencia de idioma:", targetLang);
        
        // Establecer el atributo lang en HTML
        document.documentElement.lang = targetLang;
        
        // Almacenar preferencia en localStorage
        localStorage.setItem('preferredLanguage', targetLang);
    }
    
    // Las traducciones ahora se manejan completamente por Flask-Babel en el servidor
    // Esta función se mantiene para compatibilidad pero no hace traducción manual
    function useManualTranslation(lang) {
        console.log("Traducción manual deshabilitada. Usando Flask-Babel del servidor para:", lang);
    }
    
    // Función para manejar clics en los botones de idioma
    function handleLanguageButtonClick(event) {
        event.preventDefault();
        
        const langCode = this.getAttribute('data-lang');
        console.log("Botón de idioma clickeado:", langCode);
        
        // Solo cambiar el idioma en el servidor y esperar confirmación
        fetch(`/set_language/${langCode}`)
            .then(response => {
                if (response.ok) {
                    console.log("Idioma cambiado exitosamente a:", langCode);
                    // Solo recargar DESPUÉS de que el servidor confirme el cambio
                    window.location.reload();
                } else {
                    console.error("Error al cambiar idioma:", response.status);
                }
            })
            .catch(error => {
                console.error("Error al cambiar idioma:", error);
            });
    }
    
    // Agregar eventos de clic a los botones de idioma
    const languageButtons = document.querySelectorAll('.language-btn');
    languageButtons.forEach(button => {
        button.addEventListener('click', handleLanguageButtonClick);
    });
    
    // Verificar si hay un idioma preferido almacenado
    const preferredLanguage = localStorage.getItem('preferredLanguage');
    if (preferredLanguage && preferredLanguage !== 'es') {
        // Aplicar el idioma preferido al cargar la página
        console.log("Aplicando idioma preferido:", preferredLanguage);
        setLanguagePreference(preferredLanguage);
    }
});
