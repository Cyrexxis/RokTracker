import { defineRouter } from '#q-app/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'
import routes from './routes'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  Router.beforeEach((to, from) => {
    const toTopLevel = to.path.split('/')[1]
    const fromTopLevel = from.path.split('/')[1]

    // if (fromTopLevel !== undefined && toTopLevel !== undefined) {
    //   if (fromTopLevel === 'scanner') {
    //     to.meta.transitionIn = 'animated slideInUp'
    //     to.meta.transitionOut = 'animated slideOutUp'
    //   } else if (fromTopLevel === 'settings') {
    //     to.meta.transitionIn = 'animated slideInDown'
    //     to.meta.transitionOut = 'animated slideOutDown'
    //   } else if (fromTopLevel === 'calculator') {
    //     if (toTopLevel === 'scanner') {
    //       to.meta.transitionIn = 'animated slideInDown'
    //       to.meta.transitionOut = 'animated slideOutDown'
    //     } else if (toTopLevel === 'settings') {
    //       to.meta.transitionIn = 'animated slideInUp'
    //       to.meta.transitionOut = 'animated slideOutUp'
    //     }
    //   }
    // }
    if (fromTopLevel !== undefined && toTopLevel !== undefined) {
      if (fromTopLevel === 'scanner') {
        to.meta.transitionIn = 'animated slideInUp fast'
        to.meta.transitionOut = 'animated slideOutUp fast'
      } else if (fromTopLevel === 'settings') {
        to.meta.transitionIn = 'animated slideInDown fast'
        to.meta.transitionOut = 'animated slideOutDown fast'
      } else if (fromTopLevel === 'calculator') {
        if (toTopLevel === 'scanner') {
          to.meta.transitionIn = 'animated slideInDown fast'
          to.meta.transitionOut = 'animated slideOutDown fast'
        } else if (toTopLevel === 'settings') {
          to.meta.transitionIn = 'animated slideInUp fast'
          to.meta.transitionOut = 'animated slideOutUp fast'
        }
      }
    }
  })

  return Router
})
