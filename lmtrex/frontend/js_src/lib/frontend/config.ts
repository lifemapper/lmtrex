import type { RA, RR } from '../config';

export type LifemapperLayerTypes = 'raster';

export const lifemapperLayerVariations: RR<
  LifemapperLayerTypes,
  { layerLabel: string; transparent: boolean; opacity?: number }
> = {
  raster: {
    layerLabel: 'Lifemapper Distribution Model',
    transparent: true,
  },
};

// These fields should be present for locality to be mappable
export const requiredLocalityColumns: RA<string> = [
  'locality.latitude1',
  'locality.longitude1',
] as const;

export const mappingLocalityColumns: RA<string> = [
  ...requiredLocalityColumns,
  'locality.latitude2',
  'locality.longitude2',
  'locality.latlongtype',
  'locality.latlongaccuracy',
];

export const lifemapperMessagesMeta = {
  errorDetails: {
    className: 'error-details',
    title: 'The following errors were reported by Lifemapper:',
  },
  infoSection: {
    className: 'info-section',
  },
};
