const reGuid = /^\w{8}-(\w{4}-){3}\w{12}$/;
const isGuid = (guid)=>guid.match(reGuid) !== null;

const institutionCode = getQueryParameter(
  'institution_code',
  (value)=>value.length>0
);
const collectionCode = getQueryParameter(
  'collection_code',
  (value)=>value.length>0
);
const publishingOrgKey = getQueryParameter(
  'publishing_org_key',
  isGuid
);
let datasetKey = getQueryParameter(
  'dataset_key',
  isGuid
);
let collectionMapDestructor = undefined;
let dataSets = undefined;

const fetchDataSets = async ()=>
  publishingOrgKey ?
     fetch(
      `https://api.gbif.org/v1/dataset/search/?publishingOrg=${publishingOrgKey}`)
      .then(result=>result.json())
     .then(({results})=>Object.fromEntries(
       results.map(result=>
         [result['key'],result['title']])
       )
     ) :
    {};

loader(()=>Promise.all([
  publishingOrgKey
    ? getInstitutionMapMeta(publishingOrgKey).then(mapData=>
        showStatsMap(
          mapData,
          {publishingOrg: publishingOrgKey},
          document.querySelector('#institution-distribution .leaflet-map')
        )
      )
    : Promise.resolve(),
  fetchDataSets().then(async (datasets)=>{
    dataSets = datasets;
    if(Object.keys(datasets).length === 0)
      return;
    if(!(datasetKey in datasets))
      datasetKey = Object.keys(datasets)[0];
    populateDataSetList(datasets, datasetKey);
    return changeCollection(datasetKey);
  })
]),()=>{
  document.querySelector('#institution-distribution h3').textContent = `
    Geographic distribution of all species from ${institutionCode} based on
    GBIF`;
  activeMaps.forEach((map)=>map.invalidateSize());
});

async function changeCollection(collection){
  datasetKey = collection;
  if(collectionMapDestructor)
    collectionMapDestructor();
  collectionMapDestructor = await showStatsMap(
    await getCollectionMapData(datasetKey),
    {datasetKey},
    document.querySelector('#collection-distribution .leaflet-map')
  );
  document.querySelector('#collection-distribution h3').textContent = `
    Geographic distribution of all species in the "${dataSets[collection]}"
    collection based on GBIF`;
}

function populateDataSetList(dataSets, currentDataSet){
  const listOfCollections =
    document.querySelector('#change-collection select');
  listOfCollections.innerHTML = Object.entries(dataSets).map(([key, label])=>
    `<option
      value="${key}"
      ${key===currentDataSet ? 'selected': ''}
    >${label}</option>`
  ).join('');
  listOfCollections.addEventListener(
    'change',
    ()=>changeCollection(listOfCollections.value)
  );
}