<template>
  <v-dialog v-model="showDialog" max-width="600px" persistent>
    <v-card>
      <v-card-title class="text-h6 pa-4">
        <v-icon start>mdi-tag-multiple</v-icon>
        Управление тегами
        <v-chip
          v-if="note"
          color="primary"
          variant="flat"
          size="small"
          class="ml-2"
        >
          {{ note.title || 'Без названия' }}
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-4">
        <!-- Создание нового тега -->
        <v-row align="center" class="mb-4">
          <v-col cols="8">
            <v-text-field
              v-model="newTagName"
              label="Новый тег"
              outlined
              dense
              clearable
              placeholder="Введите название тега..."
              :loading="saving"
              @keyup.enter="addNewTag"
            />
          </v-col>
          <v-col cols="4" class="d-flex">
            <v-btn
              color="primary"
              :disabled="!newTagName.trim() || saving"
              @click="addNewTag"
              class="ma-0 w-100"
              rounded
              :loading="saving"
            >
              <v-icon start>mdi-plus</v-icon>
              Добавить
            </v-btn>
          </v-col>
        </v-row>

        <v-divider class="my-4" />

        <div class="text-subtitle-2 mb-2">Теги заметки:</div>
        <v-sheet
          class="pa-3 border rounded"
          style="min-height: 120px; max-height: 320px; overflow-y: auto"
        >
          <div
            v-if="currentTags.length === 0"
            class="text-center py-8 text-grey"
          >
            <v-icon size="48" class="mb-2">mdi-tag-off-outline</v-icon>
            <div>Тегов пока нет</div>
            <div class="text-caption">Добавьте теги выше</div>
          </div>

          <div class="d-flex flex-wrap gap-2">
            <v-chip
              v-for="(tag, index) in currentTags"
              :key="index"
              color="primary"
              variant="flat"
              size="large"
              closable
              @click:close="removeTag(tag)"
              class="ma-1"
            >
              <v-icon start size="small">mdi-tag</v-icon>
              {{ tag }}
            </v-chip>
          </div>
        </v-sheet>

        <!-- Информация о количестве -->
        <div class="mt-3 text-caption text-grey d-flex justify-space-between">
          <span>Всего тегов: {{ currentTags.length }}</span>
        </div>

        <!-- Предложенные теги из других заметок -->
        <v-alert
          v-if="suggestedTags.length > 0"
          color="info"
          variant="tonal"
          class="mt-4"
        >
          <template #title> Теги из других заметок: </template>
          <div class="d-flex flex-wrap gap-1 mt-2">
            <v-chip
              v-for="tag in suggestedTags"
              :key="tag"
              color="info"
              variant="outlined"
              size="small"
              @click="addExistingTag(tag)"
              class="cursor-pointer"
            >
              <v-icon start size="x-small">mdi-plus</v-icon>
              {{ tag }}
            </v-chip>
          </div>
        </v-alert>
      </v-card-text>

      <v-card-actions class="pa-4 d-flex justify-end gap-2">
        <v-btn variant="text" @click="close" :disabled="saving"> Отмена </v-btn>
        <v-btn
          color="primary"
          @click="saveTags"
          :loading="saving"
          :disabled="saving"
        >
          <v-icon start>mdi-content-save</v-icon>
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TagDialog',
  props: {
    modelValue: { type: Boolean, required: true },
    note: { type: Object, default: null },
  },

  data() {
    return {
      showDialog: this.modelValue,
      newTagName: '',
      currentTags: [], // Храним только имена тегов как строки
      saving: false,
    };
  },

  computed: {
    suggestedTags() {
      if (!this.note) return [];

      // Собираем все уникальные теги из всех заметок
      const allTags = new Set();
      this.getAllNotes()?.forEach((note) => {
        if (note.id !== this.note.id && note.tags) {
          const tagNames = this.extractTagNames(note.tags);
          tagNames.forEach((tag) => {
            if (tag && !this.currentTags.includes(tag)) {
              allTags.add(tag);
            }
          });
        }
      });

      return Array.from(allTags).slice(0, 10);
    },
  },

  watch: {
    modelValue(val) {
      this.showDialog = val;
      if (val) {
        this.opened();
      }
    },

    showDialog(val) {
      this.$emit('update:modelValue', val);
    },

    note: {
      handler(newNote) {
        if (newNote) {
          this.initTags();
        }
      },
      immediate: true,
      deep: true,
    },
  },

  methods: {
    getAllNotes() {
      return this.$parent.notes || [];
    },

    extractTagNames(tags) {
      if (!tags || !Array.isArray(tags)) return [];

      return tags
        .map((tag) => {
          if (typeof tag === 'object' && tag !== null && tag.name) {
            return tag.name;
          }
          return tag;
        })
        .filter((tag) => tag && typeof tag === 'string');
    },

    opened() {
      console.log('Dialog opened, note:', this.note);
      this.initTags();
    },

    initTags() {
      if (this.note && this.note.tags) {
        // Извлекаем только имена тегов
        this.currentTags = this.extractTagNames(this.note.tags);
        console.log('Initialized currentTags:', this.currentTags);
      } else {
        this.currentTags = [];
        console.log('Initialized empty currentTags');
      }
      this.newTagName = '';
    },

    addNewTag() {
      const tagName = this.newTagName?.trim();
      console.log('Adding tag:', tagName);
      console.log('Current tags before:', this.currentTags);

      if (!tagName) {
        console.log('Tag name is empty');
        return;
      }

      if (this.currentTags.includes(tagName)) {
        console.log('Tag already exists:', tagName);
        this.newTagName = '';
        return;
      }

      // Создаем новый массив для реактивности
      this.currentTags = [...this.currentTags, tagName];
      this.newTagName = '';

      console.log('Current tags after:', this.currentTags);
    },

    addExistingTag(tagName) {
      if (tagName && !this.currentTags.includes(tagName)) {
        this.currentTags = [...this.currentTags, tagName];
      }
    },

    removeTag(tagName) {
      this.currentTags = this.currentTags.filter((tag) => tag !== tagName);
    },

    async saveTags() {
      if (!this.note?.id) {
        this.close();
        return;
      }

      this.saving = true;
      try {
        console.log('Saving tags:', this.currentTags);

        // Отправляем PUT запрос с массивом строк (имен тегов)
        await axios.put(`/api/notes/${this.note.id}`, {
          title: this.note.title,
          content: this.note.content,
          tags: this.currentTags, // Отправляем массив строк
        });

        this.$emit('tag-updated');

        // Используем альтернативный способ показа уведомления
        this.showNotification('Теги обновлены успешно', 'success');
        this.close();
      } catch (err) {
        console.error('Ошибка сохранения тегов', err);
        this.showNotification('Не удалось сохранить теги', 'error');
      } finally {
        this.saving = false;
      }
    },

    showNotification(message, type = 'info') {
      // Способ 1: Используем Vuetify snackbar если доступен
      if (this.$root && this.$root.$vuetify) {
        // Создаем временный snackbar
        const snackbar = document.createElement('div');
        snackbar.className = `v-snackbar v-snackbar--${type}`;
        snackbar.innerHTML = `
          <div class="v-snackbar__wrapper">
            <div class="v-snackbar__content">${message}</div>
            <div class="v-snackbar__actions">
              <button class="v-btn v-btn--text v-btn--rounded">Закрыть</button>
            </div>
          </div>
        `;
        document.body.appendChild(snackbar);

        setTimeout(() => {
          if (document.body.contains(snackbar)) {
            document.body.removeChild(snackbar);
          }
        }, 3000);
      }
      // Способ 2: Простой alert как fallback
      else {
        alert(message);
      }
    },

    close() {
      this.showDialog = false;
      this.newTagName = '';
      this.saving = false;
      this.currentTags = [];
    },
  },
};
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
.gap-1 {
  gap: 4px;
}
.cursor-pointer {
  cursor: pointer;
}
</style>
