// src/services/reservationService.js
import apiClient from './apiClient';

// Meglévő függvények
const getMyReservations = () => {
  return apiClient.get('/reservation/reservations/mine');
};

const createReservation = (reservationData) => {
  return apiClient.post('/reservation/add', reservationData);
};

const cancelReservation = (reservationId) => {
  return apiClient.delete(`/reservation/cancel/${reservationId}`);
};

// --- ÚJ FÜGGVÉNY: Szolgáltatások hozzáadása saját foglaláshoz ---
/**
 * Szolgáltatásokat ad hozzá a bejelentkezett felhasználó saját foglalásához.
 * A backend POST /api/reservation/{reservationId}/services végpontját hívja.
 * @param {number|string} reservationId A cél foglalás azonosítója.
 * @param {number[]} serviceIds A hozzáadandó szolgáltatások azonosítóinak tömbje.
 * @returns {Promise<AxiosResponse<any>>} Az API válasz Promise-a. A data várhatóan a frissített InvoiceSummarySchema.
 */
const addServicesToMyReservation = (reservationId, serviceIds) => {
  // Az input data formátuma a backend AddServicesSchema alapján: { "service_ids": [1, 2, ...] }
  const payload = {
    service_ids: serviceIds
  };
  // Az interceptor automatikusan hozzáadja a tokent.
  return apiClient.post(`/reservation/${reservationId}/services`, payload);
};
// --- /ÚJ FÜGGVÉNY VÉGE ---

export default {
  getMyReservations,
  createReservation,
  cancelReservation,
  addServicesToMyReservation, // <<< Exportáld az új függvényt is
};