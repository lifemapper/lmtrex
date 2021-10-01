import React from 'react';
import type { State } from 'typesafe-reducer';
import { generateReducer } from 'typesafe-reducer';

import type { Component, RA, RR } from '../config';
import { LeafletMap } from './leaflet';
import type { Actions } from './leafletReducer';
import type {
  JsonLeafletLayers,
  LocalityData,
  OccurrenceData,
} from './occurrence';

export type MainState = State<
  'MainState',
  {
    customLeafletLayers: undefined | JsonLeafletLayers;
    occurrencePoints: undefined | RA<OccurrenceData>;
    extendedOccurrencePoints: RR<number, LocalityData>;
  }
>;

export type States = MainState;

export type StateWithOptions = States & {
  options: {
    dispatch: (action: Actions) => void;
    overlays: JsonLeafletLayers;
    layerDetails: RA<Component | string>;
  };
};

export const stateReducer = generateReducer<
  Component | undefined,
  StateWithOptions
>({
  MainState({
    action: {
      customLeafletLayers,
      occurrencePoints,
      extendedOccurrencePoints,
      options: { overlays, layerDetails },
    },
  }) {
    return (
      <>
        {layerDetails.map((value, index) => (
          <p key={index}>{value}</p>
        ))}
        <LeafletMap
          customLeafletLayers={customLeafletLayers}
          occurrencePoints={occurrencePoints}
          extendedOccurrencePoints={extendedOccurrencePoints}
          overlays={overlays}
        />
        ;
      </>
    );
  },
});
