<template>
  <v-dialog v-model="localDialog" max-width="700px">
    <v-card>
      <v-card-title>
        <span class="text-h6">
          {{ isEdit ? 'Редактировать заметку' : 'Создать заметку' }}
        </span>
      </v-card-title>

      <v-card-text>
        <v-form>
          <v-text-field v-model="local.title" label="Заголовок" required />
          <v-textarea v-model="local.content" label="Содержимое" rows="4" />

          <div class="mt-4">
            <div class="subtitle-2 mb-2">Теги</div>

            <v-autocomplete
              v-model="local.tagIds"
              :items="tags"
              item-text="name"
              item-value="id"
              multiple
              chips
              clearable
            />
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="close">Отмена</v-btn>
        <v-btn color="primary" @click="save">
          {{ isEdit ? 'Сохранить' : 'Создать' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'AddNoteDialog',

  props: {
    modelValue: { type: Boolean, default: false },
    tags: { type: Array, default: () => [] },
    noteToEdit: { type: Object, default: null },
  },

  data() {
    return {
      localDialog: this.modelValue, // локальная копия
      local: {
        title: '',
        content: '',
        tagIds: [],
      },
    };
  },

  computed: {
    isEdit() {
      return !!this.noteToEdit;
    },
  },

  watch: {
    // Обновление локальной переменной при открытии
    modelValue(val) {
      this.localDialog = val;

      if (val) {
        if (this.isEdit) {
          this.local.title = this.noteToEdit.title;
          this.local.content = this.noteToEdit.content;
          this.local.tagIds = this.noteToEdit.tags.map((t) => t.id);
        } else {
          // При создании — очистить форму
          this.local.title = '';
          this.local.content = '';
          this.local.tagIds = [];
        }
      }
    },

    // отправляем изменения обратно родителю
    localDialog(val) {
      this.$emit('update:modelValue', val);
    },
  },

  methods: {
    close() {
      this.localDialog = false;
    },

    save() {
      this.$emit(this.isEdit ? 'updated' : 'created', { ...this.local });
      this.close();
    },
  },
};
</script>
