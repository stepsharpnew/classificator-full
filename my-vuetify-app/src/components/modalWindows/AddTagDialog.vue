<template>
  <v-dialog v-model="visible" max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h6">Добавить тег</span>
      </v-card-title>

      <v-card-text>
        <v-form>
          <v-text-field v-model="name" label="Название тега" />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="close">Отмена</v-btn>
        <v-btn color="primary" @click="create">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddTagDialog',
  data() {
    return {
      visible: false,
      name: '',
    };
  },
  mounted() {
    // слушаем глобальное событие для редактирования
    this.$root.$on('edit-tag', (tag) => {
      this.name = tag.name || '';
      this.visible = true;
      this.editingTag = tag;
    });
  },
  methods: {
    close() {
      this.visible = false;
      this.name = '';
      this.editingTag = null;
      this.$emit('input', false);
    },
    async create() {
      if (!this.name.trim()) return;
      try {
        await axios.post('/tags', { name: this.name.trim() });
        this.$emit('created');
        this.close();
      } catch (e) {
        console.error('create tag error:', e);
        alert('Ошибка создания тега');
      }
    },
  },
};
</script>
