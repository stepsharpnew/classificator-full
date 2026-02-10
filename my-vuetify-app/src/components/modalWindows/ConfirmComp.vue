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

    <v-dialog v-model="confirmDialog" max-width="400">
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
      confirmDialog: false
    }
  },
  methods: {
    openDialog() {
      this.confirmDialog = true
    },
    async confirmDelete() {
      try {
        console.log(this.item);
        
        const deleted = await axios.delete(`${this.deleteUrl}?id=${this.item.id}`)
        console.log(deleted);
        
        this.$emit('deleted', this.item)
      } catch (e) {
        console.error('Ошибка удаления:', e)
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
