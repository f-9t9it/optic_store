<template>
  <div class="os-root">
    <div v-for="side in sides" :class="`os-header ${side}`">{{ side }}</div>
    <div v-for="side in sides" :class="get_side_class(side, ['os-label'])">
      <span v-for="param in params">{{ param }}</span>
    </div>
    <div class="os-row-header first">Distance</div>
    <div v-for="side in sides" :class="get_side_class(side, ['os-value'])">
      <prescription-form-field
        v-for="param in params"
        :key="`${param}_${side}`"
        v-bind="get_field_props(side, param)"
      />
    </div>
    <div class="os-row-header">Add</div>
    <div v-for="side in sides" :class="get_side_class(side, ['os-value'])">
      <prescription-form-field v-bind="get_field_props(side, 'add')" />
    </div>
    <div class="os-row-header">Reading</div>
    <div
      v-for="side in sides"
      :class="get_side_class(side, ['os-value', 'last'])"
    >
      <span class="like-disabled-input">
        {{ get_formatted(side, 'sph_reading') }}
      </span>
    </div>
  </div>
</template>

<script>
import { RX_PARAMS_SPEC_DIST, RX_PARAMS_CONT_DIST } from '../utils/constants';
import PrescriptionFormField from './PrescriptionFormField.vue';

export default {
  components: { PrescriptionFormField },
  props: {
    doc: Object,
    on_change: Function,
    get_formatted: Function,
    get_step: Function,
  },
  data: function() {
    return { sides: ['right', 'left'] };
  },
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
    get_side_class: function(side, always = []) {
      return always.reduce((a, x) => Object.assign({ [x]: true }, a), {
        right: side === 'right',
        left: side === 'left',
        four: this.doc.type === 'Spectacles',
        six: this.doc.type === 'Contacts',
      });
    },
    get_field_props: function(side, param) {
      return {
        param,
        side,
        disabled: this.doc.docstatus !== 0,
        step: this.get_step(param),
        value: parseFloat(this.doc[`${param}_${side}`]),
        get_formatted: this.get_formatted,
        on_change: this.on_change,
      };
    },
    get_other_label: function(param) {
      if (param === 'pd') {
        return 'PD';
      }
      if (param === 'prism') {
        return 'Prism';
      }
      if (param === 'iop') {
        return 'Intraocular Pressure';
      }
      return param;
    },
  },
};
</script>

<style lang="scss" scoped>
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.os-root {
  display: grid;
  grid-template-columns: 100px [right] 1fr [left] 1fr;
  grid-template-rows: [side] 1fr auto repeat(3, 1fr) auto 1fr;
  align-items: center;
}
.os-header {
  grid-row: side;
  color: #8d99a6;
  font-weight: bold;
  text-transform: capitalize;
  text-align: center;
  height: 100%;
}
.os-row-header {
  grid-column: 1;
  &.first {
    grid-row: 3;
  }
}
.os-header,
.os-label,
.os-value {
  &.right {
    grid-column: right;
    border-right: 1px solid #ebeff2;
  }
  &.left {
    grid-column: left;
  }
}
.os-label,
.os-value {
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  padding: 0 2px;
  & > * {
    margin: 2px;
  }
  &.four > * {
    width: calc(25% - 2 * 2px);
  }
  &.six > * {
    width: calc(16.67% - 2 * 2px);
  }
  & > span {
    &.like-disabled-input {
      font-size: inherit;
      text-align: right;
    }
  }
  &.last {
    padding-bottom: 2px;
  }
}
.os-label > span,
.os-row-header {
  text-transform: uppercase;
  font-size: 0.8em;
  color: #8d99a6;
}

.os-label {
  border-top: 1px solid #ebeff2;
  padding-top: 2px;
  & > span {
    text-align: center;
    padding-top: 10px;
  }
}
.os-value > input {
  text-align: right;
}
</style>
