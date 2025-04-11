<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6"> 
        <v-card class="elevation-12" outlined>
          <v-toolbar color="secondary" dark flat> 
            <v-toolbar-title>Regisztráció</v-toolbar-title>
          </v-toolbar>
          <v-form @submit.prevent="handleRegister">
            <v-card-text>
              <v-alert
                v-model="showRegisterError"
                type="error"
                density="compact"
                closable
                class="mb-4"
                v-if="authStore.registerError"
              >
                {{ authStore.registerError }}
              </v-alert>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="formData.name"
                    label="Teljes Név"
                    prepend-inner-icon="mdi-account"
                    required
                    :rules="[rules.required]"
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="formData.email"
                    label="Email cím"
                    prepend-inner-icon="mdi-email-outline"
                    type="email"
                    required
                    :rules="[rules.required, rules.email]"
                    autocomplete="username"
                    variant="outlined"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12" md="6">
                   <v-text-field
                    v-model="formData.password"
                    label="Jelszó"
                    prepend-inner-icon="mdi-lock-outline"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    :rules="[rules.required, rules.minLength(6)]"
                    autocomplete="new-password"
                    variant="outlined"
                    @click:append-inner="showPassword = !showPassword"
                    hint="Legalább 6 karakter"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                 <v-col cols="12" md="6">
                    <v-text-field
                        v-model="formData.phone"
                        label="Telefonszám"
                        prepend-inner-icon="mdi-phone"
                        required
                        :rules="[rules.required]"
                        variant="outlined"
                    ></v-text-field>
                 </v-col>
              </v-row>

              <v-divider class="my-4"></v-divider>
              <p class="text-subtitle-1 mb-2">Lakcím</p>

              <v-row>
                 <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="formData.address.city"
                        label="Város"
                        required
                        :rules="[rules.required]"
                         variant="outlined"
                    ></v-text-field>
                 </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                        v-model="formData.address.postalcode"
                        label="Irányítószám"
                        type="number"
                        required
                        :rules="[rules.required, rules.numeric]"
                        variant="outlined"
                    ></v-text-field>
                 </v-col>
              </v-row>
               <v-row>
                 <v-col cols="12">
                    <v-text-field
                        v-model="formData.address.street"
                        label="Utca, házszám"
                        required
                        :rules="[rules.required]"
                        variant="outlined"
                    ></v-text-field>
                 </v-col>
               </v-row>

            </v-card-text>
            <v-card-actions class="pa-4">
              <v-spacer></v-spacer>
              <v-btn
                :loading="authStore.isLoading"
                :disabled="authStore.isLoading"
                color="secondary"
                type="submit"
                large
              >
                Regisztráció
              </v-btn>
            </v-card-actions>
          </v-form>
           <v-card-text class="text-center">
              Már van fiókod? <router-link :to="{ name: 'login' }">Bejelentkezés</router-link>
           </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { reactive, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
// import { useRouter } from 'vue-router'; // Ha kellene átirányítás innen

const authStore = useAuthStore();
// const router = useRouter();

// Reaktív objektum az űrlap adataihoz
const formData = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
  address: {
    city: '',
    street: '',
    postalcode: ''
  }
});

const showPassword = ref(false);
const showRegisterError = ref(false);

// Validációs szabályok objektuma
const rules = {
  required: value => !!value || 'Ez a mező kötelező.',
  email: value => /.+@.+\..+/.test(value) || 'Érvénytelen email formátum.',
  minLength: (len) => value => (value && value.length >= len) || `Legalább ${len} karakter szükséges.`,
  numeric: value => /^\d+$/.test(value) || 'Csak számok adhatók meg.'
};

// Figyeljük a store hiba állapotát
watch(() => authStore.registerError, (newError) => {
  showRegisterError.value = !!newError;
});

// Regisztráció kezelő függvény
const handleRegister = () => {
    // TODO: Érdemes lenne a v-form validációt is ellenőrizni itt a submit előtt
    // const { valid } = await form.value.validate(); if (!valid) return;

    showRegisterError.value = false; // Hiba törlése új próbálkozásnál
    // Adatok előkészítése (irányítószám konverzió)
    const userData = {
        ...formData,
        address: {
        ...formData.address,
        postalcode: formData.address.postalcode ? parseInt(formData.address.postalcode, 10) : null
        }
    };
    authStore.register(userData);
};
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px - 20px);
}
.v-card {
    margin-top: 20px;
    margin-bottom: 20px;
}
/* Opcionális: A hint (jelszó) jobb láthatósága */
.v-text-field :deep(.v-messages__message) {
    line-height: 1.2em;
}
</style>