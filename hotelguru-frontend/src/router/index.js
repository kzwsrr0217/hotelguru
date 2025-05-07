// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';     
import RegisterView from '../views/RegisterView.vue'; 
import DashboardView from '../views/DashboardView.vue';
import RoomsView from '../views/RoomsView.vue'; 
import MyReservationsView from '../views/MyReservationsView.vue'; 
import AdminView from '../views/admin/AdminView.vue'; 
import AccessDeniedView from '../views/AccessDeniedView.vue'; 
import AdminRoomsView from '../views/admin/AdminRoomsView.vue'; // <<< Új import
import UserProfileView from '../views/UserProfileView.vue'; // <<< ÚJ IMPORT



import { useAuthStore } from '@/stores/auth';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') },
    { // <<< Új védett útvonal
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true } // Jelöljük, hogy ehhez bejelentkezés kell
    },
    { // <<< Új útvonal a szobákhoz
      path: '/rooms',
      name: 'rooms',
      component: RoomsView,
    },
    {
      path: '/my-reservations', // <<< Új útvonal
      name: 'my-reservations',
      component: MyReservationsView,
      meta: { requiresAuth: true } // Csak bejelentkezve érhető el
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true } // Bármely bejelentkezett user eléri
    },
    {
      path: '/my-reservations',
      name: 'my-reservations',
      component: MyReservationsView,
      meta: { requiresAuth: true } // Bármely bejelentkezett user eléri (Guest is)
    },
    {
      // <<< Módosítjuk az /admin útvonalat vagy létrehozunk egy újat (/admin/rooms) >>>
      // Most módosítsuk a meglévőt:
      path: '/admin/rooms', // <<< Legyen ez az útvonal
      name: 'admin-rooms', // <<< Név is legyen specifikusabb
      component: AdminRoomsView, // <<< Az új komponensre mutat
      meta: {
        requiresAuth: true,
        roles: ['Administrator'] // Csak Adminisztrátor!
      }
    },
    { // <<< Új Access Denied útvonal
        path: '/access-denied',
        name: 'access-denied',
        component: AccessDeniedView,
    },
    {
      path: '/profile', // Vagy '/user/profile'
      name: 'user-profile',
      component: UserProfileView,
      meta: { requiresAuth: true } // Bejelentkezés szükséges
    }
    // --- Később ide jöhetnek a többi védett útvonal ---
    // Pl.:
    // {
    //   path: '/my-reservations',
    //   name: 'my-reservations',
    //   component: () => import('../views/MyReservationsView.vue'),
    //   meta: { requiresAuth: true, roles: ['Guest'] } // Szerepkör ellenőrzés is lehet
    // },
    // {
    //   path: '/admin/rooms',
    //   name: 'admin-rooms',
    //   component: () => import('../views/admin/AdminRoomsView.vue'),
    //   meta: { requiresAuth: true, roles: ['Administrator'] } // Csak Admin
    // },
  ],
});

// --- Navigációs Gárda Implementálása ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const userRoles = authStore.getUserRoles; // Felhasználó szerepköreinek lekérése

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  // Összegyűjtjük az összes szükséges szerepkört az útvonal hierarchiából
  const requiredRoles = to.matched.flatMap(record => record.meta.roles || []);

  // Ellenőrizzük, hogy a user rendelkezik-e legalább EGY szükséges szerepkörrel
  // Csak akkor releváns, ha vannak megadva szükséges szerepkörök
  const hasRequiredRole = requiredRoles.length === 0 || requiredRoles.some(role => userRoles.includes(role));

  console.log(`Navigating to ${to.path}. Requires Auth: ${requiresAuth}. Is Auth: ${isAuthenticated}. Required Roles: ${requiredRoles}. User Roles: ${userRoles}. Has Role: ${hasRequiredRole}`); // Debug log

  if (requiresAuth && !isAuthenticated) {
    // Ha védett és nincs bejelentkezve -> Login
    console.log(`Guard: Redirecting to login (auth required).`);
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else if (requiresAuth && isAuthenticated && !hasRequiredRole) {
    // Ha védett, be van jelentkezve, de NINCS meg a szükséges szerepköre -> Access Denied
    console.log(`Guard: Redirecting to access-denied (missing roles).`);
    next({ name: 'access-denied' });
  }
  else {
    // Minden más esetben (nem védett, vagy be van jelentkezve és van joga) -> Továbbengedjük
    next();
  }
});
// --- Gárda Vége ---

export default router;