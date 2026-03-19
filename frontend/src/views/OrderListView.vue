<template>
  <div>
    <h2>{{ isVendor ? 'Vendor Order Management' : 'My Orders' }}</h2>
    <div style="margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
        <el-input v-if="isVendor" v-model="filterForm.username" placeholder="Username" style="width: 150px;" clearable @clear="fetchOrders" @keyup.enter="handleFilter" />
        <el-input v-if="isVendor" v-model="filterForm.user_id" placeholder="User ID" style="width: 100px;" clearable @clear="fetchOrders" @keyup.enter="handleFilter" />
        <el-input v-model="filterForm.order_id" placeholder="Order ID" style="width: 100px;" clearable @clear="fetchOrders" @keyup.enter="handleFilter" />
        <el-select v-model="filterForm.status" placeholder="Status" clearable style="width: 150px;" @change="handleFilter">
            <el-option label="Pending" value="Pending" />
            <el-option label="Shipped" value="Shipped" />
            <el-option label="Cancelled" value="Cancelled" />
            <el-option label="Hold" value="Hold" />
        </el-select>
        <el-button type="primary" @click="handleFilter">Filter</el-button>
    </div>
    <el-table :data="orders" style="width: 100%" v-loading="loading">
        <el-table-column label="Order" width="80">
            <template #default="scope">
                {{ scope.row.id }}
            </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Date" width="180">
            <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleDateString() }}<br>
                <span style="color: #999; font-size: 0.85em;">{{ new Date(scope.row.created_at).toLocaleTimeString() }}</span>
            </template>
        </el-table-column>
        <el-table-column v-if="isVendor" label="User" width="120">
            <template #default="scope">
                <div style="line-height: 1.2;">
                    <div>{{ scope.row.username }}</div>
                    <div style="color: #999; font-size: 0.85em;">ID: {{ scope.row.user_id }}</div>
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
                <el-tag size="small">{{ scope.row.status }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="Total" min-width="100">
             <template #default="scope">
                ${{ scope.row.total_amount }}
            </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
             <template #default="scope">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <el-button size="small" @click="showDetail(scope.row)" style="margin-left: 0; width: 100%;">Detail</el-button>
                    
                    <template v-if="!isVendor && (scope.row.status === 'Pending' || scope.row.status === 'Hold')">
                        <el-button 
                            type="danger" 
                            size="small" 
                            @click="handleCancel(scope.row)"
                            style="margin-left: 0; width: 100%;"
                        >
                            Cancel
                        </el-button>
                    </template>

                    <template v-if="isVendor && (scope.row.status === 'Pending' || scope.row.status === 'Hold')">
                        <el-button 
                            type="success" 
                            size="small" 
                            @click="handleShip(scope.row)"
                            style="margin-left: 0; width: 100%;"
                        >
                            Ship
                        </el-button>
                        <el-button 
                            v-if="scope.row.status === 'Pending'"
                            type="warning" 
                            size="small" 
                            @click="handleHold(scope.row)"
                            style="margin-left: 0; width: 100%;"
                        >
                            Hold
                        </el-button>
                        <el-button 
                            type="danger" 
                            size="small" 
                            @click="handleVendorCancel(scope.row)"
                            style="margin-left: 0; width: 100%;"
                        >
                            Cancel
                        </el-button>
                    </template>
                </div>
            </template>
        </el-table-column>
    </el-table>

    <div style="margin-top: 20px; text-align: right;" v-if="total > 0">
        <el-pagination 
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
    </div>

    <el-dialog v-model="detailVisible" title="Order Details" width="600px">
        <div v-if="currentOrder">
            <p><strong>Order ID:</strong> {{ currentOrder.id }}</p>
            <p><strong>Date:</strong> {{ new Date(currentOrder.created_at).toLocaleString() }}</p>
            <p v-if="currentOrder.shipped_at"><strong>Shipped Date:</strong> {{ new Date(currentOrder.shipped_at).toLocaleString() }}</p>
            <p v-if="currentOrder.cancelled_at"><strong>Cancelled Date:</strong> {{ new Date(currentOrder.cancelled_at).toLocaleString() }}</p>
            <p><strong>Status:</strong> <el-tag>{{ currentOrder.status }}</el-tag></p>
            <p><strong>Shipping Address:</strong> {{ currentOrder.shipping_address || 'N/A' }}</p>
            <el-divider>Items</el-divider>
            <el-table :data="currentOrder.items" style="width: 100%">
                <el-table-column prop="product_name" label="Product">
                    <template #default="scope">
                        <div>
                            <span 
                                style="color: #409EFF; cursor: pointer; text-decoration: underline;" 
                                @click="$router.push(`/product/${scope.row.product_id}`)"
                            >
                                {{ scope.row.product_name }}
                            </span>
                            <div v-if="scope.row.custom_dimensions" style="font-size: 0.8em; color: #999;">
                                Dimensions: {{ scope.row.custom_dimensions }}
                            </div>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column prop="quantity" label="Quantity" width="100" />
                <el-table-column label="Unit Price" width="100">
                    <template #default="scope">
                        ${{ Number(scope.row.unit_price).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column label="Subtotal" width="100">
                    <template #default="scope">
                        ${{ (scope.row.unit_price * scope.row.quantity).toFixed(2) }}
                    </template>
                </el-table-column>
                <el-table-column label="Review" width="140" v-if="!isVendor && (currentOrder.status === 'Shipped' || currentOrder.status === 'Completed')">
                    <template #default="scope">
                        <div style="display: flex; flex-direction: column; gap: 5px;">
                            <el-button v-if="!scope.row.has_review" type="primary" size="small" @click="openReviewDialog(scope.row)">Review</el-button>
                            <el-button v-else type="success" size="small" @click="$router.push(`/product/${scope.row.product_id}`)">View/Edit</el-button>
                            
                            <!-- Long-term review buttons moved to Product Detail Page > Long-term Review Tab -->
                        </div>
                    </template>
                </el-table-column>
            </el-table>
            <div style="text-align: right; margin-top: 20px; font-size: 1.2em; font-weight: bold;">
                <div v-if="Number(currentOrder.total_amount) < 999 && currentOrder.items.reduce((acc, item) => acc + (item.unit_price * item.quantity), 0) < 999" style="font-size: 0.8em; color: #f56c6c; margin-bottom: 5px;">
                    Shipping Fee: $20.00
                </div>
                <div v-if="currentOrder.discount_amount > 0" style="font-size: 0.8em; color: green; margin-bottom: 5px;">
                    Discount ({{ currentOrder.coupon_code }}): -${{ currentOrder.discount_amount }}
                </div>
                Total: ${{ Number(currentOrder.total_amount).toFixed(2) }}
            </div>
        </div>
    </el-dialog>

    <!-- Review Dialog -->
    <el-dialog v-model="reviewVisible" :title="reviewForm.stage > 0 ? `Long-term Review (${reviewForm.stage} Days)` : 'Write Review'" width="500px">
        <el-form :model="reviewForm" label-position="top">
            <!-- X7: Multi-dimensional Scoring -->
            <template v-if="reviewForm.stage > 0">
                <el-form-item label="Durability & Quality">
                    <el-rate v-model="reviewForm.rating" show-text />
                </el-form-item>
                <!-- Long-term doesn't need logistics/service ratings usually, or we repurpose them -->
                <!-- Let's just keep single rating for simplicity or repurpose -->
            </template>
            <template v-else>
                <el-form-item label="Item as Described">
                    <el-rate v-model="reviewForm.rating" show-text />
                </el-form-item>
                <el-form-item label="Logistics Service">
                    <el-rate v-model="reviewForm.rating_logistics" show-text />
                </el-form-item>
                <el-form-item label="Service Attitude">
                    <el-rate v-model="reviewForm.rating_service" show-text />
                </el-form-item>
            </template>

            <!-- X8: Preset Tags -->
            <div style="margin-bottom: 10px;">
                <span style="font-size: 0.9em; color: #666; margin-right: 10px;">Quick Tags:</span>
                <el-tag 
                    v-for="tag in currentTags" 
                    :key="tag" 
                    style="margin-right: 5px; cursor: pointer;" 
                    @click="addTag(tag)"
                    effect="plain"
                >
                    {{ tag }}
                </el-tag>
            </div>

            <el-form-item :label="reviewForm.stage > 0 ? 'Usage Experience' : 'Comment'">
                <el-input v-model="reviewForm.comment" type="textarea" :rows="4" :placeholder="reviewForm.stage > 0 ? 'How has the product held up? Any issues?' : 'Write your review here...'" />
            </el-form-item>
            
            <el-form-item label="Photos">
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <div v-for="(photo, index) in reviewForm.photos" :key="index" style="position: relative;">
                        <img :src="photo" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />
                        <div 
                            style="position: absolute; top: -5px; right: -5px; background: red; color: white; border-radius: 50%; cursor: pointer; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 12px;"
                            @click="removeReviewPhoto(index)"
                        >
                            x
                        </div>
                    </div>
                    <el-upload
                        action="#"
                        :show-file-list="false"
                        :auto-upload="true"
                        :http-request="uploadReviewPhoto"
                    >
                        <div style="width: 80px; height: 80px; border: 1px dashed #d9d9d9; border-radius: 4px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                            <el-icon><Plus /></el-icon>
                        </div>
                    </el-upload>
                </div>
            </el-form-item>

            <!-- X9: Anonymous Review -->
            <el-form-item>
                <el-checkbox v-model="reviewForm.is_anonymous">Post Anonymously</el-checkbox>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="reviewVisible = false">Cancel</el-button>
            <el-button type="primary" @click="submitReview" :loading="reviewLoading">Submit Review</el-button>
        </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getOrders, getOrder, cancelOrder, shipOrder, holdOrder, getAdminOrders, getAdminOrder } from '@/api/order'
import { createReview, createLongTermReview } from '@/api/review'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const route = useRoute()
const orders = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentOrder = ref(null)

// Review Dialog
const reviewVisible = ref(false)
const reviewForm = ref({
    rating: 5,
    rating_logistics: 5,
    rating_service: 5,
    comment: '',
    photos: [], // URLs
    review_type: 'instant', // T4
    is_anonymous: false
})
const currentOrderItem = ref(null)
const reviewLoading = ref(false)

const presetTags = ['High Quality', 'Fast Shipping', 'Great Service', 'Value for Money', 'Recommended']
const longTermTags = ['Still Good', 'Very Durable', 'Worn Out', 'Worth the Wait', 'Good Condition', 'Issues Appeared']

const currentTags = computed(() => {
    return reviewForm.value.stage > 0 ? longTermTags : presetTags
})

const addTag = (tag) => {
    if (reviewForm.value.comment) {
        reviewForm.value.comment += ` ${tag}`
    } else {
        reviewForm.value.comment = tag
    }
}

const openReviewDialog = (item, stage = 0) => {
    currentOrderItem.value = item
    reviewForm.value = { 
        rating: 5, 
        rating_logistics: 5, 
        rating_service: 5, 
        comment: '', 
        photos: [], 
        review_type: stage > 0 ? 'long_term' : 'instant',
        is_anonymous: false,
        stage: stage
    }
    reviewVisible.value = true
}

const uploadReviewPhoto = async (options) => {
    const { file } = options
    const formData = new FormData()
    formData.append('file', file)
    
    try {
        const { default: request } = await import('@/utils/request')
        const res = await request({
            url: '/upload/',
            method: 'post',
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        reviewForm.value.photos.push(res.url)
        ElMessage.success('Photo uploaded')
    } catch (e) {
        console.error(e)
        ElMessage.error('Upload failed')
    }
}

const removeReviewPhoto = (index) => {
    reviewForm.value.photos.splice(index, 1)
}

const submitReview = async () => {
    if (!reviewForm.value.comment) {
        ElMessage.warning('Please write a comment')
        return
    }
    
    reviewLoading.value = true
    try {
        if (reviewForm.value.stage > 0) {
            // Long-term review
            await createLongTermReview({
                user_id: authStore.user.id,
                order_item_id: currentOrderItem.value.id,
                rating: reviewForm.value.rating,
                comment: reviewForm.value.comment,
                photos: reviewForm.value.photos,
                is_anonymous: reviewForm.value.is_anonymous,
                stage: reviewForm.value.stage
            })
        } else {
            // Instant review
            await createReview({
                user_id: authStore.user.id,
                order_item_id: currentOrderItem.value.id,
                rating: reviewForm.value.rating,
                rating_logistics: reviewForm.value.rating_logistics,
                rating_service: reviewForm.value.rating_service,
                comment: reviewForm.value.comment,
                photos: reviewForm.value.photos,
                is_anonymous: reviewForm.value.is_anonymous
            })
        }
        ElMessage.success('Review submitted successfully')
        reviewVisible.value = false
        // Refresh order details to update "Reviewed" status
        showDetail(currentOrder.value) 
    } catch (e) {
        console.error(e)
        // Error message handled by request interceptor (e.g. profanity)
    } finally {
        reviewLoading.value = false
    }
}


// Pagination & Filter
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterForm = ref({
    status: '',
    username: '',
    user_id: '',
    order_id: ''
})

const isVendor = computed(() => {
    return route.path.startsWith('/admin')
})

const showDetail = async (order) => {
    loading.value = true
    try {
        let fullOrder
        if (isVendor.value) {
            fullOrder = await getAdminOrder(order.id)
        } else {
            fullOrder = await getOrder(order.id)
        }
        currentOrder.value = fullOrder
        detailVisible.value = true
    } catch (e) {
        console.error(e)
        ElMessage.error('Failed to load order details')
    } finally {
        loading.value = false
    }
}

const fetchOrders = async () => {
    // If not vendor, require login
    if (!isVendor.value && !authStore.token) return 

    loading.value = true
    try {
        const params = {
            page: currentPage.value,
            page_size: pageSize.value
        }
        
        if (filterForm.value.status) params.status = filterForm.value.status
        if (filterForm.value.username) params.username = filterForm.value.username
        if (filterForm.value.user_id) params.user_id = filterForm.value.user_id
        if (filterForm.value.order_id) params.order_id = filterForm.value.order_id
        
        let res
        if (isVendor.value) {
            res = await getAdminOrders(params)
            orders.value = res.results
            total.value = res.total
        } else {
            // User API
            res = await getOrders(params)
            let data = Array.isArray(res) ? res : res.results
            // Sort by created_at descending
            data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            
            // Client side pagination for user view
            // If filtering by Order ID, the backend will return only 1 match (or 0)
            // But we still need to handle it.
            // If filter params exist, we might not need client side pagination logic if backend filtered,
            // BUT backend 'orders_list' doesn't support pagination params yet (it ignores page/page_size)
            // So we always do client-side pagination for user orders.
            
            total.value = data.length
            const start = (currentPage.value - 1) * pageSize.value
            const end = start + pageSize.value
            orders.value = data.slice(start, end)
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const handleFilter = () => {
    currentPage.value = 1
    fetchOrders()
}

const handleSizeChange = (val) => {
    pageSize.value = val
    fetchOrders()
}

const handlePageChange = (val) => {
    currentPage.value = val
    fetchOrders()
}

const handleCancel = (order) => {
    ElMessageBox.confirm(
        'Are you sure you want to cancel this order?',
        'Warning',
        {
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          type: 'warning',
        }
    ).then(async () => {
        try {
            await cancelOrder(order.id)
            ElMessage.success('Order cancelled')
            fetchOrders()
        } catch (e) {
            console.error(e)
        }
    })
}

const handleHold = (order) => {
     ElMessageBox.confirm(
        'Are you sure you want to hold this order?',
        'Confirm',
        {
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          type: 'info',
        }
    ).then(async () => {
        try {
            await holdOrder(order.id)
            ElMessage.success('Order status changed to Hold')
            fetchOrders()
        } catch (e) {
            console.error(e)
            ElMessage.error('Failed to hold order')
        }
    })
}

const handleShip = (order) => {
     ElMessageBox.confirm(
        'Are you sure you want to mark this order as shipped?',
        'Confirm',
        {
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          type: 'info',
        }
    ).then(async () => {
        try {
            await shipOrder(order.id)
            ElMessage.success('Order shipped')
            fetchOrders()
        } catch (e) {
            console.error(e)
            ElMessage.error('Failed to ship order')
        }
    })
}

const handleVendorCancel = (order) => {
    ElMessageBox.confirm(
        'Are you sure you want to cancel this order?',
        'Warning',
        {
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          type: 'warning',
        }
    ).then(async () => {
        try {
            await cancelOrder(order.id)
            ElMessage.success('Order cancelled')
            fetchOrders()
        } catch (e) {
            console.error(e)
            ElMessage.error('Failed to cancel order')
        }
    })
}

onMounted(async () => {
    const orderId = route.query.order_id
    if (orderId) {
        filterForm.value.order_id = orderId
    }
    await fetchOrders()
    if (orderId) {
        await showDetail({ id: Number(orderId) })
    }
})
</script>
