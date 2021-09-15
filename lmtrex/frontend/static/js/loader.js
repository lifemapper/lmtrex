const loader = (task, callback) =>
  task().then((innerHTML) => {
    document.getElementById('content').innerHTML = innerHTML;
    document.body.classList.remove('loading');
    document.getElementById('loader').remove();
    callback?.();
  }).catch((error) => {
    console.error(error);
    document.body.innerHTML = `
      Unexpected error occurred:<br>
      ${error.toString()}
    `;
  });