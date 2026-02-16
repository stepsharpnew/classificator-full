<template>
  <v-container fluid class="pa-4 bg-grey-lighten-4 min-h-screen">
    <MainNavBar />
    <v-row class="mb-5">
      <v-col cols="auto">
        <EquipmentCreateDialog
          :departments="departments"
          :user-department-id="userDepartmentId"
          :can-choose-department="canChooseDepartment"
          @created="refreshSkziList"
          @closed="onEquipmentDialogClosed"
          @notify="onNotify"
          :item="selectedItem"
          :mode="selectedMode"
        />
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
            label="Поиск (Инв., Зав., Наименование, Рег.№ СКЗИ)"
            variant="outlined"
            density="comfortable"
            hide-details
            v-model="filters.search"
            @input="onFilterChange()"
          ></v-text-field>
        </v-col>
        <v-col cols="2" class="d-flex align-center">
          <v-btn variant="elevated" color="error" @click="resetFilters">
            Сброс
          </v-btn>
        </v-col>
      </v-row>
      <div class="d-flex align-center mt-3 mb-2 px-2 text-body2">
        <span class="text-medium-emphasis">
          Всего СКЗИ: <strong>{{ totalCount }}</strong>
        </span>
      </div>
      <v-card-text class="pa-0 ma-0" v-if="items.length > 0">
        <v-row
          class="text-center font-weight-bold mt-4 bg-grey-lighten-3 rounded-t table-row"
          style="font-size: 0.98rem"
        >
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap col-number-header">№</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Инв. №</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Зав. №</v-col>
          <v-col cols="1" class="d-flex flex-column justify-center align-start text-truncate px-1">Наименование</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Рег. № СКЗИ</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Акт приёма СКЗИ</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Дата акта</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Сертификат</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Дата ок. серт.</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Номер журнала</v-col>
          <v-col cols="1" class="d-flex justify-center align-center col-wrap">Кому выдано</v-col>
          <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Управление</v-col>
        </v-row>
        <v-divider></v-divider>
        <v-row
          v-for="(item, index) in items"
          :key="item.id"
          class="text-center align-center py-3 border-b table-row"
        >
          <v-col cols="1" class="d-flex justify-center align-center col-number">
            {{ (page - 1) * itemsPerPage + index + 1 }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.equipment?.inventory_number || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.equipment?.factory_number || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex flex-column justify-center align-start text-truncate px-1">
            <v-tooltip v-if="item.equipment?.eq_type?.name" location="top">
              <template #activator="{ props }">
                <span v-bind="props" class="text-truncate d-inline-block" style="max-width: 100%; cursor: default">
                  <template v-if="getClassificatorPath(item.equipment?.eq_type)">
                    <span class="classificator-number">{{ getClassificatorPath(item.equipment.eq_type) }}</span>
                    <span> </span>
                  </template>
                  <span>{{ item.equipment?.eq_type?.name }}</span>
                </span>
              </template>
              <template #default>
                <span class="equipment-tooltip-content">{{ getEquipmentFullName(item.equipment) }}</span>
              </template>
            </v-tooltip>
            <span v-else>—</span>
            <div class="d-flex flex-column mt-1 eq-labels-block">
              <span v-if="item.equipment?.eq_type?.staff_number" class="eq-name-label">
                <span class="eq-label-text">Табель</span> {{ item.equipment.eq_type.staff_number }}
              </span>
              <span v-if="item.equipment?.eq_type?.fnn != null && item.equipment?.eq_type?.fnn !== ''" class="eq-name-label">
                <span class="eq-label-text">ФНН</span> {{ item.equipment.eq_type.fnn }}
              </span>
            </div>
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.registration_number || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.act_of_receiving_skzi || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ formatDate(item.date_of_act_of_receiving) }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.sertificate_number || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ formatDate(item.end_date_of_sertificate) }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center">
            {{ item.nubmer_of_jornal || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex justify-center align-center col-wrap px-1">
            {{ item.issued_to_whoom || '—' }}
          </v-col>
          <v-col cols="1" class="d-flex flex-column justify-center align-center">
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
            <div class="d-flex justify-center align-center gap-x-2">
              <ChangeDepartmentDialog
                :item="equipmentForItem(item)"
                @transferred="fetchData"
                @notify="onNotify"
              />
              <ConfirmArchiveDialog :item="equipmentForItem(item)" @archived="fetchData" />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-text v-else class="ma-2 pa-5 w-100 d-flex align-center">
        <div>Нет записей СКЗИ</div>
      </v-card-text>
    </v-card>
    <v-pagination
      v-model="page"
      :length="pageCount"
      :total-visible="7"
      @update:modelValue="onPageChange"
      rounded="circle"
    ></v-pagination>

  <NotificationDialog
    v-model="notification.show"
    :message="notification.message"
    :type="notification.type"
    :fade-out="notification.fadeOut"
  />
  </v-container>
</template>

<script>
import axios from 'axios';
import MainNavBar from '../components/MainNavBar.vue';
import EquipmentCreateDialog from '../modalWindows/addEquipModal.vue';
import ChangeDepartmentDialog from '../modalWindows/ChangeDepartmentDialog.vue';
import ConfirmArchiveDialog from '../modalWindows/ConfirmArchiveDialog.vue';
import ConfirmComp from '../modalWindows/ConfirmComp.vue';
import NotificationDialog from '../modalWindows/NotificationDialog.vue';

export default {
  name: 'SkziPage',
  components: {
    MainNavBar,
    EquipmentCreateDialog,
    ChangeDepartmentDialog,
    ConfirmArchiveDialog,
    ConfirmComp,
    NotificationDialog,
  },
  data() {
    return {
      page: 1,
      selectedMode: '',
      selectedItem: null,
      deletedItem: null,
      items: [],
      departments: [],
      filters: { search: '' },
      totalCount: 0,
      itemsPerPage: 20,
      userDepartmentId: '',
      canChooseDepartment: false,
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
      return Math.ceil(this.totalCount / this.itemsPerPage) || 1;
    },
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      return d.toLocaleDateString('ru-RU');
    },
    async fetchData() {
      const offset = (this.page - 1) * this.itemsPerPage;
      const params = {
        limit: this.itemsPerPage,
        offset,
      };
      if (this.filters.search) params.search = this.filters.search;
      const res = await axios.get('/api/skzi', { params });
      this.items = res.data.items || [];
      this.totalCount = res.data.total_count || 0;
    },
    onFilterChange() {
      this.page = 1;
      this.fetchData();
    },
    resetFilters() {
      this.filters.search = '';
      this.page = 1;
      this.fetchData();
    },
    onPageChange() {
      this.fetchData();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    async refreshSkziList() {
      await this.fetchData();
    },
    editItem(skziItem) {
      const eq = skziItem.equipment;
      if (!eq) return;
      this.selectedItem = { ...eq, skzi: [skziItem] };
      this.selectedMode = 'edit';
    },
    copyItem(skziItem) {
      const eq = skziItem.equipment;
      if (!eq) return;
      this.selectedItem = { ...eq, skzi: [skziItem] };
      this.selectedMode = 'copy';
    },
    deleteItem(skziItem) {
      this.deletedItem = skziItem?.equipment || skziItem;
    },
    onEquipmentDialogClosed() {
      this.selectedItem = null;
      this.selectedMode = '';
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
    equipmentForItem(skziItem) {
      return skziItem?.equipment || skziItem;
    },
    getClassificatorPath(eqType) {
      if (!eqType || !eqType.classificator_path) return null;
      return String(eqType.classificator_path);
    },
    getEquipmentFullName(equipment) {
      if (!equipment?.eq_type?.name) return '';
      const path = this.getClassificatorPath(equipment.eq_type);
      return path ? `${path} ${equipment.eq_type.name}`.trim() : equipment.eq_type.name;
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
      } catch (e) {
        this.userDepartmentId = '';
        this.canChooseDepartment = false;
      }
    }
    const deptRes = await axios.get('/api/departments');
    this.departments = deptRes.data ? [...new Set(deptRes.data)] : [];
    await this.fetchData();
  },
  beforeUnmount() {
    if (this.notificationHideTimeout) clearTimeout(this.notificationHideTimeout);
  },
};
</script>

<style scoped>
.col-number {
  font-size: 0.9rem;
}
.col-wrap {
  max-width: 100px;
  word-wrap: break-word;
  word-break: break-word;
  white-space: normal;
  overflow-wrap: break-word;
  text-align: center;
  line-height: 1.3;
}
.classificator-number {
  font-weight: bold;
  color: #1976d2;
  margin-right: 4px;
  font-size: 1.05em;
}
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
.col-number-header {
  font-size: 0.9rem;
}
.table-row {
  min-height: 80px;
}
</style>
<style>
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
