import type { IR, R, RA, RR } from '../config';
import L from '../leaflet';
import type { AggregatorLayer } from '../leafletUtils';
import {
  addAggregatorOverlays,
  isOverlayDefault,
  legendGradient,
  legendPoint,
  showMap,
} from '../leafletUtils';
import type { LifemapperLayerTypes } from './config';
import { lifemapperLayerVariations, lifemapperMessagesMeta } from './config';
import { resolveMap } from './entry';

export function initializeMap(): void {
  const mapContainer = document.getElementById('map');
  if (!mapContainer) return;
  const pre = mapContainer.getElementsByTagName('pre')[0];
  const response: LifemapperMapResponse = JSON.parse(pre.textContent ?? '');
  pre.remove();
  const map = mapContainer.getElementsByClassName('leaflet-map')[0];
  const mapDetails = mapContainer.getElementsByClassName('map-details')[0];

  if (!map) return;
  drawMap(response, map as HTMLElement, mapDetails as HTMLElement).catch(
    console.error
  );

  const statsPageParameters = [
    {
      name: 'institution_code',
      key: 'dwc:institutionCode',
      providers: ['idb', 'gbif'],
    },
    {
      name: 'collection_code',
      key: 'dwc:collectionCode',
      providers: ['idb', 'gbif'],
    },
    {
      name: 'publishing_org_key',
      key: 'gbif:publishingOrgKey',
      providers: ['gbif'],
    },
  ]
    .map(({ name, key, providers }) => [
      name,
      providers
        .map((provider) =>
          extractField(response.occurrence_info, provider, key)
        )
        .find((value) => value),
    ])
    .filter(
      (entry): entry is [string, string] =>
        typeof entry[0] !== 'undefined' && typeof entry[1] !== 'undefined'
    );
  const statsQueryString = statsPageParameters
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');
  const statsContainer = document.getElementById('stats');
  if (!statsContainer) throw new Error('Unable to find the stats container');
  if (statsQueryString.length === 0) statsContainer.remove();
  else {
    const parameters = Object.fromEntries(statsPageParameters);
    const paragraph = statsContainer.getElementsByTagName('p')[0];
    paragraph.textContent = [
      'Distribution maps of all species in the ',
      `${parameters.collection_code} collection and`,
      `${parameters.institution_code} institution are available `,
    ].join('');
    paragraph.innerHTML += `<a
      href="/api/v1/stats/?${statsQueryString}"
    >here</a>.`;
  }
}

type LifemapperResponse = IR<
  {
    'internal:provider': { readonly code: string };
  } & IR<string>
>;

const extractField = (
  responses: RA<LifemapperResponse>,
  aggregator: string,
  field: string
): string | undefined =>
  responses.find(
    (response) => response['internal:provider']?.code === aggregator
  )?.[field] as string | undefined;

type LifemapperMapResponse = {
  readonly errors: IR<IR<string> | string>;
  // eslint-disable-next-line @typescript-eslint/naming-convention
  readonly occurrence_info: RA<LifemapperResponse>;
  // eslint-disable-next-line @typescript-eslint/naming-convention
  readonly name_info: RA<LifemapperResponse>;
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
};

async function drawMap(
  response: LifemapperMapResponse,
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

function getGbifLayers(taxonKey: string | undefined): RA<AggregatorLayer> {
  if (typeof taxonKey === 'undefined') return [];
  return [
    [
      {
        default: isOverlayDefault('gbif', true),
        label: `GBIF ${legendGradient('#ee0', '#d11')}`,
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
