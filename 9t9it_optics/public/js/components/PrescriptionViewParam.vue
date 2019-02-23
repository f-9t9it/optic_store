<template>
  <dl class="root">
    <dt>{{ label }}</dt>
    <dd v-for="side in sides">
      <span class="text-capitalize">{{ side }}</span>
      <span>{{ get_formatted(side, field) }}</span>
    </dd>
  </dl>
</template>

<script>
export default {
  props: {
    label: String,
    sides: Array,
    field: String,
    get_formatted: Function,
  },
};
</script>

<style scoped>
.root {
  padding: 16px;
  min-width: 128px;
}
.root > dd {
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
}
.root > dd > span:first-child:after {
  content: ': ';
}
</style>
