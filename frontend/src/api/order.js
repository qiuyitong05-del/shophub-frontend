import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

export function createOrder(data) {
  const authStore = useAuthStore()
  return request({
    url: '/checkout/',
    method: 'post',
    data: { ...data, user_id: authStore.user?.id }
  })
}

export function getOrders(params) {
  const authStore = useAuthStore()
  return request({
    url: '/orders/',
    method: 'get',
    params: { ...params, user_id: authStore.user?.id }
  })
}

export function getAdminOrders(params) {
  return request({
    url: '/admin/orders/',
    method: 'get',
    params
  })
}

export function getAdminOrder(id) {
    return request({
        url: `/admin/orders/${id}/`,
        method: 'get'
    })
}

export function getOrder(id) {
    return request({
        url: `/orders/${id}/`,
        method: 'get'
    })
}

export function getDefaultAddress() {
  const authStore = useAuthStore()
  return request({
    url: '/address/default/',
    method: 'get',
    params: { user_id: authStore.user?.id }
  })
}

export function cancelOrder(id) {
    return request({
        url: `/orders/${id}/cancel/`,
        method: 'post'
    })
}

export function shipOrder(id) {
    return request({
        url: `/admin/orders/${id}/ship/`,
        method: 'post'
    })
}

export function holdOrder(id) {
    return request({
        url: `/admin/orders/${id}/hold/`,
        method: 'post'
    })
}
