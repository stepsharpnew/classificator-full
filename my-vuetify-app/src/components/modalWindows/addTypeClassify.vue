<template>
  <v-dialog v-model="isOpen" max-width="500px">
    <v-card>
      <v-card-title class="text-h6 font-weight-bold">
        Добавить новый элемент
      </v-card-title>

      <v-card-text>
        <v-form ref="form" v-model="isValid">
          <v-text-field
            v-model="formData.path"
            label="Путь *"
            placeholder="Выберите путь"
            dense
            outlined
            required
          />

          <v-select
            v-if="typeModal != 'classification'"
            v-model="formData.type"
            :items="types"
            item-title="label"
            item-value="value"
            label="Тип"
            placeholder="Выберите тип (необязательно)"
            dense
            outlined
          />

          <v-textarea
            v-model="formData.name"
            label="Название *"
            placeholder="Введите название"
            dense
            outlined
            rows="2"
            required
          />
          <v-text-field
            v-if="typeModal != 'classification'"
            v-model="formData.fnn"
            label="ФНН *"
            placeholder="Введите ФНН"
            dense
            outlined
            required
          />
        </v-form>
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn color="success" @click="createItem">Создать</v-btn>
        <v-btn color="error" @click="closeDialog">Отмена</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'AddTypeClassify',

  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
    typeModal: {
      type: String,
      required: true,
    },
  },

  emits: ['update:modelValue', 'create'],

  data() {
    return {
      isOpen: this.modelValue,
      isValid: false,
      formData: {
        path: '',
        type: '',
        name: '',
        fnn: '',
      },
      types: [
        { label: 'SSIUS', value: 'ssius' },
        { label: 'SIUS', value: 'sius' },
        { label: '(Пусто)', value: '' },
      ],
    };
  },

  watch: {
    modelValue(val) {
      this.isOpen = val;
    },
    isOpen(val) {
      this.$emit('update:modelValue', val);
    },
  },

  methods: {
    createItem() {
      //   if (!this.formData.path || !this.formData.type || !this.formData.name)
      //     return;
      this.$emit('createItem', { typeModal: this.typeModal, ...this.formData });
      this.resetForm();
      this.closeDialog();
    },
    closeDialog() {
      this.isOpen = false;
    },
    resetForm() {
      this.formData = { path: '', type: '', name: '', fnn: '' };
    },
  },
};
</script>
