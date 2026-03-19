<template>
  <div>
    <div v-if="loading" style="text-align: center; padding: 50px;">
        <el-icon class="is-loading" size="30"><Loading /></el-icon>
        <p>Loading product...</p>
    </div>
    <div v-else>
        <el-button @click="goBack" style="margin-bottom: 20px;">Back</el-button>
        <el-row :gutter="40" v-if="product">
            <el-col :xs="24" :md="10">
                <el-carousel v-if="mediaList.length > 0" :height="carouselHeight" indicator-position="outside" :autoplay="false">
                    <el-carousel-item v-for="(item, index) in mediaList" :key="item.id">
                        <div v-if="item.type === 'video'" style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #000;">
                             <video 
                                :src="item.url" 
                                controls 
                                style="max-width: 100%; max-height: 100%;"
                            ></video>
                        </div>
                        <el-image 
                            v-else
                            :src="item.url" 
                            style="width: 100%; height: 100%;" 
                            fit="contain" 
                            :preview-src-list="imagePreviewList"
                            :initial-index="getPreviewIndex(item.url)"
                            hide-on-click-modal
                            preview-teleported
                        />
                    </el-carousel-item>
                </el-carousel>
                <el-image 
                    v-else 
                    :src="product.thumbnail" 
                    style="width: 100%; height: auto; max-height: 400px; border-radius: 8px;" 
                    fit="contain"
                    :preview-src-list="[product.thumbnail]"
                    hide-on-click-modal
                    preview-teleported
                />
            </el-col>
            <el-col :xs="24" :md="14">
                <h1 class="product-title">{{ product.name }}</h1>
                <p class="category">Category: {{ product.category_name }}</p>
                <p class="price">${{ product.price }}</p>
                <el-divider />
                <p class="description">{{ product.description }}</p>

                <!-- C1: Extra attributes -->
                <div v-if="product.features || (product.tags && product.tags.length > 0 && product.tags.some(t => t.trim() !== ''))" style="margin-top: 20px; background: #f9f9f9; padding: 15px; border-radius: 8px;">
                    <div v-if="product.features" style="margin-top: 15px;">
                        <h4>Features</h4>
                        <div v-html="product.features" style="margin-top: 5px; padding-left: 20px;"></div>
                    </div>
                    
                    <div v-if="product.tags && product.tags.length > 0 && product.tags.some(t => t.trim() !== '')" style="margin-top: 15px;">
                        <strong>Tags:</strong>
                        <div style="margin-top: 5px;">
                            <template v-for="(tag, index) in product.tags" :key="index">
                                <el-tag 
                                    v-if="tag && tag.trim()"
                                    style="margin-right: 8px; margin-bottom: 5px;"
                                    type="info"
                                    effect="plain"
                                >
                                    #{{ tag }}
                                </el-tag>
                            </template>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; display: flex; align-items: center;">
                    <el-input-number v-model="quantity" :min="1" :max="Math.max(1, product.stock_quantity)" controls-position="right" :disabled="product.stock_quantity <= 0" />
                    <el-button type="primary" style="margin-left: 20px;" @click="handleAddToCart" :disabled="product.stock_quantity <= 0">
                        {{ product.stock_quantity <= 0 ? 'Sold Out' : 'Add to Cart' }}
                    </el-button>
                    <el-button type="danger" plain style="margin-left: 10px;" @click="handleAddToWishlist">
                        <el-icon><Star /></el-icon>
                    </el-button>
                    <!-- X10: Contact Seller -->
                    <el-button type="info" plain style="margin-left: 10px;" @click="$router.push('/chat')">
                        <el-icon><ChatDotRound /></el-icon> Chat
                    </el-button>
                    <!-- X11: Space Fit Check -->
                    <el-button v-if="product.width && product.height" type="warning" plain style="margin-left: 10px;" @click="showFitDialog = true">
                        <el-icon><FullScreen /></el-icon> Check Fit
                    </el-button>
                </div>
                <p style="margin-top: 10px; color: #999;">Stock: {{ product.stock_quantity }}</p>
            </el-col>
        </el-row>
        
        <!-- Tabs for Reviews and Q&A -->
        <div style="margin-top: 50px;">
            <el-tabs v-model="activeTab" @tab-click="handleTabClick">
                <el-tab-pane label="Instant Reviews" name="instant">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Customer Reviews ({{ instantReviews.length }})</h3>
                        <el-select v-model="reviewSort" placeholder="Sort by" style="width: 150px" @change="fetchReviews">
                            <el-option label="Most Helpful" value="helpful" />
                            <el-option label="Newest" value="newest" />
                            <el-option label="Highest Rating" value="highest" />
                            <el-option label="Lowest Rating" value="lowest" />
                        </el-select>
                    </div>
                    <div v-if="instantReviews.length > 0">
                        <div v-for="review in instantReviews" :key="review.id" style="border-bottom: 1px solid #eee; padding: 20px 0;">
                            <!-- Review Item Component Logic Here -->
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <el-rate v-model="review.rating" disabled show-score text-color="#ff9900" />
                                <span style="margin-left: 10px; font-weight: bold; color: #333;">{{ review.username }}</span>
                                <span style="margin-left: auto; color: #999; font-size: 0.9em;">{{ new Date(review.created_at).toLocaleDateString() }}</span>
                            </div>
                            <p style="margin: 10px 0; line-height: 1.5;">{{ review.comment }}</p>
                            
                            <div v-if="review.photos && review.photos.length > 0" style="margin-top: 10px; display: flex; gap: 10px;">
                                <el-image 
                                    v-for="photo in review.photos" 
                                    :key="photo.id" 
                                    :src="photo.image_url" 
                                    style="width: 100px; height: 100px; border-radius: 4px;"
                                    fit="cover"
                                    :preview-src-list="review.photos.map(p => p.image_url)"
                                    preview-teleported
                                />
                            </div>

                            <!-- Follow-ups -->
                            <div v-if="review.followups && review.followups.length > 0" style="margin-top: 15px; padding-left: 20px; border-left: 2px solid #eee;">
                                <div v-for="fp in review.followups" :key="fp.id" style="margin-bottom: 10px;">
                                    <p style="font-size: 0.9em; color: #666; margin: 0;"><strong>Follow-up ({{ new Date(fp.created_at).toLocaleDateString() }}):</strong> {{ fp.comment }}</p>
                                </div>
                            </div>
                            
                            <!-- Vendor Reply -->
                            <div v-if="review.vendor_reply" style="margin-top: 15px; background: #f0f9eb; padding: 15px; border-radius: 8px; border-left: 4px solid #67c23a;">
                                <div style="font-weight: bold; color: #67c23a; margin-bottom: 5px;">Vendor Reply:</div>
                                <p style="margin: 0; color: #606266;">{{ review.vendor_reply }}</p>
                                <div style="margin-top: 5px; font-size: 0.8em; color: #999;">{{ new Date(review.reply_at).toLocaleDateString() }}</div>
                            </div>

                            <!-- Actions: Vote, Edit, Delete, Follow-up -->
                            <div style="margin-top: 15px; display: flex; gap: 15px; align-items: center;">
                                <el-button 
                                    size="small" 
                                    :type="review.user_vote === 'helpful' ? 'success' : ''" 
                                    plain 
                                    @click="handleVote(review, 'helpful')"
                                    :disabled="authStore.user && authStore.user.id === review.user"
                                >
                                    Helpful ({{ review.helpful_count || 0 }})
                                </el-button>
                                <el-button 
                                    size="small" 
                                    :type="review.user_vote === 'unhelpful' ? 'warning' : ''" 
                                    plain 
                                    @click="handleVote(review, 'unhelpful')"
                                    :disabled="authStore.user && authStore.user.id === review.user"
                                >
                                    Unhelpful ({{ review.unhelpful_count || 0 }})
                                </el-button>

                                <template v-if="authStore.user && authStore.user.id === review.user">
                                    <el-divider direction="vertical" />
                                    <el-button size="small" type="primary" link @click="openEditReview(review)" :disabled="review.edit_count >= 1">Edit {{ review.edit_count >= 1 ? '(Limit Reached)' : '' }}</el-button>
                                    <el-button size="small" type="danger" link @click="handleDeleteReview(review)">Delete</el-button>
                                    <el-button size="small" type="primary" link @click="openFollowUp(review)">Add Follow-up</el-button>
                                </template>
                            </div>
                        </div>
                    </div>
                    <el-empty v-else description="No reviews yet" />
                </el-tab-pane>

                <el-tab-pane label="Long-term Reviews" name="long_term">
                    <div style="margin-bottom: 20px;">
                        <el-alert title="Long-term reviews focus on durability and performance after extended use." type="info" show-icon :closable="false" />
                    </div>

                    <!-- New Review Invitation Button -->
                    <div v-if="reviewEligibility && reviewEligibility.eligible && reviewEligibility.available_stage" style="margin-bottom: 20px;">
                        <el-alert
                            :title="`You have owned this product for ${reviewEligibility.days_owned} days!`"
                            type="success"
                            :description="`You are eligible to write a ${reviewEligibility.available_stage}-day review.`"
                            show-icon
                            :closable="false"
                            style="margin-bottom: 10px;"
                        />
                        <el-button type="primary" @click="openLongTermReviewDialog">
                            Write {{ reviewEligibility.available_stage }}-Day Review
                        </el-button>
                    </div>

                    <div v-if="longTermReviews.length > 0">
                         <div v-for="review in longTermReviews" :key="review.id" style="border-bottom: 1px solid #eee; padding: 20px 0;">
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <el-rate v-model="review.rating" disabled show-score text-color="#ff9900" />
                                <span style="margin-left: 10px; font-weight: bold; color: #333;">{{ review.username }}</span>
                                <el-tag v-if="review.stage" size="small" type="warning" style="margin-left: 10px;">{{ review.stage }} Days</el-tag>
                                <span style="margin-left: auto; color: #999; font-size: 0.9em;">{{ new Date(review.created_at).toLocaleDateString() }}</span>
                            </div>
                            <p style="margin: 10px 0; line-height: 1.5;">{{ review.comment }}</p>
                            
                            <div v-if="review.photos && review.photos.length > 0" style="margin-top: 10px; display: flex; gap: 10px;">
                                <el-image 
                                    v-for="photo in review.photos" 
                                    :key="photo.id" 
                                    :src="photo.image_url" 
                                    style="width: 100px; height: 100px; border-radius: 4px;"
                                    fit="cover"
                                    :preview-src-list="review.photos.map(p => p.image_url)"
                                    preview-teleported
                                />
                            </div>
                            
                            <!-- Vendor Reply -->
                            <div v-if="review.vendor_reply" style="margin-top: 15px; background: #f0f9eb; padding: 15px; border-radius: 8px; border-left: 4px solid #67c23a;">
                                <div style="font-weight: bold; color: #67c23a; margin-bottom: 5px;">Vendor Reply:</div>
                                <p style="margin: 0; color: #606266;">{{ review.vendor_reply }}</p>
                                <div style="margin-top: 5px; font-size: 0.8em; color: #999;">{{ new Date(review.reply_at).toLocaleDateString() }}</div>
                            </div>
                        </div>
                    </div>
                    <el-empty v-else description="No long-term reviews yet" />
                </el-tab-pane>



                <el-tab-pane label="Q&A" name="qa">
                    <div style="margin-bottom: 20px; display: flex; justify-content: space-between;">
                        <h3>Questions & Answers</h3>
                        <el-button type="primary" @click="qaDialogVisible = true">Ask Question</el-button>
                    </div>
                    <div v-if="questions.length > 0">
                        <div v-for="q in questions" :key="q.id" style="margin-bottom: 20px; border: 1px solid #eee; padding: 15px; border-radius: 4px;">
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <el-tag :type="q.tag === 'seller' ? 'danger' : 'success'" size="small" style="margin-right: 10px;">
                                    {{ q.tag === 'seller' ? 'Ask Seller' : 'Ask Buyers' }}
                                </el-tag>
                                <span style="font-weight: bold;">{{ q.username }}: </span>
                                <span style="margin-left: 5px;">{{ q.content }}</span>
                                <el-button 
                                    v-if="authStore.user && (authStore.user.id === q.user || authStore.user.is_staff)" 
                                    type="danger" 
                                    link 
                                    size="small" 
                                    style="margin-left: auto;"
                                    @click="handleDeleteQuestion(q)"
                                >
                                    Delete
                                </el-button>
                            </div>
                            <div style="margin-left: 20px; border-left: 2px solid #ddd; padding-left: 10px;">
                                <div v-for="ans in q.answers" :key="ans.id" style="margin-top: 10px;">
                                    <p style="margin: 0; font-size: 0.9em; display: flex; align-items: center;">
                                        <span style="font-weight: bold; color: #409EFF;" v-if="ans.is_merchant_reply">Merchant: </span>
                                        <span style="font-weight: bold;" v-else>{{ ans.username }}: </span>
                                        <span style="margin-left: 5px; flex: 1;">{{ ans.content }}</span>
                                        <el-button 
                                            v-if="authStore.user && authStore.user.id === ans.user" 
                                            type="primary" 
                                            link 
                                            size="small"
                                            @click="openEditAnswer(ans)"
                                        >
                                            Modify
                                        </el-button>
                                        <el-button 
                                            v-if="authStore.user && authStore.user.is_staff" 
                                            type="danger" 
                                            link 
                                            size="small"
                                            @click="handleDeleteAnswer(ans)"
                                        >
                                            Delete
                                        </el-button>
                                    </p>
                                </div>
                                <el-button size="small" type="text" style="margin-top: 5px;" @click="openAnswerDialog(q)">Reply</el-button>
                            </div>
                        </div>
                    </div>
                    <el-empty v-else description="No questions yet" />
                </el-tab-pane>
            </el-tabs>
        </div>

        <!-- C4: Related Products -->
        <div v-if="relatedProducts.length > 0" style="margin-top: 50px;">
            <h3 style="margin-bottom: 20px;">Related Products</h3>
            <el-row :gutter="20">
                <el-col :span="6" :xs="12" v-for="rp in relatedProducts" :key="rp.id">
                    <el-card :body-style="{ padding: '0px' }" shadow="hover" @click="$router.push(`/product/${rp.id}`)" style="cursor: pointer; height: 100%; display: flex; flex-direction: column;">
                        <div style="width: 100%; padding-top: 100%; position: relative; background: #f9f9f9;">
                            <img :src="rp.thumbnail" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" />
                        </div>
                        <div style="padding: 15px; flex-grow: 1; display: flex; flex-direction: column;">
                            <span style="font-weight: 600; display: block; margin-bottom: 8px; font-size: 0.95rem; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{{ rp.name }}</span>
                            <!-- Brief description snippet (C4 requirement) -->
                            <span v-if="rp.description" style="color: #666; font-size: 0.8rem; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                {{ rp.description }}
                            </span>
                            <span style="color: var(--color-secondary); font-weight: 700; margin-top: auto;">${{ rp.price }}</span>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>
        
        <el-empty v-else-if="!product" description="Product not found" />

        <!-- Dialogs -->
        <!-- Ask Question Dialog -->
        <el-dialog v-model="qaDialogVisible" title="Ask a Question" width="500px">
            <el-form :model="qaForm">
                <el-form-item label="Type">
                    <el-radio-group v-model="qaForm.tag">
                        <el-radio label="seller">Ask Seller (Public Answer)</el-radio>
                        <el-radio label="buyer">Ask Buyers (Invite Owners)</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="Question">
                    <el-input v-model="qaForm.content" type="textarea" :rows="3" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="qaDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitQuestion">Submit</el-button>
            </template>
        </el-dialog>

        <!-- Answer Dialog -->
        <el-dialog v-model="answerDialogVisible" title="Post Answer" width="500px">
            <p style="margin-bottom: 10px;"><strong>Question:</strong> {{ currentQuestion?.content }}</p>
            <el-input v-model="answerContent" type="textarea" :rows="3" placeholder="Your answer..." />
            <template #footer>
                <el-button @click="answerDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitAnswer">Submit</el-button>
            </template>
        </el-dialog>

        <!-- Edit Answer Dialog -->
        <el-dialog v-model="editAnswerVisible" title="Edit Answer" width="500px">
            <el-input v-model="editAnswerContent" type="textarea" :rows="3" />
            <template #footer>
                <el-button @click="editAnswerVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitEditAnswer">Update</el-button>
            </template>
        </el-dialog>

        <!-- Edit Review Dialog -->
        <el-dialog v-model="editReviewVisible" title="Edit Review" width="500px">
            <el-form :model="editReviewForm">
                <el-form-item label="Rating">
                    <el-rate v-model="editReviewForm.rating" show-text />
                </el-form-item>
                <el-form-item label="Comment">
                    <el-input v-model="editReviewForm.comment" type="textarea" :rows="4" />
                </el-form-item>
                <div style="color: #999; font-size: 0.85em; margin-bottom: 15px;">
                    Note: Photos cannot be changed. You can only edit the text and rating once.
                </div>
            </el-form>
            <template #footer>
                <el-button @click="editReviewVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitEditReview">Update Review</el-button>
            </template>
        </el-dialog>

        <!-- Follow-up Dialog -->
        <el-dialog v-model="followUpVisible" title="Add Follow-up" width="500px">
            <el-input v-model="followUpComment" type="textarea" :rows="3" placeholder="Update your experience..." />
            <template #footer>
                <el-button @click="followUpVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitFollowUp">Submit</el-button>
            </template>
        </el-dialog>

        <!-- Long-term Review Dialog -->
        <el-dialog v-model="longTermDialogVisible" :title="`Write ${reviewEligibility?.available_stage}-Day Review`" width="500px">
            <el-form :model="reviewForm" label-position="top">
                <el-form-item label="Durability & Quality Rating">
                    <el-rate v-model="reviewForm.rating" show-text :texts="['Poor', 'Fair', 'Average', 'Good', 'Excellent']" />
                </el-form-item>
                
                <el-form-item label="Usage Experience">
                    <div style="margin-bottom: 10px;">
                        <el-tag 
                            v-for="tag in longTermTags" 
                            :key="tag" 
                            class="review-tag" 
                            :effect="reviewForm.comment.includes(tag) ? 'dark' : 'plain'"
                            @click="toggleTag(tag)"
                            style="cursor: pointer; margin-right: 5px; margin-bottom: 5px;"
                        >
                            {{ tag }}
                        </el-tag>
                    </div>
                    <el-input v-model="reviewForm.comment" type="textarea" :rows="4" placeholder="How has the product held up over time?" />
                </el-form-item>
                
                <el-form-item label="Photos (Optional)">
                    <input type="file" ref="fileInput" @change="handlePhotoUpload" accept="image/*" style="margin-bottom: 10px;" />
                    <div class="photo-preview">
                        <div v-for="(url, idx) in reviewForm.photos" :key="idx" class="photo-item">
                            <el-image :src="url" style="width: 50px; height: 50px;" fit="cover" />
                            <el-icon class="remove-icon" @click="removePhoto(idx)"><CircleCloseFilled /></el-icon>
                        </div>
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="longTermDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="submitLongTermReview">Submit Review</el-button>
            </template>
        </el-dialog>

        <!-- X11: Space Fit Dialog -->
        <el-dialog v-model="showFitDialog" title="Does it fit my space?" width="400px">
            <p>Enter your space dimensions to check compatibility.</p>
            <el-form label-position="top">
                <el-form-item label="Space Width (cm)">
                    <el-input-number v-model="spaceDims.width" :min="1" />
                </el-form-item>
                <el-form-item label="Space Height (cm)">
                    <el-input-number v-model="spaceDims.height" :min="1" />
                </el-form-item>
                <el-form-item label="Space Depth/Length (cm)">
                    <el-input-number v-model="spaceDims.depth" :min="1" />
                </el-form-item>
            </el-form>
            <div v-if="fitResult !== null" class="fit-result" :class="{ 'fit-success': fitResult, 'fit-fail': !fitResult }">
                <el-icon v-if="fitResult"><CircleCheckFilled /></el-icon>
                <el-icon v-else><CircleCloseFilled /></el-icon>
                <span>{{ fitResult ? 'It Fits!' : 'Not Fit' }}</span>
            </div>
            <template #footer>
                <el-button @click="checkFit" type="primary">Check</el-button>
            </template>
        </el-dialog>

        <!-- X12: Custom Size Dialog -->
        <el-dialog v-model="showCustomSizeDialog" title="Customize Dimensions" width="400px">
            <p>Please enter your desired dimensions for this product.</p>
            <el-form label-position="top">
                <el-form-item label="Width (cm)">
                    <el-input-number v-model="customDims.width" :min="1" />
                </el-form-item>
                <el-form-item label="Height (cm)">
                    <el-input-number v-model="customDims.height" :min="1" />
                </el-form-item>
                <el-form-item label="Depth (cm)">
                    <el-input-number v-model="customDims.depth" :min="1" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="confirmCustomAddToCart" type="primary">Add to Cart</el-button>
            </template>
        </el-dialog>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getProduct, getProductEligibility } from '@/api/product'
import { getProductReviews, editReview, deleteReview, addReviewFollowup, voteReview, createLongTermReview } from '@/api/review'
import { getProductQuestions, createQuestion, createAnswer, deleteQuestion, deleteAnswer, editAnswer } from '@/api/qa'
import { addToWishlist } from '@/api/wishlist'
import { uploadImage } from '@/api/utils' // Assuming this exists, or use axios directly
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { Loading, Star, ChatDotRound, FullScreen, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const reviews = ref([])
const instantReviews = ref([])
const longTermReviews = ref([])
const questions = ref([])
const reviewSort = ref('helpful')
const activeTab = ref('instant')

const relatedProducts = ref([])
const loading = ref(false)
const quantity = ref(1)
const cartStore = useCartStore()
const authStore = useAuthStore()

// X11 & X12 State
const showFitDialog = ref(false)
const spaceDims = ref({ width: 100, height: 100, depth: 100 })
const fitResult = ref(null)
const showCustomSizeDialog = ref(false)
const customDims = ref({ width: 0, height: 0, depth: 0 })

// Q&A State
const qaDialogVisible = ref(false)
const qaForm = ref({ tag: 'seller', content: '' })
const answerDialogVisible = ref(false)
const currentQuestion = ref(null)
const answerContent = ref('')
const editAnswerVisible = ref(false)
const currentAnswer = ref(null)
const editAnswerContent = ref('')

// Review Actions State
const editReviewVisible = ref(false)
const editReviewForm = ref({})
const currentReview = ref(null)
const followUpVisible = ref(false)
const followUpComment = ref('')

// Long-term Review State
const reviewEligibility = ref(null)
const longTermDialogVisible = ref(false)
const reviewForm = ref({ rating: 5, comment: '', photos: [] })
const longTermTags = ['Still Good', 'Worn Out', 'Great Value', 'Needs Repair', 'Consistent Performance']

const mediaList = computed(() => {
    if (!product.value) return []
    let list = []
    
    // Add photos
    if (product.value.photos && product.value.photos.length > 0) {
        list = product.value.photos.map(p => ({ 
            id: p.id, 
            url: p.photo_url, 
            type: 'image' 
        }))
    } else if (product.value.thumbnail) {
        // Fallback to thumbnail if no extra photos
        list.push({ 
            id: 'thumb', 
            url: product.value.thumbnail, 
            type: 'image' 
        })
    }
    
    // Add video
    if (product.value.video_url) {
        list.push({ 
            id: 'video', 
            url: product.value.video_url, 
            type: 'video' 
        })
    }
    return list
})

const imagePreviewList = computed(() => {
    return mediaList.value
        .filter(m => m.type === 'image')
        .map(m => m.url)
})

const getPreviewIndex = (url) => {
    return imagePreviewList.value.indexOf(url)
}

const goBack = () => {
    if (window.history.state && window.history.state.back) {
        router.back()
    } else {
        router.push('/')
    }
}

const checkFit = () => {
    if (!product.value.width || !product.value.height) return
    const pW = Number(product.value.width)
    const pH = Number(product.value.height)
    const pD = Number(product.value.depth || 0)
    const sW = spaceDims.value.width
    const sH = spaceDims.value.height
    const sD = spaceDims.value.depth
    let fits = (pW <= sW && pH <= sH && pD <= sD)
    fitResult.value = fits
}

const confirmCustomAddToCart = async () => {
    const dimStr = `${customDims.value.width}x${customDims.value.height}x${customDims.value.depth}cm`
    try {
        await cartStore.addItem(product.value.id, quantity.value, dimStr)
        showCustomSizeDialog.value = false
        ElMessage.success('Added customized product to cart')
    } catch (e) {}
}

const fetchReviews = async () => {
    try {
        const type = activeTab.value === 'long_term' ? 'long_term' : 'instant'
        // If tab is 'qa', we don't fetch reviews
        if (activeTab.value === 'qa') return

        const res = await getProductReviews(route.params.id, { sort: reviewSort.value, type })
        const data = Array.isArray(res) ? res : res.results
        
        if (type === 'long_term') {
            longTermReviews.value = data
        } else {
            instantReviews.value = data
        }
    } catch (e) {
        console.error(e)
    }
}

const fetchQuestions = async () => {
    try {
        const res = await getProductQuestions(route.params.id)
        questions.value = res
    } catch (e) {
        console.error(e)
    }
}

const handleTabClick = (tab) => {
    if (tab.paneName === 'qa') {
        fetchQuestions()
    } else {
        fetchReviews()
    }
}

const fetchEligibility = async () => {
    if (!authStore.user) return
    try {
        const res = await getProductEligibility(route.params.id, { user_id: authStore.user.id })
        reviewEligibility.value = res
    } catch (e) { console.error(e) }
}

const fetchProduct = async () => {
    loading.value = true
    product.value = null // Reset
    relatedProducts.value = []
    try {
        const res = await getProduct(route.params.id)
        product.value = res
        if (res.related_products) {
            relatedProducts.value = res.related_products
        }

        // Init custom dims
        if (res.width) customDims.value.width = Number(res.width)
        else customDims.value.width = 100 // Default fallback
        
        if (res.height) customDims.value.height = Number(res.height)
        else customDims.value.height = 100 // Default fallback
        
        if (res.depth) customDims.value.depth = Number(res.depth)
        else customDims.value.depth = 50 // Default fallback
        
        // Handle navigation with query params (e.g. from notification)
        if (route.query.action === 'review' && route.query.type === 'long_term') {
            activeTab.value = 'long_term'
        } else {
            // Default behavior
            if (activeTab.value === 'qa') fetchQuestions()
            else fetchReviews()
        }
        
        // If we switched tab due to query, fetch data for that tab
        if (activeTab.value === 'long_term') fetchReviews()
        
        // Check eligibility
        fetchEligibility()

    } catch (e) {
        ElMessage.error('Failed to load product: ' + (e.message || 'Unknown error'))
    } finally {
        loading.value = false
    }
}

const handleAddToCart = async () => {
    if (!authStore.token) {
        ElMessage.warning('Please login first')
        // Use fullPath to ensure we return exactly here
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }
    
    // Check if customizable
    if (product.value.is_customizable) {
        showCustomSizeDialog.value = true
        return
    }

    try {
        await cartStore.addItem(product.value.id, quantity.value)
        ElMessage.success('Added to cart')
    } catch (e) { }
}

const handleAddToWishlist = async () => {
    if (!authStore.token) {
        ElMessage.warning('Please login first')
        // Use fullPath to ensure we return exactly here
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }
    try {
        const res = await addToWishlist({
            user_id: authStore.user.id,
            product_id: product.value.id
        })
        ElMessage.success(res.message)
    } catch (e) {
        console.error(e)
    }
}

// Q&A Functions
const submitQuestion = async () => {
    if (!authStore.token) {
        ElMessage.warning('Please login first')
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }
    if (!qaForm.value.content) return
    try {
        const res = await createQuestion({
            user_id: authStore.user.id,
            product_id: product.value.id,
            ...qaForm.value
        })
        if (res.message) ElMessage.success(res.message)
        else ElMessage.success('Question submitted')
        qaDialogVisible.value = false
        qaForm.value.content = ''
        fetchQuestions()
    } catch (e) {
        console.error(e)
    }
}

const openAnswerDialog = (q) => {
    currentQuestion.value = q
    answerContent.value = ''
    answerDialogVisible.value = true
}

const submitAnswer = async () => {
    if (!authStore.token) return ElMessage.warning('Please login')
    if (!answerContent.value) return
    try {
        const res = await createAnswer(currentQuestion.value.id, {
            user_id: authStore.user.id,
            content: answerContent.value
        })
        if (res.message) ElMessage.success(res.message) // Coupon reward
        else ElMessage.success('Answer submitted')
        answerDialogVisible.value = false
        answerContent.value = ''
        fetchQuestions()
    } catch (e) {
        // Handle error manually to check response data
        if (e.response && e.response.data && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            console.error(e)
            ElMessage.error('Failed to submit answer')
        }
    }
}

const handleDeleteQuestion = async (q) => {
    try {
        await ElMessageBox.confirm('Are you sure you want to delete this question?', 'Warning', { type: 'warning' })
        await deleteQuestion(q.id, authStore.user.id)
        ElMessage.success('Question deleted')
        fetchQuestions()
    } catch (e) {}
}

const handleDeleteAnswer = async (ans) => {
    try {
        await ElMessageBox.confirm('Are you sure you want to delete this answer?', 'Warning', { type: 'warning' })
        await deleteAnswer(ans.id, authStore.user.id)
        ElMessage.success('Answer deleted')
        fetchQuestions()
    } catch (e) {}
}

const openEditAnswer = (ans) => {
    currentAnswer.value = ans
    editAnswerContent.value = ans.content
    editAnswerVisible.value = true
}

const submitEditAnswer = async () => {
    if (!editAnswerContent.value) return
    try {
        await editAnswer(currentAnswer.value.id, {
            user_id: authStore.user.id,
            content: editAnswerContent.value
        })
        ElMessage.success('Answer updated')
        editAnswerVisible.value = false
        fetchQuestions()
    } catch (e) {
        ElMessage.error('Failed to update answer')
    }
}

// Review Action Functions
const handleVote = async (review, type) => {
    if (!authStore.token) return ElMessage.warning('Please login to vote')
    try {
        const res = await voteReview(review.id, { user_id: authStore.user.id, vote_type: type })
        if (res && res.message) {
            ElMessage.success(res.message)
        }
        await fetchReviews() // Refresh to show new counts
    } catch (e) { console.error(e) }
}

const openEditReview = (review) => {
    currentReview.value = review
    editReviewForm.value = { ...review }
    editReviewVisible.value = true
}

const submitEditReview = async () => {
    try {
        await editReview(currentReview.value.id, {
            user_id: authStore.user.id,
            rating: editReviewForm.value.rating,
            comment: editReviewForm.value.comment
        })
        ElMessage.success('Review updated')
        editReviewVisible.value = false
        fetchReviews()
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            ElMessage.error('Failed to update review')
        }
    }
}

const handleDeleteReview = async (review) => {
    try {
        await ElMessageBox.confirm('Are you sure you want to delete this review?', 'Warning', { type: 'warning' })
        await deleteReview(review.id, { user_id: authStore.user.id })
        ElMessage.success('Review deleted')
        fetchReviews()
    } catch (e) { }
}

const openFollowUp = (review) => {
    currentReview.value = review
    followUpComment.value = ''
    followUpVisible.value = true
}

const submitFollowUp = async () => {
    try {
        await addReviewFollowup(currentReview.value.id, {
            user_id: authStore.user.id,
            comment: followUpComment.value
        })
        ElMessage.success('Follow-up added')
        followUpVisible.value = false
        fetchReviews()
    } catch (e) { console.error(e) }
}

// Long-term Review Logic
const openLongTermReviewDialog = () => {
    reviewForm.value = { rating: 5, comment: '', photos: [] }
    longTermDialogVisible.value = true
}

const toggleTag = (tag) => {
    if (reviewForm.value.comment.includes(tag)) {
        reviewForm.value.comment = reviewForm.value.comment.replace(tag, '').trim()
    } else {
        reviewForm.value.comment = (reviewForm.value.comment + ' ' + tag).trim()
    }
}

const handlePhotoUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    try {
        const res = await uploadImage(file)
        reviewForm.value.photos.push(res.url)
        event.target.value = '' // Reset input
    } catch (e) {
        ElMessage.error('Failed to upload image')
    }
}

const removePhoto = (idx) => {
    reviewForm.value.photos.splice(idx, 1)
}

const submitLongTermReview = async () => {
    if (!reviewForm.value.comment) return ElMessage.warning('Please write a comment')
    try {
        await createLongTermReview({
            user_id: authStore.user.id,
            order_item_id: reviewEligibility.value.order_item_id,
            stage: reviewEligibility.value.available_stage,
            rating: reviewForm.value.rating,
            comment: reviewForm.value.comment,
            photos: reviewForm.value.photos
        })
        ElMessage.success('Review submitted! Coupon sent.')
        longTermDialogVisible.value = false
        fetchEligibility() 
        fetchReviews()
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            ElMessage.error('Failed to submit')
        }
    }
}

const windowWidth = ref(window.innerWidth)
const carouselHeight = computed(() => {
    return windowWidth.value < 768 ? '300px' : '400px'
})

const updateWidth = () => {
    windowWidth.value = window.innerWidth
}

onMounted(() => {
    window.addEventListener('resize', updateWidth)
    fetchProduct()
})

// Cleanup listener
import { onUnmounted } from 'vue'
onUnmounted(() => {
    window.removeEventListener('resize', updateWidth)
})

watch(() => route.params.id, (newId) => {
    if (newId) fetchProduct()
})
</script>

<style scoped>
.price {
    font-size: 2rem;
    color: #f56c6c;
    font-weight: bold;
}
.category {
    color: #909399;
}
.description {
    font-size: 1.1rem;
    line-height: 1.6;
}

.fit-result {
    margin-top: 20px;
    font-size: 1.2rem;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: center;
}
.fit-success {
    color: #67C23A;
}
.fit-fail {
    color: #F56C6C;
}

.photo-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}
.photo-item {
    position: relative;
    display: inline-block;
}
.remove-icon {
    position: absolute;
    top: -5px;
    right: -5px;
    color: red;
    background: white;
    border-radius: 50%;
    cursor: pointer;
}

@media (max-width: 768px) {
    .product-title {
        font-size: 1.5rem;
        margin-top: 20px;
    }
    .price {
        font-size: 1.5rem;
    }
    .description {
        font-size: 1rem;
    }
}
</style>