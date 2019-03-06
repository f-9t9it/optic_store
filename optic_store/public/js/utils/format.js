export function get_formatted(doc) {
  return function(side, param) {
    const value = doc[`${param}_${side}`];
    if (['sph', 'cyl', 'sph_reading', 'add'].includes(param)) {
      return `${value > 0 ? '+' : ''}${value.toFixed(2)}`;
    }
    if ('axis' === param) {
      return `${value}°`;
    }
    if ('va' === param) {
      return value.toFixed(2);
    }
    if ('pd' === param) {
      return `${value.toFixed(0)}mm`;
    }
    if ('prism' === param) {
      return value.toFixed(1);
    }
    if ('iop' === param) {
      return `${value.toFixed(2)}mmHg`;
    }
    return value;
  };
}
