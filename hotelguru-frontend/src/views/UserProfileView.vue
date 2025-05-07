<template>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8" lg="6">
          <v-card>
            <v-card-title class="headline">
              Profilom Szerkesztése
            </v-card-title>
            <v-card-text>
              <v-form ref="profileForm" @submit.prevent="saveProfile">
                <v-text-field
                  v-if="authStore.user && authStore.user.name"
                  label="Név"
                  :model-value="authStore.user.name"
                  readonly
                  disabled
                  variant="filled"
                  class="mb-3"
                ></v-text-field>
  
                <v-text-field
                  v-model="userData.email"
                  label="Email cím"
                  type="email"
                  :rules="[rules.required, rules.email]"
                  required
                  class="mb-3"
                ></v-text-field>
  
                <v-text-field
                  v-model="userData.phone_number"
                  label="Telefonszám"
                  :rules="[rules.required]"
                  required
                  class="mb-3"
                ></v-text-field>
  
                <v-divider class="my-4"></v-divider>
                <p class="text-h6 mb-2">Cím</p>
                <v-text-field
                  v-model="userData.address.city"
                  label="Város"
                  :rules="[rules.required]"
                  required
                  class="mb-3"
                ></v-text-field>
                <v-text-field
                  v-model="userData.address.street"
                  label="Utca, házszám"
                  :rules="[rules.required]"
                  required
                  class="mb-3"
                ></v-text-field>
                <v-text-field
                  v-model="userData.address.postalcode"
                  label="Irányítószám"
                  type="number"
                  :rules="[rules.required]"
                  required
                  class="mb-3"
                ></v-text-field>
                 <v-divider class="my-4"></v-divider>
                </v-form>
              </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="saveProfile" :loading="isLoading" :disabled="isLoading">
                Mentés
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
  
      <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout" location="top right">
        {{ snackbar.message }}
      </v-snackbar>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'; // computed importálva
  import { useAuthStore } from '@/stores/auth';
  // import userService from '@/services/userService'; // Ha lenne
  
  // Store
  const authStore = useAuthStore();
  
  // Refs
  const profileForm = ref(null); // Ref az űrlaphoz
  const userData = ref({
    email: '',
    phone_number: '', // Backend `UserUpdateSchema` ezt várja
    address: {
      city: '',
      street: '',
      postalcode: null, // Kezdetben lehet null vagy üres string
    },
    // password: '' // Jelszómódosítás esetén kellene
  });
  const isLoading = ref(false);
  const snackbar = ref({
    show: false,
    message: '',
    color: '',
    timeout: 3000,
  });
  
  // Egyszerű validációs szabályok
  const rules = {
    required: value => !!value || 'Kötelező mező.',
    email: value => /.+@.+\..+/.test(value) || 'Érvénytelen email formátum.',
  };
  
  // Computed property a User ID-hez (rövidítés)
  const userId = computed(() => authStore.user?.id);
  
  // Adatbetöltés (onMounted)
  onMounted(async () => {
    if (authStore.isAuthenticated && userId.value) {
      isLoading.value = true; // Töltést jelzünk
      try {
        // Megpróbáljuk betölteni a profilt az authStore-ból
        await authStore.fetchUserProfile(); // Feltételezve, hogy ez az action létezik vagy létrehozzuk
        // Frissítjük a helyi userData ref-et a store adataival
        if (authStore.userProfile) { // Feltételezve, hogy a store ide tölti be
            userData.value.email = authStore.userProfile.email || '';
            userData.value.phone_number = authStore.userProfile.phone || ''; // Backend phone, frontend phone_number
            if (authStore.userProfile.address) {
              userData.value.address = { ...authStore.userProfile.address };
            }
        } else {
             console.warn("User profile data not found in store after fetch.");
             // Esetleg az alap user adatokkal próbálkozunk (bár az hiányos)
             userData.value.email = authStore.user?.email || ''; // Ha a user objektum tartalmazza
        }
         console.log("UserProfileView mounted. User ID:", userId.value);
         console.log("Initial userData:", JSON.parse(JSON.stringify(userData.value))); // Mély másolás logoláshoz
  
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
        showSnackbar('Nem sikerült betölteni a profiladatokat.', 'error');
      } finally {
        isLoading.value = false;
      }
    }
  });
  
  // Snackbar megjelenítése
  const showSnackbar = (message, color = 'success') => {
    snackbar.value.message = message;
    snackbar.value.color = color;
    snackbar.value.show = true;
  };
  
  // Profil mentése
  const saveProfile = async () => {
    if (!userId.value) {
      showSnackbar('Hiba: Nincs bejelentkezett felhasználó.', 'error');
      return;
    }
  
    // Opcionális: Vuetify űrlap validáció
    const { valid } = await profileForm.value?.validate();
    if (!valid) {
      showSnackbar('Kérjük, javítsa a hibás mezőket!', 'warning');
      return;
    }
  
    isLoading.value = true;
    try {
      // Előkészítjük a küldendő adatokat (csak a releváns mezőket)
      const dataToUpdate = {
          email: userData.value.email,
          phone_number: userData.value.phone_number,
          address: {
              city: userData.value.address.city,
              street: userData.value.address.street,
              // Biztosítjuk, hogy a postalcode szám legyen, ha nem üres
              postalcode: userData.value.address.postalcode ? parseInt(userData.value.address.postalcode, 10) : null,
          }
          // Ha lenne jelszó módosítás:
          // password: userData.value.new_password || undefined // Csak akkor küldjük, ha van új jelszó
      };
  
      // Eltávolítjuk a null/undefined értékeket, ha a backend nem szereti őket
      // (Ez függ a backend implementációtól)
      // Object.keys(dataToUpdate).forEach(key => dataToUpdate[key] === undefined && delete dataToUpdate[key]);
      // if (dataToUpdate.address && Object.keys(dataToUpdate.address).length === 0) {
      //     delete dataToUpdate.address;
      // }
  
      console.log("Data being sent to update:", JSON.parse(JSON.stringify(dataToUpdate))); // Küldés előtti log
  
      // Az auth.js store-ban kell létrehozni az updateUserProfile action-t
      await authStore.updateUserProfile(userId.value, dataToUpdate);
  
      showSnackbar('Profil sikeresen frissítve!', 'success');
    } catch (error) {
      console.error("Profile update failed:", error);
      const errorMessage = error.response?.data?.message || error.message || 'Profil frissítése sikertelen.';
      showSnackbar(errorMessage, 'error');
    } finally {
      isLoading.value = false;
    }
  };
  </script>
  
  <style scoped>
  /* Stílusok itt */
  </style>