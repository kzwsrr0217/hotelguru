// src/stores/auth.js
import { defineStore } from 'pinia';
import apiClient from '@/services/apiClient';
import router from '@/router';

// Helper function to decode JWT (basic implementation, use a library like jwt-decode in production)
// WARNING: This does NOT validate the token signature! Validation happens on the backend.
function decodeToken(token) {
  try {
    if (!token) return null;
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
}


export const useAuthStore = defineStore('auth', {
  state: () => {
    // Próbáljuk meg betölteni a tokent és a usert a localStorage-ból induláskor
    const storedTokens = localStorage.getItem('userTokens');
    let accessToken = null;
    let refreshToken = null;
    let roles = [];
    let user = null; // Tartalmazhatja pl. { id: ..., name: ..., email: ... }

    if (storedTokens) {
      try {
        const tokenData = JSON.parse(storedTokens);
        accessToken = tokenData.access_token;
        refreshToken = tokenData.refresh_token;

        // Próbáljuk dekódolni a tokent a szerepkörökért és ID-ért
        const payload = decodeToken(accessToken);
        if (payload) {
           roles = payload.roles || [];
           // Itt betehetnénk több adatot is a payload-ból, ha a backend beleteszi
           // De a teljes user adatért jobb lenne egy /user/me hívás
           user = { id: payload.sub }; // 'sub' (subject) általában a user ID
        }

      } catch (e) {
        console.error("Error initializing auth state from localStorage", e);
        localStorage.removeItem('userTokens'); // Töröljük a hibás adatot
      }
    }

    return {
      accessToken: accessToken,
      refreshToken: refreshToken,
      user: user, // Felhasználó adatai (kezdetben null vagy localStorage-ból)
      roles: roles, // Szerepkörök (kezdetben üres vagy localStorage-ból)
      loginError: null,
      registerError: null,
      isLoading: false,
    };
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUserRoles: (state) => state.roles,
    getUserId: (state) => state.user?.id,
    // Opcionális: ellenőrzés specifikus szerepkörre
    hasRole: (state) => (roleName) => state.roles.includes(roleName),
  },
  actions: {
    async login(credentials) {
      this.isLoading = true;
      this.loginError = null;
      try {
        const response = await apiClient.post('/user/login', credentials);
        const { access_token, refresh_token } = response.data;

        this.accessToken = access_token;
        this.refreshToken = refresh_token;

        localStorage.setItem('userTokens', JSON.stringify({ access_token, refresh_token }));

        // Dekódoljuk a tokent az adatokért (ID, roles)
        const payload = decodeToken(access_token);
        if (payload) {
          this.user = { id: payload.sub /* ...több adat... */ };
          this.roles = payload.roles || [];
          console.log("User roles after login:", this.roles); // Debug log
        } else {
           console.error("Could not decode token after login.");
           this.logout(); // Hiba esetén kijelentkeztetés
           return; // Ne menjünk tovább
        }

        // Ideális esetben itt lenne egy this.fetchUserData() hívás, ami
        // egy /user/me végpontról kérné le a teljes user objektumot.

        router.push({ name: 'dashboard' }); // Vagy a felhasználó dashboardjára

      } catch (error) {
        console.error("Login failed:", error.response?.data || error.message);
        this.loginError = error.response?.data?.message || 'Bejelentkezési hiba történt.';
        this.clearAuthData(); // Hiba esetén töröljük az adatokat
      } finally {
        this.isLoading = false;
      }
    },

    logout() {
       this.clearAuthData();
       router.push('/login'); // Irányítsd át a login oldalra
    },

    // Segédfüggvény az adatok törlésére
    clearAuthData() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.roles = [];
      this.loginError = null;
      this.registerError = null;
      localStorage.removeItem('userTokens');
    },

    async register(userData) {
      // TODO: Implement registration logic
      // Hasonlóan a loginhoz, de a '/user/registrate' végpontot hívja
      // Sikeres regisztráció után pl. átirányítás a login oldalra
       this.isLoading = true;
       this.registerError = null;
       try {
           const response = await apiClient.post('/user/registrate', userData);
           console.log("Registration successful:", response.data);
           // Opcionális: Automatikus bejelentkeztetés regisztráció után?
           // Vagy csak átirányítás a loginra:
           router.push({ name: 'login', query: { registered: 'success' } });
       } catch (error) {
           console.error("Registration failed:", error.response?.data || error.message);
           // Backend specifikus hibaüzenet keresése
           if (error.response?.data?.message) {
               this.registerError = error.response.data.message;
           } else if (error.response?.data?.detail?.json) { // APIFlask validation error?
              // Próbáljuk meg szebben megformázni a validációs hibákat
              try {
                  const validationErrors = error.response.data.detail.json;
                  this.registerError = Object.entries(validationErrors)
                      .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
                      .join('; ');
              } catch {
                   this.registerError = 'Regisztrációs hiba (érvénytelen adatok).';
              }
           }
           else {
               this.registerError = 'Ismeretlen regisztrációs hiba történt.';
           }
       } finally {
           this.isLoading = false;
       }
    },

    // --- Token Frissítés Helye (Később!) ---
    // async refreshTokenAction() { ... }

  },
});