import '../../static/css/main.css';
import '../../static/css/stats.css';

import type { IR, RA } from '../config';
import type L from '../leaflet';
import { showMap } from '../leafletUtils';
import { getQueryParameter, loader } from '../utils';
import {
  changeCollectionMap,
  getCollectionMapData,
  getInstitutionMapMeta,
} from './collectionStats';

const reGuid = /^\w{8}-(\w{4}-){3}\w{12}$/;
const isGuid = (guid: string): boolean => reGuid.exec(guid) !== null;

const institutionCode = getQueryParameter(
  'institution_code',
  (value) => value.length > 0
);
const publishingOrgKey = getQueryParameter('publishing_org_key', isGuid);
let datasetKey = getQueryParameter('dataset_key', isGuid);
let institutionMap: L.Map | undefined = undefined;
const institutionMapContainer = document.querySelector(
  '#institution-distribution .leaflet-map'
);
let collectionMap: L.Map | undefined = undefined;
const collectionMapContainer = document.querySelector(
  '#collection-distribution .leaflet-map'
);

if (!institutionMapContainer || !collectionMapContainer)
  throw new Error('Unable to find mind containers');

const fetchDataSets = async (): Promise<IR<string>> =>
  publishingOrgKey
    ? fetch(
        `https://api.gbif.org/v1/dataset/search/?publishingOrg=${publishingOrgKey}`
      )
        .then(async (result) => result.json())
        .then(
          ({
            results,
          }: {
            readonly results: RA<{
              readonly key: string;
              readonly title: string;
            }>;
          }) =>
            Object.fromEntries(
              results.map((result) => [result.key, result.title])
            )
        )
    : {};

loader(
  async () =>
    Promise.all([
      publishingOrgKey
        ? getInstitutionMapMeta(publishingOrgKey).then((mapData) => {
            institutionMap = showMap(
              institutionMapContainer as HTMLElement,
              'institution'
            )[0];
            changeCollectionMap(
              mapData,
              { publishingOrg: publishingOrgKey },
              institutionMapContainer as HTMLElement,
              institutionMap
            );
          })
        : Promise.resolve(),
      fetchDataSets().then((datasets) => {
        if (Object.keys(datasets).length === 0) return;
        if (!(datasetKey in datasets)) datasetKey = Object.keys(datasets)[0];
        populateDataSetList(datasets, datasetKey);
        collectionMap = showMap(
          collectionMapContainer as HTMLElement,
          'collection'
        )[0];
        return changeCollection(datasetKey);
      }),
    ]),
  () => {
    const header = document.querySelector('#institution-distribution h3');
    if (!header) throw new Error('Unable to find map header');
    header.textContent = `
      Geographic distribution of all species from ${institutionCode} based on
      GBIF`;
    [collectionMap, institutionMap].forEach((map) => map?.invalidateSize());
  }
);

async function changeCollection(collection: string): Promise<void> {
  datasetKey = collection;
  if (!collectionMapContainer) throw new Error('Unable to find the map');
  if (!collectionMap) throw new Error('Collection map is not defined');
  changeCollectionMap(
    await getCollectionMapData(datasetKey),
    { datasetKey },
    collectionMapContainer as HTMLElement,
    collectionMap
  );
  const header = document.querySelector('#collection-distribution h3');
  if (!header) throw new Error('Unable to find map header');
  header.textContent = `
    Geographic distribution of all species in the collection 
    based on GBIF`;
}

function populateDataSetList(
  dataSets: IR<string>,
  currentDataSet: string
): void {
  const listOfCollections = document.querySelector('#change-collection select');
  if (!listOfCollections)
    throw new Error('Unable to find the list of datasets');
  listOfCollections.innerHTML = Object.entries(dataSets)
    .map(
      ([key, label]) =>
        `<option
      value="${key}"
      ${key === currentDataSet ? 'selected' : ''}
    >${label}</option>`
    )
    .join('');
  listOfCollections.addEventListener('change', async () =>
    changeCollection((listOfCollections as HTMLSelectElement).value)
  );
}
