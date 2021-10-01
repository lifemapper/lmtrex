import React from 'react';

import type { Component, IR, R, RA, RR } from '../config';
import L from '../leaflet';
import type { AggregatorLayer } from '../leafletUtils';
import {
  addAggregatorOverlays,
  isOverlayDefault,
  legendGradient,
  legendPoint,
  showMap,
} from '../leafletUtils';
import frontEndText from '../localization/frontend';
import { getQueryParameter, inversePromise } from '../utils';
import type { LifemapperLayerTypes } from './config';
import {
  lifemapperLayerVariations,
  lifemapperMessagesMeta,
  VERSION,
} from './config';
import type { BrokerRecord } from './entry';
import { reducer } from './leafletReducer';
import { stateReducer } from './leafletState';
import type {
  IncomingMessage,
  JsonLeafletLayers,
  LocalityData,
  OccurrenceData,
  OutgoingMessage,
} from './occurrence';
import { extractField } from './utils';

export const [resolveMap, getMap] =
  inversePromise<Readonly<[L.Map, L.Control.Layers, HTMLElement]>>();

export function LeafletContainer({
  occurrence,
  scientificName,
}: {
  occurrence: RA<BrokerRecord> | undefined;
  scientificName: string | undefined;
}): Component {
  const [state, dispatch] = React.useReducer(reducer, {
    type: 'MainState',
    customLeafletLayers: undefined,
    occurrencePoints: undefined,
    extendedOccurrencePoints: {},
  });

  const sendMessage = (action: OutgoingMessage): void =>
    window.opener?.postMessage(action, origin);

  React.useEffect(() => {
    const origin = getQueryParameter('origin', (origin) =>
      origin.startsWith('http')
    );

    if (!origin || !window.opener) return undefined;

    sendMessage({ type: 'LoadedAction', version: VERSION });
    const eventHandler = (event: MessageEvent<IncomingMessage>) => {
      if (
        event.source !== window.opener ||
        event.origin !== origin ||
        typeof event.data?.type !== 'string'
      )
        return;
      dispatch(event.data);
    };
    window.addEventListener('message', eventHandler);

    return (): void => window.removeEventListener('message', eventHandler);
  });

  const [projectionLayers, projectionDetails] =
    useProjectionLayers(scientificName);
  const [idbLayers, idbDetails] = useIdbLayers(occurrence, scientificName);
  const [gbifLayers, gbifDetails] = useGbifLayers(occurrence);

  return (
    stateReducer(undefined, {
      ...state,
      options: {
        dispatch,
        overlays: {
          ...projectionLayers,
          ...idbLayers,
          ...gbifLayers,
        },
        layerDetails: [
          frontEndText('mapDescription'),
          ...projectionDetails,
          ...idbDetails,
          ...gbifDetails,
        ],
      },
    }) ?? <i />
  );
}

function useProjectionLayers(
  scientificName: string | undefined
): Readonly<[JsonLeafletLayers, RA<Component>]> {
  const [response, setResponse] = React.useState<
    | undefined
    | {
        readonly errors: IR<IR<string> | string>;
        readonly records: [
          {
            readonly records: {
              readonly 's2n:endpoint': string;
              readonly 's2n:modtime': string;
              // eslint-disable-next-line @typescript-eslint/naming-convention
              readonly 's2n:layer_name': string;
              // eslint-disable-next-line @typescript-eslint/naming-convention
              readonly 's2n:layer_type': LifemapperLayerTypes;
              readonly 's2n:sdm_projection_scenario_code'?: string;
            }[];
          }
        ];
      }
  >(undefined);

  React.useEffect(() => {
    if (typeof scientificName === 'undefined') return;
    fetch(
      `/api/v1/map/?namestr=${scientificName}&scenariocode=worldclim-curr&provider=lm`
    )
      .then(async (response) => response.json())
      .then(setResponse)
      .catch(console.error);
  }, [scientificName]);

  if (typeof scientificName === 'undefined') return [{}, []];

  return [{}, []];
}

function useIdbLayers(
  occurrence: RA<BrokerRecord> | undefined,
  scientificName: string | undefined
): Readonly<[JsonLeafletLayers, RA<string>]> {
  if (
    typeof occurrence === 'undefined' ||
    typeof scientificName === 'undefined'
  )
    return [{}, []];

  return [{}, [frontEndText('iDigBioDescription')]];
}

function getGbifLayers(taxonKey: string | undefined): RA<AggregatorLayer> {
  if (typeof taxonKey === 'undefined') return [];
  return [
    [
      {
        default: isOverlayDefault('gbif', true),
        label: '',
      },
      L.tileLayer(
        'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
        {
          attribution: '',
          // @ts-expect-error
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

function useGbifLayers(
  occurrence: RA<BrokerRecord> | undefined
): Readonly<[JsonLeafletLayers, RA<string>]> {
  const taxonKey =
    typeof occurrence === 'undefined'
      ? undefined
      : extractField(occurrence, 'gbif', 'responses');
  if (typeof taxonKey === 'undefined') return [{}, []];

  return [
    {
      [`GBIF ${legendGradient('#ee0', '#d11')}`]: {},
    },
    [frontEndText('gbifDescription')],
  ];
}

export function LeafletMap({
  customLeafletLayers,
  occurrencePoints,
  extendedOccurrencePoints,
  overlays,
}: {
  customLeafletLayers: JsonLeafletLayers | undefined;
  occurrencePoints: RA<OccurrenceData> | undefined;
  extendedOccurrencePoints: IR<LocalityData>;
  overlays: JsonLeafletLayers;
}): Component {
  const leafletMap = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {}, []);

  React.useEffect(() => {}, [customLeafletLayers]);

  React.useEffect(() => {}, [occurrencePoints]);

  React.useEffect(() => {}, [extendedOccurrencePoints]);

  const availableOverlays = Object.keys(overlays);
  React.useEffect(() => {}, [availableOverlays]);

  return (
    <div className="leaflet-map-container">
      <div className="leaflet-map" ref={leafletMap} />
    </div>
  );
}

async function drawMap(
  mapContainer: HTMLElement,
  mapDetails: HTMLElement
): Promise<void> {
  const messages: RR<'errorDetails' | 'infoSection', string[]> = {
    errorDetails: [],
    infoSection: [],
  };

  const layerCounts: R<number> = {};
  let lifemapperLayers: RA<AggregatorLayer> = [];
  try {
    lifemapperLayers = response.records[0].records
      .filter(
        (record) =>
          record['s2n:sdm_projection_scenario_code'] === 'worldclim-curr' &&
          record['s2n:layer_type'] === 'raster'
      )
      .map<AggregatorLayer | undefined>((record) => {
        const layerType = record['s2n:layer_type'];
        layerCounts[layerType] ??= 0;
        layerCounts[layerType] += 1;

        if (layerCounts[layerType] > 10) return undefined;

        const showLayerNumber =
          response.records[0].records.filter(
            (record) => record['s2n:layer_type'] === layerType
          ).length !== 1;

        const isFirstOfType = layerCounts[layerType] === 1;
        return [
          {
            label: `${lifemapperLayerVariations[layerType].layerLabel}${
              showLayerNumber ? ` (${layerCounts[layerType]})` : ''
            }`,
            default: isOverlayDefault(
              `layerType${isFirstOfType ? '_first' : ''}`,
              isFirstOfType
            ),
          },
          L.tileLayer.wms(record['s2n:endpoint'], {
            layers: record['s2n:layer_name'],
            opacity: 0.7,
            transparent: true,
            // @ts-expect-error
            service: 'wms',
            version: '1.0',
            height: '400',
            format: 'image/png',
            request: 'getmap',
            srs: 'epsg:3857',
            width: '800',
          }),
        ];
      })
      .filter(
        (record): record is AggregatorLayer => typeof record !== 'undefined'
      );

    const modificationTime = response.records[0].records[0]['s2n:modtime'];
    const dateObject = new Date(modificationTime);
    const formattedModificationTime = `<time
      datetime="${dateObject.toISOString()}"
    >${dateObject.toDateString()}</time>`;
    messages.infoSection.push(`
      It also displays a predicted distribution model from Lifemapper. Model
      computed with default Maxent parameters: ${formattedModificationTime}`);
  } catch {
    console.warn('Failed to find Lifemapper projection map for this species');
  }

  mapDetails.innerHTML = Object.entries(messages)
    .filter(([, messages]) => messages.length > 0)
    .map(([name, messages]) => {
      const meta =
        lifemapperMessagesMeta[name as keyof typeof lifemapperMessagesMeta];
      return `<span
        class="lifemapper-message-section ${meta.className}"
      >
        ${'title' in meta ? `<h4>${meta.title}</h4><br>` : ''}
        ${messages.join('<br>')}
      </span>`;
    })
    .join('');

  const idbScientificName =
    extractField(response.occurrence_info, 'idb', 'dwc:scientificName') ??
    extractField(response.name_info, 'gbif', 's2n:canonical_name');
  const idbCollectionCode = extractField(
    response.occurrence_info,
    'idb',
    'dwc:collectionCode'
  );
  const gbifTaxonKey = extractField(
    response.name_info,
    'gbif',
    's2n:gbif_taxon_key'
  );

  const [leafletMap, layerGroup] = showMap(mapContainer, 'occurrence');
  resolveMap?.([leafletMap, layerGroup, mapContainer]);

  let hasLayers = false;
  const addLayers = addAggregatorOverlays(leafletMap, layerGroup, () => {
    hasLayers = true;
  });
  addLayers(lifemapperLayers);
  addLayers(getGbifLayers(gbifTaxonKey));
  addLayers(await getIdbLayers(idbScientificName, idbCollectionCode));

  if (!hasLayers) {
    leafletMap.off();
    leafletMap.remove();
    const parent = mapContainer.parentElement;
    if (!parent) return;
    parent.textContent = 'Unable to find any information for this record';
  }
}

async function getIdbLayer(
  scientificName: string,
  collectionCode: string | undefined,
  options: AggregatorLayer[0],
  className?: string
): Promise<AggregatorLayer | undefined> {
  let request: Response | undefined;
  try {
    request = await fetch('https://search.idigbio.org/v2/mapping/', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        rq: {
          scientificname: scientificName,
          ...(typeof collectionCode === 'string'
            ? {
                collectioncode: collectionCode,
              }
            : {}),
        },
        type: 'auto',
        threshold: 100_000,
      }),
    });
  } catch {
    return undefined;
  }
  const response = await request.json();
  const pointCount = response.itemCount;
  if (pointCount === 0) return undefined;

  const serverUrl = response.tiles;
  return [
    options,
    L.tileLayer(serverUrl, {
      attribution: 'iDigBio and the user community',
      className: className ?? 'saturated',
    }),
  ];
}

async function getIdbLayers(
  scientificName: string | undefined,
  collectionCode: string | undefined
): Promise<RA<AggregatorLayer>> {
  if (typeof scientificName === 'undefined') return [];

  const layers = await Promise.all([
    getIdbLayer(scientificName, undefined, {
      label: `iDigBio ${legendPoint('#197')}`,
      default: isOverlayDefault('idb', true),
    }),
    getIdbLayer(
      scientificName,
      collectionCode,
      {
        label: `iDigBio (${
          collectionCode ?? 'collection'
        } points only) ${legendPoint('#e68')}`,
        default: isOverlayDefault('idb_collection', true),
      },
      'hue-rotate'
    ),
  ]);

  return layers.filter(
    (data): data is AggregatorLayer => typeof data !== 'undefined'
  );
}
