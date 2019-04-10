<template>
  <div class="checkbox">
    <label>
      <span v-if="disabled" class="disp-area">
        <i :class="get_disp_class(`${param}_${side}`)" />
      </span>
      <span v-else class="input-area">
        <input type="checkbox" :name="`${param}_${side}`" @click="on_click" />
      </span>
      <span class="label-area small">{{ param }}</span>
    </label>
  </div>
</template>

<script>
export default {
  props: {
    param: String,
    side: String,
    on_change: Function,
    value: Number,
    disabled: Boolean,
  },
  methods: {
    get_disp_class: function(value) {
      if (this.value) {
        return 'octicon octicon-check';
      }
      return 'fa fa-square disabled-check';
    },
    on_click: function(e) {
      const { name, checked } = e.target;
      return this.on_change({ target: { name, value: checked ? 1 : 0 } });
    },
  },
};
</script>

<style lang="scss" scoped>
.checkbox {
  margin: 0 0.5em;
  & .octicon {
    margin-right: 3px;
  }
  & .label-area {
    text-transform: capitalize;
  }
}
</style>
