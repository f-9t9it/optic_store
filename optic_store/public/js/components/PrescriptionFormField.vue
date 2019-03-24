<template>
  <span v-if="disabled" class="os-disabled like-disabled-input">
    {{ get_formatted(side, param) }}
  </span>
  <input
    v-else
    class="form-control"
    :name="`${param}_${side}`"
    :type="type"
    :step="step"
    v-model="scrubbed"
    @input="on_input"
  />
</template>

<script>
export default {
  props: {
    param: String,
    side: String,
    type: { type: String, default: 'number' },
    step: String,
    on_change: Function,
    value: [String, Number],
    disabled: Boolean,
    get_formatted: Function,
  },
  data: function() {
    return {
      scrubbed: this.value,
    };
  },
  methods: {
    on_input: function(e) {
      this.scrubbed = this.on_change(e);
    },
  },
  watch: {
    value: function(value) {
      this.scrubbed = value;
    },
  },
};
</script>

<style lang="scss" scoped>
.os-disabled {
  font-size: inherit;
  text-align: right;
}
</style>
