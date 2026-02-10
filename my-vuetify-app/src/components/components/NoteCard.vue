<template>
  <v-card outlined>
    <v-card-title>
      <div>
        <div class="text-subtitle-1 font-weight-medium">{{ note.title }}</div>
        <div class="grey--text text--small">id: {{ note.id }}</div>
      </div>

      <v-spacer />

      <v-btn icon @click="$emit('edit', note)">
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
      <v-btn icon @click="remove">
        <v-icon color="red">mdi-delete</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <div v-if="note.content" class="mb-3">{{ note.content }}</div>

      <div>
        <v-chip
          v-for="t in note.tags || []"
          :key="t.id"
          small
          class="ma-1"
          label
        >
          {{ t.name }}
        </v-chip>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios';
export default {
  name: 'NoteCard',
  props: {
    note: { type: Object, required: true },
    allTags: { type: Array, default: () => [] },
  },
  methods: {
    async remove() {
      if (!confirm('Удалить заметку?')) return;
      try {
        await axios.delete(`/notes/${this.note.id}`);
        this.$emit('deleted');
      } catch (e) {
        console.error('delete note error:', e);
        alert('Ошибка при удалении');
      }
    },
  },
};
</script>
