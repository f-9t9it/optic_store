<template>
  <span v-if="disabled" class="os-disabled like-disabled-input">
    {{ get_formatted(side, param) }}
  </span>
  <input
    v-else
    class="form-control"
    :name="`${param}_${side}`"
    v-model="scrubbed"
    @input="on_input"
    @blur="on_blur"
  />
</template>

<script>
export default {
  props: {
    param: String,
    side: String,
    on_change: Function,
    value: String,
    disabled: Boolean,
    get_formatted: Function,
    on_blur: { type: Function, default: () => {} },
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
