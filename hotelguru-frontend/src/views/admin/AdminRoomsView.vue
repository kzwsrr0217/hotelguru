<template>
    <v-container>
      <div class="d-flex justify-space-between align-center mb-4 flex-wrap ga-2">
          <h1 class="text-h4">Szobakezelés (Admin)</h1>
          <v-btn color="primary" @click="openAddDialog">
              <v-icon start>mdi-plus-box-outline</v-icon>
              Új Szoba Hozzáadása
          </v-btn>
      </div>
  
      <v-row v-if="isLoading" justify="center" class="my-10">
          <v-col cols="auto">
              <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
              <p class="text-center mt-2">Adatok betöltése...</p>
          </v-col>
      </v-row>
      <v-row v-else-if="error" justify="center">
          <v-col cols="12" md="8">
               <v-alert type="error" density="compact" variant="tonal">
                   {{ error }}
               </v-alert>
          </v-col>
      </v-row>
  
      <v-data-table
        v-else
        :headers="tableHeaders"
        :items="rooms"
        item-value="id"
        class="elevation-1"
        :loading="isLoading"
        loading-text="Adatok betöltése..."
        no-data-text="Nincsenek szobák a rendszerben."
        density="compact"
      >
        <template v-slot:[`item.price`]="{ item }">
          {{ formatPrice(item.price) }}
        </template>
  
         <template v-slot:[`item.is_available`]="{ item }">
           <v-chip :color="item.is_available ? 'green' : 'red'" dark size="small" label density="comfortable">
              {{ item.is_available ? 'Igen' : 'Nem' }}
           </v-chip>
         </template>
  
          <template v-slot:[`item.actions`]="{ item }">
           <v-tooltip location="top" text="Szerkesztés">
              <template v-slot:activator="{ props }">
                   <v-icon v-bind="props" size="small" class="mr-2" @click="editRoom(item)" color="blue">mdi-pencil</v-icon>
              </template>
           </v-tooltip>
           <v-tooltip location="top" text="Törlés">
               <template v-slot:activator="{ props }">
                   <v-icon v-bind="props" size="small" @click="confirmDeleteRoom(item)" color="red">mdi-delete</v-icon>
               </template>
           </v-tooltip>
         </template>
  
      </v-data-table>
  
      <v-dialog v-model="editDialog.show" persistent max-width="600px">
        <v-card>
          <v-card-title>
            <span class="text-h5">Szoba Szerkesztése (Szobaszám: {{ editDialog.item.number }})</span>
          </v-card-title>
          <v-form v-model="editDialog.valid" @submit.prevent="saveEditedRoom">
              <v-card-text>
                <v-alert v-if="editDialog.error" type="error" density="compact" closable class="mb-4" variant="tonal">
                    {{ editDialog.error }}
                </v-alert>
                <v-container>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field
                        v-model="editDialog.item.name"
                        label="Név/Megnevezés"
                        variant="outlined"
                        density="compact"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12">
                       <v-textarea
                          v-model="editDialog.item.description"
                          label="Leírás"
                          variant="outlined"
                          density="compact"
                          rows="3"
                        ></v-textarea>
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model.number="editDialog.item.price"
                        label="Ár (Ft/éj)"
                        type="number"
                        step="100"
                        min="0"
                        required
                        :rules="[rules.required, rules.numeric, rules.nonNegative]"
                        variant="outlined"
                        density="compact"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6">
                       <v-switch
                           v-model="editDialog.item.is_available"
                           :label="editDialog.item.is_available ? 'Elérhető' : 'Nem elérhető'"
                           color="primary"
                           inset
                           hide-details
                        ></v-switch>
                    </v-col>
                     <v-col cols="12">
                        <v-text-field
                           v-model="editDialog.item.room_type_id"
                           label="Szoba Típus ID"
                           type="number"
                           required
                           :rules="[rules.required, rules.numeric]"
                           variant="outlined"
                           density="compact"
                           hint="Létező típus ID-ját add meg (pl. 1-4)"
                           persistent-hint
                         ></v-text-field>
                           {/* TODO: Később lecserélni v-select-re, ami lekéri a típusokat */}
                     </v-col>
                  </v-row>
                </v-container>
                 <small class="px-4">* Kötelező mező</small>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey darken-1" variant="text" @click="closeEditDialog" :disabled="editDialog.loading">
                  Mégse
                </v-btn>
                <v-btn color="primary" variant="elevated" type="submit" :loading="editDialog.loading" :disabled="editDialog.valid === false">
                  Mentés
                </v-btn>
              </v-card-actions>
          </v-form>
        </v-card>
      </v-dialog>
      <v-dialog v-model="deleteDialog.show" persistent max-width="450px">
          <v-card>
              <v-card-title class="text-h5 error--text">
                  <v-icon start color="error">mdi-delete-alert-outline</v-icon>
                  Szoba Törlése Megerősítés
              </v-card-title>
              <v-card-text>
                  Biztosan törölni szeretnéd a(z)
                  <strong>#{{ deleteDialog.item?.number }} - {{ deleteDialog.item?.name }}</strong>
                  szobát? Ez a művelet nem vonható vissza!
                  <v-expand-transition>
                     <v-alert v-if="deleteDialog.error" type="error" density="compact" class="mt-3" variant="tonal">
                      {{ deleteDialog.error }}
                     </v-alert>
                  </v-expand-transition>
              </v-card-text>
              <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="grey darken-1" variant="text" @click="closeDeleteDialog" :disabled="deleteDialog.loading">
                      Mégse
                  </v-btn>
                  <v-btn color="error" variant="elevated" :loading="deleteDialog.loading" @click="executeDeleteRoom">
                      Törlés
                  </v-btn>
              </v-card-actions>
          </v-card>
      </v-dialog>
      <v-dialog v-model="addDialog.show" persistent max-width="600px">
          <v-card>
          <v-card-title>
              <span class="text-h5">Új Szoba Létrehozása</span>
          </v-card-title>
          <v-form v-model="addDialog.valid" @submit.prevent="saveNewRoom">
              <v-card-text>
                  <v-alert v-if="addDialog.error" type="error" density="compact" closable class="mb-4" variant="tonal">
                      {{ addDialog.error }}
                  </v-alert>
                  <v-container>
                  <v-row>
                      <v-col cols="12" sm="6">
                      <v-text-field
                          v-model.number="addDialog.newItem.number"
                          label="Szobaszám*"
                          type="number"
                          required
                          :rules="[rules.required, rules.numeric]"
                          variant="outlined"
                          density="compact"
                      ></v-text-field>
                      </v-col>
                      <v-col cols="12" sm="6">
                          <v-text-field
                          v-model.number="addDialog.newItem.floor"
                          label="Emelet*"
                          type="number"
                          required
                          :rules="[rules.required, rules.numeric]"
                          variant="outlined"
                          density="compact"
                      ></v-text-field>
                      </v-col>
                      <v-col cols="12">
                      <v-text-field
                          v-model="addDialog.newItem.name"
                          label="Név/Megnevezés*"
                          required
                          :rules="[rules.required]"
                          variant="outlined"
                          density="compact"
                      ></v-text-field>
                      </v-col>
                      <v-col cols="12">
                          <v-textarea
                          v-model="addDialog.newItem.description"
                          label="Leírás (opcionális)"
                          variant="outlined"
                          density="compact"
                          rows="2"
                          ></v-textarea>
                      </v-col>
                      <v-col cols="12" sm="6">
                      <v-text-field
                          v-model.number="addDialog.newItem.price"
                          label="Ár (Ft/éj)*"
                          type="number"
                          step="100"
                          min="0"
                          required
                          :rules="[rules.required, rules.numeric, rules.nonNegative]"
                          variant="outlined"
                          density="compact"
                      ></v-text-field>
                      </v-col>
                      <v-col cols="12" sm="6">
                          <v-text-field
                              v-model.number="addDialog.newItem.room_type_id"
                              label="Szoba Típus ID*"
                              type="number"
                              required
                              :rules="[rules.required, rules.numeric]"
                              variant="outlined"
                              density="compact"
                              hint="Add meg a létező típus ID-ját (pl. 1-4)"
                              persistent-hint
                          ></v-text-field>
                          {/* TODO: Később v-select */}
                      </v-col>
                      <v-col cols="12">
                          <v-switch
                              v-model="addDialog.newItem.is_available"
                              :label="addDialog.newItem.is_available ? 'Elérhető' : 'Nem elérhető (pl. karbantartás)'"
                              color="primary"
                              inset
                              hide-details
                          ></v-switch>
                      </v-col>
                  </v-row>
                  </v-container>
                  <small class="px-4">* Kötelező mező</small>
              </v-card-text>
              <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="grey darken-1" variant="text" @click="closeAddDialog" :disabled="addDialog.loading">
                  Mégse
                  </v-btn>
                  <v-btn color="success" variant="elevated" type="submit" :loading="addDialog.loading" :disabled="addDialog.valid === false">
                  Hozzáadás
                  </v-btn>
              </v-card-actions>
          </v-form>
          </v-card>
      </v-dialog>
      {/* HOZZÁADÁS DIALÓGUS VÉGE */}
  
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted, reactive } from 'vue';
  import adminService from '@/services/adminService';
  
  const rooms = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  
  // Edit Dialog State
  const editDialog = reactive({
    show: false, loading: false, error: null, valid: null,
    item: { id: null, number: null, name: '', description: '', price: 0, is_available: true, room_type_id: null }
  });
  
  // Delete Dialog State
  const deleteDialog = reactive({
      show: false, loading: false, error: null, item: null
  });
  
  // Add Dialog State
  const defaultNewItem = () => ({
      number: null, floor: null, name: '', description: '', price: null, is_available: true, room_type_id: null
  });
  const addDialog = reactive({
    show: false, loading: false, error: null, valid: null, newItem: defaultNewItem()
  });
  
  // Table Headers
  const tableHeaders = [
    { title: 'Szobaszám', key: 'number', sortable: true }, { title: 'Név', key: 'name', sortable: true },
    { title: 'Típus', key: 'room_type.name', sortable: true }, { title: 'Ár', key: 'price', align: 'end', sortable: true },
    { title: 'Elérhető', key: 'is_available', align: 'center', sortable: true },
    { title: 'Akciók', key: 'actions', align: 'center', sortable: false },
  ];
  
  // Validation Rules
  const rules = {
    required: value => (value !== null && value !== undefined && value !== '') || 'Ez a mező kötelező.',
    numeric: value => /^\d+$/.test(value) || 'Csak számok adhatók meg.',
    nonNegative: value => (value !== null && value >= 0) || 'Az érték nem lehet negatív.',
  };
  
  // Formatter
  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return new Intl.NumberFormat('hu-HU', { style: 'currency', currency: 'HUF', maximumFractionDigits: 0 }).format(price);
  };
  
  // Fetch Logic
  const fetchAdminRooms = async () => {
    isLoading.value = true; error.value = null;
    try { const response = await adminService.getAllRoomsAdmin(); rooms.value = response.data; }
    catch (err) { console.error("Failed to fetch admin rooms:", err.response?.data || err.message); error.value = "Hiba történt a szobák lekérése közben."; }
    finally { isLoading.value = false; }
  };
  
  // Edit Logic
  const editRoom = (item) => {
    editDialog.item.id = item.id; editDialog.item.number = item.number; editDialog.item.name = item.name || '';
    editDialog.item.description = item.description || ''; editDialog.item.price = item.price === null || item.price === undefined ? 0 : item.price;
    editDialog.item.is_available = item.is_available; editDialog.item.room_type_id = item.room_type_id || item.room_type?.id || null;
    editDialog.error = null; editDialog.loading = false; editDialog.valid = null; editDialog.show = true;
  };
  const closeEditDialog = () => { editDialog.show = false; };
  const saveEditedRoom = async () => {
    // if (editDialog.valid === false) return; // Szigorúbb validációhoz
    editDialog.loading = true; editDialog.error = null;
    try {
      const dataToUpdate = { name: editDialog.item.name, description: editDialog.item.description,
        price: parseFloat(editDialog.item.price) || 0, is_available: editDialog.item.is_available,
        room_type_id: editDialog.item.room_type_id ? parseInt(editDialog.item.room_type_id) : null // Biztosítjuk, hogy int vagy null legyen
      };
      await adminService.updateRoomAdmin(editDialog.item.id, dataToUpdate);
      closeEditDialog(); await fetchAdminRooms(); alert('Szoba sikeresen frissítve!'); // TODO: Snackbar
    } catch (err) { console.error("Failed to update room:", err.response?.data || err.message); editDialog.error = err.response?.data?.message || "Hiba történt a mentés során."; }
    finally { editDialog.loading = false; }
  };
  
  // Delete Logic
  const confirmDeleteRoom = (item) => { deleteDialog.item = item; deleteDialog.error = null; deleteDialog.loading = false; deleteDialog.show = true; };
  const closeDeleteDialog = () => { deleteDialog.show = false; };
  const executeDeleteRoom = async () => {
      if (!deleteDialog.item || deleteDialog.item.id === null) return;
      deleteDialog.loading = true; deleteDialog.error = null;
      try { const roomId = deleteDialog.item.id; await adminService.deleteRoomAdmin(roomId); closeDeleteDialog(); await fetchAdminRooms(); alert('Szoba sikeresen törölve!'); // TODO: Snackbar
      } catch (err) { console.error("Failed to delete room:", err.response?.data || err.message); deleteDialog.error = err.response?.data?.message || "Hiba történt a törlés során."; }
      finally { deleteDialog.loading = false; }
  };
  
  // Add Logic
  const openAddDialog = () => { addDialog.newItem = defaultNewItem(); addDialog.error = null; addDialog.loading = false; addDialog.valid = null; addDialog.show = true; };
  const closeAddDialog = () => { addDialog.show = false; };
  const saveNewRoom = async () => {
      if (addDialog.valid === false) return; // Szigorúbb validációhoz
      addDialog.loading = true; addDialog.error = null;
      try {
          const dataToSend = { ...addDialog.newItem,
              number: parseInt(addDialog.newItem.number), floor: parseInt(addDialog.newItem.floor),
              price: parseFloat(addDialog.newItem.price), room_type_id: parseInt(addDialog.newItem.room_type_id)
          };
          // Ellenőrzés, hogy a konverziók sikeresek voltak-e (NaN, stb.) - Opcionális
          if (isNaN(dataToSend.number) || isNaN(dataToSend.floor) || isNaN(dataToSend.price) || isNaN(dataToSend.room_type_id)) {
              throw new Error("Érvénytelen szám formátum valamelyik mezőben.");
          }
          await adminService.addRoomAdmin(dataToSend);
          closeAddDialog(); await fetchAdminRooms(); alert('Szoba sikeresen hozzáadva!'); // TODO: Snackbar
      } catch (err) { console.error("Failed to add room:", err.response?.data || err.message); addDialog.error = err.response?.data?.message || "Hiba történt a hozzáadás során."; }
      finally { addDialog.loading = false; }
  };
  
  // Initial data fetch
  onMounted(fetchAdminRooms);
  </script>
  
  <style scoped>
  .v-data-table { margin-top: 20px; }
  .v-icon { cursor: pointer; }
  .v-alert { margin-bottom: 1rem; }
  /* Kis igazítás az ár validációs hibához */
  .v-input--error :deep(.v-input__details) { margin-bottom: -10px; }
  </style>