document.body.addEventListener('click', (event) => {

  const dictionaryLabel = event.target.closest('.dictionary-label');
  if (dictionaryLabel !== null){
    dictionaryLabel.parentElement.classList.toggle('collapsed');
    return;
  }
  const collapsed = event.target.closest('.collapsed');
  if (collapsed !== null){
    collapsed.classList.toggle('collapsed');
    return;
  }

  const sectionHeader = event.target.closest('.section-header');
  if(sectionHeader !== null){
    sectionHeader.parentElement.classList.toggle('section-collapsed');
  }

});