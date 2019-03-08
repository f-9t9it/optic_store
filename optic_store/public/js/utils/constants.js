export const RX_PARAMS_SPEC_DIST = ['sph', 'cyl', 'axis', 'va'];
export const RX_PARAMS_CONT_DIST = [...RX_PARAMS_SPEC_DIST, 'bc', 'dia'];
export const RX_PARAMS_OTHER = ['pd', 'prism', 'iop'];

export function get_all_rx_params() {
  const params = [
    ...RX_PARAMS_CONT_DIST,
    ...RX_PARAMS_OTHER,
    'add',
    'sph_reading',
  ];
  return ['right', 'left']
    .map(side => params.map(param => `${param}_${side}`))
    .flat();
}
