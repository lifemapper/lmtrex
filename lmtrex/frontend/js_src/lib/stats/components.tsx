import * as React from 'react';

import { useLeaflet } from '../components/leaflet';
import type { Component, IR } from '../config';
import { leafletTileServers } from '../config';
import L from '../leaflet';
import statsText from '../localization/stats';
import type { GbifMapData } from './utils';

export function GbifMap({
  mapOptions,
  getMapData,
}: {
  mapOptions: IR<unknown>;
  getMapData: () => Promise<GbifMapData>;
}): Component {
  const mapContainer = React.useRef<HTMLDivElement | null>(null);
  const [leafletMap] = useLeaflet({
    mapContainer: mapContainer.current,
  });

  const [mapData, setMapData] = React.useState<
    GbifMapData | 'error' | 'loading' | undefined
  >(undefined);

  const [minValue, setMinValue] = React.useState<number | undefined>(undefined);
  const [maxValue, setMaxValue] = React.useState<number | undefined>(undefined);
  const hasYears =
    typeof minValue !== 'undefined' && typeof maxValue !== 'undefined';

  React.useEffect(() => {
    getMapData()
      .then((mapData) => {
        setMapData(mapData);
        if (
          typeof minValue === 'undefined' ||
          typeof maxValue === 'undefined'
        ) {
          setMinValue(
            Math.round(
              (mapData.minYear ?? 0) +
                ((mapData.maxYear ?? 0) - (mapData.minYear ?? 0)) *
                  defaultSliderPosition
            )
          );
          setMaxValue(mapData.maxYear);
        }
      })
      .catch((error) => {
        console.error(error);
        setMapData('error');
      });
  }, [mapOptions]);

  const overlay = React.useRef<L.Layer | undefined>(undefined);
  React.useEffect(() => {
    if (typeof leafletMap === 'undefined') return;
    if (overlay.current) leafletMap.removeLayer(overlay.current);
    overlay.current = L.tileLayer(
      'https://api.gbif.org/v2/map/occurrence/{source}/{z}/{x}/{y}{format}?{params}',
      {
        attribution: '',
        source: 'density',
        format: '@1x.png',
        params: Object.entries({
          srs: 'EPSG:3857',
          style: 'classic.poly',
          bin: 'hex',
          ...(hasYears ? { year: `${minValue ?? ''},${maxValue ?? ''}` } : {}),
          ...mapOptions,
        })
          .map(([key, value]) => `${key}=${value}`)
          .join('&'),
      }
    );
    overlay.current.addTo(leafletMap);
    const labelsLayer = Object.values(leafletTileServers.overlays)[0]();
    labelsLayer.bringToFront();
  }, [leafletMap, minValue, maxValue]);

  return typeof mapData === 'object' || mapData === 'loading' ? (
    <>
      <YearSlider
        minYear={typeof mapData === 'object' ? mapData.minYear : undefined}
        maxYear={typeof mapData === 'object' ? mapData.maxYear : undefined}
        minValue={minValue ?? 0}
        maxValue={maxValue ?? 0}
        onMinValueChange={setMinValue}
        onMaxValueChange={setMaxValue}
      />
      <div className="leaflet-map-container">
        <div className="leaflet-map" ref={mapContainer} />
      </div>
    </>
  ) : mapData === 'error' ? (
    <p className="alert alert-error" role="alert">
      {statsText('noMapForInstitution')}
    </p>
  ) : undefined;
}

const defaultSliderPosition = 0.4;

export function YearSlider({
  minYear,
  maxYear,
  minValue,
  maxValue,
  onMinValueChange: handleMinValueChange,
  onMaxValueChange: handleMaxValueChange,
}: {
  minYear: number | undefined;
  maxYear: number | undefined;
  minValue: number;
  maxValue: number;
  onMinValueChange: (min: number) => void;
  onMaxValueChange: (max: number) => void;
}): Component {
  function handleMinChange({
    target,
  }: React.ChangeEvent<HTMLInputElement>): void {
    const minValue = Number.parseInt(target.value);
    handleMinValueChange(Math.min(minValue, maxValue));
    handleMaxValueChange(Math.max(minValue, maxValue));
  }

  function handleMaxChange({
    target,
  }: React.ChangeEvent<HTMLInputElement>): void {
    const maxValue = Number.parseInt(target.value);
    handleMinValueChange(Math.min(minValue, maxValue));
    handleMaxValueChange(Math.max(minValue, maxValue));
  }

  const isDisabled =
    typeof minYear === 'undefined' || typeof maxYear === 'undefined';

  return (
    <p>
      Showing occurrences collected between these years:
      <br />
      <span className="slider">
        <input
          type="number"
          className="min"
          aria-label="Start year"
          min={minYear}
          max={maxYear}
          disabled={isDisabled}
          onChange={handleMinChange}
        />
        <span className="slider-inputs" aria-hidden="true">
          <input
            type="range"
            className="max"
            min={minYear}
            max={maxYear}
            disabled={isDisabled}
            onChange={handleMaxChange}
          />
          <input
            type="range"
            className="min"
            min={minYear}
            max={maxYear}
            disabled={isDisabled}
            onChange={handleMinChange}
          />
        </span>
        <input
          type="number"
          className="max"
          aria-label="End year"
          min={minYear}
          max={maxYear}
          disabled={isDisabled}
          onChange={handleMaxChange}
        />
      </span>
    </p>
  );
}
