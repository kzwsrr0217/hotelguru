<template>
  <v-container>
    <h1 class="text-h4 text-center mb-6">Foglalásaim</h1>

    <v-row v-if="isLoading" justify="center" class="my-10">
      <v-col cols="auto">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="text-center mt-2 text-medium-emphasis">Foglalások betöltése...</p>
      </v-col>
    </v-row>

    <v-row v-else-if="error" justify="center">
       <v-col cols="12" md="8">
           <v-alert
               type="error"
               density="compact"
               variant="tonal"
               closable
             >
               {{ error }}
             </v-alert>
       </v-col>
    </v-row>

    <v-row v-else-if="reservations.length === 0" justify="center">
         <v-col cols="12" md="8">
             <v-alert
               type="info"
               variant="tonal"
               density="compact"
             >
               Nincsenek aktuális vagy jövőbeli foglalásaid.
             </v-alert>
         </v-col>
     </v-row>

    <v-row v-else>
      <v-col
        v-for="res in reservations"
        :key="res.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card outlined class="reservation-card d-flex flex-column" height="100%">
          <v-card-title class="d-flex justify-space-between">
            <span>Foglalás #{{ res.id }}</span>
            <v-chip :color="statusColor(res.status)" size="small" label>
                {{ formatStatus(res.status) }}
            </v-chip>
          </v-card-title>
          <v-card-subtitle>
             Foglalva: {{ formatDate(res.reservation_date) }}
          </v-card-subtitle>
          <v-divider class="my-2"></v-divider>
          <v-card-text class="flex-grow-1"> 
            <p><v-icon small start>mdi-calendar-range</v-icon> <strong>Időszak:</strong> {{ formatDate(res.start_date) }} - {{ formatDate(res.end_date) }}</p>
            <p><v-icon small start>mdi-bed-outline</v-icon> <strong>Szobák:</strong> {{ getRoomNumbers(res.rooms) }}</p>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-if="canCancel(res.status)"
              color="error"
              variant="text"
              size="small"
              @click="confirmCancel(res)"
              :loading="cancelDialog.loading && cancelDialog.reservation?.id === res.id"
              :disabled="cancelDialog.loading"
            >
              Lemondás
            </v-btn>
             <v-btn
              color="grey"
              variant="text"
              size="small"
              disabled
             >
              Részletek
             </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

     <v-dialog v-model="cancelDialog.show" persistent max-width="450px">
        <v-card>
            <v-card-title class="text-h5 error--text">
                <v-icon start color="error">mdi-alert-circle-outline</v-icon>
                Foglalás Lemondása
            </v-card-title>
            <v-card-text>
                Biztosan le szeretnéd mondani a(z) <strong>#{{ cancelDialog.reservation?.id }}</strong> azonosítójú foglalást
                (szoba: {{ getRoomNumbers(cancelDialog.reservation?.rooms) }},
                 időszak: {{ formatDate(cancelDialog.reservation?.start_date) }} - {{ formatDate(cancelDialog.reservation?.end_date) }})?
                 <v-expand-transition>
                   <v-alert v-if="cancelDialog.error" type="error" density="compact" class="mt-3" variant="tonal">
                    {{ cancelDialog.error }}
                   </v-alert>
                 </v-expand-transition>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey darken-1" variant="text" @click="cancelDialog.show = false" :disabled="cancelDialog.loading">Mégse</v-btn>
                <v-btn color="error" variant="elevated" :loading="cancelDialog.loading" @click="executeCancel">Lemondás Megerősítése</v-btn>
            </v-card-actions>
        </v-card>
     </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import reservationService from '@/services/reservationService';
// Auth store most nem kell, mert a service küldi a tokent
console.log('Imported reservationService:', reservationService); // <<< ÚJ LOG

const reservations = ref([]);
const isLoading = ref(false);
const error = ref(null);

// Lemondás dialógus állapota
const cancelDialog = reactive({
    show: false,
    loading: false,
    error: null,
    reservation: null, // Az a foglalás, amit lemondani készülünk
});

// ---- Segédfüggvények ----
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try { const date = new Date(dateString); if (isNaN(date.getTime())) return dateString; return date.toLocaleDateString('hu-HU'); } catch { return dateString; }
};

const formatStatus = (statusEnumString) => {
  const statusKey = statusEnumString?.includes('.') ? statusEnumString.split('.')[1] : statusEnumString;
  const statusMap = { Canceled:'Lemondva', Depending:'Függőben', Success:'Visszaigazolva', Expired:'Lejárt', CheckedIn:'Bejelentkezve', CheckedOut:'Kijelentkezve' };
  return statusMap[statusKey] || statusKey;
};

const statusColor = (statusEnumString) => {
    const statusKey = statusEnumString?.includes('.') ? statusEnumString.split('.')[1] : statusEnumString;
    switch (statusKey?.toLowerCase()) {
        case 'success': return 'green-darken-1';
        case 'checkedin': return 'blue-darken-1';
        case 'checkedout': return 'indigo-darken-1';
        case 'depending': return 'orange-darken-1';
        case 'canceled': return 'grey-darken-1';
        case 'expired': return 'red-darken-1';
        default: return 'blue-grey';
    }
};

const getRoomNumbers = (rooms) => {
  if (!rooms || rooms.length === 0) return 'N/A';
  return rooms.map(room => room.number).join(', ');
};
// ---- Segédfüggvények Vége ----


// --- Lemondás Logika ---
const canCancel = (statusEnumString) => {
    const statusKey = statusEnumString?.includes('.') ? statusEnumString.split('.')[1] : statusEnumString;
    // Itt a backend fogja a pontos szabályt (pl. dátum) ellenőrizni,
    // de a UI-n letilthatjuk a gombot a már egyértelműen nem lemondható státuszoknál.
    return ['Depending', 'Success'].includes(statusKey);
};

const confirmCancel = (reservation) => {
      console.log("confirmCancel called with reservation:", JSON.stringify(reservation)); // <<< ÚJ LOG
      if (!reservation || typeof reservation.id === 'undefined') {
          console.error("confirmCancel received invalid reservation object!"); // <<< Hiba log
      }
      cancelDialog.reservation = reservation;
      cancelDialog.error = null;
      cancelDialog.loading = false;
      cancelDialog.show = true;
      console.log("cancelDialog state after confirmCancel:", JSON.stringify(cancelDialog)); // <<< ÚJ LOG
  };

// executeCancel - Tényleges API hívással és lista frissítéssel
const executeCancel = async () => {
    console.log("executeCancel: Function called."); // <<< LOG 1
    const reservationId = cancelDialog.reservation?.id;
    console.log("executeCancel: Reservation ID:", reservationId); // <<< LOG 2
    if (!reservationId) 
    {
        console.error("executeCancel: No reservation ID found in dialog state."); // <<< LOG (hiba)
        cancelDialog.error = "Hiba: Nincs kiválasztva foglalás a lemondáshoz."; // Adjunk itt is visszajelzést
        return;
    }
    cancelDialog.loading = true;
    cancelDialog.error = null;
    console.log(`executeCancel: Set loading=true for ID: ${reservationId}. Making API call...`); // <<< LOG 3

    try {
        // Tényleges API hívás a lemondáshoz
        const response = await reservationService.cancelReservation(reservationId);
        console.log("executeCancel: API call successful:", response); // <<< LOG 4

        cancelDialog.show = false; // Dialógus bezárása
        
        console.log("executeCancel: Re-fetching reservations after cancellation..."); // <<< LOG 5
        await fetchReservations(); // Lista frissítése
        console.log("executeCancel: Reservations re-fetched."); // <<< LOG 6

        // Opcionális: Sikerüzenet (pl. Snackbar)
        // showSnackbar(response.data.message || 'Foglalás sikeresen lemondva.', 'success');

        // Sikeres lemondás után frissítjük a foglalások listáját
        await fetchReservations();

        // Opcionális: Sikerüzenet (pl. Snackbar)
        // showSnackbar(response.data.message || 'Foglalás sikeresen lemondva.', 'success');

    } catch (err) {
        console.error("executeCancel: API call failed:", err.response || err); // <<< LOG (hiba)
        // Hibaüzenet megjelenítése a dialógusban
        cancelDialog.error = err.response?.data?.message || 'Hiba történt a lemondás során.';
    } finally {
        console.log("executeCancel: Setting loading=false."); // <<< LOG 7
        cancelDialog.loading = false; // Töltés vége a dialógusban
    }
};
// --- Lemondás Logika Vége ---


// Foglalások lekérése
const fetchReservations = async () => {
  isLoading.value = true;
  error.value = null;
  // reservations.value = []; // Nem ürítjük ki azonnal, csak ha hiba van, vagy ha megjött az új adat
  try {
    const response = await reservationService.getMyReservations();
    reservations.value = response.data; // Felülírjuk a listát a friss adatokkal
  } catch (err) {
    console.error("Failed to fetch reservations:", err.response?.data || err.message);
    error.value = 'Hiba történt a foglalások lekérése közben.';
    reservations.value = []; // Hiba esetén ürítjük
    if (err.response?.status === 401) {
      error.value += ' (Lejárt munkamenet?). Próbáljon újra bejelentkezni.';
      // Opcionális: Kijelentkeztetés
      // const authStore = useAuthStore(); // Importálni kellene
      // authStore.logout();
    }
  } finally {
    isLoading.value = false;
  }
};

// Komponens betöltődésekor lekérjük a foglalásokat
onMounted(fetchReservations);
</script>

<style scoped>
.reservations-container { max-width: 1200px; margin: 20px auto; padding: 20px; }
h1 { text-align: center; margin-bottom: 30px; }
.loading, .error { text-align: center; font-size: 1.2em; padding: 20px; }
.error { color: red; }
.no-reservations { text-align: center; padding: 20px; }

/* Státusz chipek jobb láthatósága */
.v-chip--label { font-size: 0.8em; height: 22px; font-weight: 500; }

.reservation-card { transition: box-shadow 0.3s ease-in-out; }
.reservation-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.reservation-card p { display: flex; align-items: center; gap: 8px; /* Térköz az ikon és a szöveg között */ }
.reservation-card p .v-icon { color: rgba(0, 0, 0, 0.6); /* Ikon színe */ }
</style>