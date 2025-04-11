// src/views/DashboardView.vue
<template>
  <div>
    <h1>Dashboard</h1>
    <p>Ez egy védett oldal...</p>
    <div v-if="authStore.user">...</div>

    <hr>
    <button @click="callJwtTest" :disabled="testLoading">
      JWT Teszt Végpont Hívása
    </button>
    <p v-if="testResult">Teszt eredmény: {{ testResult }}</p>
    <p v-if="testError" style="color: red;">Teszt hiba: {{ testError }}</p>

  </div>
</template>

<script setup>
import { ref } from 'vue'; // ref importálása
import { useAuthStore } from '@/stores/auth';
import apiClient from '@/services/apiClient'; // apiClient importálása

const authStore = useAuthStore();
const testResult = ref(null); // Teszt eredményének tárolása
const testError = ref(null);  // Teszt hibájának tárolása
const testLoading = ref(false); // Betöltési állapot

const callJwtTest = async () => {
  testLoading.value = true;
  testResult.value = null;
  testError.value = null;
  console.log("Calling /jwt_test endpoint...");
  try {
    // Az apiClient automatikusan hozzáadja a tokent
    const response = await apiClient.get('/reservation/jwt_test');
    console.log("JWT Test Response:", response);
    testResult.value = response.data; // Sikeres válasz eltárolása
  } catch (err) {
    console.error("JWT Test Failed:", err.response || err);
    testError.value = err.response?.data?.message || err.message || 'Ismeretlen hiba'; // Hiba eltárolása
    // Ha 401-et kapunk itt is, az nagy baj
    if (err.response?.status === 401) {
        testError.value += " (Unauthorized - A token validáció alapvetően hibás?)";
    }
  } finally {
    testLoading.value = false;
  }
};
</script>

<style scoped>
    hr { margin: 20px 0; }
    button { margin-right: 10px; }
</style>