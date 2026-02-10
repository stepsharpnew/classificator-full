<script setup>
import { onMounted, onUnmounted } from 'vue';
import { startTokenRefreshInterval, stopTokenRefreshInterval } from './plugins/auth';

onMounted(() => {
  // Запускаем периодическую проверку токена при монтировании приложения
  startTokenRefreshInterval();
});

onUnmounted(() => {
  // Останавливаем проверку при размонтировании
  stopTokenRefreshInterval();
});
</script>

<template>
  <v-app>
    <v-main>
      <div class="main-content">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<style scoped>
.main-content {
  /* max-width: 900px; */
  padding: 0px 0px;
  background: #ffcdcd;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(80, 80, 180, 0.08);
}
</style>
