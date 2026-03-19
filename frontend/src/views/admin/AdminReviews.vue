
<template>
  <div class="admin-reviews">
    <h2>Customer Reviews</h2>
    <el-table :data="pagedReviews" v-loading="loading">
        <el-table-column prop="product_name" label="Product" width="200">
            <template #default="scope">
                <div style="display: flex; align-items: center;">
                    <el-image :src="scope.row.product_thumbnail" style="width: 40px; height: 40px; margin-right: 10px;" />
                    <span>{{ scope.row.product_name }}</span>
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="username" label="User" width="120" />
        <el-table-column prop="review_type" label="Type" width="100">
            <template #default="scope">
                <el-tag :type="scope.row.review_type === 'long_term' ? 'warning' : ''">
                    {{ scope.row.review_type === 'long_term' ? 'Long-term' : 'Instant' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="rating" label="Ratings" width="200">
            <template #default="scope">
                <div style="font-size: 0.9em;">
                    <div>Overall: <el-rate v-model="scope.row.rating" disabled show-score text-color="#ff9900" size="small" /></div>
                    <div v-if="scope.row.rating_logistics">Logistics: <el-rate v-model="scope.row.rating_logistics" disabled show-score text-color="#ff9900" size="small" /></div>
                    <div v-if="scope.row.rating_service">Service: <el-rate v-model="scope.row.rating_service" disabled show-score text-color="#ff9900" size="small" /></div>
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="comment" label="Comment" />
        <el-table-column label="Date" width="150">
            <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleDateString() }}
            </template>
        </el-table-column>
        <el-table-column label="Reply" width="100">
            <template #default="scope">
                <el-button type="primary" size="small" @click="openReplyDialog(scope.row)">
                    {{ scope.row.vendor_reply ? 'Edit Reply' : 'Reply' }}
                </el-button>
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

    <el-dialog v-model="replyVisible" title="Reply to Review" width="500px">
        <div v-if="currentReview" style="margin-bottom: 20px; background: #f9f9f9; padding: 10px; border-radius: 4px;">
            <p><strong>User:</strong> {{ currentReview.username }}</p>
            <p><strong>Comment:</strong> {{ currentReview.comment }}</p>
            <p><strong>Type:</strong> {{ currentReview.review_type }}</p>
        </div>
        <el-input v-model="replyText" type="textarea" :rows="4" placeholder="Write your reply..." />
        <template #footer>
            <el-button @click="replyVisible = false">Cancel</el-button>
            <el-button type="primary" @click="submitReply" :loading="replyLoading">Submit Reply</el-button>
        </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAdminReviews, replyReview } from '@/api/review'
import { ElMessage } from 'element-plus'

const reviews = ref([])
const loading = ref(false)
const replyVisible = ref(false)
const currentReview = ref(null)
const replyText = ref('')
const replyLoading = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)

const total = computed(() => reviews.value.length)
const pagedReviews = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return reviews.value.slice(start, start + pageSize.value)
})

const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
}

const handlePageChange = (page) => {
    currentPage.value = page
}

const fetchReviews = async () => {
    loading.value = true
    try {
        const res = await getAdminReviews()
        reviews.value = Array.isArray(res) ? res : res.results
        currentPage.value = 1
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const openReplyDialog = (review) => {
    currentReview.value = review
    replyText.value = review.vendor_reply || ''
    replyVisible.value = true
}

const submitReply = async () => {
    if (!replyText.value) return
    replyLoading.value = true
    try {
        await replyReview(currentReview.value.id, { reply: replyText.value })
        ElMessage.success('Reply submitted')
        replyVisible.value = false
        fetchReviews()
    } catch (e) {
        console.error(e)
        ElMessage.error('Failed to submit reply')
    } finally {
        replyLoading.value = false
    }
}

onMounted(() => {
    fetchReviews()
})
</script>

<style scoped>
.admin-reviews {
    padding: 20px;
}
</style>
