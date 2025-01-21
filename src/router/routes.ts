import CalculatorPage from 'src/pages/CalculatorPage.vue'
import ScannerPage from 'src/pages/ScannerPage.vue'
import SettingsPage from 'src/pages/SettingsPage.vue'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/scanner',
  },
  { path: '/scanner', component: ScannerPage },
  { path: '/calculator', component: CalculatorPage },
  { path: '/settings', component: SettingsPage },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
