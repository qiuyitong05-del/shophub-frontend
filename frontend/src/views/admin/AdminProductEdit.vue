<template>
  <div class="admin-product-edit">
    <div class="header">
      <h2>{{ isEdit ? 'Edit Product' : 'Add Product' }}</h2>
      <el-button @click="$router.back()">Back</el-button>
    </div>

    <el-form :model="form" label-width="120px" :rules="rules" ref="formRef" v-loading="loading">
      <el-form-item label="Name" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      
      <el-form-item label="Category" prop="category">
        <el-select v-model="form.category" placeholder="Select Category">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="Price" prop="price">
        <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0" />
      </el-form-item>

      <el-form-item label="Stock" prop="stock_quantity">
        <el-input-number v-model="form.stock_quantity" :min="0" />
      </el-form-item>
      
      <el-form-item label="Thumbnail" prop="thumbnail">
        <div style="display: flex; width: 100%; gap: 10px;">
             <el-input v-model="form.thumbnail" placeholder="Enter URL or Browse" />
             <el-upload
                action="#"
                :show-file-list="false"
                :auto-upload="true"
                :http-request="uploadThumbnail"
             >
                <el-button type="primary">Browse</el-button>
             </el-upload>
        </div>
        <div v-if="form.thumbnail && !form.thumbnail.startsWith('uploading')" style="margin-top: 10px;">
            <img :src="form.thumbnail" style="height: 100px; object-fit: contain; border: 1px solid #ddd; padding: 2px;" />
        </div>
      </el-form-item>

      <!-- Product Photos (Moved here or just reorganized) -->
      <el-form-item label="Product Photos">
          <div v-if="isEdit">
              <div v-for="(photo, index) in form.photos" :key="photo.id || index" style="margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
                  <img v-if="photo.photo_url" :src="photo.photo_url" style="width: 50px; height: 50px; object-fit: cover; border: 1px solid #ddd;" />
                  <el-input v-model="photo.photo_url" placeholder="Photo URL" style="flex: 1;" />
                  <el-upload
                    action="#"
                    :show-file-list="false"
                    :auto-upload="true"
                    :http-request="(options) => uploadProductPhoto(options, index)"
                  >
                     <el-button>Browse</el-button>
                  </el-upload>
                  <el-button type="danger" @click="removePhoto(index, photo.id)">Delete</el-button>
              </div>
              <div style="margin-top: 10px;">
                <el-button type="primary" plain @click="addPhotoField">
                    <el-icon style="margin-right: 5px;"><Plus /></el-icon> Add Product Photo
                </el-button>
              </div>
          </div>
          <div v-else>
              <el-alert title="Please save the product first before adding extra photos." type="info" show-icon :closable="false" />
          </div>
      </el-form-item>

      <el-form-item label="Video" prop="video_url">
        <div style="display: flex; width: 100%; gap: 10px;">
             <el-input v-model="form.video_url" placeholder="Enter Video URL or Browse" />
             <el-upload
                action="#"
                :show-file-list="false"
                :auto-upload="true"
                :http-request="uploadVideo"
                accept="video/*"
             >
                <el-button type="primary">Browse</el-button>
             </el-upload>
        </div>
        <div v-if="form.video_url && !form.video_url.startsWith('uploading')" style="margin-top: 10px;">
            <video :src="form.video_url" controls style="height: 150px; border: 1px solid #ddd; padding: 2px;"></video>
        </div>
      </el-form-item>
      
      <el-form-item label="Tags" prop="tags">
        <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="Select or enter tags"
            style="width: 100%"
        >
            <el-option v-for="tag in availableTags" :key="tag.id" :label="tag.name" :value="tag.name" />
        </el-select>
        <div style="margin-top: 5px; color: #999; font-size: 0.8em;">Select existing tags or type a new one and press Enter</div>
      </el-form-item>

      <el-form-item label="Features (HTML)" prop="features">
        <el-input v-model="form.features" type="textarea" :rows="6" placeholder="<ul><li>Feature 1</li><li>Feature 2</li></ul>" />
        <div style="margin-top: 5px; color: #999; font-size: 0.8em;">Supports HTML tags like &lt;p&gt;, &lt;ul&gt;, &lt;li&gt;, &lt;strong&gt;</div>
      </el-form-item>

      <el-form-item label="Description" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
      
      <el-form-item label="Active" prop="is_active">
        <el-switch v-model="form.is_active" />
      </el-form-item>

      <!-- Product Photos -->
      <div v-if="isEdit">
      </div>
      <div v-else>
      </div>

      <el-form-item style="margin-top: 30px;">
        <el-button type="primary" @click="onSubmit">Save</el-button>
        <el-button @click="$router.back()">Cancel</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAdminProduct, createProduct, updateProduct, getCategories, removeProductPhoto, getTags } from '@/api/product'
import { ElMessage } from 'element-plus'

import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const categories = ref([])
const availableTags = ref([])
const thumbnailPreview = ref('')
const thumbnailFile = ref(null)

const form = ref({
  name: '',
  price: 0,
  description: '',
  stock_quantity: 0,
  category: '',
  thumbnail: '',
  video_url: '',
  tags: [], // Change to array
  features: '',
  is_active: true,
  photos: [] // { id, photo_url }
})

const handleThumbnailChange = (file) => {
    // Legacy function, no longer used with new upload logic
}

const uploadThumbnail = async (options) => {
    const { file } = options
    const formData = new FormData()
    formData.append('file', file)
    
    // Show uploading state
    form.value.thumbnail = 'uploading...'
    
    try {
        const { default: request } = await import('@/utils/request')
        const res = await request({
            url: '/upload/',
            method: 'post',
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        form.value.thumbnail = res.url
        ElMessage.success('Thumbnail uploaded')
    } catch (e) {
        console.error(e)
        ElMessage.error('Upload failed')
        form.value.thumbnail = ''
    }
}

const uploadVideo = async (options) => {
    const { file } = options
    const formData = new FormData()
    formData.append('file', file)
    
    // Show uploading state
    form.value.video_url = 'uploading...'
    
    try {
        const { default: request } = await import('@/utils/request')
        const res = await request({
            url: '/upload/',
            method: 'post',
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        form.value.video_url = res.url
        ElMessage.success('Video uploaded')
    } catch (e) {
        console.error(e)
        ElMessage.error('Upload failed')
        form.value.video_url = ''
    }
}

const uploadProductPhoto = async (options, index) => {
    const { file } = options
    const formData = new FormData()
    formData.append('file', file)
    
    // Show uploading state
    form.value.photos[index].photo_url = 'uploading...'
    
    try {
        const { default: request } = await import('@/utils/request')
        const res = await request({
            url: '/upload/',
            method: 'post',
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        form.value.photos[index].photo_url = res.url
        ElMessage.success('Photo uploaded')
    } catch (e) {
        console.error(e)
        ElMessage.error('Upload failed')
        form.value.photos[index].photo_url = ''
    }
}

const rules = {
  name: [{ required: true, message: 'Required', trigger: 'blur' }],
  price: [{ required: true, message: 'Required', trigger: 'blur' }],
  category: [{ required: true, message: 'Required', trigger: 'change' }],
  thumbnail: [
      { 
          required: true, 
          message: 'Please enter URL or upload a thumbnail', 
          trigger: 'blur' 
      }
  ]
}

const isEdit = computed(() => route.params.id !== undefined)

const fetchCategories = async () => {
    try {
        const res = await getCategories()
        categories.value = Array.isArray(res) ? res : res.results
    } catch (e) {
        console.error(e)
    }
}

const fetchAvailableTags = async () => {
    try {
        const res = await getTags()
        availableTags.value = Array.isArray(res) ? res : res.results
    } catch (e) {
        console.error(e)
    }
}

const fetchProductData = async () => {
    if (!isEdit.value) return
    loading.value = true
    try {
        const data = await getAdminProduct(route.params.id)
        form.value = {
            ...data,
            category: data.category_id, // Use category_id from response
            tags: data.tags || [] // Ensure it's an array
        }
        // Ensure photos is array
        if (!form.value.photos) form.value.photos = []
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const addPhotoField = () => {
    form.value.photos.push({ photo_url: '' })
}

const removePhoto = async (index, photoId) => {
    if (photoId) {
        try {
            await removeProductPhoto(route.params.id, photoId)
            ElMessage.success('Photo removed')
        } catch (e) {
            console.error(e)
            ElMessage.error('Failed to remove photo')
            return
        }
    }
    form.value.photos.splice(index, 1)
}

const onSubmit = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            loading.value = true
            try {
                // Ensure category ID is set correctly
                // Convert tags array to comma-separated string for backend compatibility
                const tagsString = Array.isArray(form.value.tags) ? form.value.tags.join(',') : form.value.tags
                
                const payload = { 
                    ...form.value, 
                    category_id: form.value.category,
                    tags: tagsString
                }
                
                let productId = route.params.id
                let isNew = !isEdit.value
                
                if (isNew) {
                    const res = await createProduct(payload)
                    productId = res.id
                } else {
                    await updateProduct(productId, payload)
                }
                
                // For product photos, we just need to ensure they are added via separate API calls if they are new?
                // The updateProduct/createProduct API might not handle nested photos creation automatically unless DRF serializer is set up for it.
                // Our current AdminProductSerializer is a ModelSerializer.
                // If we send 'photos' list in payload, DRF default create() doesn't handle nested writable fields unless overridden.
                // However, we have a separate logic for adding photos via `admin_add_product_photo`.
                // The user enters URL in the photos list.
                // If these are new URLs, we need to add them.
                // If they are existing photos (have ID), we leave them.
                
                // Let's iterate and add new photos
                // But wait, if user edited the URL of an existing photo?
                // Our UI doesn't really support editing URL of existing photo easily (delete and add new is better).
                // Let's assume new entries (no ID) need to be added.
                
                if (form.value.photos && form.value.photos.length > 0) {
                    const { default: request } = await import('@/utils/request')
                    
                    for (const photo of form.value.photos) {
                        if (!photo.id && photo.photo_url && photo.photo_url !== 'uploading...') {
                            // It's a new photo
                            await request({
                                url: `/admin/products/${productId}/photos/add/`,
                                method: 'post',
                                data: { photo_url: photo.photo_url }
                            })
                        }
                    }
                }
                
                ElMessage.success(isNew ? 'Product created' : 'Product updated')
                if (isNew) {
                    router.push('/admin/products')
                } else {
                    router.push(`/product/${productId}`)
                }
            } catch (e) {
                console.error(e)
                const errorMsg = e.response?.data ? JSON.stringify(e.response.data) : 'Operation failed'
                ElMessage.error(errorMsg)
            } finally {
                loading.value = false
            }
        }
    })
}

onMounted(() => {
    fetchCategories()
    fetchAvailableTags()
    fetchProductData()
})
</script>

<style scoped>
.admin-product-edit {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
</style>
