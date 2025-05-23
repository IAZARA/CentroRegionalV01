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
    
    // Función para activar la traducción del navegador
    function activateTranslation(targetLang) {
        console.log("Activando traducción a:", targetLang);
        
        // Establecer el atributo lang en HTML
        document.documentElement.lang = targetLang;
        
        // Si el navegador es compatible con la API de traducción de Google
        if (window.google && window.google.translate) {
            try {
                const translateElement = google.translate.TranslateElement;
                new translateElement({
                    pageLanguage: 'es',
                    includedLanguages: 'en,pt,es',
                    layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
                    autoDisplay: false
                }, 'google_translate_element');
                
                // Seleccionar el idioma
                const selectElement = document.querySelector('.goog-te-combo');
                if (selectElement) {
                    selectElement.value = targetLang;
                    selectElement.dispatchEvent(new Event('change'));
                }
            } catch (e) {
                console.error("Error al activar Google Translate:", e);
            }
        } else {
            console.log("Google Translate no disponible, usando alternativa");
            // Método alternativo: usar la traducción manual basada en diccionarios
            useManualTranslation(targetLang);
        }
        
        // Almacenar preferencia en localStorage
        localStorage.setItem('preferredLanguage', targetLang);
    }
    
    // Función para aplicar traducciones manuales
    function useManualTranslation(lang) {
        // Diccionarios de traducción completos
        const translations = {
            'en': {
                'Inicio': 'Home',
                'Búsqueda': 'Search',
                'Mapa': 'Map',
                'Documentos': 'Documents',
                'Eventos': 'Events',
                'Acerca del Observatorio': 'About the Observatory',
                'Accesos': 'Access',
                'Mapa Interactivo': 'Interactive Map',
                'Legislación': 'Legislation',
                'Agenda MinSeg': 'MinSeg Agenda',
                'Ministerio de Seguridad Nacional de la República Argentina': 'Ministry of National Security of the Argentine Republic',
                'Ministerio de Seguridad Nacional': 'Ministry of National Security',
                'Observatorio de Drogas Sintéticas': 'Synthetic Drugs Observatory',
                'Bienvenido': 'Welcome',
                'Cerrar sesión': 'Logout',
                'Iniciar sesión': 'Login',
                'La plataforma se establece como una iniciativa estratégica del Ministerio de Seguridad Nacional, orientada a monitorear, analizar y evaluar el fenómeno de las drogas sintéticas en el continente americano.': 'The platform is established as a strategic initiative of the Ministry of National Security, aimed at monitoring, analyzing and evaluating the phenomenon of synthetic drugs in the American continent.',
                'El centro tiene como finalidad recopilar, clasificar y valorar información pública proveniente de fuentes confiables, como diarios y medios de comunicación, para generar inteligencia estratégica que permita identificar tendencias, patrones y riesgos emergentes asociados al tráfico, producción y consumo de estas sustancias.': 'The center aims to collect, classify and assess public information from reliable sources, such as newspapers and media, to generate strategic intelligence that allows identifying trends, patterns and emerging risks associated with the trafficking, production and consumption of these substances.',
                'Dirigido a tomadores de decisiones, organismos de seguridad nacionales e internacionales, autoridades gubernamentales y actores clave en la lucha contra el narcotráfico, el observatorio busca fortalecer la capacidad de respuesta regional mediante la creación de tableros de control dinámicos y accesibles en línea, promoviendo la cooperación y el intercambio de información entre los países del continente.': 'Aimed at decision-makers, national and international security agencies, government authorities and key actors in the fight against drug trafficking, the observatory seeks to strengthen regional response capacity through the creation of dynamic and accessible online control panels, promoting cooperation and information exchange among the countries of the continent.',
                'Dirección Nacional de Gestión de Bases de Datos de Seguridad': 'National Directorate of Security Database Management',
                'Todos los derechos reservados': 'All rights reserved',
                '© 2025 Observatorio de Drogas Sintéticas': '© 2025 Synthetic Drugs Observatory',
                
                /* Traducciones para la página de legislación */
                'Legislación Internacional': 'International Legislation',
                'Legislación Argentina': 'Argentine Legislation',
                'Legislación Brasil': 'Brazilian Legislation',
                'Legislación Chile': 'Chilean Legislation',
                'Legislación Colombiana': 'Colombian Legislation',
                'Legislación México': 'Mexican Legislation',
                'Ver documento': 'View document',
                'Constitución de la Nación Argentina': 'Constitution of the Argentine Nation',
                'Ley 23737 - Modificación al Codigo Penal – Narcotrafico': 'Law 23737 - Amendment to the Penal Code - Drug Trafficking',
                'Ley 17818 - Normas para su comercialización. Ley de estupefacientes': 'Law 17818 - Regulations for commercialization. Narcotics Law',
                'Ley 26.045 - Ley del Registro Nacional de Precursores Químicos': 'Law 26.045 - National Registry of Chemical Precursors Law',
                'Ley N° 26.052 - Ley de Desfederalización Parcial de la Competencia Penal': 'Law No. 26.052 - Law of Partial Defederalization of Criminal Jurisdiction',
                'Ley 27319 - Delitos Complejos': 'Law 27319 - Complex Crimes',
                'Ley 11.343 (2006)': 'Law 11.343 (2006)',
                'Ley N° 20.000 (1997)': 'Law No. 20.000 (1997)',
                'Ley 30 - Estatuto de Estupefacientes': 'Law 30 - Narcotics Statute',
                'Ley 599 - Código Penal': 'Law 599 - Penal Code',
                'Ley 624 - Acuerdo entre Colombia y España sobre cooperación': 'Law 624 - Agreement between Colombia and Spain on cooperation',
                'Ley 745 - Tipificación de contravención y porte de dosis personal': 'Law 745 - Classification of contravention and carrying of personal dose',
                'Convención para la Supresión del Tráfico Ilícito de Estupefacientes': 'Convention for the Suppression of Illicit Traffic in Narcotic Drugs'
            },
            'pt': {
                'Inicio': 'Início',
                'Búsqueda': 'Pesquisa',
                'Mapa': 'Mapa',
                'Documentos': 'Documentos',
                'Eventos': 'Eventos',
                'Acerca del Observatorio': 'Sobre o Observatório',
                'Accesos': 'Acessos',
                'Mapa Interactivo': 'Mapa Interativo',
                'Legislación': 'Legislação',
                'Agenda MinSeg': 'Agenda MinSeg',
                'Ministerio de Seguridad Nacional de la República Argentina': 'Ministério da Segurança Nacional da República Argentina',
                'Ministerio de Seguridad Nacional': 'Ministério da Segurança Nacional',
                'Observatorio de Drogas Sintéticas': 'Observatório de Drogas Sintéticas',
                'Bienvenido': 'Bem-vindo',
                'Cerrar sesión': 'Sair',
                'Iniciar sesión': 'Entrar',
                'La plataforma se establece como una iniciativa estratégica del Ministerio de Seguridad Nacional, orientada a monitorear, analizar y evaluar el fenómeno de las drogas sintéticas en el continente americano.': 'A plataforma se estabelece como uma iniciativa estratégica do Ministério da Segurança Nacional, orientada a monitorar, analisar e avaliar o fenômeno das drogas sintéticas no continente americano.',
                'El centro tiene como finalidad recopilar, clasificar y valorar información pública proveniente de fuentes confiables, como diarios y medios de comunicación, para generar inteligencia estratégica que permita identificar tendencias, patrones y riesgos emergentes asociados al tráfico, producción y consumo de estas sustancias.': 'O centro tem como finalidade coletar, classificar e avaliar informações públicas provenientes de fontes confiáveis, como jornais e meios de comunicação, para gerar inteligência estratégica que permita identificar tendências, padrões e riscos emergentes associados ao tráfico, produção e consumo dessas substâncias.',
                'Dirigido a tomadores de decisiones, organismos de seguridad nacionales e internacionales, autoridades gubernamentales y actores clave en la lucha contra el narcotráfico, el observatorio busca fortalecer la capacidad de respuesta regional mediante la creación de tableros de control dinámicos y accesibles en línea, promoviendo la cooperación y el intercambio de información entre los países del continente.': 'Dirigido a tomadores de decisão, organismos de segurança nacionais e internacionais, autoridades governamentais e atores-chave na luta contra o narcotráfico, o observatório busca fortalecer a capacidade de resposta regional mediante a criação de painéis de controle dinâmicos e acessíveis online, promovendo a cooperação e o intercâmbio de informações entre os países do continente.',
                'Dirección Nacional de Gestión de Bases de Datos de Seguridad': 'Direção Nacional de Gestão de Bancos de Dados de Segurança',
                'Todos los derechos reservados': 'Todos os direitos reservados',
                '© 2025 Observatorio de Drogas Sintéticas': '© 2025 Observatório de Drogas Sintéticas',
                
                /* Traducciones para la página de legislación */
                'Legislación Internacional': 'Legislação Internacional',
                'Legislación Argentina': 'Legislação Argentina',
                'Legislación Brasil': 'Legislação Brasileira',
                'Legislación Chile': 'Legislação Chilena',
                'Legislación Colombiana': 'Legislação Colombiana',
                'Legislación México': 'Legislação Mexicana',
                'Ver documento': 'Ver documento',
                'Constitución de la Nación Argentina': 'Constituição da Nação Argentina',
                'Ley 23737 - Modificación al Codigo Penal – Narcotrafico': 'Lei 23737 - Modificação do Código Penal - Narcotráfico',
                'Ley 17818 - Normas para su comercialización. Ley de estupefacientes': 'Lei 17818 - Normas para sua comercialização. Lei de entorpecentes',
                'Ley 26.045 - Ley del Registro Nacional de Precursores Químicos': 'Lei 26.045 - Lei do Registro Nacional de Precursores Químicos',
                'Ley N° 26.052 - Ley de Desfederalización Parcial de la Competencia Penal': 'Lei Nº 26.052 - Lei de Desfederalização Parcial da Competência Penal',
                'Ley 27319 - Delitos Complejos': 'Lei 27319 - Crimes Complexos',
                'Ley 11.343 (2006)': 'Lei 11.343 (2006)',
                'Ley N° 20.000 (1997)': 'Lei Nº 20.000 (1997)',
                'Ley 30 - Estatuto de Estupefacientes': 'Lei 30 - Estatuto de Entorpecentes',
                'Ley 599 - Código Penal': 'Lei 599 - Código Penal',
                'Ley 624 - Acuerdo entre Colombia y España sobre cooperación': 'Lei 624 - Acordo entre Colômbia e Espanha sobre cooperação',
                'Ley 745 - Tipificación de contravención y porte de dosis personal': 'Lei 745 - Tipificação de contravenção e porte de dose pessoal',
                'Convención para la Supresión del Tráfico Ilícito de Estupefacientes': 'Convenção para a Supressão do Tráfico Ilícito de Entorpecentes'
            }
        };
        
        if (!translations[lang]) {
            console.error("No hay traducciones disponibles para:", lang);
            return;
        }
        
        // Aplicar traducciones a elementos con clase 'translatable' o texto visible
        // Primero buscar párrafos completos y elementos de texto principales
        const paragraphElements = document.querySelectorAll('p, h1, h2, h3, h4, h5');
        paragraphElements.forEach(element => {
            const originalText = element.textContent.trim();
            // Buscar tanto texto exacto como texto contenido en los párrafos
            if (translations[lang][originalText]) {
                element.textContent = translations[lang][originalText];
                element.setAttribute('data-original-text', originalText);
            } else {
                // Buscar coincidencias parciales en párrafos largos
                for (const [sourceText, translatedText] of Object.entries(translations[lang])) {
                    if (sourceText.length > 50 && originalText.includes(sourceText)) {
                        // Reemplazar la parte que coincide
                        element.textContent = element.textContent.replace(sourceText, translatedText);
                        element.setAttribute('data-translated', 'partial');
                    }
                }
            }
        });
        
        // Luego aplicar traducciones a elementos más pequeños como enlaces, botones, etc.
        const smallElements = document.querySelectorAll('a, button, span, li, label, strong, em, div.title');
        smallElements.forEach(element => {
            const originalText = element.textContent.trim();
            if (translations[lang][originalText]) {
                element.textContent = translations[lang][originalText];
                element.setAttribute('data-original-text', originalText);
            }
        });
    }
    
    // Función para manejar clics en los botones de idioma
    function handleLanguageButtonClick(event) {
        event.preventDefault();
        
        const langCode = this.getAttribute('data-lang');
        console.log("Botón de idioma clickeado:", langCode);
        
        // Realizar una solicitud AJAX para informar al servidor
        fetch(`/browser_translate/${langCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("Traducción activada:", data.language_name);
                    // Activar la traducción del navegador
                    activateTranslation(langCode);
                    
                    // También actualizar la sesión del servidor (petición paralela)
                    fetch(`/set_language/${langCode}`);
                    
                    // Recargar la página para aplicar los cambios
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error("Error al activar la traducción:", error);
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
        activateTranslation(preferredLanguage);
    }
});
