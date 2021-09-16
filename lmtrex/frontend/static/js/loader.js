const loader = (task, callback) =>
  task()
    .then((innerHTML) => {
      if (typeof innerHTML === 'string')
        document.getElementsByTagName('main')[0].innerHTML = innerHTML;
      document.body.classList.remove('loading');
      document.getElementById('loader').remove();
      callback?.();
    })
    .catch((error) => {
      console.error(error);
      document.body.innerHTML = `
        Unexpected error occurred:<br>
        ${error.toString()}
      `;
    });
