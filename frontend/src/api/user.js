import request from '@/utils/request'

export function getUserProfile() {
  return request({
    url: '/user/profile/',
    method: 'get'
  })
}

export function updateUserProfile(data) {
  return request({
    url: '/user/profile/',
    method: 'post',
    data
  })
}
