<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12" outlined>
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Bejelentkezés</v-toolbar-title>
          </v-toolbar>
          <v-form @submit.prevent="handleLogin">
            <v-card-text>
              <v-alert
                v-model="showLoginError"
                type="error"
                density="compact"
                closable
                class="mb-4"
                v-if="authStore.loginError"
              >
                {{ authStore.loginError }}
              </v-alert>

              <v-text-field
                v-model="email"
                label="Email cím"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                required
                :rules="emailRules"
                autocomplete="username"
                variant="outlined"
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Jelszó"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                :type="showPassword ? 'text' : 'password'"
                required
                :rules="passwordRules"
                autocomplete="current-password"
                variant="outlined"
                @click:append-inner="showPassword = !showPassword"
              ></v-text-field>

            </v-card-text>
            <v-card-actions class="pa-4">
              <v-spacer></v-spacer>
              <v-btn
                :loading="authStore.isLoading"
                :disabled="authStore.isLoading"
                color="primary"
                type="submit"
                large
              >
                Bejelentkezés
              </v-btn>
            </v-card-actions>
          </v-form>
           <v-card-text class="text-center">
              Még nincs fiókod? <router-link :to="{ name: 'register' }">Regisztráció</router-link>
           </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
// useRouter importálása már nem feltétlenül kell itt, ha nem használjuk direktben
// import { useRouter } from 'vue-router';

// Store példányosítása
const authStore = useAuthStore();

// Reaktív változók az űrlap mezőkhöz
const email = ref('');
const password = ref('');
const showPassword = ref(false); // Jelszó láthatóságának váltásához
const showLoginError = ref(false); // Hibaüzenet láthatóságához

// Egyszerű validációs szabályok (Vuetify használja)
const emailRules = [
  value => !!value || 'Az email cím kötelező.',
  value => /.+@.+\..+/.test(value) || 'Érvénytelen email formátum.',
];
const passwordRules = [
  value => !!value || 'A jelszó kötelező.',
  // value => value.length >= 6 || 'A jelszónak legalább 6 karakternek kell lennie.', // Ha szükséges
];

// Figyeljük a store hiba állapotát, és megjelenítjük az alertet
watch(() => authStore.loginError, (newError) => {
  showLoginError.value = !!newError;
});

// Bejelentkezés kezelő függvény
const handleLogin = () => {
  // A v-form kezeli a validációt, de itt is ellenőrizhetnénk,
  // mielőtt meghívjuk a store akciót, ha összetettebb logika kellene.
  // Pl. a v-form ref-jével: form.value.validate() -> promise-t ad vissza

  // Reseteljük a hibaüzenet láthatóságát minden próbálkozásnál
  showLoginError.value = false;
  // Store akció hívása
  authStore.login({
    email: email.value,
    password: password.value
  });
};

</script>

<style scoped>
/* A scoped stílusok nagyrészt törölhetők, mert a Vuetify kezeli, */
/* de néhány specifikusat megtarthatunk vagy hozzáadhatunk. */
.fill-height {
  min-height: calc(100vh - 64px - 20px); /* Alkalmazkodás az app bar-hoz */
}
/* Opcionális: Kártya jobb megjelenése kisebb képernyőn */
.v-card {
    margin-top: 20px;
    margin-bottom: 20px;
}
</style>