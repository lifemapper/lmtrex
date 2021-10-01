export const camelToHuman = (value: string): string =>
  capitalize(value.replace(/([a-z])([A-Z])/g, '$1 $2')).replace(/Dna\b/, 'DNA');

export const capitalize = (string: string): string =>
  string.charAt(0).toUpperCase() + string.slice(1);
