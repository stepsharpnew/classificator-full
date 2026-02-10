import { createApp } from 'vue';
import App from './App.vue';
import './plugins/auth.js';
import vuetify from './plugins/vuetify';
import router from './router';

const app = createApp(App);
const toastPlugin = {
  install(app) {
    app.config.globalProperties.$toast = {
      success(message) {
        console.log('✅', message);
        // Можно добавить Vuetify snackbar здесь
      },
      error(message) {
        console.log('❌', message);
      },
      info(message) {
        console.log('ℹ️', message);
      },
    };
  },
};

app.use(toastPlugin);
app.use(router);
app.use(vuetify);
app.mount('#app');
