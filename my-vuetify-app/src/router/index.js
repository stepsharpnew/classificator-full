import { createRouter, createWebHistory } from 'vue-router';
import { clearTokens, getAccessToken, getRefreshToken } from '../plugins/auth';
import ArchivePage from '../components/pages/ArchivePage.vue';
import ClassificationPage from '../components/pages/ClassificationPage.vue';
import DepartmentPage from '../components/pages/DepartmentPage.vue';
import HomePage from '../components/pages/HomePage.vue';
import LoginPage from '../components/pages/LoginPage.vue';
import NotesPage from '../components/pages/NotesPage.vue';
import RequestPage from '../components/pages/RequestPage.vue';
import SkziPage from '../components/pages/SkziPage.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },
  {
    path: '/classification',
    name: 'classification',
    component: ClassificationPage,
  },
  {
    path: '/archive',
    name: 'archive',
    component: ArchivePage,
  },
  {
    path: '/request',
    name: 'request',
    component: RequestPage,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },
  {
    path: '/department',
    name: 'department',
    component: DepartmentPage,
  },
  {
    path: '/notes',
    name: 'notes',
    component: NotesPage,
  },
  {
    path: '/skzi',
    name: 'skzi',
    component: SkziPage,
  },
  {
    path: '/management',
    name: 'management',
    component: SkziPage,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Глобальный перехватчик авторизации
router.beforeEach((to, from, next) => {
  // Предотвращаем бесконечные редиректы
  if (to.path === from.path && to.path === '/login') {
    return next();
  }

  const publicPages = ['/login'];
  const authRequired = !publicPages.includes(to.path);
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();

  // Если пользователь на странице логина и уже авторизован, перенаправляем на главную
  if (to.path === '/login' && accessToken && refreshToken) {
    return next('/');
  }

  // Если требуется авторизация
  if (authRequired) {
    // Если нет access токена
    if (!accessToken) {
      // Если есть refresh токен, можно попробовать обновить (но это сделает interceptor)
      if (!refreshToken) {
        clearTokens();
        // Используем replace: false, чтобы избежать проблем с навигацией
        return next({ path: '/login', replace: true });
      }
      // Если есть refresh токен, разрешаем переход (interceptor обновит токен)
      return next();
    }

    // Проверяем, не истек ли access токен
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const exp = payload.exp * 1000;
      // Если токен истек более чем на 1 минуту, проверяем refresh токен
      if (Date.now() >= exp - 60000) {
        if (!refreshToken) {
          clearTokens();
          return next({ path: '/login', replace: true });
        }
        // Если есть refresh токен, разрешаем переход (interceptor обновит токен)
        return next();
      }
    } catch (e) {
      // Если не удалось декодировать токен, проверяем refresh токен
      if (!refreshToken) {
        clearTokens();
        return next({ path: '/login', replace: true });
      }
      return next();
    }
  }

  next();
});

export default router;
