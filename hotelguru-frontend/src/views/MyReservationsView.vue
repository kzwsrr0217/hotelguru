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
             
             <div v-if="res.invoice_services && res.invoice_services.length > 0" class="mt-3">
                <p><v-icon small start>mdi-room-service-outline</v-icon> <strong>Igénybe vett szolgáltatások:</strong></p>
                <v-list density="compact" lines="one" class="pa-0">
                  <v-list-item v-for="service in res.invoice_services" :key="service.id" class="pl-0">
                    <v-list-item-title class="text-caption">{{ service.name }}</v-list-item-title>
                    <template v-slot:append>
                      <span class="text-caption">{{ service.price.toLocaleString('hu-HU') }} Ft</span>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
             <p v-else-if="canAddServices(res.status)" class="text-caption mt-2">
                Még nincsenek extra szolgáltatások hozzáadva ehhez a foglaláshoz.
             </p>
             </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
               v-if="canAddServices(res.status)"
               color="secondary"
               variant="tonal" 
               size="small"
               @click="openAddServicesDialog(res)"
             >
               <v-icon start>mdi-plus-circle-outline</v-icon>
               Szolgáltatások
             </v-btn>
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

    <v-dialog v-model="addServicesDialog.show" persistent max-width="600px">
      <v-card :loading="isLoadingServices || isSubmittingServices">
        <template v-slot:loader="{ isActive }">
           <v-progress-linear :active="isActive" color="secondary" height="4" indeterminate ></v-progress-linear>
        </template>

        <v-card-title>
          <span class="text-h5">Szolgáltatások hozzáadása</span>
          <div class="text-subtitle-1">Foglalás #{{ addServicesDialog.reservation?.id }}</div>
        </v-card-title>

        <v-card-text>
          <v-alert v-if="errorServices" type="error" density="compact" class="mb-3" variant="tonal">
            Hiba a szolgáltatások betöltésekor: {{ errorServices }}
          </v-alert>
          <v-alert v-if="!isLoadingServices && availableServices.length === 0 && !errorServices" type="info" density="compact" variant="tonal">
            Nincsenek elérhető extra szolgáltatások.
          </v-alert>

          <v-list lines="two" select-strategy="classic" v-if="availableServices.length > 0">
            <v-list-subheader>Választható szolgáltatások:</v-list-subheader>
             <v-list-item
                v-for="service in availableServices"
                :key="service.id"
                :value="service.id"
                @click="toggleServiceSelection(service.id)"
              >
                <template v-slot:prepend="{ isSelected }">
                    <v-list-item-action start>
                        <v-checkbox-btn :model-value="isSelected"></v-checkbox-btn>
                    </v-list-item-action>
                </template>

                <v-list-item-title>{{ service.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ service.description }}</v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip label size="small">{{ service.price.toLocaleString('hu-HU') }} Ft</v-chip>
                </template>
             </v-list-item>
          </v-list>
          <small v-else-if="!isLoadingServices && !errorServices">Nincsenek elérhető szolgáltatások.</small>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" variant="text" @click="closeAddServicesDialog" :disabled="isSubmittingServices">Mégse</v-btn>
          <v-btn
            color="secondary"
            variant="elevated"
            @click="submitAddServices"
            :loading="isSubmittingServices"
            :disabled="isLoadingServices || selectedServiceIds.length === 0"
          >
            Kiválasztottak Hozzáadása
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout" location="top right">
      {{ snackbar.message }}
    </v-snackbar>

  </v-container>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import reservationService from '@/services/reservationService';
import serviceService from '@/services/serviceService'; // Importáljuk az új service-t

// Meglévő Ref-ek és State
const reservations = ref([]);
const isLoading = ref(false); // Foglalások betöltése
const error = ref(null);     // Foglalások betöltési hiba

// Meglévő Lemondás Dialógus állapota
const cancelDialog = reactive({
    show: false,
    loading: false,
    error: null,
    reservation: null,
});

// --- Új Refs a Szolgáltatás Hozzáadáshoz ---
const availableServices = ref([]);       // Összes elérhető szolgáltatás
const isLoadingServices = ref(false);    // Szolgáltatások betöltése
const errorServices = ref(null);         // Szolgáltatások betöltési hiba
const addServicesDialog = reactive({     // Dialógus állapota
  show: false,
  reservation: null,
});
const selectedServiceIds = ref([]);      // Kiválasztott szolgáltatások ID-jai
const isSubmittingServices = ref(false); // Mentés folyamatban
// --- /Új Refs ---

// Snackbar visszajelzéshez
const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 3000
});

// ---- Meglévő Segédfüggvények ----
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
// ---- /Meglévő Segédfüggvények ----

// Snackbar megjelenítése
const showSnackbar = (message, color = 'success') => {
  snackbar.value.message = message;
  snackbar.value.color = color;
  snackbar.value.show = true;
};

// --- Meglévő Lemondás Logika ---
const canCancel = (statusEnumString) => {
    const statusKey = statusEnumString?.includes('.') ? statusEnumString.split('.')[1] : statusEnumString;
    return ['Depending', 'Success'].includes(statusKey);
};

const confirmCancel = (reservation) => {
      console.log("confirmCancel called with reservation:", JSON.stringify(reservation));
      if (!reservation || typeof reservation.id === 'undefined') {
          console.error("confirmCancel received invalid reservation object!");
          return;
      }
      cancelDialog.reservation = reservation;
      cancelDialog.error = null;
      cancelDialog.loading = false;
      cancelDialog.show = true;
      console.log("cancelDialog state after confirmCancel:", JSON.stringify(cancelDialog));
};

const executeCancel = async () => {
    console.log("executeCancel: Function called.");
    const reservationId = cancelDialog.reservation?.id;
    console.log("executeCancel: Reservation ID:", reservationId);
    if (!reservationId) {
        console.error("executeCancel: No reservation ID found in dialog state.");
        cancelDialog.error = "Hiba: Nincs kiválasztva foglalás a lemondáshoz.";
        return;
    }
    cancelDialog.loading = true;
    cancelDialog.error = null;
    console.log(`executeCancel: Set loading=true for ID: ${reservationId}. Making API call...`);

    try {
        const response = await reservationService.cancelReservation(reservationId);
        console.log("executeCancel: API call successful:", response);
        cancelDialog.show = false; // Dialógus bezárása
        showSnackbar(response.data.message || 'Foglalás sikeresen lemondva.', 'success'); // Snackbar hozzáadva
        console.log("executeCancel: Re-fetching reservations after cancellation...");
        await fetchReservations(); // Lista frissítése
        console.log("executeCancel: Reservations re-fetched.");
    } catch (err) {
        console.error("executeCancel: API call failed:", err.response || err);
        cancelDialog.error = err.response?.data?.message || 'Hiba történt a lemondás során.';
        showSnackbar(cancelDialog.error, 'error'); // Snackbar hiba esetén is
    } finally {
        console.log("executeCancel: Setting loading=false.");
        cancelDialog.loading = false;
    }
};
// --- /Meglévő Lemondás Logika ---

// --- ÚJ: Szolgáltatásokkal kapcsolatos metódusok ---
const fetchAvailableServices = async () => {
  // Csak akkor töltjük be, ha még nem történt meg, vagy hiba volt
  if (availableServices.value.length > 0 || isLoadingServices.value) {
      return;
  }
  isLoadingServices.value = true;
  errorServices.value = null;
  console.log("[Services] Fetching available services...");
  try {
    const response = await serviceService.getAllServices();
    availableServices.value = response.data || []; // Biztosítjuk, hogy tömb legyen
    console.log("[Services] Available services loaded:", availableServices.value);
  } catch (err) {
    errorServices.value = err.response?.data?.message || err.message || 'Hiba a szolgáltatások betöltésekor.';
    console.error("[Services] Error fetching available services:", err);
    availableServices.value = []; // Hiba esetén üres lista
  } finally {
    isLoadingServices.value = false;
  }
};

const canAddServices = (statusEnumString) => {
  const statusKey = statusEnumString?.includes('.') ? statusEnumString.split('.')[1] : statusEnumString;
  return ['Success', 'CheckedIn'].includes(statusKey);
};

const openAddServicesDialog = (reservation) => {
  console.log("[Services] Opening Add Services dialog for reservation:", reservation.id);
  addServicesDialog.reservation = reservation;
  selectedServiceIds.value = []; // Kiválasztás törlése
  // TODO: Meglévő szolgáltatások előválasztása (ha a backend visszaadja)
  addServicesDialog.show = true;
  fetchAvailableServices(); // Dialógus megnyitásakor (újra)lekérjük
};

const closeAddServicesDialog = () => {
  addServicesDialog.show = false;
  // Ne nullázzuk a reservation-t, mert a submit még használhatja
  // addServicesDialog.reservation = null;
  selectedServiceIds.value = [];
};

const toggleServiceSelection = (serviceId) => {
    const index = selectedServiceIds.value.indexOf(serviceId);
    if (index === -1) {
        selectedServiceIds.value.push(serviceId);
    } else {
        selectedServiceIds.value.splice(index, 1);
    }
    console.log("[Services] Selected IDs:", selectedServiceIds.value);
};


const submitAddServices = async () => {
  if (!addServicesDialog.reservation || !addServicesDialog.reservation.id) {
     showSnackbar('Hiba: Nem azonosítható a foglalás.', 'error');
     console.error("[Services] Cannot submit, reservation ID missing in dialog state.");
     return;
  }
   if (selectedServiceIds.value.length === 0) {
    showSnackbar('Nincs szolgáltatás kiválasztva.', 'warning');
    return;
  }

  isSubmittingServices.value = true;
  const reservationId = addServicesDialog.reservation.id;
  const serviceIdsToAdd = [...selectedServiceIds.value]; // Másolat készítése

  console.log(`[Services] Submitting services for Res ID ${reservationId}:`, serviceIdsToAdd);

  try {
    const response = await reservationService.addServicesToMyReservation(reservationId, serviceIdsToAdd);
    console.log("[Services] API response after adding services:", response.data);
    showSnackbar('Szolgáltatások sikeresen hozzáadva!', 'success');
    closeAddServicesDialog();
    // Frissítjük a foglalásokat, hogy az esetlegesen frissült számlaadatok megjelenjenek
    // (Bár a backend válasza itt az Invoice, nem a foglalás)
    // Ideálisabb lenne csak az adott foglalás adatait frissíteni, ha lehetséges.
    await fetchReservations();
  } catch (err) {
    const errorMessage = err.response?.data?.message || err.message || 'Hiba történt a szolgáltatások hozzáadásakor.';
    showSnackbar(errorMessage, 'error');
    console.error("[Services] Error submitting services:", err);
  } finally {
    isSubmittingServices.value = false;
  }
};
// --- /ÚJ: Szolgáltatásokkal kapcsolatos metódusok ---


// --- Foglalások lekérése ---
const fetchReservations = async () => {
  isLoading.value = true;
  error.value = null;
  console.log("[Reservations] Fetching reservations...");
  try {
    const response = await reservationService.getMyReservations();
    reservations.value = response.data || []; // Biztosítjuk, hogy tömb legyen
    console.log("[Reservations] Reservations fetched:", reservations.value);
  } catch (err) {
    console.error("[Reservations] Failed to fetch reservations:", err.response?.data || err.message);
    error.value = 'Hiba történt a foglalások lekérése közben.';
    reservations.value = [];
    if (err.response?.status === 401) {
      error.value += ' (Lejárt munkamenet?). Próbáljon újra bejelentkezni.';
    }
  } finally {
    isLoading.value = false;
  }
};
// --- /Foglalások lekérése ---

// Komponens betöltődésekor
onMounted(fetchReservations); // Csak a foglalásokat töltjük be alapból

</script>

<style scoped>
/* Meglévő és új stílusok */
.reservations-container { max-width: 1200px; margin: 20px auto; padding: 20px; }
h1 { text-align: center; margin-bottom: 30px; }
.loading, .error { text-align: center; font-size: 1.2em; padding: 20px; }
.error { color: red; }
.no-reservations { text-align: center; padding: 20px; }

.v-chip--label { font-size: 0.8em; height: 22px; font-weight: 500; }

.reservation-card { transition: box-shadow 0.3s ease-in-out; border: 1px solid #e0e0e0; } /* Finomított keret */
.reservation-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.reservation-card p { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; } /* Alsó margó a p elemeknek */
.reservation-card p .v-icon { color: rgba(0, 0, 0, 0.6); }
.v-card-actions { padding-top: 0; } /* Csökkentett padding a gombok felett */

/* Dialógus stílusok (opcionális) */
.v-list-item-title { font-weight: 500; }
.v-list-item-subtitle { font-size: 0.85em; color: rgba(0,0,0,0.7); }
.v-list-item { cursor: pointer; } /* Jelzi, hogy kattintható */
</style>