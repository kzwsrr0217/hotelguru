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
    let user = null; // Csak alapvető adatok a tokenből (pl. ID)
    let userProfile = null; // Teljes profiladatok itt lesznek tárolva

    if (storedTokens) {
      try {
        const tokenData = JSON.parse(storedTokens);
        accessToken = tokenData.access_token;
        refreshToken = tokenData.refresh_token;

        // Próbáljuk dekódolni a tokent a szerepkörökért és ID-ért
        const payload = decodeToken(accessToken);
        if (payload) {
           roles = payload.roles || [];
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
      user: user, // Alap user adatok (pl. ID)
      userProfile: userProfile, // Teljes profiladatok (kezdetben null)
      roles: roles, // Szerepkörök (kezdetben üres vagy localStorage-ból)
      loginError: null,
      registerError: null,
      isLoading: false,
      profileUpdateError: null, // Hiba tárolása frissítéskor
    };
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUserRoles: (state) => state.roles,
    getUserId: (state) => state.user?.id, // A user ID-t a 'user' objektumból vesszük
    // Opcionális: ellenőrzés specifikus szerepkörre
    hasRole: (state) => (roleName) => state.roles.includes(roleName),
    // Opcionális getter a teljes profilhoz
    // getUserProfileData: (state) => state.userProfile, // Használhatjuk ezt a komponensben
  },
  actions: { // <<< --- ACTIONS BLOKK KEZDETE --- >>>
    async login(credentials) {
      this.isLoading = true;
      this.loginError = null;
      this.userProfile = null; // Profil törlése új login előtt
      try {
        const response = await apiClient.post('/user/login', credentials);
        const { access_token, refresh_token } = response.data;

        this.accessToken = access_token;
        this.refreshToken = refresh_token;
        localStorage.setItem('userTokens', JSON.stringify({ access_token, refresh_token }));

        const payload = decodeToken(access_token);
        if (payload) {
          // A `user` state-et az ID-val és a szerepkörökkel frissítjük
          this.user = { id: payload.sub };
          this.roles = payload.roles || [];
          console.log("[AuthStore] User roles after login:", this.roles);

          // Most, hogy van tokenünk és user ID-nk, lekérjük a teljes profilt
          await this.fetchUserProfile(); // <<< PROFIL BETÖLTÉSE LOGIN UTÁN
        } else {
           console.error("[AuthStore] Could not decode token after login.");
           this.logout();
           return;
        }
        router.push({ name: 'dashboard' }); // Vagy a felhasználó dashboardjára
      } catch (error) {
        console.error("[AuthStore] Login failed:", error.response?.data || error.message);
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
      this.userProfile = null; // <<< Profilt is töröljük kijelentkezéskor
      this.roles = [];
      this.loginError = null;
      this.registerError = null;
      this.profileUpdateError = null; // <<< Ezt is töröljük
      localStorage.removeItem('userTokens');
    },

    async register(userData) {
       this.isLoading = true;
       this.registerError = null;
       try {
           const response = await apiClient.post('/user/registrate', userData);
           console.log("[AuthStore] Registration successful:", response.data);
           // Opcionális: Automatikus bejelentkeztetés regisztráció után?
           // Vagy csak átirányítás a loginra:
           router.push({ name: 'login', query: { registered: 'success' } });
       } catch (error) {
           console.error("[AuthStore] Registration failed:", error.response?.data || error.message);
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

    // --- PROFIL ADATOK LEKÉRÉSE ---
    async fetchUserProfile() {
      // Csak akkor fussunk le, ha van user ID (tehát a tokenből kiolvastuk) és van token
      if (!this.user?.id || !this.accessToken) {
        console.warn("[AuthStore] Cannot fetch profile: User ID or access token not available.");
        this.userProfile = null; // Töröljük a profilt, ha nincs ID vagy token
        return;
      }

      // Ha már be van töltve az aktuális userhez a profil, ne hívjuk újra feleslegesen
      // (Ez opcionális optimalizálás, főleg ha a profil oldal direktben is hívja)
      // if (this.userProfile && this.userProfile.id === this.user.id) {
      //     console.log("[AuthStore] User profile already loaded for current user. Skipping fetch.");
      //     return;
      // }

      this.isLoading = true; // Jelezhetjük a betöltést
      this.profileUpdateError = null; // Hiba törlése új kérés előtt
      try {
        console.log("[AuthStore] Fetching user profile from /user/me...");
        // A backend user/routes.py-ben létrehozott /me végpontot hívjuk
        const response = await apiClient.get('/user/me'); // Hívás a /me végpontra
        this.userProfile = response.data; // Feltéve, hogy a válasz UserResponseSchema
        console.log("[AuthStore] User profile fetched successfully:", this.userProfile);

        // Frissítjük az alap 'user' state-et is, ha a userProfile több információt tartalmaz
        // Ez akkor hasznos, ha a `user` state-et használod pl. a név kiírására a nav bar-ban
        if (this.userProfile && this.user) {
            this.user.name = this.userProfile.name || this.user.name; // Feltéve, hogy a név is jön
            this.user.email = this.userProfile.email || this.user.email;
        }
      } catch (error) {
        console.error("[AuthStore] Failed to fetch user profile from /user/me:", error.response?.data || error.message);
        this.profileUpdateError = error.response?.data?.message || "Profiladatok lekérése sikertelen.";
        this.userProfile = null; // Hiba esetén töröljük
      } finally {
        this.isLoading = false;
      }
    },

    // --- PROFIL FRISSÍTÉSE ---
    async updateUserProfile(userId, data) {
      // A `userId` paraméter itt a path paraméterhez kell, de a jogosultságot a backend kezeli
      if (!this.user?.id || this.user.id !== userId) {
          console.warn("[AuthStore] User ID mismatch or not logged in for profile update. Update relies on backend authorization.");
          // Hiba dobása itt megakadályozná a próbálkozást, de a backendnek kell ezt levédenie
          // throw new Error("Jogosultsági hiba a profil frissítésekor.");
      }

      this.isLoading = true;
      this.profileUpdateError = null;
      try {
        console.log(`[AuthStore] Updating profile for user ${userId} with data:`, JSON.parse(JSON.stringify(data)));
        // A backend user/routes.py-ban lévő PUT /user/update/{uid} végpontot hívjuk
        const response = await apiClient.put(`/user/update/${userId}`, data);
        console.log("[AuthStore] Profile update API response:", response.data);

        if (response.data) {
          // Frissítjük a userProfile state-et a visszakapott (frissített) adatokkal
          this.userProfile = { ...this.userProfile, ...response.data };
          // Frissíthetjük az alap user state-et is, ha kell
          if (this.user && response.data.email) {
              this.user.email = response.data.email;
          }
          if (this.user && response.data.name) { // Ha a név is visszajön
              this.user.name = response.data.name;
          }
          console.log("[AuthStore] Local userProfile state updated:", this.userProfile);
        }
        return response.data; // Visszaadjuk a választ a komponensnek (pl. további frissítéshez)
      } catch (error) {
        console.error("[AuthStore] Profile update API call failed:", error.response?.data || error.message);
        this.profileUpdateError = error.response?.data?.message || 'Profil frissítése sikertelen.';
        throw error; // Dobjuk tovább a hibát, hogy a komponens is elkapja és kezelhesse (pl. snackbar)
      } finally {
        this.isLoading = false;
      }
    },
    // --- /ÚJ ACTION VÉGE ---

    // --- Token Frissítés Helye (Később!) ---
    // async refreshTokenAction() { ... }

  } // <<< --- ACTIONS BLOKK VÉGE --- >>>
});