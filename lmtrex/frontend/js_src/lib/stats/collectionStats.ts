import '../../css/slider.css';

import type { IR, RA } from '../config';
import { leafletTileServers } from '../config';
import L from '../leaflet';

type GbifMapData = {
  readonly minYear?: number;
  readonly maxYear?: number;
};

export async function getInstitutionMapMeta(
  publishingOrgKey: string
): Promise<GbifMapData> {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?publishingOrg=${publishingOrgKey}`
  );
  return request.json();
}

export async function getCollectionMapData(
  datasetKey: string
): Promise<GbifMapData> {
  const request = await fetch(
    `https://api.gbif.org/v2/map/occurrence/density/capabilities.json?datasetKey=${datasetKey}`
  );
  return request.json();
}

let overlay: L.Layer | undefined;

const sliderChangeHandler =
  (
    inputs: RA<HTMLInputElement>,
    redrawMap: (minYear: number, maxYear: number) => void
  ) =>
  (event: HTMLElementEventMap['change']) => {
    if (!event.target) throw new Error('Invalid event target');
    const element = event.target as HTMLInputElement;

    const boundaries = Object.fromEntries(
      inputs
        .filter((input) => input.type === element.type)
        .map((input) => [
          input.classList.contains('min') ? 'min' : 'max',
          input.value,
        ])
    );

    if (element.type === 'range' && boundaries.min > boundaries.max) {
      if (element.classList.contains('min')) {
        boundaries.max = boundaries.min;
        const input = inputs.find(
          (input) => input.type === element.type && input !== event.target
        );
        if (!input) throw new Error('Unable to find the accompanying input');
        input.value = boundaries.max;
      } else {
        boundaries.min = boundaries.max;
        element.value = boundaries.max;
      }
    }

    inputs
      .filter((input) => input.type !== element.type)
      .forEach((input) => {
        input.value =
          boundaries[input.classList.contains('min') ? 'min' : 'max'];
      });

    redrawMap(Number.parseInt(boundaries.min), Number.parseInt(boundaries.max));
  };

const defaultSliderPosition = 0.4;

export function changeCollectionMap(
  mapData: GbifMapData,
  mapOptions: IR<unknown>,
  mapContainer: HTMLElement,
  map: L.Map
): void {
  if (!mapContainer.parentElement)
    throw new Error('Map does not have a parent');

  const slider = mapContainer.parentElement.getElementsByClassName('slider')[0];
  const inputs = Array.from(slider.getElementsByTagName('input'));

  const hasYears = 'minYear' in mapData && 'maxYear' in mapData;
  const { minYear, maxYear } = mapData;
  const defaultMinValue = Math.round(
    (minYear ?? 0) + ((maxYear ?? 0) - (minYear ?? 0)) * defaultSliderPosition
  );
  const defaultMaxValue = maxYear ?? 0;
  inputs.forEach((input) => {
    input.min = `${minYear ?? '0'}`;
    input.max = `${maxYear ?? '0'}`;
    const value = input.classList.contains('min')
      ? defaultMinValue
      : defaultMaxValue;
    input.value =
      typeof value === 'undefined' || Number.isNaN(value) ? '' : `${value}`;
    if (hasYears)
      input.addEventListener('change', sliderChangeHandler(inputs, redrawMap));
    else input.disabled = true;
  });

  function redrawMap(minYear: number, maxYear: number): void {
    if (overlay) map.removeLayer(overlay);
    overlay = L.tileLayer(
      'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
      {
        attribution: '',
        // @ts-expect-error
        source: 'density',
        format: '@1x.png',
        params: Object.entries({
          srs: 'EPSG:3857',
          style: 'classic.poly',
          bin: 'hex',
          ...(hasYears ? { year: `${minYear},${maxYear}` } : {}),
          ...mapOptions,
        })
          .map(([key, value]) => `${key}=${value}`)
          .join('&'),
      }
    );
    overlay.addTo(map);
    const labelsLayer = Object.values(leafletTileServers.overlays)[0]();
    labelsLayer.bringToFront();
  }

  redrawMap(defaultMinValue, defaultMaxValue);
}
