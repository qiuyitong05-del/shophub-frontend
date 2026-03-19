
import request from '@/utils/request'

export function getProductQuestions(productId) {
  return request({
    url: `/products/${productId}/questions/`,
    method: 'get'
  })
}

export function createQuestion(data) {
  return request({
    url: '/questions/create/',
    method: 'post',
    data
  })
}

export function getNotifications(params) {
  return request({
    url: '/notifications/',
    method: 'get',
    params
  })
}

export function createAnswer(questionId, data) {
  return request({
    url: `/questions/${questionId}/answer/`,
    method: 'post',
    data
  })
}

export function deleteQuestion(questionId, userId) {
  return request({
    url: `/questions/${questionId}/delete/`,
    method: 'delete',
    params: { user_id: userId }
  })
}

export function deleteAnswer(answerId, userId) {
  return request({
    url: `/answers/${answerId}/delete/`,
    method: 'delete',
    params: { user_id: userId }
  })
}

export function editAnswer(answerId, data) {
  return request({
    url: `/answers/${answerId}/edit/`,
    method: 'post',
    data
  })
}
