<template>
  <v-dialog v-model="dialogVisible" max-width="450px" persistent>
    <v-card>
      <v-card-title class="text-h6">Редактировать пользователя</v-card-title>
      <v-card-text>
        <div class="mb-4">
          <div class="text-body-2 text-medium-emphasis mb-1">{{ user?.first_name }} {{ user?.last_name }}</div>
          <div class="text-caption">{{ user?.login }}</div>
        </div>
        <v-checkbox
          v-model="isSkziAdmin"
          label="Администратор СКЗИ"
          hide-details
          color="primary"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="close">Отмена</v-btn>
        <v-btn color="primary" :loading="loading" @click="submit">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'EditUserDialog',
  props: {
    modelValue: { type: Boolean, default: false },
    user: { type: Object, default: null },
  },
  emits: ['update:modelValue', 'updated'],

  data() {
    return {
      dialogVisible: this.modelValue,
      isSkziAdmin: false,
      loading: false,
    };
  },

  watch: {
    modelValue(val) {
      this.dialogVisible = val;
      if (val && this.user) {
        this.isSkziAdmin = !!this.user.is_skzi_admin;
      }
    },
    dialogVisible(val) {
      this.$emit('update:modelValue', val);
    },
    user: {
      immediate: true,
      handler(u) {
        if (u) this.isSkziAdmin = !!u.is_skzi_admin;
      },
    },
  },

  methods: {
    close() {
      this.dialogVisible = false;
    },
    async submit() {
      if (!this.user?.login) return;
      this.loading = true;
      try {
        await axios.put('/api/user', {
          login: this.user.login,
          is_skzi_admin: this.isSkziAdmin,
        });
        this.$emit('updated');
        this.close();
      } catch (e) {
        const msg = e?.response?.data?.detail ?? e?.response?.data?.error?.msg ?? 'Ошибка сохранения';
        this.$emit('notify', { message: msg, type: 'error' });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
