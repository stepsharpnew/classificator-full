<template>
  <v-dialog v-model="dialogVisible" max-width="500px" persistent>
    <v-card>
      <v-card-title class="text-h6">Добавить подразделение</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="isValid">
          <v-text-field
            v-model="name"
            label="Название"
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
  emits: ['update:modelValue', 'dep-created'],

  data() {
    return {
      dialogVisible: this.modelValue, // локальная копия пропа
      isValid: false,
      name: '',
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

  methods: {
    close() {
      this.dialogVisible = false;
    },
    async submit() {
      if (!this.$refs.form.validate()) return;
      try {
        const res = await axios.post(
          `/api/department?name=${this.name}`,
          this.form,
        );
        console.log(res.data);

        this.$emit('dep-created');
        this.close();
      } catch (e) {
        console.error('Ошибка создания пользователя', e);
      }
    },
  },
};
</script>
