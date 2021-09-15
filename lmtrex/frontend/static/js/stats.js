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
  (value)=>value.length>0
);

loader(
  ()=>Promise.resolve(document.getElementById('content').innerHTML),
  ()=>{
    showCollectionStats(publishingOrgKey, document.querySelector('#institution-distribution .leaflet-map'));
    document.querySelector('#institution-distribution h3').innerText
      = `Distribution of ${institutionCode} occurrences`;
    document.querySelector('#collection-distribution h3').innerText
      = `Distribution of ${collectionCode} occurrences`;
  }
);