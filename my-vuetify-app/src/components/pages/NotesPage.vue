<template>
  <div>
    <MainNavBar />

    <!-- Верхняя панель с созданием заметки -->
    <v-container fluid class="pa-6 bg-grey-lighten-4">
      <v-card elevation="2" class="pa-6 rounded-lg">
        <v-card-title class="text-h5 pa-0 mb-4">
          <v-icon start color="primary">mdi-note-plus</v-icon>
          Новая заметка
        </v-card-title>

        <v-row>
          <!-- Заголовок -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="newNote.title"
              label="Заголовок"
              outlined
              rounded
              placeholder="Введите заголовок..."
              :maxlength="50"
              counter
              clearable
            >
              <template #prepend-inner>
                <v-icon color="grey">mdi-format-title</v-icon>
              </template>
            </v-text-field>
          </v-col>

          <!-- Теги -->
          <v-col cols="12" md="4">
            <v-combobox
              v-model="newNote.tags"
              label="Теги"
              multiple
              chips
              outlined
              rounded
              placeholder="Добавьте теги..."
              clearable
              :search-input.sync="tagSearch"
              @keydown.enter="addTag"
            >
              <template #prepend-inner>
                <v-icon color="grey">mdi-tag-multiple</v-icon>
              </template>

              <template #selection="{ attrs, item, select, selected }">
                <v-chip
                  v-bind="attrs"
                  :input-value="selected"
                  close
                  @click="select"
                  @click:close="removeTag(item)"
                  color="primary"
                  size="small"
                  class="ma-1"
                >
                  <v-icon start size="small">mdi-tag</v-icon>
                  {{ item }}
                </v-chip>
              </template>
            </v-combobox>
          </v-col>

          <!-- Кнопка создания -->
          <v-col cols="12" md="4" class="d-flex align-center justify-end">
            <v-btn
              color="primary"
              size="large"
              rounded
              @click="createNote"
              :disabled="!isNoteValid"
              :loading="creatingNote"
              class="w-100"
            >
              <v-icon start>mdi-plus-circle</v-icon>
              Создать заметку
            </v-btn>
          </v-col>
        </v-row>

        <!-- Содержание -->
        <v-row>
          <v-col cols="12">
            <v-textarea
              v-model="newNote.content"
              label="Содержание заметки"
              auto-grow
              outlined
              rounded
              rows="3"
              placeholder="Опишите вашу заметку..."
              :maxlength="1000"
              counter
              clearable
            >
              <template #prepend-inner>
                <v-icon color="grey">mdi-text</v-icon>
              </template>
            </v-textarea>
          </v-col>
        </v-row>

        <!-- Предпросмотр тегов -->
        <v-row v-if="newNote.tags.length > 0">
          <v-col cols="12">
            <v-card variant="outlined" class="pa-3 rounded-lg">
              <div class="text-caption text-grey mb-2">Добавленные теги:</div>
              <div class="d-flex flex-wrap gap-1">
                <v-chip
                  v-for="(tag, index) in newNote.tags"
                  :key="index"
                  color="primary"
                  variant="flat"
                  size="small"
                  closable
                  @click:close="removeTag(tag)"
                >
                  {{ tag }}
                </v-chip>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card>
    </v-container>

    <!-- Список заметок -->
    <v-container fluid class="pa-6 bg-grey-lighten-4">
      <v-card elevation="3" class="pa-4">
        <!-- Панель поиска -->
        <v-row class="pa-3 bg-blue-lighten-4 rounded gap-x-4 mb-4">
          <v-col cols="12" md="4">
            <v-text-field
              label="Поиск по тексту (заголовок, содержание)"
              variant="outlined"
              density="comfortable"
              hide-details
              v-model="filters.search"
              @input="onSearchInput"
              clearable
            >
              <template #prepend-inner>
                <v-icon color="grey">mdi-magnify</v-icon>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-autocomplete
              label="Поиск по тегам"
              variant="outlined"
              density="comfortable"
              hide-details
              v-model="filters.selectedTag"
              item-title="name"
              item-value="name"
              :items="tagSuggestions"
              :loading="tagSuggestionLoading"
              @update:search="onTagInput"
              @update:modelValue="fetchNotes()"
              clearable
              multiple
              chips
            >
              <template #prepend-inner>
                <v-icon color="grey">mdi-tag-multiple</v-icon>
              </template>
              <template #selection="{ attrs, item, select, selected }">
                <v-chip
                  v-bind="attrs"
                  :input-value="selected"
                  close
                  @click="select"
                  @click:close="removeSearchTag(item.raw.name)"
                  color="primary"
                  size="small"
                  class="ma-1"
                >
                  {{ item.raw.name }}
                </v-chip>
              </template>
            </v-autocomplete>
          </v-col>
          <v-col cols="12" md="2" class="d-flex align-center">
            <v-btn variant="elevated" color="error" @click="resetFilters">
              Сброс
            </v-btn>
          </v-col>
          <v-col cols="12" md="2" class="d-flex align-center">
            <div class="text-caption text-grey">
              Всего: {{ totalCount }}
            </div>
          </v-col>
        </v-row>

        <!-- Заголовки таблицы -->
        <v-row class="font-weight-bold mb-2 pa-3">
          <v-col cols="12" md="6" class="text-subtitle-4">Заметка</v-col>
          <v-col cols="12" md="3" class="text-subtitle-4">Теги</v-col>
          <v-col cols="12" md="3" class="text-subtitle-4">Действия</v-col>
        </v-row>
        <v-divider />

        <!-- Список заметок -->
        <div v-if="notes.length === 0 && !loadingNotes" class="text-center pa-8">
          <v-icon size="64" color="grey-lighten-1">mdi-note-off-outline</v-icon>
          <p class="text-h6 text-grey mt-4">Заметок пока нет</p>
          <p class="text-grey">Создайте свою первую заметку!</p>
        </div>

        <div v-if="loadingNotes" class="text-center pa-8">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="text-grey mt-4">Загрузка заметок...</p>
        </div>

        <v-row v-for="note in notes" :key="note.id" class="mb-4 align-center">
          <!-- Содержимое заметки -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="pa-4 h-100">
              <div class="d-flex justify-space-between align-start mb-2">
                <v-card-title class="text-h6 pa-0">
                  {{ note.title || 'Без названия' }}
                </v-card-title>
                <v-chip
                  v-if="note.author"
                  size="small"
                  color="grey-lighten-2"
                  variant="flat"
                >
                  {{ note.author.login }}
                </v-chip>
              </div>

              <v-card-text class="pa-0">
                <p class="text-body-1 mb-2">{{ note.content }}</p>

                <div class="text-caption text-grey">
                  <span>Создано: {{ formatDate(note.created_at) }}</span>
                  <v-divider
                    vertical
                    class="mx-2 d-inline-block"
                    style="height: 12px"
                  />
                  <span>Обновлено: {{ formatDate(note.updated_at) }}</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Теги -->
          <v-col cols="12" md="3">
            <div class="d-flex flex-wrap ga-2">
              <v-chip
                v-for="tag in getTagNames(note.tags)"
                :key="tag"
                color="primary"
                variant="flat"
                size="small"
                @click:close="removeTag(note.id, tag)"
              >
                {{ tag }}
              </v-chip>

              <!-- Если тегов нет -->
              <v-chip
                v-if="getTagNames(note.tags).length === 0"
                color="grey"
                size="small"
                variant="outlined"
              >
                нет тегов
              </v-chip>
            </div>
          </v-col>

          <!-- Действия -->
          <v-col cols="12" md="3">
            <div class="d-flex flex-wrap ga-2">
              <v-btn
                color="primary"
                variant="outlined"
                size="small"
                @click="openTagDialog(note)"
              >
                <v-icon start>mdi-tag-plus</v-icon>
                Теги
              </v-btn>

              <v-btn
                color="error"
                variant="outlined"
                size="small"
                @click="deleteNote(note.id)"
              >
                <v-icon start>mdi-delete</v-icon>
                Удалить
              </v-btn>

              <v-btn
                color="secondary"
                variant="outlined"
                size="small"
                @click="openEditDialog(note)"
              >
                <v-icon start>mdi-pencil</v-icon>
                Редактировать
              </v-btn>
            </div>
          </v-col>
        </v-row>

        <!-- Пагинация -->
        <v-row v-if="totalCount > filters.limit" class="mt-4">
          <v-col cols="12" class="d-flex justify-center">
            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
              @update:modelValue="onPageChange"
              rounded="circle"
            ></v-pagination>
          </v-col>
        </v-row>
      </v-card>
    </v-container>

    <TagDialog
      v-model="showTagDialog"
      :note="selectedNote"
      @tag-updated="fetchNotes"
    />

    <!-- Диалог редактирования заметки -->
    <v-dialog v-model="showEditDialog" max-width="600px">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon start>mdi-pencil</v-icon>
          Редактировать заметку
        </v-card-title>

        <v-card-text class="pa-4">
          <v-text-field
            v-model="editingNote.title"
            label="Заголовок"
            outlined
            class="mb-4"
          />

          <v-textarea
            v-model="editingNote.content"
            label="Содержание"
            auto-grow
            outlined
            rows="4"
          />
        </v-card-text>

        <v-card-actions class="pa-4 d-flex justify-end gap-2">
          <v-btn variant="text" @click="showEditDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="updateNote" :loading="updatingNote">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import MainNavBar from '../components/MainNavBar.vue';
import TagDialog from '../components/TagDialog.vue';

export default {
  components: { MainNavBar, TagDialog },

  data() {
    return {
      newNote: {
        title: '',
        content: '',
        tags: [],
      },
      tagSearch: '',
      creatingNote: false,
      notes: [],
      newNoteContent: '',
      showTagDialog: false,
      showEditDialog: false,
      selectedNote: null,
      editingNote: {
        id: null,
        title: '',
        content: '',
      },
      updatingNote: false,
      loadingNotes: false,
      filters: {
        search: '',
        selectedTag: [],
        limit: 20,
        offset: 0,
      },
      tagSuggestions: [],
      tagSuggestionLoading: false,
      tagSuggestionTimeout: null,
      searchTimeout: null,
      totalCount: 0,
      currentPage: 1,
    };
  },
  computed: {
    isNoteValid() {
      return this.newNote.title.trim() && this.newNote.content.trim();
    },
    totalPages() {
      return Math.ceil(this.totalCount / this.filters.limit);
    },
  },

  mounted() {
    this.loadNotes();
    // Загружаем все теги для автодополнения
    this.fetchTagSuggestions('');
  },

  methods: {
    async loadNotes() {
      await this.fetchNotes();
    },

    async fetchNotes() {
      this.loadingNotes = true;
      try {
        const params = {
          limit: this.filters.limit,
          offset: this.filters.offset,
        };

        if (this.filters.search && this.filters.search.trim()) {
          params.search = this.filters.search.trim();
        }

        if (this.filters.selectedTag && this.filters.selectedTag.length > 0) {
          // Преобразуем массив тегов в строку через запятую
          params.tags = Array.isArray(this.filters.selectedTag)
            ? this.filters.selectedTag.join(',')
            : this.filters.selectedTag;
        }

        const res = await axios.get('/api/notes', { params });
        this.notes = res.data.notes || [];
        this.totalCount = res.data.total_count || 0;
      } catch (err) {
        console.error('Ошибка загрузки заметок', err);
        this.showNotification('Не удалось загрузить заметки', 'error');
      } finally {
        this.loadingNotes = false;
      }
    },

    onSearchInput() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1;
        this.filters.offset = 0;
        this.fetchNotes();
      }, 500);
    },

    onTagInput(val) {
      clearTimeout(this.tagSuggestionTimeout);
      this.tagSuggestionTimeout = setTimeout(() => {
        this.fetchTagSuggestions(val);
      }, 300);
    },

    async fetchTagSuggestions(query) {
      if (!query || query.trim().length < 1) {
        // Если запрос пустой, загружаем все теги для автодополнения
        query = '';
      }

      this.tagSuggestionLoading = true;
      try {
        const res = await axios.get('/api/tags');
        const allTags = res.data || [];
        
        // Фильтруем теги по запросу, если он есть
        let filteredTags = allTags;
        if (query && query.trim().length > 0) {
          const searchQuery = query.toLowerCase();
          filteredTags = allTags.filter(tag => 
            tag.name && tag.name.toLowerCase().includes(searchQuery)
          );
        }
        
        // Преобразуем в формат для v-autocomplete
        this.tagSuggestions = filteredTags.map(tag => ({
          name: tag.name,
          id: tag.id,
          title: tag.name,
          value: tag.name
        }));
      } catch (err) {
        console.error('Ошибка загрузки тегов', err);
        this.tagSuggestions = [];
      } finally {
        this.tagSuggestionLoading = false;
      }
    },

    removeSearchTag(tagName) {
      this.filters.selectedTag = this.filters.selectedTag.filter(t => t !== tagName);
      this.fetchNotes();
    },

    resetFilters() {
      this.filters.search = '';
      this.filters.selectedTag = [];
      this.currentPage = 1;
      this.filters.offset = 0;
      this.fetchNotes();
    },

    onPageChange(page) {
      this.currentPage = page;
      this.filters.offset = (page - 1) * this.filters.limit;
      this.fetchNotes();
      // Прокрутка вверх при смене страницы
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },


    async updateNote() {
      if (!this.editingNote.id) return;

      this.updatingNote = true;
      try {
        // Получаем текущие теги заметки
        const originalNote = this.notes.find(
          (n) => n.id === this.editingNote.id,
        );
        const tagNames = this.getTagNames(originalNote?.tags || []);

        await axios.put(`/api/notes/${this.editingNote.id}`, {
          title: this.editingNote.title,
          content: this.editingNote.content,
          tags: tagNames,
        });

        await this.fetchNotes();
        this.showEditDialog = false;
        this.showNotification('Заметка обновлена успешно', 'success');
      } catch (err) {
        console.error('Ошибка обновления заметки', err);
        this.$toast.error('Не удалось обновить заметку');
      } finally {
        this.updatingNote = false;
      }
    },

    async deleteNote(id) {
      if (!confirm('Вы уверены, что хотите удалить эту заметку?')) return;

      try {
        await axios.delete(`/api/notes/${id}`);
        await this.fetchNotes();
        this.showNotification('Заметка удалена', 'success');
      } catch (err) {
        console.error('Ошибка удаления', err);
        this.$toast.error('Не удалось удалить заметку');
      }
    },
    addTag() {
      if (
        this.tagSearch &&
        this.tagSearch.trim() &&
        !this.newNote.tags.includes(this.tagSearch.trim())
      ) {
        this.newNote.tags.push(this.tagSearch.trim());
        this.tagSearch = '';
      }
    },
    removeTag(tag) {
      this.newNote.tags = this.newNote.tags.filter((t) => t !== tag);
    },

    async createNote() {
      if (!this.isNoteValid) return;

      this.creatingNote = true;
      try {
        await axios.post('/api/notes', {
          title: this.newNote.title,
          content: this.newNote.content,
          tags: this.newNote.tags,
        });

        // Сброс формы
        this.newNote = {
          title: '',
          content: '',
          tags: [],
        };
        this.tagSearch = '';

        await this.fetchNotes();
        this.showNotification('Заметка создана успешно', 'success');
      } catch (err) {
        console.error('Ошибка создания заметки', err);
        this.showNotification('Не удалось создать заметку', 'error');
      } finally {
        this.creatingNote = false;
      }
    },

    getTagNames(tags) {
      if (!tags || !Array.isArray(tags)) return [];

      // Если теги - это объекты, извлекаем name, если строки - оставляем как есть
      return tags
        .map((tag) => {
          if (typeof tag === 'object' && tag !== null && tag.name) {
            return tag.name;
          }
          return tag;
        })
        .filter((tag) => tag && typeof tag === 'string');
    },

    openTagDialog(note) {
      this.selectedNote = note;
      this.showTagDialog = true;
    },

    showNotification(message, type) {
      // Используем $toast если доступен, иначе console
      if (this.$toast) {
        this.$toast[type](message);
      } else {
        console.log(`${type === 'success' ? '✅' : '❌'} ${message}`);
      }
    },

    openEditDialog(note) {
      this.editingNote = {
        id: note.id,
        title: note.title,
        content: note.content,
      };
      this.showEditDialog = true;
    },

    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    },
  },
};
</script>

<style scoped>
.h-100 {
  height: 100%;
}
</style>
