import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

export function getCart(params) {
  return request({
    url: '/cart/',
    method: 'get',
    params
  })
}

export function addToCart(data) {
  return request({
    url: '/cart/add/',
    method: 'post',
    data
  })
}

export function updateCartItem(data) {
  return request({
    url: '/cart/update/',
    method: 'post',
    data
  })
}

export function removeCartItem(data) {
  return request({
    url: '/cart/remove/',
    method: 'post',
    data
  })
}

export function getAvailableCoupons(params) {
  return request({
    url: '/coupons/available/',
    method: 'get',
    params
  })
}

export function moveToWishlist(data) {
  return request({
    url: '/cart/move-to-wishlist/',
    method: 'post',
    data
  })
}

export function getCartRecommendations(params) {
  return request({
    url: '/cart/recommendations/',
    method: 'get',
    params
  })
}
