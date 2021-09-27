const reGuid = /^\w{8}-(\w{4}-){3}\w{12}$/;
const isGuid = (guid) => guid.match(reGuid) !== null;

const institutionCode = getQueryParameter(
  'institution_code',
  (value) => value.length > 0
);
const collectionCode = getQueryParameter(
  'collection_code',
  (value) => value.length > 0
);
const publishingOrgKey = getQueryParameter('publishing_org_key', isGuid);
let datasetKey = getQueryParameter('dataset_key', isGuid);
let dataSets = undefined;
let institutionMap = undefined;
let institutionMapContainer = document.querySelector(
  '#institution-distribution .leaflet-map'
);
let collectionMap = undefined;
let collectionMapContainer = document.querySelector(
  '#collection-distribution .leaflet-map'
);

const fetchDataSets = async () =>
  publishingOrgKey
    ? fetch(
        `https://api.gbif.org/v1/dataset/search/?publishingOrg=${publishingOrgKey}`
      )
        .then((result) => result.json())
        .then(({ results }) =>
          Object.fromEntries(
            results.map((result) => [result['key'], result['title']])
          )
        )
    : {};

loader(
  () =>
    Promise.all([
      publishingOrgKey
        ? getInstitutionMapMeta(publishingOrgKey).then((mapData) => {
            institutionMap = showStatsMap(institutionMapContainer);
            changeCollectionMap(
              mapData,
              { publishingOrg: publishingOrgKey },
              institutionMapContainer,
              institutionMap
            );
          })
        : Promise.resolve(),
      fetchDataSets().then(async (datasets) => {
        dataSets = datasets;
        if (Object.keys(datasets).length === 0) return;
        if (!(datasetKey in datasets)) datasetKey = Object.keys(datasets)[0];
        populateDataSetList(datasets, datasetKey);
        collectionMap = await showStatsMap(collectionMapContainer);
        changeCollection(datasetKey);
      }),
    ]),
  () => {
    document.querySelector('#institution-distribution h3').textContent = `
    Geographic distribution of all species from ${institutionCode} based on
    GBIF`;
    [collectionMap, institutionMap].forEach((map) => map.invalidateSize());
  }
);

async function changeCollection(collection) {
  datasetKey = collection;
  changeCollectionMap(
    await getCollectionMapData(datasetKey),
    { datasetKey },
    collectionMapContainer,
    collectionMap
  );
  document.querySelector('#collection-distribution h3').textContent = `
    Geographic distribution of all species in the collection 
    based on GBIF`;
}

function populateDataSetList(dataSets, currentDataSet) {
  const listOfCollections = document.querySelector('#change-collection select');
  listOfCollections.innerHTML = Object.entries(dataSets)
    .map(
      ([key, label]) =>
        `<option
      value="${key}"
      ${key === currentDataSet ? 'selected' : ''}
    >${label}</option>`
    )
    .join('');
  listOfCollections.addEventListener('change', () =>
    changeCollection(listOfCollections.value)
  );
}
