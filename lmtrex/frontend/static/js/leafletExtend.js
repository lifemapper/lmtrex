/* Create a "full screen" button */
L.Control.FullScreen = L.Control.extend({
  onAdd(map) {
    const control = L.DomUtil.create('span');
    control.classList.add('leaflet-full-screen-toggle');
    control.innerHTML=`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="white">
        <path d="M0 0H7V2H2V7H0Z"/>
        <path d="M13 0H20V7H18V2H13Z"/>
        <path d="M20 20H13V18H18V13H20Z"/>
        <path d="M0 13H2V18H7V20H0Z"/>
      </svg>`;

    L.DomEvent.on(control, 'click', (event) => {
      L.DomEvent.stopPropagation(event);
      L.DomEvent.preventDefault(event);
      const isFullScreen = map._container.classList.contains('leaflet-map-full-screen');
      if(isFullScreen) {
        map._container.classList.remove('leaflet-map-full-screen');
        document.body.classList.remove('full-screen');
      }
      else {
        map._container.classList.add('leaflet-map-full-screen');
        document.body.classList.add('full-screen');
      }
    });

    this.control = control;

    return control;
  },

  onRemove() {
    // @ts-expect-error Somebody did a really poor job of typing Leaflet
    L.DomEvent.off(this.control);
  },
});

/* Adds a printer icon to print the map */
L.Control.PrintMap = L.Control.extend({
  onAdd() {
    const button = L.DomUtil.create('span');
    button.classList.add('leaflet-print-map');
    button.textContent = '🖨️';

    L.DomEvent.on(button, 'click', (event) => {
      L.DomEvent.stopPropagation(event);
      L.DomEvent.preventDefault(event);
      window.print();
    });

    this.button = button;

    return button;
  },
  onRemove() {
    // @ts-expect-error Somebody did a really poor job of typing Leaflet
    L.DomEvent.off(this.button);
  },
});


function addFullScreenButton(map) {
  new L.Control.FullScreen({ position: 'topleft' }).addTo(map);
}

function addPrintMapButton(map) {
  new L.Control.PrintMap({ position: 'topleft' }).addTo(map);
}
