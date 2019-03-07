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
    <div v-for="side in sides" :class="get_side_class(side, ['os-value'])">
      <span class="like-disabled-input">
        {{ get_formatted(side, 'sph_reading') }}
      </span>
    </div>
    <div v-for="side in sides" :class="get_side_class(side, ['os-label'])">
      <span v-for="param in params_other"> {{ get_other_label(param) }} </span>
    </div>
    <div v-for="side in sides" :class="get_side_class(side, ['os-value'])">
      <prescription-form-field
        v-for="param in params_other"
        :key="`${param}_${side}`"
        v-bind="get_field_props(side, param)"
      />
    </div>
  </div>
</template>

<script>
import {
  RX_PARAMS_SPEC_DIST,
  RX_PARAMS_CONT_DIST,
  RX_PARAMS_OTHER,
} from '../utils/constants';
import { get_formatted } from '../utils/format';
import PrescriptionFormField from './PrescriptionFormField.vue';

function get_step(param) {
  if (['sph', 'cyl', 'sph_reading', 'add', 'va', 'iop'].includes(param)) {
    return '0.01';
  }
  if ('prism' === param) {
    return '0.1';
  }
  if (['axis', 'pd'].includes(param)) {
    return '1';
  }
  return null;
}

export default {
  components: { PrescriptionFormField },
  props: { doc: Object, update: Function },
  data: function() {
    return { sides: ['right', 'left'], params_other: RX_PARAMS_OTHER };
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
    get_formatted: function(side, param) {
      return get_formatted(this.doc)(side, param);
    },
    on_change: function(e) {
      this.update(e.target.name, parseFloat(e.target.value || 0));
    },
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
        step: get_step(param),
        value: parseFloat(this.doc[`${param}_${side}`]),
        get_formatted: this.get_formatted,
        on_change: this.on_change,
      };
    },
    get_other_label: function(param) {
      if (param === 'pd') {
        return 'Pupillary Distance';
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
}
.os-label > span,
.os-row-header {
  text-transform: uppercase;
  font-size: 0.8em;
  color: #8d99a6;
}

.os-label {
  margin-top: 12px;
  border-top: 1px solid #ebeff2;
  padding-top: 2px;
  & > span {
    text-align: center;
  }
}
.os-value > input {
  text-align: right;
}
</style>
