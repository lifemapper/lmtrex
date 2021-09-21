/*
 * Imports Leaflet, adds plugins along with new controls and reexports it
 */

// eslint-disable-next-line simple-import-sort/imports
import L from 'leaflet';

import 'leaflet/dist/leaflet.css';
import '../static/css/leaflet.css';
// Marker Clustering
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';
// Create sub-layers to selectively toggle markers in clusters
import 'leaflet.featuregroup.subgroup';

import { GestureHandling } from 'leaflet-gesture-handling';

import 'leaflet/dist/leaflet.css';
import 'leaflet-gesture-handling/dist/leaflet-gesture-handling.css';

/* This code is needed to properly load the images in the Leaflet's CSS */
// @ts-expect-error
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

L.Map.addInitHook('addHandler', 'gestureHandling', GestureHandling);

/* Create a "full screen" button */
// @ts-expect-error
L.Control.FullScreen = L.Control.extend({
  onAdd(map: Readonly<L.Map>) {
    const control = L.DomUtil.create('span');
    control.classList.add('leaflet-full-screen-toggle');
    control.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="white">
        <path d="M0 0H7V2H2V7H0Z"/>
        <path d="M13 0H20V7H18V2H13Z"/>
        <path d="M20 20H13V18H18V13H20Z"/>
        <path d="M0 13H2V18H7V20H0Z"/>
      </svg>`;

    let scrollTop = 0;
    L.DomEvent.on(control, 'click', (event) => {
      L.DomEvent.stopPropagation(event);
      L.DomEvent.preventDefault(event);

      // @ts-expect-error
      const container = map._container as HTMLElement;
      const isFullScreen = container.classList.contains(
        'leaflet-map-full-screen'
      );
      if (isFullScreen) {
        container.classList.remove('leaflet-map-full-screen');
        document.body.classList.remove('full-screen');
        window.scrollTo({
          left: 0,
          top: scrollTop,
          behavior: 'auto',
        });
        // @ts-expect-error GestureHandling plugin has no type definitions
        map.gestureHandling.enable();
      } else {
        scrollTop = window.scrollY;
        container.classList.add('leaflet-map-full-screen');
        document.body.classList.add('full-screen');
        // @ts-expect-error GestureHandling plugin has no type definitions
        map.gestureHandling.disable();
      }

      map.invalidateSize();
    });

    // @ts-expect-error
    this.control = control;

    return control;
  },

  onRemove() {
    // @ts-expect-error Somebody did a really poor job of typing Leaflet
    L.DomEvent.off(this.img);
  },
});

/* Adds a printer icon to print the map */
// @ts-expect-error
L.Control.PrintMap = L.Control.extend({
  onAdd() {
    const button = L.DomUtil.create('span')!;
    button.classList.add('leaflet-print-map');
    button.textContent = '🖨️';

    L.DomEvent.on(button, 'click', (event) => {
      L.DomEvent.stopPropagation(event);
      L.DomEvent.preventDefault(event);
      window.print();
    });

    // @ts-expect-error
    this.button = button;

    return button;
  },
  onRemove() {
    // @ts-expect-error Somebody did a really poor job of typing Leaflet
    L.DomEvent.off(this.button);
  },
});

export function addFullScreenButton(map: L.Map): void {
  // @ts-expect-error
  new L.Control.FullScreen({ position: 'topleft' }).addTo(map);
}

export function addPrintMapButton(map: L.Map): void {
  // @ts-expect-error
  new L.Control.PrintMap({ position: 'topleft' }).addTo(map);
}

export default L;
