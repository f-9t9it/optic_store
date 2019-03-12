<template>
  <div class="os-root">
    <prescription-form-conditionals
      v-if="doc.type === 'Spectacles'"
      v-bind="{ doc, update, conditional_fields }"
    />
    <prescription-form-main v-bind="{ doc, update }" />
  </div>
</template>

<script>
import PrescriptionFormMain from './PrescriptionFormMain.vue';
import PrescriptionFormConditionals from './PrescriptionFormConditionals.vue';

export default {
  components: { PrescriptionFormMain, PrescriptionFormConditionals },
  props: { doc: Object, update: Function, fields: Object },
  computed: {
    conditional_fields: function() {
      if (!this.fields || !this.fields.type_of_spectacle) {
        return [];
      }
      return [this.fields.type_of_spectacle.df];
    },
  },
};
</script>

<style lang="scss" scoped></style>
