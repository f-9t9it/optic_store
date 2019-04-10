<template>
  <div class="btn-group btn-group-xs" role="group">
    <button
      :class="get_class('Near')"
      type="button"
      :name="name"
      value="Near"
      @click="on_change"
    >
      Near
    </button>
    <button
      :class="get_class('Intermediate')"
      type="button"
      :name="name"
      value="Intermediate"
      @click="on_change"
    >
      Intermediate
    </button>
  </div>
</template>

<script>
export default {
  props: {
    param: String,
    side: String,
    on_change: Function,
    value: String,
    disabled: Boolean,
  },
  computed: {
    name: function() {
      return `${this.param}_${this.side}`;
    },
  },
  methods: {
    get_class: function(value) {
      return {
        btn: true,
        'btn-info': value === this.value,
        disabled: this.disabled,
      };
    },
  },
};
</script>

<style lang="scss" scoped></style>
