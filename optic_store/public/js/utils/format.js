export function get_formatted(doc) {
  return function(side, param) {
    const value = doc[side ? `${param}_${side}` : param] || 0;
    if (['sph', 'cyl', 'sph_reading', 'add'].includes(param)) {
      return `${value > 0 ? '+' : ''}${value.toFixed(2)}`;
    }
    if ('axis' === param) {
      return `${value}°`;
    }
    if ('height' === param) {
      return `${value.toFixed(2)}mm`;
    }
    if ('pd' === param) {
      return `${value.toFixed(1)}mm`;
    }
    if ('prism' === param) {
      return value.toFixed(2);
    }
    if ('iop' === param) {
      return `${value.toFixed(2)}mmHg`;
    }
    return value;
  };
}
