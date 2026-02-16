<template>
  <div style="background-color: aliceblue">
    <MainNavBar />

    <!-- Верхняя часть с кнопками -->
    <v-container
      fluid
      class="pa-8 fill-height d-flex align-center justify-center bg-grey-lighten-4"
    >
      <v-row class="w-100" justify="center">
        <v-col cols="12" md="3" class="d-flex justify-center">
          <v-btn
            color="info"
            class="w-100 text-h6 text-white"
            elevation="4"
            rounded="lg"
            @click="showAddDep = true"
          >
            Добавить подразделение
          </v-btn>
        </v-col>
        <v-col cols="12" md="3" class="d-flex justify-center">
          <v-btn
            color="info"
            class="w-100 text-h6 text-white"
            elevation="4"
            rounded="lg"
            @click="showAddUser = true"
          >
            Добавить пользователя
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Таблица -->
    <v-container fluid class="pa-8">
      <v-card elevation="2" class="pa-4">
        <v-row class="mb-2 font-weight-bold">
          <v-col cols="6" class="text-left">Название</v-col>
          <v-col cols="6" class="text-left">Пользователи</v-col>
        </v-row>
        <v-divider></v-divider>

        <v-row
          v-for="(dep, i) in departments"
          :key="i"
          class="py-3"
          align="center"
        >
          <v-col cols="6" class="text-left">
            {{ dep.name }}
          </v-col>
          <v-col cols="6" class="text-left">
            <v-chip
              v-for="(user, j) in dep.users"
              :key="j"
              color="blue"
              class="ma-1 pa-1"
              label
              size="big"
              style="cursor: pointer"
              @click="openEditUser(user)"
            >
              {{ user.first_name }} {{ user.last_name }}
              <span v-if="user.role" class="ml-1 text-caption">({{ roleDisplayName(user.role) }})</span>
              <v-icon v-if="user.is_skzi_admin" size="small" class="ml-1" color="green">mdi-shield-check</v-icon>
              <v-icon size="small" class="ml-1">mdi-pencil</v-icon>
            </v-chip>
          </v-col>
          <v-divider></v-divider>
        </v-row>
      </v-card>
    </v-container>

    <!-- Модалка добавления пользователя -->
    <AddUserDialog v-model="showAddUser" @user-created="loadUsers" />
    <AddDepDialog v-model="showAddDep" @dep-created="loadUsers" />
    <EditUserDialog
      v-model="showEditUser"
      :user="selectedUser"
      @updated="loadUsers"
      @notify="onNotify"
    />
    <NotificationDialog
      v-model="notification.show"
      :message="notification.message"
      :type="notification.type"
    />
  </div>
</template>

<script>
import axios from 'axios';
import MainNavBar from '../components/MainNavBar.vue';
import AddUserDialog from '../modalWindows/AddUserDialog.vue';
import AddDepDialog from '../modalWindows/addDepDialog.vue';
import EditUserDialog from '../modalWindows/EditUserDialog.vue';
import NotificationDialog from '../modalWindows/NotificationDialog.vue';

export default {
  components: { MainNavBar, AddUserDialog, AddDepDialog, EditUserDialog, NotificationDialog },
  data() {
    return {
      users: [],
      departments: [],
      showAddUser: false,
      showAddDep: false,
      showEditUser: false,
      selectedUser: null,
      notification: { show: false, message: '', type: 'success' },
    };
  },

  mounted() {
    this.loadUsers();
  },

  methods: {
    openEditUser(user) {
      this.selectedUser = user;
      this.showEditUser = true;
    },
    onNotify({ message, type }) {
      this.notification = { show: true, message, type };
    },
    roleDisplayName(role) {
      if (!role) return '';
      const r = String(role).toLowerCase();
      if (r === 'chief_engineer') return 'Главный инженер';
      if (r === 'mol') return 'МОЛ';
      if (r === 'head') return 'Руководитель';
      return role;
    },
    async loadUsers() {
      try {
        const res = await axios.get('/api/users');
        this.users = res.data;

        // группировка по департаментам
        const grouped = {};
        this.users.forEach((user) => {
          const depName = user.department?.name || 'Без подразделения';
          if (!grouped[depName]) grouped[depName] = [];
          grouped[depName].push(user);
        });

        this.departments = Object.keys(grouped).map((name) => ({
          name,
          users: grouped[name],
        }));
      } catch (e) {
        console.error('Ошибка загрузки:', e);
      }
    },
    async loadDeps() {
      try {
        const res = await axios.get('/api/departments');
        this.departments = res.data;
        this.departments = Object.keys(grouped).map((name) => ({
          name,
          users: grouped[name],
        }));
      } catch (e) {
        console.error('Ошибка загрузки:', e);
      }
    },
  },
};
</script>
