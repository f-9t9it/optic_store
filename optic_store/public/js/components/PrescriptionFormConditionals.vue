<template>
  <div class="os-root">
    <div class="os-field">
      <label for="">Type of Spectacles</label>
      <span v-if="disabled" class="os-disabled like-disabled-input">
        {{ doc.type_of_spectacle }}
      </span>
      <select
        v-else
        type="text"
        class="form-control"
        name="type_of_spectacle"
        :value="doc.type_of_spectacle"
        @change="on_change"
      >
        <option v-for="type in spec_types" :value="type">{{ type }}</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    doc: Object,
    conditional_fields: Array,
    on_change: Function,
  },
  computed: {
    disabled: function() {
      return this.doc.docstatus !== 0;
    },
    spec_types: function() {
      const { options = '' } =
        this.conditional_fields.find(
          ({ fieldname }) => fieldname === 'type_of_spectacle'
        ) || {};
      return options.split('\n');
    },
  },
};
</script>

<style lang="scss" scoped>
.os-root {
  margin-bottom: 12px;
  width: calc((100% - 100px) / 2 + 100px);
}
.os-field {
  display: flex;
  flex-flow: row nowrap;
  & > label {
    margin: 0;
    font-weight: normal;
    text-transform: uppercase;
    font-size: 0.8em;
    color: #8d99a6;
    flex: 0 0 100px;
  }
  & > select,
  & > span {
    margin: 0 4px;
    width: 100%;
  }
}
</style>
