// src/services/serviceService.js
import apiClient from './apiClient';

/**
 * Lekéri az összes elérhető (nem törölt) szolgáltatást.
 * A backend /api/service/list végpontját hívja.
 * @returns {Promise<AxiosResponse<any>>} Az API válasz Promise-a. A data várhatóan egy tömb, ServiceListSchema objektumokkal.
 */
const getAllServices = () => {
  // Az interceptor automatikusan kezeli a tokent, bár ehhez a végponthoz lehet, hogy nem is kell.
  // A backend service/routes.py @bp.get("/list") végpontja nem igényel @jwt_required()-ot alapból.
  return apiClient.get('/service/list');
};

export default {
  getAllServices,
};