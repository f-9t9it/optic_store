<template>
  <section class="root">
    <dl v-for="(qty, brand) in brands">
      <dt>{{ brand }}</dt>
      <dd>{{ qty }}</dd>
    </dl>
  </section>
</template>

<script>
import groupBy from 'lodash/groupBy';
import mapValues from 'lodash/mapValues';
import sumBy from 'lodash/sumBy';
export default {
  props: { items: Array, default: [] },
  computed: {
    brands: function() {
      return mapValues(groupBy(this.items, ({ brand }) => brand || 'No Brand'), x =>
        sumBy(x, 'qty')
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.root {
  display: flex;
  flex-flow: row wrap;
  & > dl {
    min-width: 20%;
    text-align: center;
  }
  & dt {
    font-weight: normal;
  }
  & dd {
    font-size: 1.3em;
    font-weight: bold;
  }
}
</style>
