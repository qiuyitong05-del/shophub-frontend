<template>
  <div class="cart-container">
    <div class="page-header">
        <h2>Shopping Cart</h2>
    </div>

    <div v-if="cartStore.items.length === 0" class="empty-cart">
        <el-icon :size="100" class="empty-icon"><Box /></el-icon>
        <h3>Your cart is waiting to be filled with beautiful pieces!</h3>
        <el-button type="primary" size="large" @click="$router.push('/')">Go Shopping</el-button>
    </div>

    <div v-else class="cart-content">
        <!-- Select All -->
        <div class="cart-toolbar">
            <el-checkbox v-model="allSelected" size="large">Select All ({{ cartStore.items.length }})</el-checkbox>
        </div>

        <div class="cart-list">
            <div v-for="item in pagedCartItems" :key="item.product_id" class="cart-item-card">
                <div class="card-checkbox">
                    <el-checkbox :model-value="selectedProductIds.includes(item.product_id)" @change="toggleSelection(item.product_id)" />
                </div>
                <div class="card-image" @click="$router.push(`/product/${item.product_id}`)">
                    <img :src="item.product_thumbnail" />
                </div>
                <div class="card-info">
                    <div class="info-top">
                        <h3 @click="$router.push(`/product/${item.product_id}`)">{{ item.product_name }}</h3>
                        <div class="item-price">${{ Number(item.unit_price).toFixed(2) }}</div>
                    </div>
                    <div v-if="item.custom_dimensions" class="dims">Dimensions: {{ item.custom_dimensions }}</div>
                    
                    <div class="info-bottom">
                        <el-input-number v-model="item.quantity" :min="1" size="small" @change="(val) => handleUpdate(item.product_id, val)" />
                        <div class="subtotal">Subtotal: ${{ (item.unit_price * item.quantity).toFixed(2) }}</div>
                    </div>
                    
                    <div class="action-buttons">
                        <el-button link type="danger" @click="handleRemove(item.product_id)">Remove</el-button>
                        <el-button link type="primary" @click="handleMoveToWishlist(item.product_id)">Move to Wishlist</el-button>
                    </div>
                </div>
            </div>
        </div>

        <div style="margin-top: 20px; text-align: right;" v-if="cartStore.items.length > 0">
            <el-pagination 
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[5, 10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="cartStore.items.length"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
            />
        </div>
    </div>
    
    <!-- Recommendations Section -->
    <div v-if="selectedTotalPrice > 0 && selectedTotalPrice < 999 && recommendations.length > 0" class="recommendations">
        <h3>Add more to reach free shipping ($999) - You need ${{ (999 - selectedTotalPrice).toFixed(2) }} more</h3>
        <el-scrollbar>
            <div class="rec-list">
                <div v-for="item in recommendations" :key="item.id" class="rec-item">
                    <img :src="item.thumbnail" @click="$router.push(`/product/${item.id}`)" />
                    <div class="rec-info">
                        <span class="rec-name" :title="item.name">{{ item.name }}</span>
                        <span class="rec-price">${{ item.price }}</span>
                        <el-button size="small" type="primary" @click="addRecToCart(item)">Add</el-button>
                    </div>
                </div>
            </div>
        </el-scrollbar>
    </div>

    <div class="cart-footer" v-if="cartStore.items.length > 0">
        <!-- Coupon Section -->
        <div class="coupon-container">
            <h4>Available Coupons</h4>
            <div v-if="availableCoupons.length > 0">
                <el-radio-group v-model="selectedCouponId" class="coupon-group">
                    <el-radio :label="null" border>Do not use coupon</el-radio>
                    <el-radio v-for="coupon in availableCoupons" :key="coupon.user_coupon_id" :label="coupon.user_coupon_id" border>
                        {{ coupon.code }} (-${{ coupon.discount_amount }}) <span v-if="coupon.valid_until">Valid until {{ formatValidUntil(coupon.valid_until) }}</span>
                    </el-radio>
                </el-radio-group>
            </div>
            <div v-else>No applicable coupons</div>
        </div>

        <div class="summary">
            <div class="summary-row"><span>Subtotal:</span> <span>${{ selectedTotalPrice.toFixed(2) }}</span></div>
            <div v-if="selectedCouponAmount > 0" class="summary-row discount"><span>Coupon Discount:</span> <span>-${{ selectedCouponAmount.toFixed(2) }}</span></div>
            <div class="summary-row">
                <span>Shipping:</span>
                <span v-if="selectedTotalPrice < 999">$20.00</span>
                <span v-else style="color: green;">Free</span>
            </div>
            <div class="summary-total">
                <h3>Total:</h3>
                <h3>${{ finalTotal.toFixed(2) }}</h3>
            </div>
            <el-button type="primary" size="large" class="checkout-btn" @click="openCheckout" :disabled="selectedItems.length === 0">Checkout</el-button>
        </div>
    </div>

    <el-dialog v-model="showCheckoutDialog" title="Checkout" width="500px">
        <el-form label-width="120px">
            <el-form-item label="Shipping Address">
                <el-input v-model="shippingAddress" type="textarea" placeholder="Enter your shipping address" rows="3" />
            </el-form-item>
            <el-form-item label="Total Amount">
                <span style="font-weight: bold; font-size: 1.5em; color: var(--color-primary);">${{ finalTotal.toFixed(2) }}</span>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showCheckoutDialog = false">Cancel</el-button>
                <el-button type="primary" @click="handleCheckout" :loading="checkoutLoading">
                    Confirm Order
                </el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, nextTick, watch } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { createOrder, getDefaultAddress } from '@/api/order'
import { getAvailableCoupons, moveToWishlist, getCartRecommendations } from '@/api/cart'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Box } from '@element-plus/icons-vue'

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()
const showCheckoutDialog = ref(false)
const shippingAddress = ref('')
const checkoutLoading = ref(false)
// const selectedItems = ref([]) // Removed in favor of computed
const selectedProductIds = ref([])

const currentPage = ref(1)
const pageSize = ref(10)
const pagedCartItems = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return cartStore.items.slice(start, start + pageSize.value)
})
const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
}
const handlePageChange = (page) => {
    currentPage.value = page
}

// New State
const availableCoupons = ref([])
const selectedCouponId = ref(null)
const recommendations = ref([])

// Selection Logic
const toggleSelection = (id) => {
    const index = selectedProductIds.value.indexOf(id)
    if (index > -1) {
        selectedProductIds.value.splice(index, 1)
    } else {
        selectedProductIds.value.push(id)
    }
}

const toggleAll = (val) => {
    if (val) {
        selectedProductIds.value = cartStore.items.map(i => i.product_id)
    } else {
        selectedProductIds.value = []
    }
}

const allSelected = computed({
    get: () => cartStore.items.length > 0 && selectedProductIds.value.length === cartStore.items.length,
    set: (val) => toggleAll(val)
})

const selectedItems = computed(() => {
    return cartStore.items.filter(item => selectedProductIds.value.includes(item.product_id))
})

const selectedTotalPrice = computed(() => {
    return selectedItems.value.reduce((total, item) => {
        const price = Number(item.unit_price)
        const quantity = Number(item.quantity)
        const safePrice = isNaN(price) ? 0 : price
        const safeQuantity = isNaN(quantity) ? 0 : quantity
        return total + (safePrice * safeQuantity)
    }, 0)
})

const selectedCouponAmount = computed(() => {
    if (!selectedCouponId.value) return 0
    const coupon = availableCoupons.value.find(c => c.user_coupon_id === selectedCouponId.value)
    return coupon ? Number(coupon.discount_amount) : 0
})

const finalTotal = computed(() => {
    let total = selectedTotalPrice.value
    let shipping = total < 999 ? 20 : 0
    let discount = selectedCouponAmount.value
    let finalVal = total + shipping - discount
    return finalVal < 0 ? 0 : finalVal
})

// Fetch coupons and recommendations
const loadExtras = async () => {
    if (!authStore.user) return
    try {
        const cRes = await getAvailableCoupons({ user_id: authStore.user.id })
        availableCoupons.value = cRes
        if (cRes.length > 0) {
            selectedCouponId.value = cRes[0].user_coupon_id
        }
        
        const rRes = await getCartRecommendations({ user_id: authStore.user.id })
        recommendations.value = rRes
    } catch (e) { console.error(e) }
}

const handleMoveToWishlist = async (productId) => {
    try {
        await moveToWishlist({
            user_id: authStore.user.id,
            product_id: productId
        })
        ElMessage.success('Moved to wishlist')
        await cartStore.fetchCart()
    } catch (e) { console.error(e) }
}

const addRecToCart = async (item) => {
    try {
        await cartStore.addItem(item.id, 1)
        ElMessage.success('Added to cart')
        recommendations.value = recommendations.value.filter(r => r.id !== item.id)
    } catch (e) {}
}

const formatValidUntil = (dt) => {
    const d = new Date(dt)
    if (Number.isNaN(d.getTime())) return String(dt)
    return d.toLocaleDateString()
}

const openCheckout = async () => {
    if (selectedItems.value.length === 0) {
        ElMessage.warning('Please select items to checkout')
        return
    }
    
    try {
        const res = await getDefaultAddress()
        if (res && res.address) {
            shippingAddress.value = res.address
        } else if (typeof res === 'string') {
            shippingAddress.value = res
        }
    } catch (e) {
    } finally {
        showCheckoutDialog.value = true
    }
}

const handleUpdate = async (id, quantity) => {
    await cartStore.updateQuantity(id, quantity)
}

const handleRemove = async (id) => {
    await cartStore.removeItem(id)
    // Remove from selection if present
    const index = selectedProductIds.value.indexOf(id)
    if (index > -1) selectedProductIds.value.splice(index, 1)
}

const handleCheckout = async () => {
    if (!shippingAddress.value) {
        ElMessage.warning('Please enter a shipping address')
        return
    }

    checkoutLoading.value = true
    try {
        await createOrder({
            total_amount: finalTotal.value, 
            shipping_address: shippingAddress.value,
            selected_ids: selectedItems.value.map(item => item.product_id),
            user_coupon_id: selectedCouponId.value
        })
        
        ElMessage.success('Order placed successfully!')
        await cartStore.fetchCart()
        selectedProductIds.value = []
        showCheckoutDialog.value = false
        router.push('/orders')
        
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            console.error(e)
            ElMessage.error('Failed to place order')
        }
    } finally {
        checkoutLoading.value = false
    }
}

watch(() => cartStore.items, (items) => {
    if (items.length > 0 && selectedProductIds.value.length === 0) {
        selectedProductIds.value = items.map(i => i.product_id)
    }
}, { immediate: true })

watch(
    () => [cartStore.items.length, pageSize.value],
    () => {
        const maxPage = Math.max(1, Math.ceil(cartStore.items.length / pageSize.value))
        if (currentPage.value > maxPage) currentPage.value = maxPage
    }
)

onMounted(async () => {
    await cartStore.fetchCart()
    loadExtras()
})
</script>

<style scoped>
.cart-container {
    max-width: 1200px;
    margin: 40px auto;
    padding: 0 20px;
}

.page-header h2 {
    font-size: 2.5rem;
    margin-bottom: 30px;
    font-family: var(--font-serif);
    color: var(--color-secondary);
    text-align: center;
}

.empty-cart {
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

.empty-cart h3 {
    margin-bottom: 32px;
    color: var(--color-text-light);
    font-weight: 400;
}

.cart-toolbar {
    margin-bottom: 20px;
    padding: 15px 20px;
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: var(--shadow-card);
}

.cart-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.cart-item-card {
    display: flex;
    align-items: flex-start;
    background: var(--color-white);
    padding: 24px;
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    transition: all 0.3s ease;
    gap: 24px;
}

.cart-item-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.card-checkbox {
    padding-top: 10px;
}

.card-image {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    flex-shrink: 0;
}

.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.card-image:hover img {
    transform: scale(1.1);
}

.card-info {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 120px;
}

.info-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.card-info h3 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--color-text-main);
    cursor: pointer;
    transition: color 0.3s;
    font-weight: 600;
}

.card-info h3:hover {
    color: var(--color-primary);
}

.item-price {
    font-weight: 700;
    color: var(--color-secondary);
    font-size: 1.1rem;
}

.dims {
    font-size: 0.9rem;
    color: var(--color-text-light);
    margin-top: 5px;
}

.info-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
}

.subtotal {
    font-weight: 600;
    color: var(--color-primary);
}

.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    justify-content: flex-end;
}

/* Coupon Section */
.cart-footer {
    margin-top: 40px;
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}

@media (min-width: 992px) {
    .cart-footer {
        grid-template-columns: 2fr 1fr;
    }
}

.coupon-container {
    padding: 24px;
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: var(--shadow-card);
}

.coupon-container h4 {
    margin-bottom: 20px;
    color: var(--color-secondary);
}

.coupon-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Summary Section */
.summary {
    background: var(--color-white);
    padding: 30px;
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    height: fit-content;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    color: var(--color-text-main);
}

.summary-row.discount {
    color: #4CAF50;
}

.summary-total {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 24px;
}

.summary-total h3 {
    font-size: 1.5rem;
    color: var(--color-secondary);
    font-family: var(--font-serif);
}

.checkout-btn {
    width: 100%;
    font-weight: 600;
    height: 50px;
    border-radius: 25px;
    font-size: 1.1rem;
    background-color: var(--color-primary);
    border: none;
    transition: all 0.3s;
}

.checkout-btn:hover:not(:disabled) {
    background-color: var(--color-accent);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(139, 110, 78, 0.3);
}

/* Recommendations */
.recommendations {
    margin: 40px 0;
    padding: 30px;
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    border: 1px dashed var(--color-primary);
}

.recommendations h3 {
    text-align: center;
    color: var(--color-primary);
    margin-bottom: 24px;
}

.rec-list {
    display: flex;
    gap: 20px;
    padding: 10px;
}

.rec-item {
    min-width: 160px;
    background: var(--color-bg);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s;
}

.rec-item:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-hover);
}

.rec-item img {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 10px;
}

.rec-name {
    display: block;
    font-weight: 500;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rec-price {
    display: block;
    color: var(--color-secondary);
    font-weight: 700;
    margin-bottom: 10px;
}

@media (max-width: 768px) {
    .cart-item-card {
        flex-direction: column;
        align-items: stretch;
    }
    
    .card-image {
        width: 100%;
        height: 200px;
    }
    
    .card-info {
        height: auto;
        gap: 15px;
    }
    
    .info-bottom {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .action-buttons {
        justify-content: space-between;
        width: 100%;
    }
}
</style>
