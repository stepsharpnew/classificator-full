<template>
  <div>
    <v-btn color="primary" @click="openCreateDialog">
      Добавить оборудование
    </v-btn>
  </div>
  <v-dialog v-model="dialog" max-width="1200px" persistent>
    <v-card>
      <v-toolbar color="primary" dark>
        <v-toolbar-title>{{ action }} нового оборудования</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-text class="mt-4">
        <v-form ref="form" v-model="valid">
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.inventory_number"
                label="Инвентарный номер"
                :rules="[(v) => !!v || 'Обязательное поле']"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.factory_number"
                label="Заводской номер"
                outlined
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.act_of_receiving"
                label="Акт приема"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="4">
              <v-select
                v-model="formData.department_id"
                :items="departments"
                item-title="name"
                item-value="id"
                label="Отделение"
                outlined
                dense
                :disabled="isCreateMode && !!userDepartmentId && !canChooseDepartment"
                :rules="[(v) => !!v || 'Обязательное поле']"
              ></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="formData.status"
                :items="statusOptionsFiltered"
                item-title="text"
                item-value="value"
                label="Статус"
                outlined
                dense
                :rules="[(v) => !!v || 'Обязательное поле']"
              />
            </v-col>

            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.receiving_date"
                label="Дата приема"
                type="date"
                outlined
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-autocomplete
                v-model="formData.type"
                label="Наименование оборудования"
                variant="outlined"
                density="comfortable"
                hide-details
                item-title="displayName"
                item-value="id"
                :items="parentSuggestionsWithSelected"
                :loading="suggestionLoading"
                no-filter
                clearable
                @update:search="onParentSearch"
                @update:modelValue="onParentSelect"
                @update:menu="(open) => open && onParentMenuOpen()"
                :rules="[(v) => !!v || 'Обязательное поле']"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props">
                    <template v-slot:title>
                      <span
                        v-if="item.raw.classificator_path"
                        class="text-grey-darken-1 font-weight-medium"
                      >
                        {{ item.raw.classificator_path}}
                      </span>&ensp;
                      <span v-if="item.raw.classificator_path && item.raw.name">
                      </span>
                      <span>{{ item.raw.name }}</span>
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formData.comment"
                label="Комментарий"
                outlined
                dense
                rows="1"
              ></v-textarea>
            </v-col>
          </v-row>
          <!-- //----------------------------------------------------------------------------------------- -->

          <v-card-text class="m-4">
            <h1>Компоненты</h1>
            <v-row cols="12">
              <template v-for="(child, idx) in formData.childrens" :key="idx">
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="child.factory_number"
                    label="Заводской номер"
                    outlined
                    dense
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="child.status"
                    :items="statusOptionsFiltered"
                    item-title="text"
                    item-value="value"
                    label="Статус"
                    outlined
                    dense
                    :rules="[(v) => !!v || 'Обязательное поле']"
                  />
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="child.department_id"
                    :items="departments"
                    item-title="name"
                    item-value="id"
                    label="Отделение"
                    outlined
                    dense
                    :disabled="isCreateMode && !!userDepartmentId && !canChooseDepartment"
                    :rules="[(v) => !!v || 'Обязательное поле']"
                  ></v-select>
                </v-col>
                <v-col cols="12">
                  <v-autocomplete
                    :rules="[(v) => !!v || 'Обязательное поле']"
                    v-model="child.type"
                    :items="childSuggestionsWithSelected[idx] || formattedChildSuggestions[idx] || []"
                    item-title="displayName"
                    item-value="id"
                    :loading="childLoading[idx]"
                    hide-details
                    variant="outlined"
                    density="comfortable"
                    label="Наименование оборудования"
                    no-filter
                    clearable
                    @update:search="(val) => onChildSearch(val, idx)"
                    @update:modelValue="(val) => onChildSelect(val, idx)"
                    @update:menu="(open) => open && onChildMenuOpen(idx)"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>
                          <span
                            v-if="item.raw.classificator_path"
                            class="text-grey-darken-1 font-weight-medium"
                          >
                            {{ item.raw.classificator_path }}
                          </span>&ensp;
                          <span
                            v-if="item.raw.classificator_path && item.raw.name"
                          >
                          </span>
                          <span>{{ item.raw.name }}</span>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
                <v-col cols="8">
                  <v-textarea
                    v-model="child.comment"
                    label="Комментарий"
                    outlined
                    dense
                    rows="1"
                  ></v-textarea>
                </v-col>
                <v-col cols="1" class="">
                  <v-btn icon @click="removeChild(idx)">
                    <v-icon color="red">mdi-delete</v-icon>
                  </v-btn>
                </v-col>
                <v-divider />
              </template>
              <v-col cols="12" class="d-flex">
                <v-btn text small color="primary" @click="addChild">
                  <v-icon left>mdi-plus</v-icon> Добавить компонент
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-form>
      </v-card-text>

      <v-card-actions class="grey lighten-4 d-flex flex-column align-end mr-4">
        <v-spacer></v-spacer>
        <v-alert
          v-if="!valid"
          type="error"
          variant="tonal"
          density="comfortable"
          class="pa-2 rounded-lg text-body-2 font-weight-medium soft-blink"
        >
          Заполните все поля
        </v-alert>
        <div>
          <v-btn color="grey darken-1" text @click="dialog = false">
            Отмена
          </v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="submitForm"
            :disabled="!valid"
          >
            Сохранить
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {

  props: {
    departments: {
      type: Array,
      required: true,
    },
    userDepartmentId: {
      type: String,
      default: '',
    },
    canChooseDepartment: {
      type: Boolean,
      default: false,
    },
    item: {
      type: Object,
      required: false,
      default: null,
    },
    mode: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      equipmentType: '',
      equipmentTypeChild: '',
      parentSuggestions: [],
      parentLoading: false,
      parentTimeout: null,
      suggestionLoading: false,

      childSuggestions: [], // уже есть
      childLoading: {}, // <— инициализируем
      childTimeout: {},
      dialog: false,
      action: 'Создание',
      valid: false,
      loading: false,
      deleted_equipments: [],
      statusOptions: [
        { text: 'В работе', value: 'at_work' },
        { text: 'В ремонте', value: 'repair' },
        { text: 'В архиве', value: 'archive' },
        //   { text: 'В резерве', value: 'in_reserve' }
      ],
      // typeOptions : [
      //   {text: 'sius', value : '1a10091d-7a71-4d3e-8abd-a401eafdee11'},
      //   {text : 'ssius', value : "b27ca44e-5c4f-4f59-b647-0a3f7907857e"}
      // ],
      formData: {
        department_id: '',
        inventory_number: '',
        factory_number: '',
        receiving_date: new Date().toISOString().substr(0, 10),
        act_of_receiving: '',
        status: 'at_work',
        type: '',
        comment: '',
        parent_id: '',
        childrens: [],
      },
      selectedParentEquipmentType: null,
      selectedChildEquipmentType: {},
    };
  },
  computed: {
    isCreateMode() {
      return this.mode !== 'edit';
    },
    parentSuggestionsWithSelected() {
      const list = this.formattedParentSuggestions;
      if (this.formData.type && this.selectedParentEquipmentType && this.selectedParentEquipmentType.id === this.formData.type) {
        if (!list.some((i) => i.id === this.formData.type)) {
          return [this.selectedParentEquipmentType, ...list];
        }
      }
      return list;
    },
    statusOptionsFiltered() {
      if (this.mode === 'edit') {
        return this.statusOptions;
      }
      return this.statusOptions.filter((opt) => opt.value !== 'archive');
    },
    formattedParentSuggestions() {
      return this.parentSuggestions.map((item) => ({
        ...item,
        displayName: item.classificator_path
          ? `${item.classificator_path} ${item.name || ''}`.trim()
          : item.name || '',
      }));
    },
    formattedChildSuggestions() {
      const formatted = {};
      Object.keys(this.childSuggestions).forEach((idx) => {
        formatted[idx] = (this.childSuggestions[idx] || []).map((item) => ({
          ...item,
          displayName: item.classificator_path
            ? `${item.classificator_path} ${item.name || ''}`.trim()
            : item.name || '',
        }));
      });
      return formatted;
    },
    childSuggestionsWithSelected() {
      const out = {};
      const indices = (this.formData.childrens || []).map((_, idx) => idx);
      indices.forEach((idx) => {
        const list = this.formattedChildSuggestions[idx] || [];
        const selected = this.selectedChildEquipmentType[idx];
        const typeId = this.formData.childrens[idx]?.type;
        if (typeId && selected && selected.id === typeId && !list.some((i) => i.id === typeId)) {
          out[idx] = [selected, ...list];
        } else {
          out[idx] = list;
        }
      });
      return out;
    },
  },
  methods: {
    openCreateDialog() {
      this.action = 'Создание';
      const defaultDept = this.canChooseDepartment ? '' : (this.userDepartmentId || '');
      this.formData = {
        department_id: defaultDept,
        inventory_number: '',
        factory_number: '',
        receiving_date: new Date().toISOString().substr(0, 10),
        act_of_receiving: '',
        status: 'at_work',
        type: '',
        comment: '',
        parent_id: '',
        childrens: [],
      };
      this.parentSuggestions = [];
      this.childSuggestions = [];
      this.selectedParentEquipmentType = null;
      this.selectedChildEquipmentType = {};
      this.deleted_equipments = [];
      this.dialog = true;
    },
    addChild() {
      this.formData.childrens.push({
        inventory_number: '',
        factory_number: '',
        act_of_receiving: '',
        status: 'at_work',
        type: '',
        receiving_date: new Date().toISOString().substr(0, 10),
        comment: '',
        parent_id: this.formData.parent_id || '',
        id: 0,
        department_id: this.canChooseDepartment
          ? (this.formData.department_id || '')
          : (this.formData.department_id || this.userDepartmentId || ''),
      });
    },
    removeChild(index) {
      const removed = this.formData.childrens.splice(index, 1)[0];
      if (removed.id) this.deleted_equipments.push(removed.id);
    },
    async submitForm() {
      this.loading = true;
      const body = {
        updated_equipment: this.formData,
        deleted_equipments: this.deleted_equipments,
      };
      try {
        if (this.mode == 'edit') {
          const res = await axios.put('/api/equipment', body);
          if (res.data && res.data.success === false) {
            const msg = res.data.error?.msg || res.data.error || 'Ошибка при сохранении';
            this.$emit('notify', { message: msg, type: 'error' });
            return;
          }
          this.$emit('notify', { message: 'Оборудование обновлено', type: 'success' });
          this.$emit('created');
          this.dialog = false;
        } else {
          const res = await axios.post('/api/equipment', this.formData);
          if (res.data && res.data.success === false) {
            const msg = res.data.error?.msg || res.data.error || 'Ошибка при добавлении оборудования';
            this.$emit('notify', { message: msg, type: 'error' });
            return;
          }
          this.$emit('notify', { message: 'Оборудование успешно создано', type: 'success' });
          this.$emit('created');
          this.dialog = false;
        }
      } catch (err) {
        console.error('Ошибка при сохранении оборудования:', err);
        const msg = err.response?.data?.error?.msg || err.response?.data?.detail || 'Ошибка при сохранении оборудования';
        this.$emit('notify', { message: msg, type: 'error' });
      } finally {
        this.loading = false;
      }
    },
    onParentSearch(val) {
      clearTimeout(this.parentTimeout);
      this.parentTimeout = setTimeout(() => {
        this.fetchParentSuggestions(val ?? '');
      }, 300);
    },
    onParentMenuOpen() {
      if (this.parentSuggestions.length === 0 && !this.suggestionLoading) {
        this.fetchParentSuggestions('');
      }
    },
    async fetchParentSuggestions(query) {
      this.suggestionLoading = true;
      try {
        const { data } = await axios.get(`/api/equipment-type?name=${query}`);
        console.log(data);

        this.parentSuggestions = data;
      } finally {
        this.suggestionLoading = false;
      }
    },
    onParentSelect(val) {
      this.formData.type = val;
      const item = this.formattedParentSuggestions.find((i) => i.id === val);
      this.selectedParentEquipmentType = item ? { ...item } : null;
    },

    onChildSearch(val, idx) {
      clearTimeout(this.childTimeout[idx]);
      this.childTimeout[idx] = setTimeout(() => {
        this.fetchChildSuggestions(val ?? '', idx);
      }, 300);
    },
    onChildMenuOpen(idx) {
      const list = this.childSuggestions[idx];
      if ((!list || list.length === 0) && !this.childLoading[idx]) {
        this.fetchChildSuggestions('', idx);
      }
    },
    async fetchChildSuggestions(query, idx) {
      this.childLoading[idx] = true;
      try {
        const { data } = await axios.get(`/api/equipment-type?name=${query}`);
        this.childSuggestions[idx] = data;
      } finally {
        this.childLoading[idx] = false;
      }
    },
    onChildSelect(val, idx) {
      this.formData.childrens[idx].type = val;
      const list = this.formattedChildSuggestions[idx] || [];
      const item = list.find((i) => i.id === val);
      this.$set(this.selectedChildEquipmentType, idx, item ? { ...item } : null);
    },
  },
  mounted() {},
  emits: ['created', 'closed', 'update:search', 'update:modelValue'],
  watch: {
    dialog(newVal) {
      // Сбрасываем состояние при закрытии диалога
      if (!newVal) {
        this.$emit('closed');
        this.notification = { show: false, message: '', type: 'success' };
        this.parentSuggestions = [];
        this.childSuggestions = [];
        this.suggestionLoading = false;
        // Сбрасываем formData
        this.formData = {
          department_id: '',
          inventory_number: '',
          factory_number: '',
          receiving_date: new Date().toISOString().substr(0, 10),
          act_of_receiving: '',
          status: 'at_work',
          type: '',
          comment: '',
          parent_id: '',
          childrens: [],
        };
      }
    },
    item: {
      immediate: false,
      deep: true,
      handler(newItem, oldItem) {
        // Проверяем, что item действительно изменился или это первое открытие
        // Также проверяем mode, чтобы открыть диалог даже если item тот же
        if (newItem && this.mode) {
          const setSelectedParentFromEqType = (eqType) => {
            if (!eqType) return;
            const displayName = eqType.classificator_path
              ? `${eqType.classificator_path} ${eqType.name || ''}`.trim()
              : (eqType.name || '');
            this.selectedParentEquipmentType = { ...eqType, id: eqType.id, displayName };
          };
          if (this.mode == 'copy') {
            this.action = 'Создание';
            this.formData = {
              ...newItem,
              factory_number: '',
              inventory_number: '',
              parent_id: newItem.id,
              id: 0,
              department_id: this.userDepartmentId || newItem.department_id,
            };
            if (newItem.eq_type && newItem.eq_type.id) {
              this.parentSuggestions = [newItem.eq_type];
              setSelectedParentFromEqType(newItem.eq_type);
            }
          }
          if (this.mode == 'edit') {
            this.action = 'Редактирование';
            console.log(newItem);
            this.formData = {
              ...newItem,
            };
            if (newItem.eq_type && newItem.eq_type.id) {
              this.parentSuggestions = [newItem.eq_type];
              setSelectedParentFromEqType(newItem.eq_type);
            }
          }
          console.log(this.formData);

          const childDeptId = (this.mode === 'copy' && this.userDepartmentId) ? this.userDepartmentId : undefined;
          this.formData.childrens = Array.isArray(newItem.components)
            ? newItem.components.map((c, idx) => {
                if (c.eq_type && c.eq_type.id) {
                  this.childSuggestions[idx] = [c.eq_type];
                  const displayName = c.eq_type.classificator_path
                    ? `${c.eq_type.classificator_path} ${c.eq_type.name || ''}`.trim()
                    : (c.eq_type.name || '');
                  this.selectedChildEquipmentType = {
                    ...this.selectedChildEquipmentType,
                    [idx]: { ...c.eq_type, id: c.eq_type.id, displayName },
                  };
                }
                return {
                  inventory_number: c.inventory_number || '',
                  factory_number: c.factory_number || '',
                  act_of_receiving: c.act_of_receiving || '',
                  status: c.status || 'at_work',
                  department_id: childDeptId !== undefined ? childDeptId : c.department_id,
                  type: c.type || '',
                  receiving_date: c.receiving_date
                    ? c.receiving_date.substr(0, 10)
                    : new Date().toISOString().substr(0, 10),
                  comment: c.comment || '',
                  parent_id: c.parent_id || newItem.id,
                  id: c.id || 0,
                };
              })
            : [];
          this.notification = { show: false, message: '', type: 'success' };
          // Принудительно открываем диалог
          this.$nextTick(() => {
            this.dialog = true;
          });
        } else if (!newItem && oldItem) {
          // Если item стал null, закрываем диалог
          this.dialog = false;
        }
      },
    },
    mode: {
      immediate: false,
      handler(newMode, oldMode) {
        // Если mode изменился и item есть, открываем диалог
        if (newMode && this.item && newMode !== oldMode) {
          this.notification = { show: false, message: '', type: 'success' };
          this.$nextTick(() => {
            this.dialog = true;
          });
        }
      },
    },
  },
};
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}
.v-toolbar {
  border-radius: 8px 8px 0 0;
}
.soft-blink {
  animation: soft-blink 1.6s ease-in-out infinite alternate;
}

@keyframes soft-blink {
  from {
    opacity: 1;
    filter: saturate(1);
  }
  to {
    opacity: 0.65;
    filter: saturate(1.1);
  }
}
</style>
