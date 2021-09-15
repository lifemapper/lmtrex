async function getInstitutionMapMeta(publishingOrgKey) {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?publishingOrg=${publishingOrgKey}`
  );
  return await request.json();
}

async function getCollectionMapData(datasetKey) {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?datasetKey=${datasetKey}`
  );
  return await request.json();
}

let activeMaps = [];

async function showStatsMap(mapData, mapOptions, mapContainer) {
  mapContainer.style.display = '';

  const { minYear, maxYear } = mapData;

  const slider =
    mapContainer.parentElement.getElementsByClassName('slider')[0];
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
  const baseLayer = Object.values(leafletTileServers['baseMaps'])[0](false);

  const map = L.map(mapContainer, {
    maxZoom: 23,
    layers: [baseLayer, labelsLayer],
    gestureHandling: true
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
          year: `${minYear},${maxYear}`,
          ...mapOptions
        })
          .map(([key, value]) => `${key}=${value}`)
          .join('&'),
      }
    );
    overlay.addTo(map);
    labelsLayer.bringToFront();
  }
  redrawMap(defaultMinValue, defaultMaxValue);

  activeMaps.push(map);

  return ()=>{
    inputs.map(input=>input.removeEventListener('change', changeHandler));
    map.off();
    map.remove();
    activeMaps=activeMaps.filter(potentialMap=>potentialMap!==map)
  }
}
