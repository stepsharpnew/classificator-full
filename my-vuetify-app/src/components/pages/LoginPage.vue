<template>
    <v-container fluid class="pa-4  d-flex align-start justify-center" style="height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #3E578C 100%);">
      <v-card class="pa-8 rounded-lg" max-width="500" width="100%" style="font-family: 'Roboto', sans-serif; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <v-row class="justify-center mb-6">
          <v-col cols="12" class="text-center">
            <h2 class="mb-2" style="color: #1976d2; font-size: 28px; font-weight: 500;">Вход в систему</h2>
            <div class="text-caption text-medium-emphasis">Введите ваши учетные данные</div>
          </v-col>
        </v-row>
        <v-form @submit.prevent="onLogin">
          <v-text-field
            v-model="login"
            label="Логин"
            variant="outlined"
            density="comfortable"
            hide-details
            class="mb-4"
            prepend-inner-icon="mdi-account"
            bg-color="white"
          />
          <v-text-field
            v-model="password"
            label="Пароль"
            type="password"
            variant="outlined"
            density="comfortable"
            hide-details
            class="mb-6"
            prepend-inner-icon="mdi-lock"
            bg-color="white"
          />
          <v-btn
            color="primary"
            variant="elevated"
            type="submit"
            block
            size="large"
            :loading="loading"
            :disabled="loading"
          >
            <template v-slot:loader>
              <v-progress-circular
                indeterminate
                color="white"
                :width="3"
                :size="20"
              ></v-progress-circular>
              <span class="ml-2">Вход...</span>
            </template>
            <span v-if="!loading">Войти</span>
          </v-btn>
          <v-alert 
            v-if="error" 
            type="error" 
            class="mt-4"
            variant="tonal"
            density="compact"
          >
            {{ error }}
          </v-alert>
        </v-form>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    name: 'LoginPage',
    data() {
      return {
        login: '',
        password: '',
        loading: false,
        error: ''
      }
    },
    methods: {
      async onLogin() {
        this.loading = true;
        this.error = '';
        
        // Имитация задержки в 2 секунды
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          const response = await axios.post(`/api/login?login=${this.login}`, {
            password: this.password
          });
          
          // Сохраняем access/refresh токены в localStorage
          localStorage.setItem('access_token', response.data.data.access_token);
          localStorage.setItem('refresh_token', response.data.data.refresh_token);         
          this.$router.push('/');
        } catch (e) {
          console.error(e);
          this.error = 'Неверный логин или пароль';
        } finally {
          this.loading = false;
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .v-card {
    transition: all 0.3s ease;
  }
  .v-card:hover {
    /* transform: translateY(-2px); */
    box-shadow: 0 15px 35px rgba(0,0,0,0.15) !important;
  }
  </style>