function initializeMaps() {
  const mapContainer = document.getElementById('map');
  if(!mapContainer)
    return;
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
    layers = response.records[0].records
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

  let hasLayers = false;
  const addAggregatorOverlays = (layers)=>
    layers.forEach(([options, layer]) => {
      hasLayers = true;
      layerGroup.addOverlay(layer, options.label);
      if (options.default) layer.addTo(leafletMap);
    });

  addAggregatorOverlays(getGbifLayers(gbifTaxonKey));

  showCollectionStats(gbifPublishingOrgKey, collectionMap);

  addAggregatorOverlays(await idbLayersPromise);

  if(!hasLayers){
    leafletMap.off();
    leafletMap.remove();
    map.parentElement.innerText='Unable to find any information for this record'
  }
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
      classname: 'saturated',
      ...options,
    }),
  ];
}

async function getIdbLayers(scientificName, collectionCode) {
  if (!scientificName) return [];

  const layers = await Promise.all([
    getIdbLayer(scientificName, undefined, {
      label: `iDigBio ${legendPoint('#197')}`,
      default: true
    }),
    getIdbLayer(scientificName, collectionCode, {
      label: `iDigBio (${collectionCode} points only) ${legendPoint('#e68')}`,
      default: true,
      className: 'idb-local-points',
    }),
  ]);

  return layers.filter((data) => data);
}

const legendPoint = (color)=>`<span
  aria-hidden="true"
  style="--color: ${color}"
  class="leaflet-legend-point"
></span>`;

const legendGradient = (leftColor, rightColor)=>`<span
  aria-hidden="true"
  style="--left-color: ${leftColor}; --right-color: ${rightColor}"
  class="leaflet-legend-gradient"
></span>`;

function getGbifLayers(taxonKey) {
  if(!taxonKey)
    return [];
  return [
    [
      { default: true, label: `GBIF ${legendGradient('#ee0', '#d11')}` },
      L.tileLayer(
        'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
        {
          attribution: '',
          source: 'density',
          format: '@1x.png',
          className: 'saturated',
          params: Object.entries({
            srs: 'EPSG:3857',
            style: 'classic.poly',
            bin: 'hex',
            hexPerTile: 20,
            taxonKey,
          })
            .map(([key, value]) => `${key}=${value}`)
            .join('&'),
        }
      ),
    ],
  ];
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
    gestureHandling: true
  }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

  const layerGroup = L.control.layers({}, overlayLayers);
  layerGroup.addTo(map);

  addFullScreenButton(map);
  addPrintMapButton(map);

  return [map, layerGroup];
}
