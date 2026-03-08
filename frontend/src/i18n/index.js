import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import idJson from './id.json';
import enJson from './en.json';

const resources = {
    id: { translation: idJson },
    en: { translation: enJson }
};

const savedLang = localStorage.getItem('mocal_lang') || 'en';

i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: savedLang,
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false
        }
    });

export default i18n;
