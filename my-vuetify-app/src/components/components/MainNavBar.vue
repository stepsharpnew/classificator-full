<template>
  <v-app-bar
    elevation="8"
    density="comfortable"
    height="80"
    color="primary"
    class="px-6 app-bar-gradient"
  >
    <!-- Левая часть с иконкой и названием -->
    <div class="d-flex align-center">
      <v-icon class="mr-4" color="white" size="38">mdi-clipboard-list</v-icon>
      <span class="app-title"> Учет материальных средств </span>
    </div>

    <v-spacer></v-spacer>

    <!-- Средняя часть — вкладки -->
    <v-tabs
      v-model="tab"
      align-tabs="center"
      class="mr-8"
      color="white"
      slider-color="white"
    >
      <v-tab to="/">Главная</v-tab>
      <v-tab to="/classification">Классификатор</v-tab>
      <v-tab to="/skzi">СКЗИ</v-tab>
      <v-tab to="/archive">Архив</v-tab>
      <v-tab to="/request">Заявки</v-tab>
      <v-tab to="/department">Подразделения</v-tab>
      <v-tab to="/notes">Заметки</v-tab>
    </v-tabs>

    <v-spacer></v-spacer>

    <!-- Правая часть — пользователь и выход -->
    <div class="d-flex align-center">
      <v-chip
        color="rgba(255,255,255,0.15)"
        variant="flat"
        class="mr-4 px-4"
        size="large"
        style="
          backdrop-filter: blur(4px);
          color: #fff;
          font-size: 1.1rem;
          height: 48px;
        "
      >
        <v-icon start size="26" color="white">mdi-account</v-icon>
        {{ username }}
      </v-chip>

      <v-btn
        variant="flat"
        color="white"
        prepend-icon="mdi-logout"
        size="large"
        style="
          height: 48px;
          color: #1565c0;
          font-weight: 700;
          font-size: 1rem;
          background-color: #fff;
        "
        class="text-none"
        @click="Logout()"
      >
        Выход
      </v-btn>
    </div>
  </v-app-bar>
</template>

<script>
export default {
  name: 'MainNavBar',
  data() {
    return {
      username: '',
      tab: null,
    };
  },
  methods: {
    Logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.$router.push('/login');
    },
  },
  mounted() {
    try {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        const payloadBase64 = accessToken.split('.')[1];
        const payload = JSON.parse(atob(payloadBase64));
        this.username = payload.user?.login || 'Неизвестный пользователь';
      }
    } catch (err) {
      console.error('Invalid token:', err);
      this.username = 'Неизвестный пользователь';
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.$router.push('/login');
    }
  },
};
</script>

<style scoped>
.app-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.8px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
.v-tab {
  font-weight: 600;
  text-transform: none;
  font-size: 1.05rem;
}
.v-tab.v-tab--selected {
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
}
</style>
