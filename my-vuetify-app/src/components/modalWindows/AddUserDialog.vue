<template>
  <v-dialog v-model="dialogVisible" max-width="500px" persistent>
    <v-card>
      <v-card-title class="text-h6">Добавить пользователя</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="isValid">
          <v-text-field
            v-model="form.login"
            label="Логин"
            :rules="[(v) => !!v || 'Обязательно']"
          />

          <v-text-field
            v-model="form.first_name"
            label="Имя"
            :rules="[(v) => !!v || 'Обязательно']"
          />

          <v-text-field
            v-model="form.last_name"
            label="Фамилия"
            :rules="[(v) => !!v || 'Обязательно']"
          />

          <v-select
            v-model="form.department_id"
            :items="departments"
            item-title="name"
            item-value="id"
            label="Подразделение"
            :rules="[(v) => !!v || 'Выберите подразделение']"
          />

          <v-select
            v-model="form.role"
            label="Роль"
            :items="roles"
            :rules="[(v) => !!v || 'Выберите роль']"
          />

          <v-checkbox
            v-model="form.is_skzi_admin"
            label="Администратор СКЗИ"
            hide-details
            color="primary"
          />

          <v-text-field
            v-model="form.password"
            label="Пароль"
            type="password"
            :rules="[(v) => !!v || 'Обязательно']"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="close">Отмена</v-btn>
        <v-btn color="info" :disabled="!isValid" @click="submit">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
  },
  emits: ['update:modelValue', 'user-created'],

  data() {
    return {
      dialogVisible: this.modelValue, // локальная копия пропа
      isValid: false,
      form: {
        login: '',
        first_name: '',
        last_name: '',
        department_id: '', // здесь будет id, а не name
        role: '',
        password: '',
        is_skzi_admin: false,
      },
      departments: [],
      roles: ['mol', 'chief_engineer'],
    };
  },

  watch: {
    modelValue(newVal) {
      this.dialogVisible = newVal;
    },
    dialogVisible(newVal) {
      this.$emit('update:modelValue', newVal);
    },
  },

  async mounted() {
    this.fetchData();
  },

  methods: {
    close() {
      this.dialogVisible = false;
    },
    async fetchData() {
      try {
        const res = await axios.get('/api/departments');
        this.departments = res.data;
        console.log(this.departments);
      } catch (e) {
        console.error('Ошибка загрузки подразделений', e);
      }
    },
    async submit() {
      if (!this.$refs.form.validate()) return;

      // Проверяем, что выбран отдел, и передаем его id
      if (
        typeof this.form.department_id === 'object' &&
        this.form.department_id.id
      ) {
        this.form.department_id = this.form.department_id.id;
      }

      try {
        const res = await axios.post('/api/user', this.form);
        console.log(res.data);

        this.$emit('user-created');
        this.close();
      } catch (e) {
        console.error('Ошибка создания пользователя', e);
      }
    },
  },
};
</script>
