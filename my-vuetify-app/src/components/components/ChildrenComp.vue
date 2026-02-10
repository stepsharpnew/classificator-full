<template>
      <v-dialog
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"    
        transition="dialog-top-transition"
        scrim="rgba(0, 0, 0, 0.2)"  
        >
      <v-card min-height="400">
        <v-toolbar color="primary">
          <v-toolbar-title>Компоненты в составе</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="$emit('update:modelValue', false)">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text class="mt-4 pa-0">
            <v-row class="text-center font-weight-bold bg-grey-lighten-3 rounded-t" style="font-size: 0.98rem; height: 60px;">
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">№ п/п</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Инв. №</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Зав. №</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Дата<br>получения</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Акт<br>получения</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Подразделение</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Статус</v-col>
                <v-col cols="2" class="d-flex justify-center align-center text-no-wrap">Наименование</v-col>
                <v-col cols="1" class="d-flex justify-center align-center text-no-wrap">Тип</v-col>
                <v-col cols="2" class="d-flex justify-center align-center text-no-wrap">Примечания</v-col>
            </v-row>
            <v-row v-for="(item, index) in components" :key="item.id" class="text-center align-center py-3 bg-blue-2 border-b " >
                <v-col cols="1" class="d-flex justify-center align-center">{{ index +1 }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">
                    {{item.inventory_number }}
                </v-col>
                <v-col cols="1" class="d-flex justify-center align-center">{{ item.factory_number }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">{{ formatDate(item.receiving_date) }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">{{ item.act_of_receiving }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">{{ item.department?.name }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">
                    <v-chip :color="statusColor(item.status)" size="small" class="text-white text-uppercase">
                        {{ statusText(item.status) }}
                    </v-chip>
                </v-col>
                <v-col cols="2" class="d-flex justify-center align-center">{{ item.eq_type?.name }}</v-col>
                <v-col cols="1" class="d-flex justify-center align-center">{{ item.eq_type?.type || '-' }}</v-col>
                <v-col cols="2" class="d-flex justify-center align-center">{{ item.comment }}</v-col>
            </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </template>
  
  <script>
  export default {  
    name: 'ChildrenComp',
    props: {
      modelValue: Boolean,
      components: {
        type: Array,
        default: () => []
      }
    },
    data() {
      return {
        expandedItems: [],
      }
    },
    methods: {
      formatDate(date) {
        if (!date) return ''
        return new Date(date).toLocaleDateString()
      },
      statusColor(status) {
        const colors = {
          'at_work': 'success',
          'repair': 'error',
          'archive': 'grey',
        }
        return colors[status] || 'grey'
      },
      statusText(status) {
        const texts = {
          'at_work': 'В работе',
          'repair': 'В ремонте',
          'archive': 'В архиве',
        }
        return texts[status] || status
      },
    }
  }
  </script>
  