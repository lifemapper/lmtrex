const occId = getQueryParameter('occid', (occId) => occId.length > 0);
const nameStr = getQueryParameter('namestr', (nameStr) => nameStr.length > 0);
const queryString = `?occid=${occId}&namestr=${nameStr}&loader=false`;
const fetchUrl = `${window.location.origin}${window.location.pathname}${queryString}${window.location.hash}`;

loader(
  () => fetch(fetchUrl).then((response) => response.text()),
  initializeMaps
);
