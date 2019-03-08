<template>
  <div>
    <div ref="chart" />
    <div class="os-actions">
      <button
        v-for="choice in choices"
        type="button"
        :class="{ 'btn btn-xs': true, 'btn-info': showing === choice }"
        @click="showing = choice;"
      >
        {{ choice }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: { labels: Array, datasets: Array },
  data: function() {
    const choices = this.datasets.map(({ name }) => name);
    return { choices, showing: choices[0] };
  },
  methods: {
    get_chart_data: function(showing) {
      return {
        labels: this.labels,
        datasets: this.datasets.filter(({ name }) => name === showing),
      };
    },
  },
  mounted() {
    const chart = new Chart(this.$refs.chart, {
      title: 'Sales by Item Group',
      data: this.get_chart_data(this.showing),
      type: 'bar',
      height: 180,
    });
    this.$watch('showing', showing => {
      chart.update(this.get_chart_data(showing));
    });
  },
};
</script>

<style lang="scss" scoped>
.os-actions {
  & > button {
    margin: 4px;
  }
}
</style>
