<template>
  <table class="table table-condensed">
    <thead>
      <tr>
        <td />
        <th
          v-for="side in ['right', 'left']"
          :colspan="params.length"
          :class="{ 'last-right-cell': side === 'right' }"
          class="label-side"
          scope="col"
        >
          {{ side }}
        </th>
      </tr>
      <tr>
        <td />
        <th
          v-for="(param, index) in params"
          :class="{
            'label-param': true,
            'last-right-cell': index === params.length - 1,
          }"
          scope="col"
        >
          {{ param }}
        </th>
        <th
          v-for="param in params"
          :class="{ 'label-param': true }"
          scope="col"
        >
          {{ param }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">Distance</th>
        <td
          v-for="(param, index) in params"
          :class="{ 'last-right-cell': index === params.length - 1 }"
        >
          {{ get_formatted('right', param) }}
        </td>
        <td v-for="param in params">{{ get_formatted('left', param) }}</td>
      </tr>
      <tr>
        <th scope="row">Reading</th>
        <td>{{ get_formatted('right', 'sph_reading') }}</td>
        <td :colspan="params.length - 1" class="text-secondary last-right-cell">
          (<span class="label-param">Add</span>
          {{ get_formatted('right', 'add_type') }}:
          {{ get_formatted('right', 'add') }})
        </td>
        <td>{{ get_formatted('left', 'sph_reading') }}</td>
        <td :colspan="params.length - 1" class="text-secondary">
          (<span class="label-param">Add</span>
          {{ get_formatted('left', 'add_type') }}:
          {{ get_formatted('left', 'add') }})
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  props: {
    params: Array,
    get_formatted: Function,
  },
};
</script>

<style scoped>
.label-side {
  text-transform: capitalize;
  text-align: center;
}
.label-param {
  text-transform: uppercase;
  text-align: right;
  font-size: 0.8em;
}
td {
  text-align: right;
}
.text-secondary {
  text-align: left;
  color: #8d99a6;
}

/* reset bootstrap */
.table > thead > tr > th,
.table > thead > tr > td {
  border-top: none;
  border-bottom: none;
}

.table > thead > tr > td:first-child,
.table > tbody > tr > th:first-child,
.last-right-cell {
  border-right: 1px solid #d1d8dd;
}
</style>
