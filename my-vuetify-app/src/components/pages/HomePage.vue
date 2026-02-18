<template>
  <v-container fluid class="pa-4 bg-grey-lighten-4 min-h-screen">
    <MainNavBar />
    <v-row class="mb-5">
      <v-col cols="auto">
        <EquipmentCreateDialog
          :departments="departments"
          :user-department-id="userDepartmentId"
          :can-choose-department="canChooseDepartment"
          :can-edit-skzi="canEditSkzi"
          @created="refreshEquipmentList"
          @closed="onEquipmentDialogClosed"
          @notify="onNotify"
          :item="selectedItem"
          :mode="selectedMode"
        />
      </v-col>
      <v-col cols="auto">
        <!-- <v-btn color="primary" variant="outlined" @click="backupEquipment">Создать резервную копию оборудования</v-btn> -->
      </v-col>
    </v-row>

    <v-card
      class="pa-4 mb-5 mx-auto"
      max-width="97vw"
      style="font-family: 'Roboto', sans-serif"
    >
      <v-row class="pa-3 bg-blue-lighten-4 rounded gap-x-4">
        <v-col cols="2">
          <v-text-field
            label="Поиск (Инв., Зав., ФНН, Табель, Акт)"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.search"
            @input="onFilterChange()"
          ></v-text-field>
        </v-col>
        <v-col cols="4">
          <v-autocomplete
            label="Наименование оборудования"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.equipmentType"
            item-title="name"
            item-value="id"
            :items="suggestions"
            :loading="suggestionLoading"
            clearable
            no-filter
            @update:search="onNameInput"
            @update:modelValue="onFilterChange()"
            @update:menu="(open) => open && onNameMenuOpen()"
          />
        </v-col>
        <v-col cols="2">
          <v-select
            :items="departments"
            item-title="name"
            item-value="id"
            label="Подразделение"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.department"
            @update:modelValue="onFilterChange()"
          ></v-select>
        </v-col>
        <v-col cols="1">
          <v-select
            :items="years"
            label="Год"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.year"
            @update:modelValue="onFilterChange()"
          ></v-select>
        </v-col>
        <v-col cols="1">
          <v-select
            :items="typeOptions"
            item-title="title"
            item-value="value"
            label="Тип"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.type"
            @update:modelValue="onFilterChange()"
          ></v-select>
        </v-col>
        <v-col cols="2" class="d-flex align-center">
          <v-btn variant="elevated" color="error" @click="resetFilters"
            >Сброс</v-btn
          >
        </v-col>
      </v-row>
      <div class="d-flex align-center mt-3 mb-2 px-2 text-body2">
        <span class="text-medium-emphasis">
          Всего: <strong>{{ totalInWorkRepair }}</strong>
        </span>
        <span class="ml-4 text-medium-emphasis">
          Всего с учетом поиска: <strong>{{ totalCount }}</strong>
        </span>
      </div>
      <v-card-text class="pa-0 ma-0" v-if="items.length > 0">
        <v-row
          class="text-center font-weight-bold mt-4 bg-grey-lighten-3 rounded-t table-row table-header-row"
          style="font-size: 0.98rem"
        >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap col-number-header"
            >№</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Инв. №</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Зав. №</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap text-truncate"
            >Наименование</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Примечания</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >ФНН</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Дата<br />получения</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Акт<br />получения</v-col
          >

          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Тип</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Подразделение</v-col
          >
          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Статус</v-col
          >

          <v-col
            cols="1"
            class="d-flex justify-center align-center text-no-wrap"
            >Управление</v-col
          >
        </v-row>
        <v-divider></v-divider>
        <v-row
          v-for="(item, index) in items"
          :key="item.id"
          class="text-center align-center py-3 border-b"
          :class="rowClass(item) + ' table-row'"
        >
          <v-col cols="1" class="d-flex justify-center align-center col-number">
            {{ (page - 1) * itemsPerPage + index + 1 }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            <span
              v-if="item.components.length"
              class="inventory-highlight"
              @click="openChildrenModal(item.components)"
            >
              {{ item.inventory_number }}
            </span>
            <span v-else>{{ item.inventory_number }}</span>
          </v-col>
          <ChildrenComp
            v-if="item.components.length"
            v-model="showChildrenModal"
            :components="selectedComponents"
          />
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.factory_number }}
          </v-col>
          <v-col cols="1" class="d-flex flex-column justify-center align-start text-truncate px-1">
            <v-tooltip v-if="item.eq_type?.name" location="top">
              <template #activator="{ props }">
                <span v-bind="props" class="text-truncate d-inline-block" style="max-width: 100%; cursor: default">
                  <template v-if="getClassificatorPath(item.eq_type)">
                    <span class="classificator-number">
                      {{ getClassificatorPath(item.eq_type) }}
                    </span>
                    <span> </span>
                  </template>
                  <span>{{ item.eq_type.name }}</span>
                </span>
              </template>
              <template #default>
                <span class="equipment-tooltip-content">{{ getEquipmentFullName(item) }}</span>
              </template>
            </v-tooltip>
            <span v-else>—</span>
            <div class="d-flex flex-column mt-1 eq-labels-block">
              <span v-if="item.eq_type?.staff_number" class="eq-name-label">
                <span class="eq-label-text">Табель</span> {{ item.eq_type.staff_number }}
              </span>
              <span v-if="item.eq_type?.fnn != null && item.eq_type?.fnn !== ''" class="eq-name-label">
                <span class="eq-label-text">ФНН</span> {{ item.eq_type.fnn }}
              </span>
            </div>
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.comment }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.eq_type.fnn }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ formatDate(item.receiving_date) }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.act_of_receiving }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ typeDisplayName(item.eq_type?.type) }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.department?.name }}
          </v-col>
          <v-col cols="1" class="d-flex flex-column justify-center align-center">
            <v-chip
              :color="statusColor(item.status)"
              size="small"
              class="text-white text-uppercase"
              >{{ statusText(item.status) }}</v-chip
            >
            <span
              v-if="hasSkzi(item)"
              class="text-caption text-success mt-1"
              v-tooltip="'Оборудование является СКЗИ'"
            >СКЗИ ✓</span>
          </v-col>

          <v-col
            cols="1"
            class="d-flex flex-column justify-center align-center"
          >
            <!-- верхний ряд: 3 кнопки -->
            <div class="d-flex justify-center align-center mb-2 gap-x-2">
              <v-hover v-slot="{ isHovering, props }">
                <v-avatar
                  v-bind="props"
                  size="38"
                  :color="isHovering ? 'blue-lighten-4' : 'grey-lighten-3'"
                  class="elevation-2"
                  style="cursor: pointer"
                >
                  <v-icon
                    color="primary"
                    @click="editItem(item)"
                    v-tooltip="'Редактировать'"
                    >mdi-pencil</v-icon
                  >
                </v-avatar>
              </v-hover>

              <v-hover v-slot="{ isHovering, props }">
                <v-avatar
                  v-bind="props"
                  size="38"
                  :color="isHovering ? 'blue-lighten-4' : 'grey-lighten-3'"
                  class="elevation-2"
                  style="cursor: pointer"
                >
                  <v-icon
                    color="primary"
                    @click="copyItem(item)"
                    v-tooltip="'Создать по образцу'"
                    >mdi-content-copy</v-icon
                  >
                </v-avatar>
              </v-hover>
              <div>
                <ConfirmComp
                  @click="deleteItem(item)"
                  :item="deletedItem"
                  @deleted="fetchData"
                />
              </div>
            </div>

            <!-- нижний ряд: 2 кнопки -->
            <div class="d-flex justify-center align-center gap-x-2">
              <ChangeDepartmentDialog
                :item="item"
                @transferred="fetchData"
                @notify="onNotify"
              ></ChangeDepartmentDialog>
              <ConfirmArchiveDialog :item="item" @archived="fetchData" @notify="onNotify" />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-text v-else class="ma-2 pa-5 w-100 d-flex align-center">
        <div>Нет элементов удовлетворяющих условиям поиска</div>
      </v-card-text>
    </v-card>
    <v-pagination
      v-model="page"
      :length="pageCount"
      :total-visible="7"
      @update:modelValue="onPageChange"
      rounded="circle"
    ></v-pagination>
  </v-container>

  <NotificationDialog
    v-model="notification.show"
    :message="notification.message"
    :type="notification.type"
    :fade-out="notification.fadeOut"
  />
</template>

<script>
import axios from 'axios';
import ChildrenComp from '../components/ChildrenComp.vue';
import MainNavBar from '../components/MainNavBar.vue';
import EquipmentCreateDialog from '../modalWindows/addEquipModal.vue';
import ChangeDepartmentDialog from '../modalWindows/ChangeDepartmentDialog.vue';
import ConfirmArchiveDialog from '../modalWindows/ConfirmArchiveDialog.vue';
import ConfirmComp from '../modalWindows/ConfirmComp.vue';
import NotificationDialog from '../modalWindows/NotificationDialog.vue';

export default {
  components: {
    MainNavBar,
    EquipmentCreateDialog,
    ChildrenComp,
    ConfirmComp,
    ConfirmArchiveDialog,
    ChangeDepartmentDialog,
    NotificationDialog,
  },

  data() {
    return {
      page: 1,
      selectedMode: '',
      showChildrenModal: false,
      selectedComponents: [],
      selectedItem: null,
      deletedItem: null,
      items: [],
      departments: [],
      years: [],
      typeOptions: [
        { title: 'ВСЕ', value: 'all' },
        { title: 'Пусто', value: 'empty' },
        { title: 'ССИУС', value: 'ssius' },
        { title: 'СИУС', value: 'sius' },
      ],
      filters: {
        search: '',
        name: '',
        department: '',
        year: '',
        type: 'all',
        equipmentType: '',
      },
      suggestions: [],
      suggestionLoading: false,
      suggestionTimeout: null,
      totalCount: 0,
      totalInWorkRepair: 0,
      itemsPerPage: 20,
      userDepartmentId: '',
      canChooseDepartment: false,
      canEditSkzi: false,
      notification: {
        show: false,
        message: '',
        type: 'success',
        fadeOut: false,
      },
      notificationHideTimeout: null,
    };
  },
  computed: {
    pageCount() {
      return Math.ceil(this.totalCount / this.itemsPerPage);
    },
  },
  methods: {
    openDialog(item) {
      this.deletedItem = item;
      this.confirmDialog = true;
    },
    onNameInput(val) {
      clearTimeout(this.suggestionTimeout);
      this.suggestionTimeout = setTimeout(() => {
        this.fetchNameSuggestions(val ?? '');
      }, 300);
    },
    onNameMenuOpen() {
      if (this.suggestions.length === 0 && !this.suggestionLoading) {
        this.fetchNameSuggestions('');
      }
    },
    async fetchNameSuggestions(query) {
      this.suggestionLoading = true;
      try {
        const res = await axios.get(`/api/equipment-type?name=${query}`);
        this.suggestions = res.data;
      } catch (e) {
        console.error('Ошибка подсказок:', e);
      } finally {
        this.suggestionLoading = false;
      }
    },
    async refreshEquipmentList() {
      this.fetchData();
    },
    onNotify({ message, type }) {
      if (this.notificationHideTimeout) {
        clearTimeout(this.notificationHideTimeout);
        this.notificationHideTimeout = null;
      }
      this.notification = { show: true, message, type, fadeOut: false };
      if (type !== 'error') {
        const visibleMs = 500;
        const fadeOutMs = 500;
        this.notificationHideTimeout = setTimeout(() => {
          this.notification.fadeOut = true;
          this.notificationHideTimeout = setTimeout(() => {
            this.notification = { show: false, message: '', type: 'success', fadeOut: false };
            this.notificationHideTimeout = null;
          }, fadeOutMs);
        }, visibleMs);
      }
    },
    async fetchData() {
      if (this.filters.equipmentType) {
        console.log(this.filters);
      }
      const departmentsRes = await axios.get('/api/departments');
      this.departments = [...new Set(departmentsRes.data)];
      
      // Вычисляем offset на основе текущей страницы
      const offset = (this.page - 1) * this.itemsPerPage;
      
      const { type, ...restFilters } = this.filters;
      let params = { 
        ...restFilters,
        limit: this.itemsPerPage,
        offset: offset
      };
      if (type && type !== 'all') {
        params.type = type;
      }
      
      const response = await axios.get('/api/equipment', { params });
      console.log(response.data);

      this.items = response.data.equipments || [];
      this.totalCount = response.data.total_count || 0;
      this.totalInWorkRepair = response.data.total_in_work_repair ?? 0;
    },
    openChildrenModal(components) {
      this.selectedComponents = components;
      this.showChildrenModal = true;
    },

    resetFilters() {
      this.filters = {
        search: '',
        name: '',
        department: '',
        year: '',
        type: 'all',
        equipmentType: '',
      };
      this.page = 1;
      this.fetchData();
    },

    onPageChange(page) {
      this.page = page;
      this.fetchData();
      // Прокрутка вверх при смене страницы
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    onFilterChange() {
      this.page = 1;
      this.fetchData();
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return d.toLocaleDateString('ru-RU');
    },
    statusColor(status) {
      switch (status) {
        case 'at_work':
          return 'success';
        case 'repair':
          return 'error';
        case 'archive':
          return 'grey';
        default:
          return 'primary';
      }
    },

    statusText(status) {
      switch (status) {
        case 'at_work':
          return 'В работе';
        case 'repair':
          return 'В ремонте';
        case 'archive':
          return 'В архиве';
        default:
          return status;
      }
    },
    typeDisplayName(type) {
      if (type == null || type === '') return 'Пусто';
      const t = String(type).toLowerCase();
      if (t === 'ssius') return 'ССИУС';
      if (t === 'sius') return 'СИУС';
      return type;
    },
    editItem(item) {
      this.selectedItem = item;
      this.selectedMode = 'edit';
    },
    copyItem(item) {
      this.selectedItem = item;
      this.selectedMode = 'copy';
    },
    onEquipmentDialogClosed() {
      this.selectedItem = null;
      this.selectedMode = '';
    },
    async deleteItem(item) {
      this.deletedItem = item;
    },

    getClassificatorPath(eqType) {
      if (!eqType || !eqType.classificator_path) {
        return null;
      }
      
      // Возвращаем полный путь классификатора (например, "1.1.1.1.3", "2.31.23.2", "5.1.2")
      return String(eqType.classificator_path);
    },
    getEquipmentFullName(item) {
      if (!item?.eq_type?.name) return '';
      const path = this.getClassificatorPath(item.eq_type);
      return path ? `${path} ${item.eq_type.name}`.trim() : item.eq_type.name;
    },
    hasSkzi(item) {
      if (!item?.skzi) return false;
      const list = Array.isArray(item.skzi) ? item.skzi : [item.skzi];
      return list.length > 0;
    },
    rowClass(item) {
      const base = item.components.length ? 'bg-blue-lighten-5' : 'bg-white';
      return this.hasSkzi(item) ? `${base} row-skzi` : base;
    },
  },
  async mounted() {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const user = payload?.user || {};
        this.userDepartmentId = user.department_id != null ? String(user.department_id) : '';
        this.canChooseDepartment = user.role === 'chief_engineer' || user.is_superuser === true;
        this.canEditSkzi = user.role === 'chief_engineer' || user.is_superuser === true || user.is_skzi_admin === true;
      } catch (e) {
        this.userDepartmentId = '';
        this.canChooseDepartment = false;
        this.canEditSkzi = false;
      }
    }
    await this.fetchData();

    this.years = [
      ...new Set(
        this.items
          .map((item) => {
            const date = item.receiving_date
              ? new Date(item.receiving_date)
              : null;
            return date ? date.getFullYear() : null;
          })
          .filter((year) => year !== null),
      ),
    ];
  },
  beforeUnmount() {
    if (this.notificationHideTimeout) clearTimeout(this.notificationHideTimeout);
  },
};
</script>

<style scoped>
.inventory-highlight {
  font-weight: bold;
  color: red;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}

.inventory-highlight:hover {
  color: darkred;
  text-decoration: underline;
  transform: scale(1.05);
}

.classificator-number {
  font-weight: bold;
  color: #1976d2;
  margin-right: 4px;
  font-size: 1.05em;
}

/* .col-number-header,
.col-number {
  font-variant-numeric: tabular-nums;
  color: rgba(0, 0, 0, 0.55);
  flex: 0 0 2rem;
  min-width: 2rem;
  max-width: 2rem;
} */
.col-number {
  font-size: 0.9rem;
}
.col-number-header {
  font-size: 0.9rem;
}

/* подписи Табель и ФНН у наименования оборудования */
.eq-labels-block {
  gap: 2px;
  line-height: 1.2;
}
.eq-label-text {
  font-size: 0.55rem;
  color: rgba(0, 0, 0, 0.42);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin-right: 3px;
}
.eq-name-label {
  font-size: 0.65rem;
  color: rgba(0, 0, 0, 0.7);
}

/* Строка с оборудованием-СКЗИ — почти прозрачный зелёный фон */
.row-skzi {
  background-color: rgba(76, 175, 80, 0.12) !important;
}

.table-row {
  min-height: 80px;
}

/* Отделение серого заголовка от зелёной подсветки первой строки */
.table-header-row {
  overflow: hidden;
  border-bottom: 2px solid #bdbdbd;
  position: relative;
  z-index: 1;
}

</style>
<style>
/* Всплывающая подсказка наименования — ограниченная ширина, перенос строк (без scoped: рендер в teleport) */
.equipment-tooltip-content {
  display: inline-block;
  max-width: 16em;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  line-height: 1.35;
  text-align: left;
}
</style>
