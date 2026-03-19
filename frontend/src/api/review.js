
import request from '@/utils/request'

export function createReview(data) {
  return request({
    url: '/reviews/create/',
    method: 'post',
    data
  })
}

export function createLongTermReview(data) {
  return request({
    url: '/reviews/long-term/create/',
    method: 'post',
    data
  })
}

export function getProductReviews(productId, params) {
  return request({
    url: `/products/${productId}/reviews/`,
    method: 'get',
    params
  })
}

export function getAdminReviews() {
  return request({
    url: '/admin/reviews/',
    method: 'get'
  })
}

export function replyReview(reviewId, data) {
  return request({
    url: `/admin/reviews/${reviewId}/reply/`,
    method: 'post',
    data
  })
}

export function editReview(reviewId, data) {
  return request({
    url: `/reviews/${reviewId}/edit/`,
    method: 'post',
    data
  })
}

export function deleteReview(reviewId, params) {
  return request({
    url: `/reviews/${reviewId}/delete/`,
    method: 'delete',
    params
  })
}

export function addReviewFollowup(reviewId, data) {
  return request({
    url: `/reviews/${reviewId}/followup/`,
    method: 'post',
    data
  })
}

export function voteReview(reviewId, data) {
  return request({
    url: `/reviews/${reviewId}/vote/`,
    method: 'post',
    data
  })
}

