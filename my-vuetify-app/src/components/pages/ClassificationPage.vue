<template>
  <div style="background-color: aliceblue">
    <MainNavBar />

    <v-card class="classification-card pa-4">
      <v-card class="d-flex w-100 pa-4 ga-4 justify-start">
        <v-btn size="large" class="btn-top" @click="handleAddClassification"
          >Добавить классфикацию</v-btn
        >
        <v-btn size="large" class="btn-top" @click="handleAddEquipment"
          >Добавить тип оборудования</v-btn
        >
        <AddTypeClassify
          v-model="showDialog"
          :typeModal="typeModal"
          @createItem="createItem"
        />
      </v-card>
      <v-card-title class="title-row">Классификация оборудования</v-card-title>

      <v-card-text>
        <v-skeleton-loader v-if="loading" type="list-item-avatar-two-line" />

        <div v-else class="tree-container">
          <div
            v-for="(row, idx) in visibleNodes"
            :key="row.key"
            class="tree-row"
            :class="{ 'row-equipment': row.isEquipment }"
            :style="{ paddingLeft: `${row.depth * 16}px` }"
          >
            <!-- category node -->
            <template v-if="!row.isEquipment">
              <div
                class="row-left"
                @click.stop="toggleOpen(row.id)"
                @dblclick.stop="startEdit(row)"
              >
                <v-icon small class="mr-2">
                  {{ isOpen(row.id) ? 'mdi-folder-open' : 'mdi-folder' }}
                </v-icon>

                <template v-if="isEditing(row.id)">
                  <div class="d-flex ga-2 align-center">
                    <v-text-field
                      v-model="editBuffer[row.id].path"
                      dense
                      hide-details
                      label="Путь"
                      style="max-width: 160px"
                      @keyup.enter="saveNode(row)"
                    />
                    <v-text-field
                      v-model="editBuffer[row.id].name"
                      dense
                      hide-details
                      label="Наименование"
                      class="equipment-edit-field"
                      @keyup.enter="saveNode(row)"
                    />
                  </div>
                </template>

                <template v-else>
                  <v-tooltip
                    v-if="row.name && row.name.length > 40"
                    location="top"
                  >
                    <template #activator="{ props }">
                      <span class="node-name" v-bind="props">
                        {{ row.displayName }}
                      </span>
                    </template>
                    <span>{{ row.name }}</span>
                  </v-tooltip>
                  <span v-else class="node-name">{{ row.displayName }}</span>
                </template>
              </div>

              <div class="row-right">
                <div v-if="isEditing(row.id)">
                  <v-btn small class="btn-save" @click="saveNode(row)"
                    >Сохранить</v-btn
                  >
                  <v-btn small class="btn-cancel" @click="cancelEdit(row.id)"
                    >Отмена</v-btn
                  >
                </div>

                <div v-else class="row-right-default">
                  <v-chip
                    v-if="row.equipmentCount"
                    small
                    class="equipment-count-chip"
                  >
                    {{ row.equipmentCount }} ед.
                  </v-chip>
                </div>
              </div>
            </template>

            <!-- equipment node -->
            <template v-else>
              <div class="d-flex w-100 mr-4" @dblclick.stop="startEdit(row)">
                <v-icon
                  small
                  color="primary"
                  class="mr-2 mb-3"
                  v-if="!isEditing(row.id) && row.fnn != null"
                  >mdi-check-circle-outline</v-icon
                >
                <v-icon
                  small
                  color="red"
                  class="mr-2 mb-3"
                  v-if="!isEditing(row.id) && row.fnn == null"
                  >mdi-alert-circle-outline</v-icon
                >

                <template v-if="isEditing(row.id)">
                  <v-row dense align="center" class="w-100" fluid>
                    <v-col cols="10">
                      <v-text-field
                        v-model="editBuffer[row.id].name"
                        dense
                        hide-details
                        label="Наименование"
                        @keyup.enter="saveNode(row)"
                      />
                    </v-col>

                    <v-col cols="2">
                      <v-text-field
                        v-model="editBuffer[row.id].fnn"
                        dense
                        hide-details
                        label="FNN"
                        @keyup.enter="saveNode(row)"
                      />
                    </v-col>
                  </v-row>
                </template>

                <template v-else>
                  <div class="d-flex justify-start align-center ga-2">
                    <span class="equipment-name">{{ row.displayName }}</span>
                    <v-chip v-if="row.equipmentType" small color="primary" variant="outlined">
                      {{ typeDisplayName(row.equipmentType) }}
                    </v-chip>
                    <v-chip v-else small color="grey" variant="outlined">
                      -
                    </v-chip>
                  </div>
                </template>
              </div>

              <div class="equipment-actions">
                <template v-if="isEditing(row.id)">
                  <v-btn small class="btn-save" @click="saveNode(row)"
                    >Сохранить</v-btn
                  >
                  <v-btn small class="btn-cancel" @click="cancelEdit(row.id)"
                    >Отмена</v-btn
                  >
                  <!-- <v-btn small class="btn-delete" @click="deleteItem(row)"
                    >Удалить</v-btn
                  > -->
                </template>
                <template v-else>
                  <!-- edit button removed per request; only delete remains -->
                  <span class="equipment-fnn">{{ row.fnn }}</span>
                  <v-btn icon x-small @click="deleteItem(row)">
                    <v-icon x-small>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </div>
            </template>
          </div>

          <div v-if="visibleNodes.length === 0" class="empty-state">
            Данные пусты
          </div>
        </div>
      </v-card-text>
    </v-card>

    <NotificationDialog
      v-model="notification.show"
      :message="notification.message"
      :type="notification.type"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { markRaw } from 'vue';
import MainNavBar from '../components/MainNavBar.vue';
import AddTypeClassify from '../modalWindows/addTypeClassify.vue';
import NotificationDialog from '../modalWindows/NotificationDialog.vue';

export default {
  name: 'ClassificationViewOptions',
  components: { MainNavBar, AddTypeClassify, NotificationDialog },

  data() {
    return {
      // состояние
      loading: true,
      nodeMap: new Map(), // Map<id, nodeObj>
      roots: [], // array of root paths (classification ids)
      version: 0,
      showDialog: false,
      typeModal: '',
      // UI state
      openMap: {}, // { [id]: true/false }
      // single active editing id (only one can be edited)
      editing: null, // currently editing node id or null
      editBuffer: {}, // { [nodeId]: '...' }
      // notification dialog
      notification: {
        show: false,
        message: '',
        type: 'success',
      },
    };
  },

  computed: {
    // flatten visible nodes based on openMap and roots
    visibleNodes() {
      // touch version to make it reactive for recompute
      const _v = this.version;
      const out = [];
      const m = this.nodeMap;
      if (!m || m.size === 0) return out;

      const dfs = (id, depth) => {
        const node = m.get(id);
        if (!node) return;

        if (!node.isEquipment) {
          out.push({
            key: `cat-${node.id}`,
            id: node.id,
            name: node.name,
            displayName: `${node.id} ${node.name}`,
            isEquipment: false,
            equipmentCount: node.equipmentCount || 0,
            depth,
            fnn: node.fnn,
          });

          if (this.openMap[node.id]) {
            for (const childId of node.childrenPaths || []) {
              const childNode = m.get(childId);
              if (!childNode) continue;

              if (childNode.isEquipment) {
                out.push({
                  key: `eq-${childNode.id}`,
                  id: childNode.id,
                  name: childNode.name,
                  displayName: `${childNode.fullPath || childNode.parentPath} ${
                    childNode.name
                  }`.trim(),
                  isEquipment: true,
                  equipmentType: childNode.equipmentType,
                  depth: depth + 1,
                  fnn: childNode.fnn,
                });
              } else {
                dfs(childId, depth + 1);
              }
            }
          }
        }
      };

      for (const r of this.roots) {
        dfs(r, 0);
      }
      return out;
    },
  },

  methods: {
    showNotification(message, type = 'success') {
      this.notification = { show: true, message, type };
    },
    typeDisplayName(type) {
      if (type == null || type === '') return '-';
      const t = String(type).toLowerCase();
      if (t === 'ssius') return 'ССИУС';
      if (t === 'sius') return 'СИУС';
      return type;
    },
    handleAddEquipment() {
      this.showDialog = true;
      this.typeModal = 'equipment';
    },
    handleAddClassification() {
      this.showDialog = true;
      this.typeModal = 'classification';
    },
    async createItem(formData) {
      try {
        let res;
        if (formData.typeModal === 'equipment') {
          const typeParam = formData.type ? `&type=${formData.type}` : '';
          res = await axios.post(
            `/api/equipment-type?path=${formData.path}&name=${formData.name}${typeParam}&fnn=${formData.fnn || ''}`,
          );
        } else {
          res = await axios.post(
            `/api/classification?path=${formData.path}&name=${formData.name}`,
          );
        }
        if (res.data && res.data.success === false) {
          const msg = res.data.error?.msg || res.data.error || 'Неизвестная ошибка';
          this.showNotification(msg, 'error');
        } else {
          const label = formData.typeModal === 'equipment' ? 'Тип оборудования' : 'Классификация';
          this.showNotification(`${label} успешно создан(а)`);
          this.fetchClassification();
        }
      } catch (err) {
        const detail = err.response?.data?.error?.msg || err.response?.data?.detail || 'Неизвестная ошибка';
        this.showNotification(detail, 'error');
        console.error('createItem error', err);
      }
    },
    isOpen(id) {
      return !!this.openMap[id];
    },
    toggleOpen(id) {
      this.$set
        ? this.$set(this.openMap, id, !this.openMap[id])
        : (this.openMap[id] = !this.openMap[id]);
    },

    sanitizeName(n) {
      if (!n && n !== 0) return '';
      return String(n).replace(/\s+/g, ' ').trim();
    },

    // build node map: store classification nodes (keyed by path) and equipment nodes (keyed by equipment id)
    buildNodeMap(items) {
      const m = new Map();
      const rootPaths = [];

      // create classification nodes
      for (const it of items) {
        if (!it || !it.path) continue;
        const path = String(it.path);
        const node = markRaw({
          id: path,
          name: this.sanitizeName(it.name || it.id || path),
          isEquipment: false,
          childrenPaths: [], // classification children (paths) + equipment ids
          equipmentCount: Array.isArray(it.equipments)
            ? it.equipments.length
            : 0,
          raw: it,
        });
        m.set(path, node);
      }

      // link classification hierarchy by path segments
      const sortedPaths = Array.from(m.keys()).sort(
        (a, b) => a.split('.').length - b.split('.').length,
      );
      for (const path of sortedPaths) {
        const node = m.get(path);
        const parts = path.split('.');
        parts.pop();
        const parentPath = parts.join('.');
        if (parentPath && m.has(parentPath)) {
          m.get(parentPath).childrenPaths.push(path);
        } else {
          rootPaths.push(path);
        }
      }

      // attach equipment nodes (equipment keyed by their GUID id)
      for (const it of items) {
        if (!it || !it.path) continue;
        const catNode = m.get(it.path);
        if (!catNode) continue;
        const eqs = Array.isArray(it.equipments) ? it.equipments : [];
        for (const [index, eq] of eqs.entries()) {
          const eqId = eq.id;

          // добавляем новый путь
          const fullPath = `${it.path}.${index + 1}`;

          const eqNode = markRaw({
            id: eqId,
            name: this.sanitizeName(eq.name || eq.id),
            fnn: eq.fnn,
            isEquipment: true,
            parentPath: it.path,
            fullPath, // теперь у оборудования есть собственный путь
            equipmentType: eq.type,
            equipmentData: eq,
          });

          m.set(eqId, eqNode);
          catNode.childrenPaths.push(eqId);
        }
        catNode.equipmentCount = (eqs || []).length;
      }

      this.nodeMap = m;
      this.roots = rootPaths;
      this.version++;
    },

    async fetchClassification() {
      this.loading = true;
      try {
        const res = await axios.get('/api/classification');
        console.log(res.data);

        const payload =
          res.data &&
          (Array.isArray(res.data) ? res.data : res.data.data || res.data);
        if (!Array.isArray(payload)) {
          this.nodeMap = new Map();

          this.roots = [];
        } else {
          this.buildNodeMap(payload);
        }
      } catch (err) {
        console.error('fetchClassification error', err);
        this.nodeMap = new Map();
        this.roots = [];
      } finally {
        this.loading = false;
      }
    },

    // editing
    startEdit(row) {
      console.log(row);

      // close any other edit in progress
      if (this.editing && this.editing !== row.id) {
        this.cancelEdit(this.editing);
      }

      // open editing for this row
      if (this.$set) {
        this.$set(this.editBuffer, row.id, row.name);
      } else {
        this.editBuffer[row.id] = {
          name: row.name,
          fnn: row.fnn || '',
          path: row.isEquipment ? '' : row.id, // путь только для категорий
        };
      }
      this.editing = row.id;
    },
    isEditing(id) {
      return this.editing === id;
    },
    cancelEdit(id) {
      if (id == null) return;
      if (this.$delete) {
        this.$delete(this.editBuffer, id);
      } else {
        delete this.editBuffer[id];
      }
      // if closing currently active editor, clear editing
      if (this.editing === id) this.editing = null;
    },

    async saveNode(row) {
      const id = row.id;
      const { name: newName, fnn: newFnn, path: newPath } = this.editBuffer[id];
      if (!newName) {
        this.showNotification('Поле "Наименование" не должно быть пустым', 'error');
        return;
      }

      const node = this.nodeMap.get(id);
      if (!node) return;

      // Для категорий: если путь изменился — вызываем rename
      if (!node.isEquipment && newPath && newPath !== id) {
        this.cancelEdit(id);
        try {
          const res = await axios.put(
            `/api/classification/rename?old_path=${encodeURIComponent(id)}&new_path=${encodeURIComponent(newPath)}`,
          );
          if (res.data && res.data.success === false) {
            const msg = res.data.error?.msg || 'Ошибка при переименовании';
            this.showNotification(msg, 'error');
          } else {
            // Если название тоже изменилось — обновляем после переименования
            if (newName !== node.name) {
              const nameRes = await axios.put(
                `/api/classification?path=${encodeURIComponent(newPath)}&name=${encodeURIComponent(newName)}&fnn=`,
              );
              if (nameRes.data && nameRes.data.success === false) {
                this.showNotification(nameRes.data.error?.msg || 'Ошибка при обновлении названия', 'error');
              }
            }
            this.showNotification(`Нумерация изменена: ${id} → ${newPath}`);
            this.fetchClassification();
          }
        } catch (err) {
          console.error('renameNode error', err);
          const detail = err.response?.data?.error?.msg || 'Ошибка при переименовании';
          this.showNotification(detail, 'error');
        }
        return;
      }

      const prevName = node.name;
      const prevFnn = node.fnn;
      node.name = newName;
      node.fnn = newFnn;
      this.version++;
      this.cancelEdit(id);

      try {
        let res;
        if (node.isEquipment) {
          res = await axios.put(
            `/api/equipment-type?id=${encodeURIComponent(
              id,
            )}&name=${encodeURIComponent(newName)}&fnn=${encodeURIComponent(
              newFnn,
            )}`,
          );
        } else {
          const path = node.id;
          res = await axios.put(
            `/api/classification?path=${encodeURIComponent(
              path,
            )}&name=${encodeURIComponent(newName)}&fnn=${encodeURIComponent(
              newFnn,
            )}`,
          );
        }
        if (res.data && res.data.success === false) {
          const msg = res.data.error?.msg || res.data.error || 'Ошибка при сохранении';
          node.name = prevName;
          node.fnn = prevFnn;
          this.version++;
          this.showNotification(msg, 'error');
        } else {
          const label = node.isEquipment ? 'Оборудование' : 'Категория';
          this.showNotification(`${label} обновлен(а)`);
        }
      } catch (err) {
        console.error('saveNode error', err);
        node.name = prevName;
        node.fnn = prevFnn;
        this.version++;
        const detail = err.response?.data?.error?.msg || 'Ошибка при сохранении';
        this.showNotification(`${detail}. Данные восстановлены.`, 'error');
      }
    },

    async deleteItem(row) {
      if (!confirm(`Удалить элемент:\n${row.name}?`)) return;
      const id = row.id;
      const node = this.nodeMap.get(id);
      if (!node) return;

      // if directory -> call classification delete; if equipment -> call equipment-type delete
      const parentPath = node.parentPath;
      const parent = this.nodeMap.get(parentPath);
      const savedNode = node;
      const savedChildren = parent ? [...parent.childrenPaths] : null;

      // optimistic removal from map; update parent
      this.nodeMap.delete(id);
      if (parent) {
        parent.childrenPaths = parent.childrenPaths.filter((ch) => ch !== id);
        parent.equipmentCount = parent.childrenPaths.filter((ch) => {
          const c = this.nodeMap.get(ch);
          return c && c.isEquipment;
        }).length;
      }
      this.version++;

      const revert = () => {
        this.nodeMap.set(id, savedNode);
        if (parent && savedChildren) {
          parent.childrenPaths = savedChildren;
          parent.equipmentCount = savedChildren.filter((ch) => {
            const c = this.nodeMap.get(ch);
            return c && c.isEquipment;
          }).length;
        }
        this.version++;
      };

      try {
        let res;
        if (node.isEquipment) {
          res = await axios.delete(
            `/api/equipment-type?id=${encodeURIComponent(id)}`,
          );
        } else {
          const path = node.id;
          res = await axios.delete(
            `/api/classification?path=${encodeURIComponent(path)}`,
          );
        }
        if (res.data && res.data.success === false) {
          revert();
          const msg = res.data.error?.msg || res.data.error || 'Ошибка при удалении';
          this.showNotification(msg, 'error');
        } else {
          const label = node.isEquipment ? 'Оборудование' : 'Категория';
          this.showNotification(`${label} удален(а)`);
        }
      } catch (err) {
        console.error('deleteItem error', err);
        revert();
        const detail = err.response?.data?.error?.msg || 'Ошибка при удалении';
        this.showNotification(`${detail}. Данные восстановлены.`, 'error');
      }
    },
  },

  created() {
    this.fetchClassification();
  },
};
</script>

<style scoped>
.classification-card {
  max-width: 1600px;
  margin: 0 auto;
}

/* header */
.title-row {
  font-weight: 900;
  font-size: 1.7rem;
}

/* tree container */
.tree-container {
  width: 100%;
  max-height: 70vh;
  overflow: auto;
}

/* row */
.tree-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  box-sizing: border-box;
  border-bottom: 1px solid rgba(0, 0, 0, 0.02);
}

/* equipment row highlight */
.row-equipment {
  background: transparent;
  cursor: pointer;
}

/* left side section */
.row-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

/* name styles */
.node-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.equipment-name {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 10px;
  cursor: pointer;
}

/* right side */
.row-right {
  display: flex;
  align-items: center;
}

.row-right-default {
  display: flex;
  align-items: center;
}

/* equipment editing */
.equipment-edit-field {
  width: 1000px;
  max-width: 60vw;
}

/* actions area */
.equipment-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* chips */
.equipment-count-chip {
  background-color: #edf2ff;
  font-size: 0.75rem;
}

/* buttons */
.btn-save {
  background-color: #58b368;
  color: white;
  min-width: 80px;
  text-transform: none;
}
.btn-cancel {
  background-color: #1e88e5;
  color: white;
  min-width: 80px;
  text-transform: none;
}
.btn-delete {
  background-color: #ff6f6f;
  color: white;
  min-width: 80px;
  text-transform: none;
}
.btn-top {
  background-color: #1e88e5;
  font-size: larger;
  color: white;
  min-width: 80px;
  text-transform: none;
}

.empty-state {
  padding: 12px;
  color: rgba(0, 0, 0, 0.6);
}
.equipment-fnn-field {
  width: 300px;
}

.equipment-fnn {
  font-size: 1.4rem;
  color: #7199ff;
  min-width: 120px;
  text-align: right;
  margin-right: 50px;
}
</style>
