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

/*
 *Const institutionCode = getQueryParameter(
 *'institution_code',
 *(value) => value.length > 0
 *);
 */
const publishingOrgKey = getQueryParameter('publishing_org_key', isGuid);
let datasetKey = getQueryParameter('dataset_key', isGuid);

let institutionMap: L.Map | undefined = undefined;
let collectionMap: L.Map | undefined = undefined;

const institutionContainer = document.getElementById(
  'institution-distribution'
);
const collectionContainer = document.getElementById('collection-distribution');
const listOfCollectionsContainer = document.getElementById('change-collection');

if (
  !institutionContainer ||
  !collectionContainer ||
  !listOfCollectionsContainer
)
  throw new Error('Unable to find map containers');

const institutionMapContainer =
  institutionContainer.getElementsByClassName('leaflet-map')[0];
const collectionMapContainer =
  collectionContainer.getElementsByClassName('leaflet-map')[0];
const listOfCollections =
  listOfCollectionsContainer.getElementsByTagName('select')[0];

let hasData = true;

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

function noDataMessage(): void {
  document.getElementsByTagName('main')[0].innerHTML = `
    <p class="alert alert-error">Unable to find any data</p>
  `;
  hasData = false;
}

loader(
  async () =>
    Promise.all([
      publishingOrgKey
        ? getInstitutionMapMeta(publishingOrgKey)
            .then((mapData) => {
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
            .catch((error) => {
              console.error(error);
              noDataMessage();
            })
        : Promise.resolve(),
      fetchDataSets()
        .then((datasets) => {
          if (Object.keys(datasets).length === 0) {
            noDataMessage();
            return;
          }
          if (!(datasetKey in datasets)) datasetKey = Object.keys(datasets)[0];
          populateDataSetList(datasets, datasetKey);
          collectionMap = showMap(
            collectionMapContainer as HTMLElement,
            'collection'
          )[0];
          return changeCollection(datasetKey);
        })
        .catch((error) => {
          console.error(error);
          noDataMessage();
        }),
    ]),
  () => {
    if (!hasData) return;
    const header = document.querySelector('#institution-distribution h3');
    if (!header) throw new Error('Unable to find map header');
    header.textContent = `
      Geographic distribution of all digitized specimens for all species for all
      collections at KU based on data in GBIF`;
    [collectionMap, institutionMap].forEach((map) => map?.invalidateSize());
  }
);

async function changeCollection(collection: string): Promise<void> {
  if (!hasData) return;
  datasetKey = collection;
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
    Geographic distribution of all digitized specimen localities for all species
    in the collection based on data in GBIF`;
}

function populateDataSetList(
  dataSets: IR<string>,
  currentDataSet: string
): void {
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
    changeCollection(listOfCollections.value)
  );
}
