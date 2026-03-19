<template>
  <div class="admin-analytics-container">
    <h1 class="page-title">Admin Analytics Dashboard</h1>

    <div class="analytics-grid">
      <!-- Search Analytics Section -->
      <section class="analytics-card">
        <h2>🔍 Top Search Terms</h2>
        <div class="card-content-scroll">
            <div v-if="loadingSearch" class="loading">Loading...</div>
            <div v-else-if="searchData.length === 0" class="empty">No search history yet.</div>
            <ul v-else class="data-list">
              <li v-for="(item, index) in searchData" :key="index">
                <span class="rank">#{{ index + 1 }}</span>
                <div class="keyword-wrapper">
                    <span class="keyword">{{ item.keyword }}</span>
                    <router-link 
                        v-if="item.product_id" 
                        :to="{ name: 'admin-product-edit', params: { id: item.product_id } }"
                        class="match-link"
                        title="Edit matched product"
                    >
                        <el-icon><Edit /></el-icon> {{ item.product_name }}
                    </router-link>
                </div>
                <span class="count">{{ item.count }}</span>
              </li>
            </ul>
        </div>
      </section>

      <!-- Wishlist Analytics Section -->
      <section class="analytics-card">
        <h2>❤️ Wishlist Popularity</h2>
        <p class="subtitle">Issue targeted coupons to interested users</p>
        
        <div class="card-content-scroll">
            <div v-if="loadingWishlist" class="loading">Loading...</div>
            <div v-else-if="wishlistData.length === 0" class="empty">No wishlist data yet.</div>
            <table v-else class="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Product</th>
                  <th>Wishlist Count</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in wishlistData" :key="item.id">
                  <td>#{{ index + 1 }}</td>
                  <td class="product-name">{{ item.name }}</td>
                  <td class="highlight">{{ item.wishlist_count }}</td>
                  <td>${{ item.price }}</td>
                  <td>{{ item.stock }}</td>
                  <td>
                    <button 
                      class="action-btn" 
                      @click="openCouponModal(item)"
                      :disabled="item.wishlist_count === 0"
                    >
                      Issue Coupon
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
        </div>
      </section>

      <!-- Browse History Section -->
      <section class="analytics-card">
        <h2>👀 User Browse History</h2>
        <div class="card-content-scroll">
            <div v-if="loadingBrowse" class="loading">Loading...</div>
            <div v-else-if="browseData.length === 0" class="empty">No browse history yet.</div>
            <div v-else>
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Product</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in browseData" :key="item.id">
                      <td>{{ item.username }}</td>
                      <td>{{ item.product_name }}</td>
                      <td>{{ new Date(item.viewed_at).toLocaleString() }}</td>
                    </tr>
                  </tbody>
                </table>
                <!-- Pagination -->
                <div class="pagination" v-if="browseTotal > browsePageSize">
                    <button :disabled="browsePage === 1" @click="changeBrowsePage(browsePage - 1)">Prev</button>
                    <span>Page {{ browsePage }}</span>
                    <button :disabled="browsePage * browsePageSize >= browseTotal" @click="changeBrowsePage(browsePage + 1)">Next</button>
                </div>
            </div>
        </div>
      </section>
    </div>

    <!-- Coupon Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Issue Coupon for "{{ selectedProduct?.name }}"</h3>
        <p>Targeting {{ selectedProduct?.wishlist_count }} users.</p>
        
        <div class="form-group">
          <label>Discount Amount ($)</label>
          <input type="number" v-model="couponForm.amount" min="1" step="0.5">
        </div>
        
        <div class="form-group">
          <label>Valid Days</label>
          <input type="number" v-model="couponForm.days" min="1">
        </div>

        <div class="modal-actions">
          <button @click="closeModal" class="cancel-btn">Cancel</button>
          <button @click="issueCoupon" class="confirm-btn" :disabled="processing">
            {{ processing ? 'Issuing...' : 'Send Coupons' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { Edit } from '@element-plus/icons-vue'

const searchData = ref([])
const wishlistData = ref([])
const browseData = ref([])
const loadingSearch = ref(true)
const loadingWishlist = ref(true)
const loadingBrowse = ref(true)

const browsePage = ref(1)
const browsePageSize = ref(10)
const browseTotal = ref(0)

const showModal = ref(false)
const selectedProduct = ref(null)
const processing = ref(false)
const couponForm = ref({
  amount: 5,
  days: 7
})

const fetchSearchAnalytics = async () => {
  try {
    const response = await request.get('/admin/analytics/search/')
    searchData.value = response
  } catch (error) {
    console.error('Failed to fetch search analytics', error)
  } finally {
    loadingSearch.value = false
  }
}

const fetchWishlistAnalytics = async () => {
  try {
    const response = await request.get('/admin/analytics/wishlist/')
    wishlistData.value = response
  } catch (error) {
    console.error('Failed to fetch wishlist analytics', error)
  } finally {
    loadingWishlist.value = false
  }
}

const fetchBrowseAnalytics = async () => {
    loadingBrowse.value = true
    try {
        const res = await request.get('/admin/analytics/browse/', {
            params: { page: browsePage.value, page_size: browsePageSize.value }
        })
        browseData.value = res.results
        browseTotal.value = res.total
    } catch (error) {
        console.error(error)
    } finally {
        loadingBrowse.value = false
    }
}

const changeBrowsePage = (p) => {
    browsePage.value = p
    fetchBrowseAnalytics()
}

const openCouponModal = (product) => {
  selectedProduct.value = product
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedProduct.value = null
  couponForm.value = { amount: 5, days: 7 }
}

const issueCoupon = async () => {
  if (!selectedProduct.value) return
  
  processing.value = true
  try {
    const response = await request.post('/admin/marketing/wishlist-coupon/', {
      product_id: selectedProduct.value.id,
      discount_amount: couponForm.value.amount,
      days_valid: couponForm.value.days
    })
    alert(response.message)
    closeModal()
  } catch (error) {
    console.error('Failed to issue coupon', error)
    alert('Failed to issue coupon')
  } finally {
    processing.value = false
  }
}

onMounted(() => {
  fetchSearchAnalytics()
  fetchWishlistAnalytics()
  fetchBrowseAnalytics()
})
</script>

<style scoped>
.admin-analytics-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Merriweather', serif;
  color: #5D4037;
}

.page-title {
  text-align: center;
  margin-bottom: 40px;
  font-size: 2.5rem;
  color: #3E2723;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

@media (min-width: 768px) {
  .analytics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.analytics-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border: 1px solid #EFEBE9;
  display: flex;
  flex-direction: column;
  height: 500px; /* Fixed height */
}

.card-content-scroll {
    flex: 1;
    overflow-y: auto; /* Enable vertical scroll */
    padding-right: 5px; /* Space for scrollbar */
}

/* Custom scrollbar styling */
.card-content-scroll::-webkit-scrollbar {
    width: 6px;
}
.card-content-scroll::-webkit-scrollbar-track {
    background: #f1f1f1; 
}
.card-content-scroll::-webkit-scrollbar-thumb {
    background: #D7CCC8; 
    border-radius: 3px;
}
.card-content-scroll::-webkit-scrollbar-thumb:hover {
    background: #A1887F; 
}

.analytics-card h2 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  border-bottom: 2px solid #D7CCC8;
  padding-bottom: 10px;
}

.subtitle {
  color: #8D6E63;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.data-list {
  list-style: none;
  padding: 0;
}

.data-list li {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.rank {
  font-weight: bold;
  color: #A1887F;
  width: 40px;
}

.keyword-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.keyword {
  font-weight: 600;
}

.match-link {
    font-size: 0.8rem;
    color: #8D6E63;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 2px;
}

.match-link:hover {
    text-decoration: underline;
    color: #5D4037;
}

.count {
  color: #8D6E63;
  align-self: center; /* Center vertically if multiple lines */
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background-color: #FAFAFA;
  font-weight: 600;
  color: #5D4037;
}

.highlight {
  color: #D84315;
  font-weight: bold;
}

.action-btn {
  background-color: #8D6E63;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover:not(:disabled) {
  background-color: #6D4C41;
}

.action-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #5D4037;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #D7CCC8;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  background: transparent;
  border: 1px solid #8D6E63;
  color: #8D6E63;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn {
  background: #8D6E63;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
