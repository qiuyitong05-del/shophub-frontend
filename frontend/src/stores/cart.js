import { defineStore } from 'pinia'
import { getCart, addToCart, removeCartItem, updateCartItem } from '@/api/cart'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: []
  }),
  actions: {
    async fetchCart() {
      const auth = useAuthStore()
      if (!auth.token) return
      try {
          const res = await getCart({ user_id: auth.user.id })
          this.items = (Array.isArray(res) ? res : res.results) || []
      } catch (e) { console.error(e) }
    },
    async addItem(product_id, quantity, custom_dimensions) {
      const auth = useAuthStore()
      if (!auth.token) return
      try {
        const payload = {
            user_id: auth.user.id || auth.user_id,
            product_id,
            quantity
        }
        if (custom_dimensions) {
            payload.custom_dimensions = custom_dimensions
        }
        await addToCart(payload)
        await this.fetchCart()
      } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            // Check if error message is already shown by interceptor
            // If so, do nothing
        }
        throw e
      }
    },
    async removeItem(product_id) {
        const auth = useAuthStore()
        await removeCartItem({ user_id: auth.user.id, product_id })
        await this.fetchCart()
    },
    async updateQuantity(product_id, quantity) {
        const auth = useAuthStore()
        await updateCartItem({ user_id: auth.user.id, product_id, quantity })
        await this.fetchCart()
    }
  },
  getters: {
      totalPrice: (state) => {
          if (!Array.isArray(state.items)) return 0
          return state.items.reduce((total, item) => {
              const price = Number(item.unit_price)
              const quantity = Number(item.quantity)
              const safePrice = isNaN(price) ? 0 : price
              const safeQuantity = isNaN(quantity) ? 0 : quantity
              return total + (safePrice * safeQuantity)
          }, 0)
      },
      itemCount: (state) => {
          if (!Array.isArray(state.items)) return 0
          return state.items.reduce((count, item) => {
              const quantity = Number(item.quantity)
              return count + (isNaN(quantity) ? 0 : quantity)
          }, 0)
      }
  }
})
