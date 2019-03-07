<template>
  <span v-if="disabled" class="os-disabled like-disabled-input">
    {{ get_formatted(side, param) }}
  </span>
  <input
    v-else
    class="form-control"
    :name="`${param}_${side}`"
    type="number"
    :step="step"
    :value="value"
    @input="on_change"
  />
</template>

<script>
export default {
  props: {
    param: String,
    side: String,
    step: String,
    on_change: Function,
    value: Number,
    disabled: Boolean,
    get_formatted: Function,
  },
};
</script>

<style lang="scss" scoped>
.os-disabled {
  font-size: inherit;
  text-align: right;
}
</style>
