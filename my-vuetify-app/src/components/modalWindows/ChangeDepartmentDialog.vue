<template>
  <div>
    <!-- Кнопка с иконкой -->
    <v-hover v-slot="{ isHovering, props }">
      <v-avatar
        v-bind="props"
        size="38"
        :color="isHovering ? 'blue-lighten-4' : 'grey-lighten-3'"
        class="elevation-2"
        style="cursor: pointer"
        @click="openDialog"
      >
        <v-icon color="primary" v-tooltip="'Передать оборудование'"
          >mdi-swap-horizontal</v-icon
        >
      </v-avatar>
    </v-hover>

    <!-- Диалог подтверждения -->
    <v-dialog v-model="confirmDialog" max-width="700">
      <v-card>
        <v-card-title class="text-h6 red--text">
          Передача оборудования
        </v-card-title>

        <v-card-text>
          <div class="pa-2 mb-4" style="border: 1px solid #ccc">
            <div>Инв.№ {{ item.inventory_number }}</div>
            <div>Зав.№ {{ item.factory_number }}</div>
            <div>Тип: {{ item.eq_type?.type || '-' }}</div>
            <div v-if="item.components.length">
              В составе: {{ item.components.length }} ед. оборудования
            </div>
          </div>

          <v-row>
            <v-col cols="6" class="d-flex align-center">
              <v-checkbox
                v-model="betweenDepartments"
                label="Между отделениями"
                hide-details
                density="compact"
              />
            </v-col>
            <v-select
              v-if="betweenDepartments"
              :items="departments"
              item-title="name"
              item-value="id"
              label="Подразделение"
              variant="outlined"
              density="comfortable"
              hide-details
              v-model="dep"
              @update:modelValue="fetchDep()"
            ></v-select>
            <v-col cols="6" v-if="!betweenDepartments">
              <v-text-field
                v-model="department"
                label="Название подразделения..."
                dense
                hide-details
              />
            </v-col>
            <v-col cols="12" v-if="!betweenDepartments">
              <v-text-field
                v-model="reason"
                label="Основание *"
                dense
                hide-details
                required
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="green" @click="confirmTransfer">Подтвердить</v-btn>
          <v-btn color="red" text @click="cancel">Отмена</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ConfirmTransferDialog',
  props: {
    item: { type: Object, required: true },
    transferUrl: { type: String, default: '/api/request' },
  },
  data() {
    return {
      type: 'decommissioning',
      confirmDialog: false,
      betweenDepartments: false,
      reason: '',
      dep: '',
      department: '',
      departments: [],
    };
  },
  async mounted() {
    console.log(this.item);

    this.fetchDep();
  },
  methods: {
    openDialog() {
      this.confirmDialog = true;
    },
    async fetchDep() {
      const departmentsRes = await axios.get('/api/departments');
      this.departments = [...new Set(departmentsRes.data)];
    },
    async confirmTransfer() {
      try {
        const payload = {
          equipment_id: this.item.id,
          type: this.type,
          act: this.reason,
          from_department: this.item.department.name,
          to_department: this.dep || department,
        };
        console.log(payload);

        const response = await axios.post(this.transferUrl, null, {
          params: payload,
        });
        console.log('Передача выполнена:', response.data);

        this.$emit('transferred', this.item);
      } catch (error) {
        console.error('Ошибка передачи оборудования:', error);
      } finally {
        this.confirmDialog = false;
      }
    },
    cancel() {
      this.confirmDialog = false;
    },
  },
};
</script>
