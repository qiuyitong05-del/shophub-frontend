<template>
  <div class="admin-product-list">
    <div class="header">
      <h2>Product Management</h2>
      <el-button type="primary" round @click="$router.push('/admin/product/add')">Add Product</el-button>
    </div>

    <div class="filter-container">
      <el-select v-model="searchType" placeholder="Select Field" class="filter-item">
        <el-option label="Product Name" value="name" />
        <el-option label="Product ID" value="id" />
        <el-option label="Price" value="price" />
      </el-select>
      
      <!-- Status Filter -->
      <el-select v-model="statusFilter" placeholder="Status" class="filter-item" clearable @change="triggerSearch">
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
      </el-select>

      <!-- Price Range Inputs -->
      <template v-if="searchType === 'price'">
        <el-input
          v-model="minPrice"
          placeholder="Min Price"
          class="filter-input"
          type="number"
          clearable
          @keyup.enter="triggerSearch"
        />
        <span class="separator">-</span>
        <el-input
          v-model="maxPrice"
          placeholder="Max Price"
          class="filter-input"
          type="number"
          clearable
          @keyup.enter="triggerSearch"
        />
        <el-button type="primary" round class="search-btn" @click="triggerSearch">Search</el-button>
      </template>

      <!-- Keyword Input -->
      <el-input
        v-else
        v-model="searchKeyword"
        placeholder="Enter keyword..."
        class="search-input"
        clearable
        @keyup.enter="triggerSearch"
      >
        <template #append>
            <el-button type="primary" class="search-btn-inner" @click="triggerSearch">Search</el-button>
        </template>
      </el-input>
    </div>

    <div class="table-container">
        <el-table :data="products" style="width: 100%" v-loading="loading" stripe border header-cell-class-name="table-header">
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column label="Thumbnail" width="100" align="center">
            <template #default="scope">
              <el-image 
                :src="scope.row.thumbnail" 
                style="width: 50px; height: 50px; border-radius: 4px;" 
                fit="cover" 
                :preview-src-list="[scope.row.thumbnail]"
                preview-teleported
              />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Name" min-width="200" />
          <el-table-column prop="price" label="Price" width="120" sortable>
              <template #default="scope">
                  <span class="price-text">${{ scope.row.price }}</span>
              </template>
          </el-table-column>
          <el-table-column prop="is_active" label="Status" width="120" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="dark" round>
                {{ scope.row.is_active ? 'Active' : 'Inactive' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="200" align="center" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" round plain @click="$router.push(`/admin/product/edit/${scope.row.id}`)">Edit</el-button>
              <el-button 
                size="small" 
                :type="scope.row.is_active ? 'danger' : 'success'" 
                round
                plain
                @click="toggleStatus(scope.row)"
              >
                {{ scope.row.is_active ? 'Disable' : 'Enable' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
    </div>
    
    <div class="pagination-container">
        <el-pagination 
            background
            layout="prev, pager, next" 
            :total="total" 
            :page-size="pageSize"
            @current-change="handlePageChange"
        />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { getAdminProducts, patchProduct } from '@/api/product'
import { ElMessage } from 'element-plus'

const products = ref([])
const allProducts = ref([]) // Store all if client-side filtering
const loading = ref(false)
const searchType = ref('name')
const statusFilter = ref('')
const searchKeyword = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchProducts = async () => {
    loading.value = true
    try {
        const res = await getAdminProducts()
        const results = Array.isArray(res) ? res : res.results
        allProducts.value = results
        applyFilters()
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const applyFilters = () => {
    let filtered = allProducts.value
    
    // Status Filter
    if (statusFilter.value) {
        const isActive = statusFilter.value === 'active'
        filtered = filtered.filter(p => p.is_active === isActive)
    }
    
    // Search Filter
    if (searchType.value === 'price') {
        if (minPrice.value) {
            filtered = filtered.filter(p => parseFloat(p.price) >= parseFloat(minPrice.value))
        }
        if (maxPrice.value) {
            filtered = filtered.filter(p => parseFloat(p.price) <= parseFloat(maxPrice.value))
        }
    } else if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(p => {
            if (searchType.value === 'name') {
                return p.name.toLowerCase().includes(keyword)
            } else if (searchType.value === 'id') {
                return String(p.id).includes(keyword)
            } else {
                return p.name.toLowerCase().includes(keyword) || String(p.id).includes(keyword)
            }
        })
    }
    
    total.value = filtered.length
    
    // Client-side pagination
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    products.value = filtered.slice(start, end)
}

const triggerSearch = () => {
    currentPage.value = 1
    applyFilters()
}

const handlePageChange = (page) => {
    currentPage.value = page
    applyFilters()
}

const toggleStatus = async (row) => {
    try {
        await patchProduct(row.id, { is_active: !row.is_active })
        row.is_active = !row.is_active
        ElMessage.success(`Product ${row.is_active ? 'enabled' : 'disabled'}`)
    } catch (e) {
        console.error(e)
        ElMessage.error('Failed to update status')
    }
}

// Watchers to clear inputs when search type changes
watch(searchType, (newVal) => {
    searchKeyword.value = ''
    minPrice.value = ''
    maxPrice.value = ''
    applyFilters()
})

onMounted(() => {
    fetchProducts()
})
</script>

<style scoped>
.admin-product-list {
    padding: 20px;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}
.header h2 {
    font-family: var(--font-serif);
    color: var(--color-secondary);
}
.filter-container {
    background: var(--color-white);
    padding: 20px;
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
}

.filter-item {
    width: 150px;
}

.filter-input {
    width: 150px;
}

.search-input {
    width: 300px;
}

.search-btn {
    margin-left: 10px;
}

.separator {
    color: var(--color-text-light);
}

:deep(.el-table) {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

:deep(.table-header) {
    background-color: #F5F7FA !important;
    color: var(--color-secondary);
    font-weight: 700;
}

:deep(.el-table__row--striped td) {
    background-color: #FAFAFA !important;
}

.price-text {
    font-weight: 600;
    color: var(--color-primary);
}

.pagination-container {
    margin-top: 30px;
    display: flex;
    justify-content: flex-end;
}
</style>
