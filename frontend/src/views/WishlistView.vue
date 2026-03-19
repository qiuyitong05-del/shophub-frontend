<template>
  <div class="wishlist-container container">
    <div class="page-header">
        <h2>My Wishlist</h2>
        <div class="header-controls">
            <div class="control-group">
                <span class="label">Sort by:</span>
                <el-select v-model="sortBy" placeholder="Sort by" class="sort-select" @change="fetchWishlist">
                    <el-option label="Date Added" value="date" />
                    <el-option label="Price Drop" value="price_drop" />
                    <el-option label="In Stock" value="in_stock" />
                </el-select>
            </div>
            
            <div class="control-group">
                <el-switch
                    v-model="isPublic"
                    active-text="Public"
                    inactive-text="Private"
                    @change="handlePrivacyChange"
                    style="--el-switch-on-color: var(--color-primary);"
                />
                <el-button v-if="shareToken" link type="primary" @click="copyShareLink" class="share-btn">
                    <el-icon><Share /></el-icon> Share Link
                </el-button>
            </div>
        </div>
    </div>

    <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" size="40" color="var(--color-primary)"><Loading /></el-icon>
    </div>

    <div v-else>
        <div v-if="items.length > 0">
            <div class="bulk-toolbar">
                <el-checkbox v-model="allSelected" @change="toggleAll">Select All</el-checkbox>
                <el-button type="primary" @click="handleBulkAddToCart" :disabled="selectedItems.length === 0">Add Selected to Cart</el-button>
            </div>

            <div class="wishlist-grid">
                <div v-for="item in pagedItems" :key="item.id" class="wishlist-card">
                    <div class="card-image-section">
                        <img :src="item.product_thumbnail" @click="$router.push(`/product/${item.product}`)" />
                        <div class="card-overlay-actions">
                            <el-button circle type="danger" :icon="Delete" @click="removeItem(item)" title="Remove"></el-button>
                        </div>
                    </div>
                    <div class="card-content">
                        <h3 @click="$router.push(`/product/${item.product}`)">{{ item.product_name }}</h3>
                        <div class="price-row">
                            <span class="price">${{ item.product_price }}</span>
                            <span v-if="item.price_drop > 0" class="drop-label">Down ${{ item.price_drop }}</span>
                        </div>
                        <div class="stock-status">
                            <span v-if="item.stock_quantity <= 0" class="status-out">Out of Stock</span>
                            <span v-else-if="item.stock_quantity < 5" class="status-low">Only {{ item.stock_quantity }} left</span>
                            <span v-else class="status-in">In Stock</span>
                        </div>
                        <div class="card-footer-actions">
                            <el-checkbox :model-value="selectedIds.includes(item.product)" @change="toggleSelection(item.product)">Select</el-checkbox>
                            <el-button type="primary" size="small" round @click="addToCart(item)" :disabled="item.stock_quantity <= 0">Add to Cart</el-button>
                        </div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 20px; text-align: right;" v-if="items.length > 0">
                <el-pagination 
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :page-sizes="[12, 24, 48, 96]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="items.length"
                    @size-change="handleSizeChange"
                    @current-change="handlePageChange"
                />
            </div>
        </div>
        
        <div v-else class="empty-state">
            <el-icon :size="80" class="empty-icon"><StarFilled /></el-icon>
            <h3>Your wishlist is empty</h3>
            <p>Save items you love to revisit later.</p>
            <el-button type="primary" @click="$router.push('/')">Explore Products</el-button>
        </div>
    </div>

    <!-- Similar Products Dialog -->
    <el-dialog v-model="showSimilarDialog" title="Similar Products" width="800px" custom-class="similar-dialog">
        <el-row :gutter="20">
            <el-col :span="8" :xs="24" v-for="rp in similarProducts" :key="rp.id">
                 <div class="similar-card" @click="goToProduct(rp.id)">
                    <img :src="rp.thumbnail" />
                    <div class="similar-info">
                        <span class="name">{{ rp.name }}</span>
                        <span class="price">${{ rp.price }}</span>
                    </div>
                </div>
            </el-col>
        </el-row>
        <el-empty v-if="similarProducts.length === 0" description="No similar products found" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getWishlist, removeFromWishlist, updateWishlistPrivacy, bulkAddToCart } from '@/api/wishlist'
import { findSimilarProducts } from '@/api/product'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Warning, InfoFilled, Delete, Share, StarFilled } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()
const items = ref([])
const loading = ref(false)
const sortBy = ref('date')
const isPublic = ref(false)
const shareToken = ref('')

const currentPage = ref(1)
const pageSize = ref(12)
const maxPage = computed(() => Math.max(1, Math.ceil(items.value.length / pageSize.value)))
const pagedItems = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return items.value.slice(start, start + pageSize.value)
})
const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
}
const handlePageChange = (page) => {
    currentPage.value = page
}

// Selection
const selectedIds = ref([])
const toggleSelection = (id) => {
    const index = selectedIds.value.indexOf(id)
    if (index > -1) selectedIds.value.splice(index, 1)
    else selectedIds.value.push(id)
}
const toggleAll = (val) => {
    if (val) selectedIds.value = items.value.map(i => i.product)
    else selectedIds.value = []
}
const allSelected = computed({
    get: () => items.value.length > 0 && selectedIds.value.length === items.value.length,
    set: (val) => toggleAll(val)
})
const selectedItems = computed(() => items.value.filter(i => selectedIds.value.includes(i.product)))


// Similar Products State
const showSimilarDialog = ref(false)
const similarProducts = ref([])

const findSimilar = async (item) => {
    try {
        const res = await findSimilarProducts(item.product)
        similarProducts.value = res
        showSimilarDialog.value = true
    } catch (e) { console.error(e) }
}

const goToProduct = (id) => {
    showSimilarDialog.value = false
    router.push(`/product/${id}`)
}

const fetchWishlist = async () => {
    loading.value = true
    try {
        const res = await getWishlist({
            user_id: authStore.user.id,
            sort: sortBy.value
        })
        items.value = res.items
        currentPage.value = 1
        isPublic.value = res.privacy === 'Public'
        shareToken.value = res.share_token
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const handlePrivacyChange = async (val) => {
    try {
        const res = await updateWishlistPrivacy({
            user_id: authStore.user.id,
            privacy: val ? 'Public' : 'Private'
        })
        shareToken.value = res.share_token
        ElMessage.success(`Wishlist is now ${val ? 'Public' : 'Private'}`)
    } catch (e) {
        console.error(e)
        // Revert on error
        isPublic.value = !val 
    }
}

const copyShareLink = () => {
    const link = `${window.location.origin}/wishlist/shared/${shareToken.value}`
    navigator.clipboard.writeText(link).then(() => {
        ElMessage.success('Link copied to clipboard')
    })
}

const addToCart = async (item) => {
    try {
        await cartStore.addItem(item.product, 1)
        ElMessage.success('Added to cart')
    } catch (e) {}
}

const removeItem = async (item) => {
    try {
        await removeFromWishlist({
            user_id: authStore.user.id,
            product_id: item.product
        })
        items.value = items.value.filter(i => i.id !== item.id)
        if (currentPage.value > maxPage.value) currentPage.value = maxPage.value
        // Remove from selection
        const idx = selectedIds.value.indexOf(item.product)
        if (idx > -1) selectedIds.value.splice(idx, 1)
        
        ElMessage.success('Removed')
    } catch (e) { console.error(e) }
}

const handleBulkAddToCart = async () => {
    try {
        const ids = selectedItems.value.map(i => i.product)
        const res = await bulkAddToCart({
            user_id: authStore.user.id,
            product_ids: ids
        })
        ElMessage.success('Items added to cart')
        fetchWishlist()
    } catch (e) { console.error(e) }
}

onMounted(() => {
    if (authStore.token) {
        fetchWishlist()
    }
})
</script>

<style scoped>
.wishlist-container {
    padding: 40px 20px;
    max-width: 1200px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40px;
    flex-wrap: wrap;
    gap: 20px;
}

.page-header h2 {
    font-size: 2.5rem;
    font-family: var(--font-serif);
    color: var(--color-secondary);
    margin: 0;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 30px;
    flex-wrap: wrap;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.label {
    color: var(--color-text-light);
    font-weight: 500;
}

.share-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: 600;
    color: var(--color-primary);
}

.loading-state {
    text-align: center;
    padding: 100px 0;
}

.bulk-toolbar {
    background: var(--color-white);
    padding: 15px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: var(--shadow-card);
}

.wishlist-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
}

.wishlist-card {
    background: var(--color-white);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.wishlist-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-hover);
}

.card-image-section {
    position: relative;
    width: 100%;
    padding-top: 100%; /* Square aspect ratio */
    background: #f8f8f8;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-image-section img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover; 
    cursor: pointer;
    transition: transform 0.5s ease;
}

.wishlist-card:hover .card-image-section img {
    transform: scale(1.05);
}

.card-overlay-actions {
    position: absolute;
    top: 10px;
    right: 10px;
    opacity: 0;
    transition: opacity 0.3s;
}

.wishlist-card:hover .card-overlay-actions {
    opacity: 1;
}

.card-content {
    padding: 20px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.card-content h3 {
    margin: 0 0 10px;
    font-size: 1.1rem;
    color: var(--color-text-main);
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.card-content h3:hover {
    color: var(--color-primary);
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.price {
    font-weight: 700;
    color: var(--color-secondary);
    font-size: 1.1rem;
}

.drop-label {
    color: #4CAF50;
    font-size: 0.85rem;
    font-weight: 600;
    background: #E8F5E9;
    padding: 2px 6px;
    border-radius: 4px;
}

.stock-status {
    margin-bottom: 15px;
    font-size: 0.9rem;
}

.status-out { color: #f56c6c; font-weight: 600; }
.status-low { color: #E6A23C; font-weight: 600; }
.status-in { color: #67C23A; }

.card-footer-actions {
    margin-top: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid rgba(0,0,0,0.05);
}

.empty-state {
    text-align: center;
    padding: 80px 20px;
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: var(--shadow-card);
}

.empty-icon {
    margin-bottom: 24px;
    color: #E0E0E0;
}

.empty-state h3 {
    margin-bottom: 10px;
    color: var(--color-text-light);
    font-weight: 400;
}

.empty-state p {
    color: #999;
    margin-bottom: 30px;
}

.similar-card {
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
    margin-bottom: 20px;
}

.similar-card:hover {
    box-shadow: var(--shadow-hover);
}

.similar-card img {
    width: 100%;
    height: 150px;
    object-fit: contain;
    background: #f9f9f9;
}

.similar-info {
    padding: 10px;
    text-align: center;
}

.similar-info .name {
    display: block;
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 0.9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.similar-info .price {
    color: var(--color-primary);
    font-weight: 700;
}

@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .header-controls {
        width: 100%;
        justify-content: space-between;
    }
    .wishlist-grid {
        grid-template-columns: 1fr;
    }
}
</style>
