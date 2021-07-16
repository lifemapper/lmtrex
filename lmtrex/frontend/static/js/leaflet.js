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

  const layerCounts = {};
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
    .map((record) => {
      layerCounts[record['s2n:layer_type']] ??= 0;
      layerCounts[record['s2n:layer_type']] += 1;

      if(layerCounts[record['s2n:layer_type']] > 10)
        return undefined;

      return {
        ...lifemapperLayerVariations[record['s2n:layer_type']],
        layerLabel:
          `${
            lifemapperLayerVariations[record['s2n:layer_type']].layerLabel
          } (${layerCounts[record['s2n:layer_type']]})`,
        isDefault: layerCounts[record['s2n:layer_type']] === 1,
        tileLayer: {
          mapUrl: record['s2n:endpoint'],
          options: {
            layers: record['s2n:layer_name'],
            opacity: 0.5,
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
      };
    }).filter(record=>record);

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

const DEFAULT_CENTER = [0,0];
const DEFAULT_ZOOM = 2;
async function showCOMap(mapContainer, listOfLayersRaw) {
  const listOfLayers = [
    ...coMapTileServers.map(({ transparent, layerLabel }) => ({
      transparent,
      layerLabel,
      isDefault: true,
      tileLayer:
        leafletTileServers[transparent ? 'overlays' : 'baseMaps'][layerLabel],
    })),
    ...listOfLayersRaw.map(
      ({ transparent, layerLabel, isDefault, tileLayer: { mapUrl, options } }) => ({
        transparent,
        layerLabel,
        isDefault: isDefault,
        tileLayer: L.tileLayer.wms(mapUrl, options),
      })
    ),
  ];

  const formatLayersDict = (listOfLayers) =>
    Object.fromEntries(
      listOfLayers.map(({ layerLabel, tileLayer }) => [layerLabel, tileLayer])
    );

  const enabledLayers = Object.values(formatLayersDict(
    listOfLayers.filter(({isDefault})=>
      isDefault
    )
  ));
  const overlayLayers = formatLayersDict(
    listOfLayers.filter(({ transparent }) =>
      transparent
    )
  );

  const map = L.map(mapContainer, {
    maxZoom: 23,
    layers: enabledLayers,
  }).setView(
    DEFAULT_CENTER,
    DEFAULT_ZOOM
  );

  const layerGroup = L.control.layers({}, overlayLayers);
  layerGroup.addTo(map);

  return [map, layerGroup];
}
