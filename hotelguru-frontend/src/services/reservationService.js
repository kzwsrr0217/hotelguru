// src/services/reservationService.js
import apiClient from './apiClient';

// Meglévő függvény a saját foglalások lekéréséhez
const getMyReservations = () => {
  return apiClient.get('/reservation/reservations/mine');
};

// <<< ÚJ FÜGGVÉNY FOGLALÁS LÉTREHOZÁSÁHOZ >>>
const createReservation = (reservationData) => {
  // reservationData objektum várható formátuma:
  // { start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD", room_numbers: [101] }
  // A backend végpontja: POST /api/reservation/add
  // Az interceptor automatikusan hozzáadja a tokent
  return apiClient.post('/reservation/add', reservationData);
};
// <<< ÚJ FÜGGVÉNY VÉGE >>>
const cancelReservation = (reservationId) => {
  // A backend végpontja: DELETE /api/reservation/cancel/{reservation_id}
  // Az interceptor automatikusan hozzáadja a tokent
  return apiClient.delete(`/reservation/cancel/${reservationId}`);
};
export default {
  getMyReservations,
  createReservation,
  cancelReservation, // <<< Exportáld az új függvényt is
};