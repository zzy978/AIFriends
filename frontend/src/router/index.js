import CreateIndex from '@/views/create/CreateIndex.vue'
import NotFoundIndex from '@/views/error/NotFoundIndex.vue'
import FriendIndex from '@/views/friend/FriendIndex.vue'
import HomepageIndex from '@/views/homepage/HomepageIndex.vue'
import LoginIndex from '@/views/user/account/LoginIndex.vue'
import RegisterIndex from '@/views/user/account/RegisterIndex.vue'
import ProfileIndex from '@/views/user/profile/ProfileIndex.vue'
import SpaceIndex from '@/views/user/space/SpaceIndex.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomepageIndex,
      name: 'homepage-index',
    },
    {
      path: '/friend',
      component: FriendIndex,
      name: 'friend-index',
    },
    {
      path: '/create',
      component: CreateIndex,
      name: 'create-index',
    },
    {
      path: '/error',
      component: NotFoundIndex,
      name: '404',
    },
    {
      path: '/user/account/register',
      component: RegisterIndex,
      name: 'user-account-register-index',
    },
    {
      path: '/user/account/login',
      component: LoginIndex,
      name: 'user-account-login-index',
    },
    {
      path: '/user/space/:user_id',
      component: SpaceIndex,
      name: 'user-space-index',
    },
    {
      path: '/user/profile',
      component: ProfileIndex,
      name: 'user-profile-index',
    },
    {
      path: '/:pathMatch(.*)*',
      component: NotFoundIndex,
      name: '404',
    },
  ],
})

export default router
