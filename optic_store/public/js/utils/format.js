export function get_formatted(doc) {
  return function(side, param) {
    const value = doc[side ? `${param}_${side}` : param] || 0;
    if (['sph', 'cyl', 'sph_reading', 'add'].includes(param)) {
      return `${value > 0 ? '+' : ''}${value.toFixed(2)}`;
    }
    if ('axis' === param) {
      return `${value}°`;
    }
    if (['pd', 'height'].includes(param)) {
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
