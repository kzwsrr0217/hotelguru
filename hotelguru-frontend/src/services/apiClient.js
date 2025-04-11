import axios from 'axios';
import { useAuthStore } from '@/stores/auth'; // Importáljuk az auth store-t IDE is!


const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // Beolvassa a .env fájlból
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Axios Interceptor a Token Hozzáadásához (KÉSŐBB AKTIVÁLJUK) ---
// Ez a rész minden kérés elé beilleszti az Authorization fejlécet,
// miután a felhasználó bejelentkezett és van tokenünk.
// Most még kikommentelve hagyjuk, amíg nincs login logika.

apiClient.interceptors.request.use(
  (config) => {
    console.log('[Interceptor] Running for request to:', config.url); // <<< DEBUG LOG
    let token = null;
    const tokenDataString = localStorage.getItem('userTokens');
    console.log('[Interceptor] Raw data from localStorage:', tokenDataString); // <<< DEBUG LOG

    if (tokenDataString) {
      try {
        const tokenData = JSON.parse(tokenDataString);
        console.log('[Interceptor] Parsed token data:', tokenData); // <<< DEBUG LOG
        token = tokenData?.access_token;
        if (!token) {
          console.log('[Interceptor] access_token not found in parsed data.'); // <<< DEBUG LOG
        }
      } catch (e) {
        console.error("[Interceptor] Error parsing token data from localStorage", e);
        localStorage.removeItem('userTokens'); // Hibás adat törlése
      }
    } else {
       console.log('[Interceptor] No "userTokens" found in localStorage.'); // <<< DEBUG LOG
    }

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log("[Interceptor] Attached token to headers."); // <<< DEBUG LOG
    } else {
      console.log("[Interceptor] No token found to attach."); // <<< DEBUG LOG
    }

    return config; // <<< Fontos, hogy a config objektumot visszaadjuk!
  },
  (error) => {
    console.error('[Interceptor] Error in request interceptor setup:', error); // <<< DEBUG LOG
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------

export default apiClient;