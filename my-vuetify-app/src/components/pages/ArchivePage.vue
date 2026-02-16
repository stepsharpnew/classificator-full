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
            @update:search="onNameInput"
            @update:modelValue="onFilterChange()"
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
      <v-card-text class="pa-0 ma-0" v-if="items.length > 0">
        <v-row
          class="text-center font-weight-bold mt-4 bg-grey-lighten-3 rounded-t archive-table-row"
          style="font-size: 0.98rem"
        >
          <!-- <v-col
              cols="1"
              class="d-flex justify-center align-center text-no-wrap"
              >№ п/п</v-col
            > -->
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
            cols="2"
            class="d-flex justify-center align-center text-no-wrap"
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
            >Акт<br />списания</v-col
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
          >
            Статус
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-row
          v-for="(item, index) in items"
          :key="item.id"
          class="text-center align-center py-3 border-b archive-table-row"
          :class="item.components.length ? 'bg-blue-lighten-5' : 'bg-white'"
        >
          <!-- <v-col cols="1" class="d-flex justify-center align-center">{{
              1 + index + (page - 1) * 10
            }}</v-col> -->
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
          <v-col cols="2" class="d-flex justify-center align-center"
            >{{ item.eq_type?.name }}
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
            >{{ item.act_of_decommissioning }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ typeDisplayName(item.eq_type?.type) }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center"
            >{{ item.department?.name }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            <v-chip
              :color="statusColor(item.status)"
              size="small"
              class="text-white text-uppercase"
              >{{ statusText(item.status) }}</v-chip
            >
          </v-col>

          <!-- <v-col cols="1" class="d-flex justify-center align-center gap-x-2">
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
          </v-col> -->
        </v-row>
      </v-card-text>
      <v-card-text v-else class="ma-2 pa-5 w-100 d-flex align-center">
        <div>Нет элементов удовлетворяющих условиям поиска в архиве</div>
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
</template>

<script>
import axios from 'axios';
import ChildrenComp from '../components/ChildrenComp.vue';
import MainNavBar from '../components/MainNavBar.vue';
import EquipmentCreateDialog from '../modalWindows/addEquipModal.vue';
import ConfirmComp from '../modalWindows/ConfirmComp.vue';

export default {
  components: {
    MainNavBar,
    EquipmentCreateDialog,
    ChildrenComp,
    ConfirmComp,
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
        { title: 'Пусто', value: '' },
        { title: 'ССИУС', value: 'ssius' },
        { title: 'СИУС', value: 'sius' },
      ],
      filters: {
        search: '',
        name: '',
        department: '',
        year: '',
        type: '',
      },
      suggestions: [],
      suggestionLoading: false,
      suggestionTimeout: null,
      totalCount: 0,
      itemsPerPage: 20,
      userDepartmentId: '',
      canChooseDepartment: false,
      canEditSkzi: false,
    };
  },
  computed: {
    pageCount() {
      return Math.ceil(this.totalCount / this.itemsPerPage);
    },
  },
  methods: {
    typeDisplayName(type) {
      if (type == null || type === '') return 'Пусто';
      const t = String(type).toLowerCase();
      if (t === 'ssius') return 'ССИУС';
      if (t === 'sius') return 'СИУС';
      return type;
    },
    openDialog(item) {
      this.deletedItem = item;
      this.confirmDialog = true;
    },
    onNameInput(val) {
      clearTimeout(this.suggestionTimeout);
      this.suggestionTimeout = setTimeout(() => {
        this.fetchNameSuggestions(val);
      }, 300);
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
    async fetchData() {
      if (this.filters.equipmentType) {
        console.log(this.filters);
      }
      const departmentsRes = await axios.get('/api/departments');
      this.departments = [...new Set(departmentsRes.data)];
      
      // Вычисляем offset на основе текущей страницы
      const offset = (this.page - 1) * this.itemsPerPage;
      
      let params = { 
        ...this.filters,
        limit: this.itemsPerPage,
        offset: offset
      };
      
      const response = await axios.get('/api/archive', { params });
      console.log(response.data);

      this.items = response.data.equipments || [];
      this.totalCount = response.data.total_count || 0;
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
        type: '',
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
    editItem(item) {
      this.selectedItem = item;
      this.selectedMode = 'edit';
    },
    copyItem(item) {
      this.selectedItem = item;
      this.selectedMode = 'copy';
    },
    async deleteItem(item) {
      this.deletedItem = item;
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
.archive-table-row {
  min-height: 80px;
}
</style>
