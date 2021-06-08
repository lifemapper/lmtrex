document.body.addEventListener('click', (event) => {

  const dictionaryLabel = event.target.closest('.dictionary-label');
  if (dictionaryLabel === null){
    const collapsed = event.target.closest('.collapsed');
    if (collapsed !== null)
      collapsed.classList.toggle('collapsed');
  }
  else
    dictionaryLabel.parentElement.classList.toggle('collapsed');

});