async function getGbifMeta(publishingOrgKey) {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?publishingOrg=${publishingOrgKey}`
  );
  return await request.json();
}

async function showCollectionStats(publishingOrgKey, collectionMap) {
  if(!publishingOrgKey)
    return;
  document.getElementById('collection-distribution').style.display = 'block';

  const { minYear, maxYear } = await getGbifMeta(publishingOrgKey);

  const slider = document.getElementsByClassName('slider')[0];
  const inputs = Array.from(slider.getElementsByTagName('input'));
  function changeHandler(event) {
    let boundaries = Object.fromEntries(
      inputs
        .filter((input) => input.type === event.target.type)
        .map((input) => [
          input.classList.contains('min') ? 'min' : 'max',
          input.value,
        ])
    );

    if (
      event.target.type === 'range' &&
      boundaries['min'] > boundaries['max']
    ) {
      if (event.target.classList.contains('min')) {
        boundaries['max'] = boundaries['min'];
        inputs.find(
          (input) => input.type === event.target.type && input !== event.target
        ).value = boundaries['max'];
      } else {
        boundaries['min'] = boundaries['max'];
        event.target.value = boundaries['max'];
      }
    }

    inputs
      .filter((input) => input.type !== event.target.type)
      .forEach((input) => {
        input.value =
          boundaries[input.classList.contains('min') ? 'min' : 'max'];
      });

    redrawMap(boundaries['min'], boundaries['max']);
  }

  const defaultMinValue = Math.round(minYear + (maxYear - minYear) * 0.4);
  const defaultMaxValue = maxYear;
  inputs.forEach((input) => {
    input.min = minYear;
    input.max = maxYear;
    input.value = input.classList.contains('min')
      ? defaultMinValue
      : defaultMaxValue;
    input.addEventListener('change', changeHandler);
  });

  const labelsLayer = Object.values(leafletTileServers['overlays'])[0]();
  const baseLayer = Object.values(leafletTileServers['baseMaps'])[0]();

  const map = L.map(collectionMap, {
    maxZoom: 23,
    layers: [baseLayer, labelsLayer],
  }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

  addFullScreenButton(map);
  addPrintMapButton(map);

  let overlay;
  function redrawMap(minYear, maxYear) {
    if (overlay) map.removeLayer(overlay);
    overlay = L.tileLayer(
      'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
      {
        attribution: '',
        source: 'density',
        format: '@1x.png',
        params: Object.entries({
          srs: 'EPSG:3857',
          style: 'classic.poly',
          bin: 'hex',
          publishingOrg: publishingOrgKey,
          year: `${minYear},${maxYear}`,
        })
          .map(([key, value]) => `${key}=${value}`)
          .join('&'),
      }
    );
    overlay.addTo(map);
    labelsLayer.bringToFront();
  }
  redrawMap(defaultMinValue, defaultMaxValue);
}
