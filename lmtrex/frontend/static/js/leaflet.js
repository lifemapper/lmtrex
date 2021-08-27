window.addEventListener('load', () => {
  Array.from(document.getElementsByClassName('leaflet-map-container')).forEach(
    (mapContainer) => {
      const pre = mapContainer.getElementsByTagName('pre')[0];
      const response = JSON.parse(pre.innerText);
      pre.remove();
      const map = mapContainer.getElementsByClassName('leaflet-map')[0];
      const collectionMap = mapContainer.getElementsByClassName(
        'leaflet-collection-map'
      )[0];
      const mapDetails = mapContainer.getElementsByClassName('map-details')[0];
      drawMap(response, map, collectionMap, mapDetails);
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
    'Satellite Map (ESRI)': () =>
      L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
          attribution:
            'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        }
      ),
  },
  overlays: {
    'Labels and boundaries': () =>
      L.tileLayer(
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

const extractField = (responses, aggregator, field) =>
  responses.find(
    (response) => response['internal:provider']['code'] === aggregator
  )?.[field];

async function drawMap(response, map, collectionMap, mapDetails) {
  const messages = {
    errorDetails: [],
    infoSection: [],
  };

  const layerCounts = {};
  let layers = [];
  try {
    response.records[0].records
      .filter(
        (record) =>
          typeof record['s2n:sdm_projection_scenario_code'] !== 'string' ||
          record['s2n:sdm_projection_scenario_code'] === 'worldclim-curr'
      )
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
        const layerType = record['s2n:layer_type'];
        layerCounts[layerType] ??= 0;
        layerCounts[layerType] += 1;

        if (layerCounts[layerType] > 10) return undefined;

        const showLayerNumber =
          response.records[0].records.filter(
            (record) => record['s2n:layer_type'] === layerType
          ).length !== 1;

        return {
          ...lifemapperLayerVariations[layerType],
          layerLabel: `${lifemapperLayerVariations[layerType].layerLabel}${
            showLayerNumber ? ` (${layerCounts[layerType]})` : ''
          }`,
          isDefault: layerCounts[layerType] === 1,
          tileLayer: {
            mapUrl: record['s2n:endpoint'],
            options: {
              layers: record['s2n:layer_name'],
              opacity: 0.7,
              service: 'wms',
              version: '1.0',
              height: '400',
              format: 'image/png',
              request: 'getmap',
              srs: 'epsg:3857',
              width: '800',
              ...lifemapperLayerVariations[layerType],
            },
          },
        };
      })
      .filter((record) => record);

    const modificationTime = response.records[0].records[0]['s2n:modtime'];
    messages.infoSection.push(`Model Creation date: ${modificationTime}`);
  } catch {
    console.warn('Failed to find LifeMapper projection map for this species');
  }

  mapDetails.innerHTML = Object.entries(messages)
    .filter(([, messages]) => messages.length > 0)
    .map(
      ([name, messages]) => `<span
    class="lifemapper-message-section ${lifemapperMessagesMeta[name].className}"
  >
    <i>${lifemapperMessagesMeta[name].title}</i><br>
    ${messages.join('<br>')}
  </span>`
    )
    .join('');

  const idbScientificName = extractField(
    response['occurrence_info'],
    'idb',
    'dwc:scientificName'
  );
  const idbCollectionCode = extractField(
    response['occurrence_info'],
    'idb',
    'dwc:collectionCode'
  );
  const gbifTaxonKey = extractField(
    response['name_info'],
    'gbif',
    's2n:gbif_taxon_key'
  );
  const gbifPublishingOrgKey = extractField(
    response['occurrence_info'],
    'gbif',
    'gbif:publishingOrgKey'
  );

  const mapPromise = showCOMap(map, layers);
  const idbLayersPromise = getIdbLayers(idbScientificName, idbCollectionCode);
  const [leafletMap, layerGroup] = await mapPromise;

  const addAggregatorOverlays = (layers) =>
    layers.forEach(([options, layer]) => {
      layerGroup.addOverlay(layer, options.label);
      if (options.default) layer.addTo(leafletMap);
    });

  addAggregatorOverlays(getGbifLayers(gbifTaxonKey));

  showCollectionStats(gbifPublishingOrgKey, collectionMap);

  addAggregatorOverlays(await idbLayersPromise);
}

async function getIdbLayer(scientificName, collectionCode, options) {
  const request = await fetch('https://search.idigbio.org/v2/mapping/', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      rq: {
        scientificname: scientificName,
        ...(collectionCode
          ? {
              collectioncode: collectionCode,
            }
          : {}),
      },
      type: 'auto',
      threshold: 100000,
    }),
  });
  const response = await request.json();
  const pointCount = response.itemCount;
  if (pointCount === 0) return undefined;

  const serverUrl = response.tiles;
  return [
    options,
    L.tileLayer(serverUrl, {
      attribution: 'iDigBio and the user community',
      ...options,
    }),
  ];
}

async function getIdbLayers(scientificName, collectionCode) {
  if (!scientificName) return [];

  const layers = await Promise.all([
    getIdbLayer(scientificName, undefined, { label: 'iDigBio', default: true }),
    getIdbLayer(scientificName, collectionCode, {
      label: `iDigBio (${collectionCode} points only)`,
      default: true,
      className: 'idb-local-points',
    }),
  ]);

  return layers.filter((data) => data);
}

function getGbifLayers(taxonKey) {
  return [
    [
      { default: false, label: 'GBIF' },
      L.tileLayer(
        'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
        {
          attribution: '',
          source: 'density',
          format: '@1x.png',
          params: Object.entries({
            srs: 'EPSG:3857',
            style: 'green.poly',
            bin: 'hex',
            taxonKey,
          })
            .map(([key, value]) => `${key}=${value}`)
            .join('&'),
        }
      ),
    ],
  ];
}

async function getGbifMeta(publishingOrgKey) {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?publishingOrg=${publishingOrgKey}`
  );
  return await request.json();
}

async function showCollectionStats(publishingOrgKey, collectionMap) {
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

  const baseLayer = Object.values(leafletTileServers['baseMaps'])[0]();

  const map = L.map(collectionMap, {
    maxZoom: 23,
    layers: [baseLayer],
  }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

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
          style: 'purpleYellow.poly',
          bin: 'hex',
          publishingOrg: publishingOrgKey,
          year: `${minYear},${maxYear}`,
        })
          .map(([key, value]) => `${key}=${value}`)
          .join('&'),
      }
    );
    overlay.addTo(map);
  }
  redrawMap(defaultMinValue, defaultMaxValue);
}

const DEFAULT_CENTER = [0, 0];
const DEFAULT_ZOOM = 2;

async function showCOMap(mapContainer, listOfLayersRaw) {
  const listOfLayers = [
    ...coMapTileServers.map(({ transparent, layerLabel }) => ({
      transparent,
      layerLabel,
      isDefault: true,
      tileLayer:
        leafletTileServers[transparent ? 'overlays' : 'baseMaps'][layerLabel](),
    })),
    ...listOfLayersRaw.map(
      ({
        transparent,
        layerLabel,
        isDefault,
        tileLayer: { mapUrl, options },
      }) => ({
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

  const enabledLayers = Object.values(
    formatLayersDict(listOfLayers.filter(({ isDefault }) => isDefault))
  );
  const overlayLayers = formatLayersDict(
    listOfLayers.filter(({ transparent }) => transparent)
  );

  const map = L.map(mapContainer, {
    maxZoom: 23,
    layers: enabledLayers,
  }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

  const layerGroup = L.control.layers({}, overlayLayers);
  layerGroup.addTo(map);

  return [map, layerGroup];
}
