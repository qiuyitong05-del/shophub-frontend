import request from '@/utils/request'

export function getProducts(params) {
  return request({
    url: '/products/',
    method: 'get',
    params
  })
}

export function getAdminProducts(params) {
  return request({
    url: '/admin/products/',
    method: 'get',
    params
  })
}

export function getProduct(id) {
  return request({
    url: `/products/${id}/`,
    method: 'get'
  })
}

export function getAdminProduct(id) {
  return request({
    url: `/admin/products/${id}/`,
    method: 'get'
  })
}

export function getCategories(params) {
    return request({
        url: '/categories/',
        method: 'get',
        params
    })
}

export function getTags() {
  return request({
    url: '/tags/',
    method: 'get'
  })
}

export function createProduct(data) {
    return request({
        url: '/admin/products/create/',
        method: 'post',
        data
    })
}

export function updateProduct(id, data) {
    return request({
        url: `/admin/products/${id}/update/`,
        method: 'post',
        data
    })
}

export function deleteProduct(id) {
    return request({
        url: `/products/${id}/`,
        method: 'delete'
    })
}

export function removeProductPhoto(productId, photoId) {
    return request({
        url: `/admin/products/${productId}/photos/${photoId}/remove/`,
        method: 'post'
    })
}

export function patchProduct(id, data) {
    return request({
        url: `/admin/products/${id}/update/`,
        method: 'post',
        data
    })
}

export function findSimilarProducts(id) {
  return request({
    url: `/products/${id}/similar/`,
    method: 'get'
  })
}

export function getProductEligibility(productId, params) {
  return request({
    url: `/products/${productId}/eligibility/`,
    method: 'get',
    params
  })
}
