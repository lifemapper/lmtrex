window.addEventListener('load', () => {
  Array.from(document.getElementsByClassName('leaflet-map-container')).forEach(
    (mapContainer) => {
      const pre = mapContainer.getElementsByTagName('pre')[0];
      const response = JSON.parse(pre.innerText);
      pre.remove();
      const map = mapContainer.getElementsByClassName('leaflet-map')[0];
      const mapDetails = mapContainer.getElementsByClassName('map-details')[0];
      drawMap(response, map, mapDetails);
    }
  );
});

const lifemapperLayerVariations = {
  raster: {
    layerLabel: 'Projection',
    transparent: true,
  },
  vector: {
    layerLabel: 'Occurrence Points',
    transparent: true,
  },
};

const coMapTileServers = [
  {
    transparent: false,
    layerLabel: 'Satellite Map (ESRI)',
  },
  {
    transparent: true,
    layerLabel: 'Labels and boundaries',
  },
];

const leafletTileServers = {
  baseMaps: {
    'Satellite Map (ESRI)': L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution:
          'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
      }
    ),
  },
  overlays: {
    'Labels and boundaries': L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
      {
        attribution:
          'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community\n',
      }
    ),
  },
};

const lifemapperMessagesMeta = {
  errorDetails: {
    className: 'error-details',
    title: 'The following errors were reported by Lifemapper:',
  },
  infoSection: {
    className: 'info-section',
    title: 'Projection Details:',
  },
};

function drawMap(response, map, mapDetails) {
  const messages = {
    errorDetails: [],
    infoSection: [],
  };

  const layers = response.records[0].records
    .sort(
      (
        { 's2n:layer_type': layerTypeLeft },
        { 's2n:layer_type': layerTypeRight }
      ) =>
        layerTypeLeft === layerTypeRight
          ? 0
          : layerTypeLeft > layerTypeRight
          ? 1
          : -1
    )
    .map((record) => ({
      ...lifemapperLayerVariations[record['s2n:layer_type']],
      tileLayer: {
        mapUrl: record['s2n:endpoint'],
        options: {
          layers: record['s2n:layer_name'],
          service: 'wms',
          version: '1.0',
          height: '400',
          format: 'image/png',
          request: 'getmap',
          srs: 'epsg:3857',
          width: '800',
          ...lifemapperLayerVariations[record['s2n:layer_type']],
        },
      },
    }));

  const modificationTime = response.records[0].records[0]['s2n:modtime'];
  messages.infoSection.push(`Model Creation date: ${modificationTime}`);

  mapDetails.innerHTML = Object.entries(messages)
    .filter(([,messages]) => messages.length > 0)
    .map(
      ([name, messages]) => `<span
    class="lifemapper-message-section ${lifemapperMessagesMeta[name].className}"
  >
    <i>${lifemapperMessagesMeta[name].title}</i><br>
    ${messages.join('<br>')}
  </span>`
    )
    .join('');

  void showCOMap(map, layers);
}

async function showCOMap(mapContainer, listOfLayersRaw) {
  const listOfLayers = [
    ...coMapTileServers.map(({ transparent, layerLabel }) => ({
      transparent,
      layerLabel,
      tileLayer:
        leafletTileServers[transparent ? 'overlays' : 'baseMaps'][layerLabel],
    })),
    ...listOfLayersRaw.map(
      ({ transparent, layerLabel, tileLayer: { mapUrl, options } }) => ({
        transparent,
        layerLabel,
        tileLayer: L.tileLayer.wms(mapUrl, options),
      })
    ),
  ];

  const formatLayersDict = (listOfLayers) =>
    Object.fromEntries(
      listOfLayers.map(({ layerLabel, tileLayer }) => [layerLabel, tileLayer])
    );

  const allLayers = Object.values(formatLayersDict(listOfLayers));
  const overlayLayers = formatLayersDict(
    listOfLayers.filter(({ transparent }) => transparent)
  );

  const map = L.map(mapContainer, {
    layers: allLayers,
  }).setView([0, 0], 1);

  const layerGroup = L.control.layers({}, overlayLayers);
  layerGroup.addTo(map);

  return [map, layerGroup];
}
