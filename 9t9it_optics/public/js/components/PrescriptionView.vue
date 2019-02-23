<template>
  <section>
    <prescription-view-table v-bind="{ params, get_formatted }" />
    <div class="solo-params">
      <prescription-view-param
        label="Pupillary Distance"
        field="pd"
        :sides="['right', 'left', 'total']"
        :get_formatted="get_formatted"
      />
      <prescription-view-param
        label="Prism"
        field="prism"
        :sides="['right', 'left']"
        :get_formatted="get_formatted"
      />
      <prescription-view-param
        label="Intraocular Pressure"
        field="iop"
        :sides="['right', 'left']"
        :get_formatted="get_formatted"
      />
    </div>
  </section>
</template>

<script>
import { RX_PARAMS_SPEC_DIST, RX_PARAMS_CONT_DIST } from '../utils/constants';
import PrescriptionViewTable from './PrescriptionViewTable.vue';
import PrescriptionViewParam from './PrescriptionViewParam.vue';

export default {
  props: { doc: Object },
  components: { PrescriptionViewTable, PrescriptionViewParam },
  computed: {
    params: function() {
      if (this.doc.type === 'Spectacles') {
        return RX_PARAMS_SPEC_DIST;
      }
      if (this.doc.type === 'Contacts') {
        return RX_PARAMS_CONT_DIST;
      }
      return [];
    },
  },
  methods: {
    get_formatted: function(side, param) {
      const value = this.doc[`${param}_${side}`];
      if (['sph', 'cyl', 'sph_reading', 'add'].includes(param)) {
        return `${value > 0 ? '+' : ''}${value.toFixed(2)}`;
      }
      if ('axis' === param) {
        return `${value}°`;
      }
      if ('va' === param) {
        return value.toFixed(2);
      }
      if ('pd' === param) {
        return `${value.toFixed(0)}mm`;
      }
      if ('prism' === param) {
        return value.toFixed(1);
      }
      if ('iop' === param) {
        return `${value.toFixed(2)}mmHg`;
      }
      return value;
    },
  },
};
</script>

<style scoped>
.solo-params {
  display: flex;
  flex-flow: row wrap;
}
</style>
