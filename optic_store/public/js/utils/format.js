export function get_formatted(doc) {
  return function(side, param) {
    const value = doc[side ? `${param}_${side}` : param] || 0;
    if (
      param.includes('sph') ||
      param.includes('cyl') ||
      param.includes('add')
    ) {
      const fval = parseFloat((value || '') + '.0');
      return format(param, fval);
    }
    if (param.includes('axis')) {
      return `${value}°`;
    }
    if (param.includes('pd')) {
      return `${parseFloat(value).toFixed(1)}mm`;
    }
    if (
      param.includes('bc') ||
      param.includes('dia') ||
      param.includes('prism')
    ) {
      return parseFloat(value).toFixed(2);
    }
    if (param.includes('iop')) {
      return `${parseFloat(value).toFixed(2)}mmHg`;
    }
    return value;
  };
}

export function format(field, value) {
  if (field.includes('sph') || field.includes('cyl') || field.includes('add')) {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}`;
  }
  return value;
}
