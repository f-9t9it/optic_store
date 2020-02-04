import { make_link } from './fields';

export default function() {
  return {
    filters: [make_link({ fieldname: 'customer', options: 'Customer' })],
  };
}
