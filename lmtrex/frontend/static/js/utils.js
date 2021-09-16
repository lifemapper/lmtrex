const urlParams = new URLSearchParams(window.location.search);

const getQueryParameter = (name, validator) =>
  validator(urlParams.get(name) ?? '') ? urlParams.get(name) : '';
