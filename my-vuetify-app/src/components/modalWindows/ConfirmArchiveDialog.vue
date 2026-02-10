<template>
  <div>
    <v-hover v-slot="{ isHovering, props }">
      <v-avatar
        v-bind="props"
        size="38"
        :color="isHovering ? 'blue-lighten-4' : 'grey-lighten-3'"
        class="elevation-2"
        style="cursor: pointer"
        @click="openDialog"
      >
        <v-icon color="primary" v-tooltip="'В архив'"
          >mdi-archive-plus-outline</v-icon
        >
      </v-avatar>
    </v-hover>

    <v-dialog v-model="confirmDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">{{ title }}</v-card-title>
        <v-card-text>
          {{ message }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="cancel">{{ cancelText }}</v-btn>
          <v-btn :color="confirmColor" @click="confirmArchive">{{
            confirmText
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ConfirmArchiveDialog',
  props: {
    item: Object,
    archiveUrl: { type: String, default: '/api/archive' },
    title: { type: String, default: 'Переместить в архив' },
    message: {
      type: String,
      default: 'Вы уверены, что хотите переместить этот элемент в архив?',
    },
    confirmText: { type: String, default: 'В архив' },
    cancelText: { type: String, default: 'Отмена' },
    confirmColor: { type: String, default: 'primary' },
  },
  data() {
    return {
      confirmDialog: false,
    };
  },
  methods: {
    openDialog() {
      this.confirmDialog = true;
    },
    async confirmArchive() {
      try {
        console.log('Архивация:', this.item);
        const archived = await axios.post(this.archiveUrl, {
          id: this.item.id,
        });
        console.log('Ответ сервера:', archived);
        this.$emit('archived', this.item);
      } catch (e) {
        console.error('Ошибка архивации:', e);
      } finally {
        this.confirmDialog = false;
      }
    },
    cancel() {
      this.confirmDialog = false;
    },
  },
};
</script>
