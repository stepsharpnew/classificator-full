import axios from 'axios';

const API_URL = '/api';

// Настраиваем axios для работы с cookies
axios.defaults.withCredentials = true;

// Флаг для отслеживания редиректа, чтобы избежать множественных редиректов
let isRedirecting = false;

// Функция для безопасного редиректа на страницу логина
function safeRedirectToLogin() {
  // Проверяем, что мы не находимся уже на странице логина
  if (typeof window === 'undefined') {
    return;
  }

  const currentPath = window.location.pathname;
  if (currentPath === '/login' || currentPath === '/login/') {
    return;
  }

  // Предотвращаем множественные редиректы
  if (isRedirecting) {
    return;
  }

  isRedirecting = true;

  // Используем requestAnimationFrame и setTimeout для отложенного редиректа,
  // чтобы не прерывать текущий рендеринг Vue компонентов
  requestAnimationFrame(() => {
    setTimeout(() => {
      try {
        // Используем replace вместо href, чтобы не создавать новую запись в истории
        // и избежать проблем с навигацией
        if (window.location.pathname !== '/login') {
          window.location.replace('/login');
        }
      } catch (e) {
        // В случае ошибки используем простой редирект
        console.warn('Ошибка при редиректе на /login:', e);
        try {
          window.location.href = '/login';
        } catch (e2) {
          console.error('Критическая ошибка редиректа:', e2);
        }
      } finally {
        // Сбрасываем флаг через небольшую задержку
        setTimeout(() => {
          isRedirecting = false;
        }, 1000);
      }
    }, 10); // Небольшая задержка для завершения текущего рендеринга
  });
}

// Флаг для предотвращения одновременных refresh запросов
let isRefreshing = false;
// Очередь запросов, ожидающих обновления токена
let failedQueue = [];

// Функция для обработки очереди после обновления токена
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export function getAccessToken() {
  return localStorage.getItem('access_token');
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

export function setTokens({ access, refresh }) {
  if (access) {
    localStorage.setItem('access_token', access);
  }
  if (refresh) {
    localStorage.setItem('refresh_token', refresh);
  }
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// Проверка истечения токена (примерная, без декодирования JWT)
function isTokenExpired(token) {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // конвертируем в миллисекунды
    // Проверяем, истекает ли токен в ближайшие 30 секунд
    return Date.now() >= exp - 30000;
  } catch (e) {
    // Если не удалось декодировать, считаем токен невалидным
    return true;
  }
}

export async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) {
    throw new Error('No refresh token');
  }

  try {
    // Отправляем refresh токен в body (бэкенд может обрабатывать и cookie, и body)
    const response = await axios.post(`${API_URL}/refresh`, { refresh }, {
      withCredentials: true // Важно для работы с cookies
    });

    // Бэкенд возвращает: { data: { access_token, refresh_token, user }, success: true }
    const responseData = response.data?.data || response.data;
    const newAccess = responseData?.access_token || responseData?.access;
    const newRefresh = responseData?.refresh_token || responseData?.refresh || refresh;

    if (newAccess) {
      setTokens({ access: newAccess, refresh: newRefresh });
      return newAccess;
    } else {
      throw new Error('No access token in response');
    }
  } catch (error) {
    // Если refresh токен истек или невалиден
    if (error.response?.status === 401 || error.response?.status === 403) {
      clearTokens();
      throw new Error('Refresh token expired or invalid');
    }
    throw error;
  }
}

// Axios request interceptor to add access token and check expiration
axios.interceptors.request.use(
  async (config) => {
    const token = getAccessToken();
    
    // Если токен истек, пытаемся обновить его перед запросом
    if (token && isTokenExpired(token)) {
      const refresh = getRefreshToken();
      if (refresh && !isRefreshing) {
        try {
          isRefreshing = true;
          const newAccess = await refreshAccessToken();
          config.headers['Authorization'] = `Bearer ${newAccess}`;
        } catch (e) {
          // Если не удалось обновить, очищаем токены
          clearTokens();
          // Перенаправляем на логин только если это не запрос на refresh
          if (!config.url?.includes('/refresh') && !config.url?.includes('/login')) {
            safeRedirectToLogin();
          }
          return Promise.reject(e);
        } finally {
          isRefreshing = false;
        }
      } else if (!refresh) {
        // Нет refresh токена - перенаправляем на логин
        clearTokens();
        if (!config.url?.includes('/login')) {
          safeRedirectToLogin();
        }
        return Promise.reject(new Error('No refresh token'));
      }
    } else if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Axios interceptor for auto-refresh on 401
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Пропускаем ошибки, которые не связаны с авторизацией
    if (error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Пропускаем запросы на login и refresh
    if (originalRequest.url?.includes('/login') || originalRequest.url?.includes('/refresh')) {
      return Promise.reject(error);
    }

    const refresh = getRefreshToken();

    // Если нет refresh токена — принудительный logout
    if (!refresh) {
      clearTokens();
      safeRedirectToLogin();
      return Promise.reject(error);
    }

    // Если уже идет процесс обновления токена, добавляем запрос в очередь
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return axios(originalRequest);
        })
        .catch(err => {
          return Promise.reject(err);
        });
    }

    // Если это первый retry
    if (!originalRequest._retry) {
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccess = await refreshAccessToken();
        
        // Обновляем заголовок по умолчанию
        axios.defaults.headers.common['Authorization'] = `Bearer ${newAccess}`;
        originalRequest.headers['Authorization'] = `Bearer ${newAccess}`;
        
        // Обрабатываем очередь ожидающих запросов
        processQueue(null, newAccess);
        
        isRefreshing = false;
        return axios(originalRequest);
      } catch (e) {
        isRefreshing = false;
        processQueue(e, null);
        clearTokens();
        safeRedirectToLogin();
        return Promise.reject(e);
      }
    }

    // Если это повторная попытка и она тоже не удалась
    clearTokens();
    safeRedirectToLogin();
    return Promise.reject(error);
  }
);

// Периодическая проверка токена при долгом нахождении на странице
let tokenCheckInterval = null;

export function startTokenRefreshInterval() {
  // Очищаем предыдущий интервал, если он существует
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval);
  }

  // Проверяем токен каждые 5 минут
  tokenCheckInterval = setInterval(async () => {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();

    if (!refreshToken) {
      clearTokens();
      if (window.location.pathname !== '/login') {
        safeRedirectToLogin();
      }
      return;
    }

    // Если access токен истек или истекает в ближайшее время, обновляем его
    if (accessToken && isTokenExpired(accessToken)) {
      try {
        await refreshAccessToken();
      } catch (e) {
        clearTokens();
        if (window.location.pathname !== '/login') {
          safeRedirectToLogin();
        }
      }
    }
  }, 5 * 60 * 1000); // 5 минут
}

export function stopTokenRefreshInterval() {
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval);
    tokenCheckInterval = null;
  }
}

// Запускаем проверку при загрузке модуля, если пользователь авторизован
if (typeof window !== 'undefined' && getRefreshToken()) {
  startTokenRefreshInterval();
}
