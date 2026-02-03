import { createRouter, createWebHistory } from 'vue-router'
import RegisterView from '../views/RegisterView.vue' // 引入刚才建的文件

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/register',
      name: 'register',
      component: RegisterView // 访问 /register 就能看到注册页
    }
  ]
})
export default router