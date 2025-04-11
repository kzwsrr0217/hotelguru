<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>
         <router-link to="/" class="toolbar-title-link">
            <v-icon left class="mr-2">mdi-home-city</v-icon>
            HotelGuru
         </router-link>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn text :to="{ name: 'home' }" class="nav-btn">Home</v-btn>
      <v-btn text :to="{ name: 'rooms' }" class="nav-btn">Szobák</v-btn>
      <v-btn text :to="{ name: 'about' }" class="nav-btn">About</v-btn>

      <template v-if="!authStore.isAuthenticated">
        <v-btn text :to="{ name: 'login' }" class="nav-btn">Login</v-btn>
        <v-btn text :to="{ name: 'register' }" class="nav-btn">Register</v-btn>
      </template>

      <template v-if="authStore.isAuthenticated">
        <v-btn text :to="{ name: 'dashboard' }" class="nav-btn">Dashboard</v-btn>
        <v-btn text :to="{ name: 'my-reservations' }" class="nav-btn">Foglalásaim</v-btn>
        <v-btn v-if="authStore.hasRole('Administrator')" text :to="{ name: 'admin-rooms' }" class="nav-btn">Szobakezelés</v-btn>

         <span v-if="authStore.user" class="user-info mr-3 ml-3">
             ID: {{ authStore.user.id }} ({{ authStore.roles.join(', ') }})
         </span>

         <v-btn icon @click="handleLogout" title="Logout">
            <v-icon>mdi-logout</v-icon> </v-btn>
      </template>

    </v-app-bar>

    <v-main>
      <v-container fluid>
          <RouterView />
      </v-container>
    </v-main>

    </v-app>
</template>

<script setup>
// Csak azok az importok kellenek, amiket ténylegesen használ a script
import { computed, watch, onMounted } from 'vue';
import { RouterLink, RouterView, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Store és router példányosítása
const authStore = useAuthStore();
// const router = useRouter(); // Csak ha kellene pl. programatikus navigáció itt

// Kijelentkezés kezelő függvény
const handleLogout = () => {
  authStore.logout();
};

// Debug logok (opcionálisak, később törölhetők)
onMounted(() => {
  console.log('[App.vue Mounted] Initial isAuthenticated state:', authStore.isAuthenticated);
});
watch(() => authStore.isAuthenticated, (newValue, oldValue) => {
  console.log(`[App.vue Watch] isAuthenticated changed from ${oldValue} to ${newValue}`);
});

// A HelloWorld komponenst és a headerMessage computed-ot eltávolítottuk,
// mert a címet most az app bar kezeli, és a HelloWorld-ot nem használjuk.

</script>

<style scoped>
/* A scoped stílusok befolyásolhatják a Vuetify komponenseket is, */
/* de sok alap stílusra már nincs szükség. */

/* Link a címsorban ne legyen aláhúzva */
.toolbar-title-link {
    color: inherit;
    text-decoration: none;
}
.toolbar-title-link:hover {
    text-decoration: none; /* Hoverre se legyen */
}

/* Felhasználói infó stílusa */
.user-info {
    color: inherit;
    font-size: 0.9em;
    align-self: center;
}

/* Navigációs gombok ne legyenek csupa nagybetűsek */
.nav-btn {
    text-transform: none;
    font-weight: normal; /* Alapértelmezetten lehet vastagabb */
}

/* Opcionális: Aktív link kiemelése */
.v-btn.v-btn--active:before {
    opacity: 0.1; /* Vagy más vizuális jelzés */
}



</style>