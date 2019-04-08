<template>
  <div class="os-root">
    <prescription-form-conditionals
      v-if="doc.type === 'Spectacles'"
      v-bind="{ doc, on_change, conditional_fields }"
    />
    <prescription-form-main
      v-bind="{ doc, on_change, get_formatted, get_step }"
    />
    <prescription-form-supplement
      v-bind="{ doc, on_change, get_formatted, get_step }"
    />
  </div>
</template>

<script>
import { get_formatted } from '../utils/format';
import PrescriptionFormMain from './PrescriptionFormMain.vue';
import PrescriptionFormConditionals from './PrescriptionFormConditionals.vue';
import PrescriptionFormSupplement from './PrescriptionFormSupplement.vue';

function get_step(param) {
  if (['sph', 'sph_reading', 'add', 'iop'].includes(param)) {
    return '0.01';
  }
  if ('cyl' === param) {
    return '0.25';
  }
  if ('prism' === param) {
    return '0.01';
  }
  if (['axis', 'pd'].includes(param)) {
    return '1';
  }
  return null;
}

export default {
  components: {
    PrescriptionFormMain,
    PrescriptionFormConditionals,
    PrescriptionFormSupplement,
  },
  props: { doc: Object, update: Function, fields: Object },
  computed: {
    conditional_fields: function() {
      if (!this.fields || !this.fields.type_of_spectacle) {
        return [];
      }
      return [this.fields.type_of_spectacle.df];
    },
  },
  methods: {
    get_formatted: function(side, param) {
      return get_formatted(this.doc)(side, param);
    },
    get_step,
    on_change: function(e) {
      return this.update(
        e.target.name,
        ['va_right', 'va_left'].includes(e.target.name)
          ? e.target.value
          : parseFloat(e.target.value || 0)
      );
    },
  },
};
</script>

<style lang="scss" scoped></style>
