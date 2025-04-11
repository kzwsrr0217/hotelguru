// src/main.js
import './assets/main.css' // Meglévő CSS

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// --- Vuetify importok ---
import 'vuetify/styles' // Alap Vuetify stílusok
import '@mdi/font/css/materialdesignicons.css'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components' // Összes komponens importálása (vagy specifikusak)
import * as directives from 'vuetify/directives' // Direktívák importálása
import '@mdi/font/css/materialdesignicons.css' // Material Design Ikonok
// ------------------------

import App from './App.vue'
import router from './router'

const app = createApp(App)

// --- Vuetify példány létrehozása ---
const vuetify = createVuetify({
  components, // Komponensek átadása
  directives, // Direktívák átadása
  // Itt lehetne témát, alapértelmezett ikonokat stb. beállítani
  // icons: {
  //  defaultSet: 'mdi', // Material Design Icons használata
  //},
})
// --------------------------------

app.use(createPinia()) // Pinia (állapotkezelő)
app.use(router)      // Router
app.use(vuetify)     // <<< Vuetify hozzáadása az alkalmazáshoz

app.mount('#app')