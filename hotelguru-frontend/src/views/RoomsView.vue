<template>
  <v-container>
    <h1 class="text-h4 text-center mb-6">Szállodai Szobák Keresése</h1>

    <v-sheet elevation="2" rounded class="pa-4 mb-6" color="grey-lighten-4">
       <v-row align="center" justify="center" dense>
         <v-col cols="12" sm="6" md="4">
           <v-text-field
             v-model="startDate"
             label="Érkezés"
             type="date"
             :min="today"
             variant="outlined"
             density="compact"
             hide-details="auto"
           ></v-text-field>
         </v-col>
         <v-col cols="12" sm="6" md="4">
            <v-text-field
             v-model="endDate"
             label="Távozás"
             type="date"
             :min="minEndDate"
             variant="outlined"
             density="compact"
             hide-details="auto"
           ></v-text-field>
         </v-col>
         <v-col cols="12" md="auto">
           <v-btn
             @click="findAvailableRooms"
             :disabled="!startDate || !endDate || isLoading"
             :loading="isLoading"
             color="primary"
             block
             class="search-button"
            >
             Keresés
           </v-btn>
         </v-col>
       </v-row>
     </v-sheet>
    <v-row v-if="isLoading" justify="center" class="my-10">
      <v-col cols="auto">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="text-center mt-2">Szobák betöltése...</p>
      </v-col>
    </v-row>

    <v-row v-if="error || bookingState.error || bookingState.success" justify="center">
       <v-col cols="12" md="10" lg="8">
           <v-alert
               v-if="error"
               type="error"
               density="compact"
               closable
               v-model="showErrorAlert"
               class="mb-4"
             >
               {{ error }}
             </v-alert>
            <v-alert
               v-if="bookingState.error"
               type="error"
               density="compact"
               closable
               v-model="showBookingErrorAlert"
               class="mb-4"
             >
               {{ bookingState.error }}
             </v-alert>
             <v-alert
               v-if="bookingState.success"
               type="success"
               density="compact"
               closable
               v-model="showBookingSuccessAlert"
               class="mb-4"
             >
               {{ bookingState.success }}
             </v-alert>
       </v-col>
    </v-row>

    <div v-if="!isLoading">
        <p v-if="filteredDates.start && filteredDates.end && !error" class="text-center text-medium-emphasis mb-4">
             Elérhető szobák: {{ formatDate(filteredDates.start) }} - {{ formatDate(filteredDates.end) }}
           </p>
        <v-row v-if="rooms.length > 0">
          <v-col
            v-for="room in rooms"
            :key="room.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card outlined hover class="room-card">
              <v-card-title class="pb-1">
                Szoba {{ room.number }}
              </v-card-title>
              <v-card-subtitle class="pb-2">
                {{ room.name || room.room_type?.name || 'N/A' }}
              </v-card-subtitle>
              <v-card-text class="pb-2">
                <div>Emelet: {{ room.floor }}</div>
                <div>Ár: <strong class="text-primary">{{ formatPrice(room.price) }} / éj</strong></div>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="success"
                  variant="elevated"
                  small
                  :disabled="!startDate || !endDate || bookingState.loading === room.id || !authStore.isAuthenticated"
                  :loading="bookingState.loading === room.id"
                  @click="initiateBooking(room)"
                 >
                  Foglalás
                 </v-btn>
              </v-card-actions>
                <v-tooltip v-if="!authStore.isAuthenticated" location="bottom" text="A foglaláshoz be kell jelentkezni." activator="parent" ></v-tooltip>

            </v-card>
          </v-col>
        </v-row>
        <v-row v-if="!isLoading && rooms.length === 0 && !error" justify="center">
             <v-col cols="auto">
                 <p class="text-center text-medium-emphasis mt-5">Nincsenek elérhető szobák a megadott feltételekkel.</p>
             </v-col>
         </v-row>
    </div>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue'; // watch hozzáadva
import { useRouter } from 'vue-router';
import roomService from '@/services/roomService';
import reservationService from '@/services/reservationService';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// Állapotok
const rooms = ref([]);
const isLoading = ref(false); // Lista töltésekor
const error = ref(null); // Lista hibájakor
const today = new Date().toISOString().split('T')[0];
const startDate = ref('');
const endDate = ref('');
const filteredDates = ref({ start: null, end: null });

const bookingState = reactive({
  loading: null, // Foglalás gomb ID-ja
  error: null,
  success: null,
});

// Alert-ek láthatósága (hogy bezárhatók legyenek)
const showErrorAlert = ref(false);
const showBookingErrorAlert = ref(false);
const showBookingSuccessAlert = ref(false);

// Figyelők az alert-ek megjelenítésére
watch(error, (newError) => { showErrorAlert.value = !!newError });
watch(() => bookingState.error, (newError) => { showBookingErrorAlert.value = !!newError });
watch(() => bookingState.success, (newSuccess) => { showBookingSuccessAlert.value = !!newSuccess });

// MinEndDate, FormatPrice, FormatDate maradnak
const minEndDate = computed(() => {
  if (!startDate.value) return today;
  try {
    const start = new Date(startDate.value);
    start.setDate(start.getDate() + 1);
    return start.toISOString().split('T')[0];
  } catch { return today; }
});
const formatPrice = (price) => {
  if (price === null || price === undefined) return 'N/A';
  return new Intl.NumberFormat('hu-HU', { style: 'currency', currency: 'HUF', maximumFractionDigits: 0 }).format(price);
};
const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return date.toLocaleDateString('hu-HU');
  } catch { return dateString; }
};

// Szobák lekérése API-ból
const fetchRooms = async (start = null, end = null) => {
  isLoading.value = true;
  error.value = null; // Hiba törlése új kereséskor
  filteredDates.value = { start, end };
  const params = {};
  if (start && end) {
    params.start_date = start;
    params.end_date = end;
  }
  try {
    const response = await roomService.findAvailableRooms(params);
    rooms.value = response.data;
  } catch (err) {
    console.error("Failed to fetch rooms:", err.response?.data || err.message);
    error.value = 'Hiba történt a szobák betöltése közben.';
    rooms.value = [];
  } finally {
    isLoading.value = false;
  }
};

// Keresés gomb funkciója
const findAvailableRooms = () => {
  bookingState.error = null;
  bookingState.success = null;
  if (startDate.value && endDate.value) {
    fetchRooms(startDate.value, endDate.value);
  } else {
    error.value = "Kérjük, válassza ki az érkezés és távozás dátumát a szűréshez.";
    rooms.value = [];
    filteredDates.value = { start: null, end: null };
  }
};

// Foglalás kezdeményezése
const initiateBooking = async (room) => {
  bookingState.error = null;
  bookingState.success = null;
  if (!startDate.value || !endDate.value) {
    bookingState.error = "Kérjük, először válasszon érkezési és távozási dátumot!";
    return;
  }
  if (!authStore.isAuthenticated) {
    bookingState.error = "A foglaláshoz be kell jelentkeznie!";
    return;
  }
  const reservationData = {
    start_date: startDate.value,
    end_date: endDate.value,
    room_numbers: [room.number],
  };
  bookingState.loading = room.id;
  try {
    const response = await reservationService.createReservation(reservationData);
    bookingState.success = `A(z) ${room.number} szoba foglalása sikeres a(z) ${formatDate(startDate.value)} - ${formatDate(endDate.value)} időszakra! Hamarosan átirányítunk...`;
    // Itt lehetne frissíteni a szobalistát is, hogy a lefoglalt eltűnjön:
    // await fetchRooms(startDate.value, endDate.value);
    setTimeout(() => {
      router.push({ name: 'my-reservations' });
    }, 3500);
  } catch (err) {
    console.error("Reservation failed:", err.response?.data || err.message);
    bookingState.error = `Foglalási hiba: ${err.response?.data?.message || 'Ismeretlen hiba.'}`;
  } finally {
    bookingState.loading = null;
  }
};

// Kezdeti betöltés
onMounted(() => {
  fetchRooms();
});
</script>

<style scoped>
/* Specifikus stílusok, ha kellenek */
.search-button {
    /* Biztosítjuk, hogy legalább akkora legyen, mint az inputok */
    height: 40px; /* Vagy igazítsd az outlined/compact text-field magasságához */
}
.room-card {
    transition: box-shadow 0.3s ease-in-out; /* Finomabb árnyékváltás */
}
.loading p {
    color: #555;
}
</style>