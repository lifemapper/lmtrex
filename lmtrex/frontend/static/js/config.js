const lifemapperLayerVariations = {
  raster: {
    layerLabel: 'Projection',
    transparent: true,
  },
  vector: {
    layerLabel: 'Occurrence Points',
    transparent: true,
  },
};

const coMapTileServers = [
  {
    transparent: false,
    layerLabel: 'Satellite Map (ESRI)',
  },
  {
    transparent: true,
    layerLabel: 'Labels and boundaries',
  },
];

const leafletTileServers = {
  baseMaps: {
    'Satellite Map (ESRI)': () =>
      L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
          className: 'grayscale',
          attribution:
            'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        }
      ),
  },
  overlays: {
    'Labels and boundaries': () =>
      L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
        {
          attribution:
            'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community\n',
          className: 'darkened',
        }
      ),
  },
};

const lifemapperMessagesMeta = {
  errorDetails: {
    className: 'error-details',
    title: 'The following errors were reported by Lifemapper:',
  },
  infoSection: {
    className: 'info-section',
    title: 'Projection Details:',
  },
};
