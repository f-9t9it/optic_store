<template>
  <div class="os-root">
    <div
      v-for="side in ['right', 'left', 'total']"
      :class="`os-header ${side}`"
    >
      {{ side }}
    </div>
    <div class="os-row-header first">PD</div>
    <div
      v-for="side in ['right', 'left', 'total']"
      :class="get_side_class(side, ['os-value'])"
    >
      <prescription-form-field
        :key="`pd_${side}`"
        v-bind="get_field_props(side, 'pd')"
      />
    </div>
    <div class="os-row-header">Prism</div>
    <div
      v-for="side in ['right', 'left']"
      :class="get_side_class(side, ['os-value'])"
    >
      <prescription-form-field
        :key="`prism_${side}`"
        v-bind="get_field_props(side, 'prism')"
      />
    </div>
    <div class="os-row-header">IOP</div>
    <div
      v-for="side in ['right', 'left']"
      :class="get_side_class(side, ['os-value'])"
    >
      <prescription-form-field
        :key="`iop_${side}`"
        v-bind="get_field_props(side, 'iop')"
      />
    </div>
  </div>
</template>

<script>
import { get_formatted } from '../utils/format';
import PrescriptionFormField from './PrescriptionFormField.vue';

export default {
  components: { PrescriptionFormField },
  props: {
    doc: Object,
    on_change: Function,
    get_formatted: Function,
    get_step: Function,
  },
  methods: {
    get_side_class: function(side, always = []) {
      return always.reduce((a, x) => Object.assign({ [x]: true }, a), {
        right: side === 'right',
        left: side === 'left',
        total: side === 'total',
      });
    },
    get_field_props: function(side, param) {
      return {
        param,
        side,
        disabled: this.doc.docstatus !== 0 || side === 'total',
        step: this.get_step(param),
        value: parseFloat(this.doc[`${param}_${side}`]),
        get_formatted: this.get_formatted,
        on_change: this.on_change,
      };
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
  width: calc((100% - 100px) / 2 + 100px);
  display: grid;
  grid-template-columns: 100px [right] 1fr [left] 1fr [total] 1fr;
  grid-template-rows: [side] 1fr repeat(3, 1fr);
  align-items: center;
}
.os-header {
  grid-row: side;
}
.os-row-header {
  grid-column: 1;
  &.first {
    grid-row: 2;
  }
}
.os-header,
.os-value {
  &.right {
    grid-column: right;
  }
  &.left {
    grid-column: left;
  }
  &.total {
    grid-column: total;
  }
}
.os-header {
  text-align: center;
}
.os-header,
.os-row-header {
  text-transform: uppercase;
  font-size: 0.8em;
  color: #8d99a6;
}
.os-value {
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  & > * {
    margin: 2px;
    width: 100%;
  }
}
</style>
