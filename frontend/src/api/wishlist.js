
import request from '@/utils/request'

export function getWishlist(params) {
  return request({
    url: '/wishlist/',
    method: 'get',
    params
  })
}

export function addToWishlist(data) {
  return request({
    url: '/wishlist/add/',
    method: 'post',
    data
  })
}

export function removeFromWishlist(data) {
  return request({
    url: '/wishlist/remove/',
    method: 'post',
    data
  })
}

export function updateWishlistPrivacy(data) {
  return request({
    url: '/wishlist/privacy/',
    method: 'post',
    data
  })
}

export function bulkAddToCart(data) {
  return request({
    url: '/wishlist/bulk-cart/',
    method: 'post',
    data
  })
}
