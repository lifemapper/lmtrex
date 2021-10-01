import type { State } from 'typesafe-reducer';
import { generateReducer } from 'typesafe-reducer';

import type { IR, RA, RR } from '../config';
import type { States } from './leafletState';
import type {
  LocalityData,
  OccurrenceData,
  OutgoingMessage,
} from './occurrence';

type BasicInformationAction = State<
  'BasicInformationAction',
  {
    systemInfo: IR<unknown>;
    leafletLayers: RR<
      'baseMaps' | 'overlays',
      IR<{
        endpoint: string;
        serverType: 'tileServer' | 'wms';
        layerOptions: IR<unknown>;
      }>
    >;
  }
>;

type LocalOccurrencesAction = State<
  'LocalOccurrencesAction',
  {
    occurrences: RA<OccurrenceData>;
  }
>;

type PointDataAction = State<
  'PointDataAction',
  {
    index: number;
    localityData: LocalityData;
  }
>;

export type IncomingMessage =
  | BasicInformationAction
  | LocalOccurrencesAction
  | PointDataAction;

type IncomingMessageExtended = IncomingMessage & {
  state: {
    readonly sendMessage: (message: OutgoingMessage) => void;
    readonly origin: string;
  };
};

export type Actions = IncomingMessage;

export const reducer = generateReducer<States, Actions>({
  BasicInformationAction: ({ action: { leafletLayers }, state }) => ({
    ...state,
    customLeafletLayers: leafletLayers,
  }),
  LocalOccurrencesAction: ({ action: { occurrences }, state }) => ({
    ...state,
    occurrencePoints: occurrences,
  }),
  PointDataAction: ({ action: { localityData, index }, state }) => ({
    ...state,
    extendedOccurrencePoints: {
      ...state.extendedOccurrencePoints,
      [index]: localityData,
    },
  }),
});
