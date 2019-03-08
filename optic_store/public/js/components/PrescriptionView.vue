<template>
  <section>
    <div v-if="doc.type === 'Spectacles'" class="os-specs">
      <dl>
        <dt>Type of Spectacles</dt>
        <dd class="like-disabled-input">{{ doc.type_of_spectacle }}</dd>
      </dl>
      <dl>
        <dt>Frame Size</dt>
        <dd class="like-disabled-input">{{ get_formatted('frame_size') }}</dd>
      </dl>
      <dl>
        <dt>Height</dt>
        <dd class="like-disabled-input">{{ doc.height_type }}</dd>
        <dd class="like-disabled-input">{{ get_formatted('height') }}</dd>
      </dl>
    </div>
    <prescription-form v-bind="{ doc }" />
  </section>
</template>

<script>
import { RX_PARAMS_SPEC_DIST, RX_PARAMS_CONT_DIST } from '../utils/constants';
import { get_formatted } from '../utils/format';
import PrescriptionForm from './PrescriptionForm.vue';

export default {
  props: { doc: Object },
  components: { PrescriptionForm },
  methods: {
    get_formatted: function(param) {
      return get_formatted(this.doc)(null, param);
    },
  },
};
</script>

<style lang="scss" scoped>
.os-specs {
  display: flex;
  margin-left: 120px;
  & dt,
  & dd {
    margin: 2px;
  }
  & > dl {
    min-width: 100px;
    & > dt {
      text-transform: uppercase;
      font-size: 0.8em;
      color: #8d99a6;
      text-align: center;
      font-weight: normal;
    }
    & > dd {
      text-align: right;
    }
  }
}
</style>
