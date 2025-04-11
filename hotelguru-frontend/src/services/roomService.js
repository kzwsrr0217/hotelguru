// src/services/roomService.js
import apiClient from './apiClient';

// <<< MÓDOSÍTOTT FÜGGVÉNY KEZDETE >>>
// Lekéri az elérhető szobákat, opcionálisan dátumtartomány alapján szűrve
const findAvailableRooms = (params = {}) => {
  // params objektum lehet pl.: { start_date: 'YYYY-MM-DD', end_date: 'YYYY-MM-DD' }
  // Ha a params üres, akkor query string sem lesz

  // Ha vannak dátumok, az új végpontot hívjuk query paraméterekkel
  if (params.start_date && params.end_date) {
     console.log("Calling /room/rooms/available with params:", params);
    // A GET kérésnél a második argumentum egy objektum, aminek a 'params' kulcsa
    // tartalmazza a query paramétereket. Axios ezt átalakítja ?start_date=...&end_date=... formára.
    return apiClient.get('/room/rooms/available', { params: params });
  } else {
    // Ha nincsenek dátumok, a régi végpontot hívjuk (általánosan elérhető szobák)
     console.log("Calling /room/list/ (no date params)");
    return apiClient.get('/room/list/');
  }
};
// <<< MÓDOSÍTOTT FÜGGVÉNY VÉGE >>>


// Meglévő függvény szoba lekéréséhez szám alapján
const getRoomByNumber = (roomNumber) => {
    return apiClient.get(`/room/show/by-number/${roomNumber}`);
}

export default {
  findAvailableRooms, // <<< Exportáljuk az átnevezett/módosított függvényt
  getRoomByNumber,
};