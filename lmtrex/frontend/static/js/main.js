document.body.addEventListener('click', (event) => {
  const dictionaryLabel = event.target.closest('.dictionary-label');
  if (dictionaryLabel !== null) {
    dictionaryLabel.parentElement.classList.toggle('collapsed');
    return;
  }
  const collapsed = event.target.closest('.collapsed');
  if (collapsed !== null) collapsed.classList.toggle('collapsed');
});

const urlParams = new URLSearchParams(window.location.search);
const queryString = `?occid=${urlParams.get('occid') ?? ''}&namestr=${
  urlParams.get('namestr') ?? ''
}&loader=false`;
const fetchUrl = `${window.location.origin}${window.location.pathname}${
  queryString}${window.location.hash}`;

fetch(fetchUrl)
  .then((response)=>response.text())
  .then((response)=>{
    document.getElementById('content').innerHTML = response;
    document.body.classList.remove('loading');
    document.getElementById('loader').remove();
    initializeMaps();
  })
  .catch((error) => {
    console.error(error);
    document.body.innerHTML = `
      Unexpected error occurred:<br>
      ${error.toString()}
    `;
  });