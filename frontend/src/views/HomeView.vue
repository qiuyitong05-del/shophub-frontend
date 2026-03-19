<template>
  <div class="home-container">
    <!-- Hero Section -->
    <div class="hero-section">
        <el-carousel :height="heroHeight" indicator-position="outside" arrow="always">
            <el-carousel-item v-for="item in heroImages" :key="item">
                <div class="hero-slide">
                    <div class="hero-bg" :style="{ backgroundImage: `url(${item})` }"></div>
                    <div class="hero-overlay"></div>
                    <div class="hero-content container">
                        <h1 class="hero-title">Elevate Your Living Space</h1>
                        <p class="hero-subtitle">Discover our curated collection of premium furniture and decor.</p>
                        <el-button type="primary" size="large" class="hero-btn" @click="scrollToProducts">Shop Now</el-button>
                    </div>
                </div>
            </el-carousel-item>
        </el-carousel>
    </div>

    <!-- Categories Section -->
    <div class="section-container container">
        <h2 class="section-title">Shop by Category</h2>
        <div class="categories-wrapper">
            <div class="categories-grid">
                <div 
                    v-for="cat in categories" 
                    :key="cat.id" 
                    class="category-card"
                    @click="filterByCategory(cat.id)"
                >
                    <div class="cat-icon">
                        <el-icon :size="32"><component :is="getCategoryIcon(cat.name)" /></el-icon>
                    </div>
                    <h3>{{ cat.name }}</h3>
                </div>
            </div>
        </div>
    </div>

    <!-- Products Section -->
    <div class="section-container container" id="products-section">
        <div class="section-header">
            <h2 class="section-title">Featured Products</h2>
            
            <!-- Search Toolbar -->
            <div class="search-toolbar">
                <el-input 
                    v-model="searchQuery" 
                    placeholder="Search products..." 
                    :prefix-icon="Search"
                    clearable 
                    class="search-input"
                    @keyup.enter="handleSearch"
                />
                <el-select v-model="selectedCategory" placeholder="Category" clearable multiple collapse-tags class="filter-select">
                    <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
                </el-select>
                <el-select v-model="selectedTags" placeholder="Tags" clearable multiple collapse-tags class="filter-select">
                    <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.name" />
                </el-select>

                <el-select v-model="sortBy" placeholder="Sort" clearable class="filter-select">
                    <el-option label="Price: Low to High" value="price_asc" />
                    <el-option label="Price: High to Low" value="price_desc" />
                </el-select>
                
                <div class="price-range">
                    <el-input v-model="minPrice" placeholder="Min" type="number" class="price-input" clearable />
                    <span class="separator">-</span>
                    <el-input v-model="maxPrice" placeholder="Max" type="number" class="price-input" clearable />
                </div>

                 <el-button type="primary" @click="handleSearch" class="filter-btn">Filter</el-button>
            </div>
        </div>

        <el-row :gutter="24" v-loading="loading">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="product in paginatedProductsDisplay" :key="product.id" style="margin-bottom: 24px;">
                <el-card :body-style="{ padding: '0px' }" class="product-card" shadow="hover" @click="$router.push(`/product/${product.id}`)">
                    <div class="image-wrapper">
                        <el-image :src="product.thumbnail" class="product-image" fit="cover" loading="lazy">
                            <template #error>
                                <div class="image-placeholder">
                                    <el-icon :size="32" color="#ccc"><Box /></el-icon>
                                </div>
                            </template>
                        </el-image>
                        <div class="overlay">
                            <el-button circle :icon="ShoppingCart" @click="(e) => handleAddToCart(product, e)" class="action-btn" title="Add to Cart"></el-button>
                            <el-button circle :icon="Star" @click="(e) => handleAddToWishlist(product, e)" class="action-btn" title="Add to Wishlist"></el-button>
                        </div>
                    </div>
                    <div class="product-info">
                        <div class="category-tag">{{ categories.find(c => c.id === product.category_id)?.name }}</div>
                        <h3 class="product-name" :title="product.name">{{ product.name }}</h3>
                        <div class="product-bottom">
                            <span class="price">${{ product.price }}</span>
                            <el-tag v-if="product.stock_quantity <= 0" type="danger" size="small" effect="dark">Sold Out</el-tag>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        
        <el-empty v-if="!loading && products.length === 0" description="No products found matching your criteria." />
        
        <div class="pagination-wrapper" v-if="products.length > 0">
            <el-pagination 
                layout="prev, pager, next" 
                :total="products.length" 
                :page-size="pageSize"
                v-model:current-page="currentPage"
                background
            />
        </div>
    </div>
    
    <!-- Shared Wishlist Dialog -->
    <el-dialog v-model="sharedWishlistDialog" title="Shared Wishlist" width="80%" destroy-on-close @closed="$router.replace('/')">
        <div v-loading="sharedWishlistLoading">
            <div v-if="sharedWishlistItems.length === 0" style="text-align: center; padding: 20px; color: #999;">This wishlist is empty.</div>
            <div class="shared-grid" v-else>
                 <div v-for="item in sharedWishlistItems" :key="item.id" class="shared-item" @click="$router.push(`/product/${item.product}`)">
                     <el-image :src="item.product_thumbnail" style="width: 100%; height: 150px; object-fit: cover; border-radius: 4px;" />
                     <div style="margin-top: 10px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.product_name }}</div>
                     <div style="color: #8B5E3C;">${{ item.product_price }}</div>
                 </div>
            </div>
        </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { getProducts, getCategories, getTags } from '@/api/product'
import { getWishlist, addToWishlist } from '@/api/wishlist'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { 
    Search, 
    ShoppingCart, 
    Star, 
    House,
    Box,
    Monitor,
    CoffeeCup,
    ArrowRight
} from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const products = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(false)

// Shared Wishlist
const sharedWishlistDialog = ref(false)
const sharedWishlistItems = ref([])
const sharedWishlistLoading = ref(false)

const checkSharedWishlist = async () => {
    if (route.name === 'shared-wishlist' && route.params.token) {
        sharedWishlistLoading.value = true
        sharedWishlistDialog.value = true
        try {
            const res = await getWishlist({ share_token: route.params.token })
            sharedWishlistItems.value = res.items
        } catch (e) {
            console.error(e)
            ElMessage.error('This wishlist is private or does not exist.')
            sharedWishlistDialog.value = false
            router.replace('/')
        } finally {
            sharedWishlistLoading.value = false
        }
    }
}
const searchQuery = ref('')
const selectedCategory = ref([])
const selectedTags = ref([])
const sortBy = ref('')
const minPrice = ref(undefined)
const maxPrice = ref(undefined)
const searchType = ref('keyword') 
const currentPage = ref(1)
const pageSize = ref(12)

const windowWidth = ref(window.innerWidth)
const heroHeight = computed(() => {
    return windowWidth.value < 768 ? '400px' : '600px'
})
const updateWidth = () => {
    windowWidth.value = window.innerWidth
}

const heroImages = [
    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
    'https://images.unsplash.com/photo-1524758631624-e2822e304c36?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80'
]

const fetchProducts = async (params = {}) => {
    loading.value = true
    try {
        const res = await getProducts({ ...params, page_size: 100 })
        if (res) {
            const rawData = Array.isArray(res) ? res : res.results
            products.value = Array.isArray(rawData) ? rawData : []
        }
    } catch (e) {
        console.error(e)
        products.value = []
    } finally {
        loading.value = false
    }
}

const paginatedProductsDisplay = computed(() => {
    if (!products.value || !Array.isArray(products.value)) return []
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return products.value.slice(start, end)
})

const applyFilters = () => {
    const params = {}
    if (searchQuery.value) params.q = searchQuery.value
    if (selectedCategory.value.length) params.category_ids = selectedCategory.value.join(',')
    if (selectedTags.value.length) params.tags = selectedTags.value.join(',')
    if (sortBy.value) params.sort = sortBy.value
    if (minPrice.value) params.min_price = minPrice.value
    if (maxPrice.value) params.max_price = maxPrice.value
    
    fetchProducts(params)
    currentPage.value = 1
}

const fetchCategories = async () => {
    try {
        const res = await getCategories()
        categories.value = Array.isArray(res) ? res : res.results
    } catch (e) {
        console.error(e)
    }
}

const fetchTags = async () => {
    try {
        const res = await getTags()
        const allTags = Array.isArray(res) ? res : res.results
        tags.value = allTags
    } catch (e) { console.error(e) }
}

const handleSearch = () => {
    applyFilters()
}

const scrollToProducts = () => {
    document.getElementById('products-section').scrollIntoView({ behavior: 'smooth' })
}

const filterByCategory = (catId) => {
    selectedCategory.value = [catId]
    applyFilters()
    scrollToProducts()
}

// Icon Mapping
const getCategoryIcon = (name) => {
    if (!name) return House
    const n = name.toLowerCase()
    if (n.includes('sofa') || n.includes('chair') || n.includes('living')) return House
    if (n.includes('bed') || n.includes('sleep')) return Box
    if (n.includes('desk') || n.includes('office')) return Monitor
    if (n.includes('table') || n.includes('dining')) return CoffeeCup
    if (n.includes('shelf') || n.includes('book')) return Box
    return House
}

// Add To Cart
const handleAddToCart = async (product, e) => {
    e.stopPropagation()
    if (!authStore.token) {
        ElMessage.warning('Please log in first')
        router.push('/login')
        return
    }
    try {
        await cartStore.addItem(product.id, 1)
        ElMessage.success('Added to cart')
    } catch (e) {
        // ElMessage.error('Failed to add to cart') // Store handles error
    }
}

// Add To Wishlist
const handleAddToWishlist = async (product, e) => {
    e.stopPropagation()
    if (!authStore.token) {
        ElMessage.warning('Please log in first')
        router.push('/login')
        return
    }
    try {
        await addToWishlist({ 
            user_id: authStore.user?.id, 
            product_id: product.id 
        })
        ElMessage.success('Added to wishlist')
    } catch (e) {
        ElMessage.error('Failed to add to wishlist')
    }
}

onMounted(() => {
    window.addEventListener('resize', updateWidth)
    fetchProducts()
    fetchCategories()
    fetchTags()
    checkSharedWishlist()
})

watch(() => route.params.token, () => {
    checkSharedWishlist()
})

onUnmounted(() => {
    window.removeEventListener('resize', updateWidth)
})
</script>

<style scoped>
.home-container {
    background-color: var(--color-bg);
    min-height: 100vh;
}

.hero-section {
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}

.hero-slide {
    height: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hero-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: blur(2px) brightness(0.9);
    transform: scale(1.05); /* Avoid blur edges */
    z-index: 0;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, transparent 20%, rgba(0,0,0,0.4) 100%); /* Vignette */
    z-index: 1;
}

.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 800px;
    padding: 0 20px;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--color-white);
    font-family: var(--font-serif);
    text-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.hero-subtitle {
    font-size: 1.2rem;
    margin-bottom: 32px;
    color: rgba(255,255,255,0.95);
    font-weight: 300;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.hero-btn {
    padding: 24px 48px;
    font-size: 1.1rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-radius: 30px;
    border: none;
    background-color: var(--color-primary) !important;
    transition: all 0.3s ease;
}

.hero-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    background-color: var(--color-accent) !important;
}

.section-container {
    padding: 60px 20px;
}

.section-title {
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: 48px;
    color: var(--color-secondary);
    font-family: var(--font-serif);
    position: relative;
}

.section-title::after {
    content: '';
    display: block;
    width: 60px;
    height: 3px;
    background: linear-gradient(to right, transparent, var(--color-primary), transparent);
    margin: 16px auto 0;
}

/* Categories */
.categories-wrapper {
    overflow-x: auto;
    padding-bottom: 20px;
    /* Custom Scrollbar for wrapper */
    scrollbar-width: thin;
    scrollbar-color: var(--color-primary) #f1f1f1;
}

.categories-wrapper::-webkit-scrollbar {
    height: 6px;
}

.categories-wrapper::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.categories-wrapper::-webkit-scrollbar-thumb {
    background: var(--color-primary);
    border-radius: 4px;
}

.categories-grid {
    display: flex;
    justify-content: flex-start;
    gap: 30px;
    margin-bottom: 10px;
    flex-wrap: nowrap;
    padding: 10px 5px; /* Space for box-shadow */
}

.category-card {
    background: var(--color-white);
    padding: 40px 30px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s ease;
    box-shadow: var(--shadow-card);
    width: 180px;
    flex: 0 0 180px; /* Prevent shrinking */
    border: 1px solid transparent;
}

.category-card:hover {
    transform: scale(1.02);
    box-shadow: var(--shadow-hover);
    border-color: var(--color-primary);
}

.cat-icon {
    width: 64px;
    height: 64px;
    background-color: #F5F0EB;
    color: var(--color-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    transition: all 0.4s ease;
}

.category-card:hover .cat-icon {
    background-color: var(--color-primary);
    color: var(--color-white);
    transform: rotateY(180deg);
}

.category-card h3 {
    font-size: 1.1rem;
    color: var(--color-secondary);
    margin: 0;
    font-weight: 600;
}

/* Filter Toolbar */
.section-header {
    margin-bottom: 40px;
}

.search-toolbar {
    display: flex;
    gap: 16px;
    align-items: center;
    background: var(--color-white);
    padding: 20px;
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    flex-wrap: wrap;
}

.search-input {
    flex: 2;
    min-width: 200px;
}

.filter-select {
    flex: 1;
    min-width: 150px;
}

.price-range {
    display: flex;
    align-items: center;
    gap: 8px;
}

.price-input {
    width: 80px;
}

.filter-btn {
    padding: 0 30px;
    height: 40px; /* Match input height */
    background-color: var(--color-primary) !important;
    border-color: var(--color-primary) !important;
}

.filter-btn:hover {
    background-color: var(--color-accent) !important;
    border-color: var(--color-accent) !important;
}

/* Product Card */
.product-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    border: none;
    border-radius: 12px;
    background: var(--color-white);
    transition: all 0.3s ease;
    overflow: hidden;
}

.image-wrapper {
    position: relative;
    padding-top: 133%; /* 3:4 Aspect Ratio (approx 70% height if including info) */
    overflow: hidden;
    background-color: #f0f0f0;
}

.product-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    transition: transform 0.6s ease;
}

.image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
    color: #ccc;
}

.product-card:hover .product-image {
    transform: scale(1.08);
}

.overlay {
    position: absolute;
    bottom: 20px;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: center;
    gap: 16px;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.4s ease;
    z-index: 10;
}

.product-card:hover .overlay {
    opacity: 1;
    transform: translateY(0);
}

.action-btn {
    background-color: var(--color-white) !important;
    color: var(--color-primary) !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    width: 45px;
    height: 45px;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.action-btn:hover {
    background-color: var(--color-primary) !important;
    color: var(--color-white) !important;
    transform: scale(1.1);
}

.product-info {
    padding: 20px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.category-tag {
    font-size: 0.75rem;
    color: #A67C52; /* Light brown */
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
    font-weight: 600;
}

.product-name {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 12px;
    color: var(--color-text-main);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.product-bottom {
    margin-top: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.price {
    font-size: 1.2rem;
    color: var(--color-secondary); /* Dark text for price */
    font-weight: 700;
}

.pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 60px;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.2rem;
    }
    .search-toolbar {
        flex-direction: column;
        align-items: stretch;
    }
    .categories-grid {
        gap: 15px; /* Smaller gap on mobile */
    }
    .category-card {
        padding: 20px 15px;
        width: 140px;
        flex: 0 0 140px;
    }
}

.shared-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
}

.shared-item {
    cursor: pointer;
    border: 1px solid #eee;
    padding: 10px;
    border-radius: 8px;
    transition: all 0.3s;
    text-align: center;
}

.shared-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
</style>
