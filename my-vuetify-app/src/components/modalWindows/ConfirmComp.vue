/* ConfirmDeleteDialog.vue */
<template>
  <div>
    <v-hover v-slot="{ isHovering, props }">
      <v-avatar
        v-bind="props"
        size="38"
        :color="isHovering ? 'red-lighten-4' : 'grey-lighten-3'"
        class="elevation-2"
        style="cursor:pointer;"
        @click="openDialog"
      >
        <v-icon color="error" v-tooltip="'Удалить'">mdi-delete</v-icon>
      </v-avatar>
    </v-hover>

    <v-dialog v-model="confirmDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h6">{{ title }}</v-card-title>
        <v-card-text>
          {{ message }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="cancel">{{ cancelText }}</v-btn>
          <v-btn :color="confirmColor" @click="confirmDelete">{{ confirmText }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="errorDialog" max-width="440" persistent>
      <v-card>
        <v-card-title class="text-h6 d-flex align-center">
          <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
          Ошибка при удалении
        </v-card-title>
        <v-card-text>
          {{ errorMessage }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="errorDialog = false">Понятно</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ConfirmDeleteDialog',
  props: {
    item : Object,
    deleteUrl: { type: String, default: '/api/equipment' },
    title: { type: String, default: 'Подтвердите удаление' },
    message: {
      type: String,
      default: 'Вы уверены, что хотите удалить этот элемент?'
    },
    confirmText: { type: String, default: 'Удалить' },
    cancelText: { type: String, default: 'Отмена' },
    confirmColor: { type: String, default: 'red' }
  },
  data() {
    return {
      confirmDialog: false,
      errorDialog: false,
      errorMessage: ''
    }
  },
  methods: {
    openDialog() {
      this.confirmDialog = true
    },
    getErrorMessage(err) {
      const data = err.response?.data
      if (!data) return err.message || 'Не удалось удалить элемент.'
      const detail = data.detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail) && detail.length) return detail.map(d => d.msg || d).join(' ')
      return data.message || data.msg || 'Не удалось удалить элемент.'
    },
    async confirmDelete() {
      try {
        await axios.delete(`${this.deleteUrl}?id=${this.item.id}`)
        this.$emit('deleted', this.item)
      } catch (e) {
        console.error('Ошибка удаления:', e)
        this.errorMessage = this.getErrorMessage(e)
        this.errorDialog = true
      } finally {
        this.confirmDialog = false
      }
    },
    cancel() {
      this.confirmDialog = false
    }
  }
}
</script>
