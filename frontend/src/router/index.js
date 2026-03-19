import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: () => import('../views/ProductDetailView.vue')
    },
    {
      path: '/cart',
      name: 'cart',
      component: () => import('../views/CartView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 1. Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.token) {
    // If it's an admin route, redirect to admin login
    if (to.meta.requiresAdmin) {
        next({ name: 'admin-login', query: { redirect: to.fullPath } })
    } else {
        next({ name: 'login', query: { redirect: to.fullPath } })
    }
  } 
  // 2. Check if route requires admin privileges
  else if (to.meta.requiresAdmin && (!authStore.user || !authStore.user.is_staff)) {
      // Redirect non-admin users trying to access admin pages
      next({ name: 'home' })
  }
  // 3. Special case for /admin root path if already logged in as admin
  else if (to.path === '/admin' && authStore.user && authStore.user.is_staff) {
      next({ name: 'admin-products' })
  }
  else {
    next()
  }
})

export default router