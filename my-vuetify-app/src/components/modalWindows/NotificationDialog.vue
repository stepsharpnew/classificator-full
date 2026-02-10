<template>
  <v-dialog v-model="visible" max-width="450" persistent>
    <v-card>
      <v-toolbar :color="isError ? 'error' : 'success'" dark dense flat>
        <v-toolbar-title class="text-body-1 font-weight-bold">
          {{ isError ? 'Ошибка' : 'Успешно' }}
        </v-toolbar-title>
        <v-spacer />
        <v-btn icon size="small" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-text class="pt-5 pb-3">
        <div class="d-flex align-start ga-3">
          <v-icon
            :color="isError ? 'error' : 'success'"
            size="32"
          >
            {{ isError ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline' }}
          </v-icon>
          <span class="text-body-1" style="white-space: pre-wrap">{{ message }}</span>
        </div>
      </v-card-text>

      <v-card-actions class="justify-end pb-4 pr-4">
        <v-btn
          :color="isError ? 'error' : 'success'"
          variant="elevated"
          @click="close"
        >
          ОК
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'NotificationDialog',

  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    message: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: 'success', // 'success' | 'error'
    },
  },

  emits: ['update:modelValue'],

  computed: {
    visible: {
      get() {
        return this.modelValue;
      },
      set(val) {
        this.$emit('update:modelValue', val);
      },
    },
    isError() {
      return this.type === 'error';
    },
  },

  methods: {
    close() {
      this.visible = false;
    },
  },
};
</script>
