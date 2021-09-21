import type { LayersControlEventHandlerFn } from 'leaflet';

import * as cache from './cache';
import type { RA } from './config';
import {
  DEFAULT_CENTER,
  DEFAULT_ZOOM,
  leafletTileServers,
  preferredBaseLayer,
} from './config';
import L, { addFullScreenButton, addPrintMapButton } from './leaflet';

export function rememberSelectedBaseLayers(
  map: L.Map,
  layerGroup: L.Control.Layers,
  cacheName: string
): void {
  const layers = leafletTileServers.baseMaps;
  const currentLayer = cache.get('leafletBaseLayer', cacheName);
  let layerLabel =
    currentLayer !== false && currentLayer in layers
      ? currentLayer
      : preferredBaseLayer;
  if (typeof layers[layerLabel] === 'undefined')
    layerLabel = Object.keys(layers)[0];
  const baseLayer = layers[layerLabel]();
  baseLayer.addTo(map);

  Object.entries(layers).forEach(([label, layer]) =>
    layerGroup.addBaseLayer(label === layerLabel ? baseLayer : layer(), label)
  );

  map.on('baselayerchange', ({ name }: { readonly name: string }) => {
    cache.set('leafletBaseLayer', cacheName, name, { overwrite: true });
  });
}

export const isOverlayDefault = (
  layerName: string,
  defaultValue: boolean
): boolean =>
  cache.get('leafletOverlays', layerName, {
    defaultValue: defaultValue ?? false,
  });

export function rememberSelectedOverlays(map: L.Map): void {
  const handleOverlayEvent: LayersControlEventHandlerFn = ({ name, type }) =>
    cache.set('leafletOverlays', name, type === 'overlayadd', {
      overwrite: true,
    });

  map.on('overlayadd', handleOverlayEvent);
  map.on('overlayremove', handleOverlayEvent);
}

export const addAggregatorOverlays =
  (leafletMap: L.Map, layerGroup: L.Control.Layers, callback?: () => void) =>
  (layers: RA<AggregatorLayer>) =>
    layers.forEach(([options, layer]) => {
      callback?.();
      layerGroup.addOverlay(layer, options.label);
      if (options.default) layer.addTo(leafletMap);
    });

export const legendPoint = (color: string): string => `<span
  aria-hidden="true"
  style="--color: ${color}"
  class="leaflet-legend-point"
></span>`;

export const legendGradient = (
  leftColor: string,
  rightColor: string
): string => `<span
  aria-hidden="true"
  style="--left-color: ${leftColor}; --right-color: ${rightColor}"
  class="leaflet-legend-gradient"
></span>`;

export type AggregatorLayer = Readonly<
  [
    {
      default?: boolean;
      label: string;
    },
    L.TileLayer | L.TileLayer.WMS | L.FeatureGroup
  ]
>;

export function showMap(
  mapContainer: HTMLElement,
  cacheName: string
): Readonly<[L.Map, L.Control.Layers]> {
  mapContainer.style.display = '';

  const map = L.map(mapContainer, {
    maxZoom: 23,
  }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

  // @ts-expect-error GestureHandling plugin has no type definitions
  map.gestureHandling.enable();

  const layerGroup = L.control.layers({}, {});
  layerGroup.addTo(map);

  addFullScreenButton(map);
  addPrintMapButton(map);
  rememberSelectedBaseLayers(map, layerGroup, cacheName);
  rememberSelectedOverlays(map);

  const addOverlays = addAggregatorOverlays(map, layerGroup);
  addOverlays(
    Object.entries(leafletTileServers.overlays).map(([label, layer]) => [
      { label, default: isOverlayDefault(label, true) },
      layer(),
    ])
  );

  return [map, layerGroup];
}
