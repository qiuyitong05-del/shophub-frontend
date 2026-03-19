<template>
  <el-container class="app-container">
    <el-header height="80px" class="header">
      <div class="header-content container">
        <!-- Logo -->
        <router-link to="/" class="logo">
            <span class="logo-text">
                <span class="logo-primary">LIVING</span><span class="logo-accent">SPACE</span>
            </span>
        </router-link>
        
        <div class="flex-grow" />
        
        <!-- Hamburger Button -->
        <button class="hamburger" @click="toggleMenu" aria-label="Toggle menu">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
        </button>

        <!-- Navigation -->
        <nav class="nav-links" :class="{ 'is-open': isMenuOpen }">
            <router-link to="/" class="nav-item" @click="closeMenu">Home</router-link>
            <router-link to="/about" class="nav-item" @click="closeMenu">About</router-link>
            
            <template v-if="authStore.token && !isStaff">
                <router-link to="/wishlist" class="nav-item icon-btn" @click="closeMenu">
                    <div class="nav-icon-wrapper">
                        <el-icon><Star /></el-icon>
                        <span class="hover-text">Wishlist</span>
                    </div>
                </router-link>
                <router-link to="/chat" class="nav-item icon-btn" @click="closeMenu">
                    <div class="nav-icon-wrapper">
                        <el-badge :value="chatStore.unreadCount" :hidden="chatStore.unreadCount === 0" is-dot class="badge">
                            <el-icon><Headset /></el-icon>
                        </el-badge>
                        <span class="hover-text">Support</span>
                    </div>
                </router-link>
                <router-link to="/cart" class="nav-item icon-btn" @click="closeMenu">
                    <div class="nav-icon-wrapper">
                        <el-badge :value="cartStore.itemCount" :hidden="cartStore.itemCount === 0" class="badge">
                            <el-icon><ShoppingCart /></el-icon>
                        </el-badge>
                        <span class="hover-text">Cart</span>
                    </div>
                </router-link>
                <router-link to="/orders" class="nav-item icon-btn" @click="closeMenu">
                    <div class="nav-icon-wrapper">
                        <el-icon><List /></el-icon>
                        <span class="hover-text">Orders</span>
                    </div>
                </router-link>
                <router-link to="/notifications" class="nav-item icon-btn" @click="closeMenu">
                    <div class="nav-icon-wrapper">
                        <el-badge :value="unreadCount" :hidden="unreadCount === 0" is-dot class="badge">
                            <el-icon><Bell /></el-icon>
                        </el-badge>
                        <span class="hover-text">Notifications</span>
                    </div>
                </router-link>
            </template>
            
            <template v-if="authStore.token && isStaff">
                <router-link to="/admin/products" class="nav-item" @click="closeMenu">Products</router-link>
                <router-link to="/admin/orders" class="nav-item" @click="closeMenu">Orders</router-link>
                <router-link to="/admin/reviews" class="nav-item" @click="closeMenu">Reviews</router-link>
                <router-link to="/admin/chat" class="nav-item" @click="closeMenu">
                    <el-badge :value="chatStore.unreadCount" :hidden="chatStore.unreadCount === 0" is-dot>
                        Chat
                    </el-badge>
                </router-link>
                <router-link to="/admin/analytics" class="nav-item" @click="closeMenu">Analytics</router-link>
                <router-link to="/notifications" class="nav-item icon-btn" @click="closeMenu">
                    <span class="mobile-label">Notifications</span>
                    <el-badge :value="unreadCount" :hidden="unreadCount === 0" type="danger" is-dot class="badge">
                        <el-icon><Bell /></el-icon>
                    </el-badge>
                </router-link>
            </template>
            
            <div class="auth-buttons">
                <template v-if="!authStore.token && !route.path.startsWith('/admin/login')">
                    <router-link to="/login" class="login-btn" @click="closeMenu">Log In</router-link>
                    <router-link to="/register" class="register-btn" @click="closeMenu">Sign Up</router-link>
                </template>
                <template v-if="authStore.token">
                    <router-link to="/profile" class="nav-item user-profile-link" @click="closeMenu">
                        Hi, {{ authStore.user?.username }}
                    </router-link>
                    <a @click="handleLogout" class="logout-btn">Log Out</a>
                </template>
            </div>
        </nav>
      </div>
    </el-header>
    
    <el-main class="main-content">
      <router-view />
    </el-main>
    
    <el-footer height="100px" class="footer">
        <div class="container footer-content">
            <p>&copy; 2026 LivingSpace Furniture. All rights reserved.</p>
            <div class="social-links">
                <a href="#">Instagram</a>
                <a href="#">Pinterest</a>
                <a href="#">Facebook</a>
            </div>
        </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useNotificationStore } from '@/stores/notification'
import { useChatStore } from '@/stores/chat'
import { useRouter, useRoute } from 'vue-router'
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { ShoppingCart, Bell, Star, Headset, List } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const notificationStore = useNotificationStore()
const chatStore = useChatStore()
const router = useRouter()
const route = useRoute()

const isMenuOpen = ref(false)
const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value
}
const closeMenu = () => {
    isMenuOpen.value = false
}

const handleLogout = () => {
    logout()
    closeMenu()
}

const unreadCount = computed(() => notificationStore.unreadCount)

const isStaff = computed(() => {
    return authStore.user && authStore.user.is_staff
})

const logout = () => {
  authStore.logout()
  notificationStore.stopPolling()
  chatStore.stopPolling()
  router.push('/login')
}

onMounted(() => {
    if (authStore.token) {
        cartStore.fetchCart()
        notificationStore.startPolling(authStore.user_id || authStore.user?.id)
        chatStore.startPolling()
    }
})

onUnmounted(() => {
    notificationStore.stopPolling()
    chatStore.stopPolling()
})
</script>

<style scoped>
.app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: var(--color-bg);
}

.header {
    background-color: var(--color-white);
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 0;
    border-bottom: 1px solid rgba(0,0,0,0.03);
}

.header-content {
    display: flex;
    align-items: center;
    height: 100%;
    justify-content: space-between;
    position: relative;
}

.logo {
    text-decoration: none;
    display: flex;
    align-items: center;
    z-index: 101;
}

.logo-text {
    font-family: var(--font-serif);
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: 2px;
}

.logo-primary {
    color: var(--color-secondary);
}

.logo-accent {
    color: var(--color-primary);
}

/* Hamburger Menu */
.hamburger {
    display: none;
    flex-direction: column;
    justify-content: space-around;
    width: 30px;
    height: 25px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0;
    z-index: 101;
}

.bar {
    width: 100%;
    height: 2px;
    background-color: var(--color-secondary);
    border-radius: 10px;
    transition: all 0.3s linear;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 32px;
}

.nav-item {
    color: var(--color-text-main);
    font-size: 0.95rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    position: relative;
    padding: 5px 0;
    font-family: var(--font-sans);
}

.nav-item::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 0;
    height: 2px;
    background-color: var(--color-primary);
    transition: width 0.3s ease;
}

.nav-item:hover {
    color: var(--color-primary);
}

.nav-item:hover::after {
    width: 100%;
}

.icon-btn {
    font-size: 1.4rem;
    display: flex;
    align-items: center;
    padding: 5px;
    color: var(--color-secondary);
}

.nav-icon-wrapper {
    display: flex;
    align-items: center;
    position: relative;
    height: 30px;
}

.hover-text {
    max-width: 0;
    opacity: 0;
    white-space: nowrap;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    font-size: 0.9rem;
    color: var(--color-primary);
    margin-left: 0;
    font-weight: 600;
}

.icon-btn:hover .hover-text {
    max-width: 150px;
    opacity: 1;
    margin-left: 8px;
}

.icon-btn .el-icon {
    transition: transform 0.4s ease;
}

.icon-btn:hover .el-icon {
    transform: scale(1.1);
}

.badge {
    display: flex;
    align-items: center;
}

.mobile-label {
    display: none;
}

.auth-buttons {
    display: flex;
    gap: 20px;
    margin-left: 20px;
    align-items: center;
}

.login-btn {
    color: var(--color-secondary);
    font-weight: 600;
    font-size: 0.95rem;
}

.login-btn:hover {
    color: var(--color-primary);
}

.register-btn {
    background-color: var(--color-primary);
    color: var(--color-white);
    padding: 10px 24px;
    border-radius: 24px;
    font-weight: 600;
    transition: all 0.3s;
    font-size: 0.95rem;
}

.register-btn:hover {
    background-color: var(--color-accent);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 110, 78, 0.2);
}

.logout-btn {
    cursor: pointer;
    color: var(--color-text-light);
    font-size: 0.9rem;
    padding: 5px 10px;
}

.user-profile-link {
    font-weight: 600;
    color: var(--color-primary) !important;
    text-transform: none;
    margin-right: 10px;
}

.logout-btn:hover {
    color: var(--color-secondary);
}

/* Mobile Responsive Styles */
@media (max-width: 768px) {
    .hamburger {
        display: flex;
    }

    .nav-links {
        position: fixed;
        top: 0;
        right: -100%;
        height: 100vh;
        width: 80%;
        background-color: var(--color-white);
        flex-direction: column;
        align-items: flex-start;
        padding: 100px 30px;
        box-shadow: -5px 0 15px rgba(0,0,0,0.1);
        transition: right 0.3s ease-in-out;
        gap: 24px;
        z-index: 100;
    }

    .nav-links.is-open {
        right: 0;
    }

    .nav-item {
        font-size: 1.1rem;
        width: 100%;
    }

    .auth-buttons {
        margin-left: 0;
        flex-direction: column;
        align-items: flex-start;
        width: 100%;
        margin-top: 20px;
    }

    .mobile-label {
        display: none;
    }
    
    .hover-text {
        max-width: 100%;
        opacity: 1;
        margin-left: 15px;
        font-size: 1.1rem;
        color: var(--color-text-main);
    }

    .icon-btn {
        width: 100%;
        justify-content: flex-start;
    }
}

.main-content {
    flex: 1;
    padding-top: 0;
}

.footer {
    background-color: var(--color-white);
    color: var(--color-text-main);
    margin-top: auto;
    display: flex;
    align-items: center;
    border-top: 1px solid rgba(0,0,0,0.05);
}

.footer-content {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}

@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        text-align: center;
    }
}

.social-links {
    display: flex;
    gap: 24px;
}

.social-links a {
    color: var(--color-text-light);
    font-size: 0.9rem;
    font-weight: 500;
}

.social-links a:hover {
    color: var(--color-primary);
}
</style>
