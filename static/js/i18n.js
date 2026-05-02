/**
 * Fase 34: Motor de Internacionalización (i18n).
 * Permite que la interfaz se adapte a cualquier idioma de forma profesional.
 */
const I18N_ENGINE = {
    currentLang: 'es',
    translations: {
        es: {
            welcome: "Bienvenido a la Experiencia Gourmet",
            order_now: "Pedir Ahora",
            checkout: "Finalizar Compra",
            status_pending: "Pendiente",
            status_cooking: "En Cocina",
            status_ready: "Listo para recoger"
        },
        en: {
            welcome: "Welcome to the Gourmet Experience",
            order_now: "Order Now",
            checkout: "Checkout",
            status_pending: "Pending",
            status_cooking: "In Kitchen",
            status_ready: "Ready for Pickup"
        }
    },
    
    t(key) {
        return this.translations[this.currentLang][key] || key;
    },
    
    setLang(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            document.dispatchEvent(new CustomEvent('langChanged', { detail: lang }));
        }
    }
};

window.i18n = I18N_ENGINE;
console.log("Enterprise i18n Engine Initialized.");
