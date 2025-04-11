// src/services/adminService.js
import apiClient from './apiClient';

// Összes szoba lekérése (admin nézet)
const getAllRoomsAdmin = () => {
  // A backend végpontja: GET /api/room/list_all_admin
  // Az interceptor küldi a tokent, a backend route pedig ellenőrzi az Admin szerepkört
  return apiClient.get('/room/list_all_admin');
};

// Szoba frissítése ID alapján
const updateRoomAdmin = (roomId, roomData) => {
  // A backend végpontja: PUT /api/admin/rooms/{roomId}
  // A roomData tartalmazza a frissítendő mezőket, pl.: { name: 'Új név', price: 18000, is_available: true }
  return apiClient.put(`/admin/rooms/${roomId}`, roomData);
};

// Szoba törlése ID alapján
const deleteRoomAdmin = (roomId) => {
  // A backend végpontja: DELETE /api/admin/rooms/{roomId}
  return apiClient.delete(`/admin/rooms/${roomId}`);
};
const addRoomAdmin = (newRoomData) => {
    // newRoomData objektumnak meg kell felelnie a backend RoomRequestSchema-jának
    // (number, floor, name, price, room_type_id, description?, is_available?)
    // Backend végpont: POST /api/admin/rooms
    return apiClient.post('/admin/rooms', newRoomData);
  };

export default {
    getAllRoomsAdmin,
    updateRoomAdmin,
    deleteRoomAdmin,
    addRoomAdmin, // <<< Export hozzáadva
  };

