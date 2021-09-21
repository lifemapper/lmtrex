import type { Action, State } from 'typesafe-reducer';
import { generateDispatch } from 'typesafe-reducer';

import type { IR, leafletTileServers, RA, RR } from '../config';
import { updateLeafletTileServers } from '../config';
import L from '../leaflet';
import { getMap } from './entry';
import type { MarkerGroups } from './leafletOccurrence';
import {
  addMarkersToMap,
  formatLocalityData,
  getMarkersFromLocalityData,
} from './leafletOccurrence';

const parseLayersFromJson = (
  json: IR<
    IR<{
      readonly endpoint: string;
      readonly serverType: 'wms' | 'tileServer';
      readonly layerOptions: IR<unknown>;
    }>
  >
) =>
  Object.fromEntries(
    Object.entries(json).map(([layerGroup, layers]) => [
      layerGroup,
      Object.fromEntries(
        Object.entries(layers).map(
          ([layerName, { endpoint, serverType, layerOptions }]) => {
            const layerClass =
              serverType === 'wms' ? L.tileLayer.wms : L.tileLayer;

            return [
              layerName,
              (
                grayscale = layerGroup === 'baseMaps' &&
                  layerName.startsWith('Satelite')
              ) =>
                layerClass(endpoint, {
                  className: grayscale ? 'grayscale' : '',
                  ...layerOptions,
                }),
            ];
          }
        )
      ),
    ])
  ) as typeof leafletTileServers;

type LoadedAction = Action<'LoadedAction', { version: string }>;

type GetPinInfoAction = Action<'GetPinInfoAction', { index: number }>;

export type OutgoingMessage = LoadedAction | GetPinInfoAction;

let markers: RA<MarkerGroups> | undefined;
let occurrences: RA<OccurrenceData> | undefined;
const fetchedMarkers = new Set<number>();

export const dispatch = generateDispatch<IncomingMessageExtended>({
  BasicInformationAction: ({ leafletLayers }) => {
    updateLeafletTileServers(parseLayersFromJson(leafletLayers));
  },
  async LocalOccurrencesAction({
    occurrences: occurrencesData,
    state: { sendMessage, origin },
  }) {
    occurrences = occurrencesData;
    const [leafletMap, layerGroup] = await getMap();
    markers = occurrencesData.map(
      ({ localityData, collectionObjectId }, index) =>
        getMarkersFromLocalityData({
          localityData,
          markerClickCallback() {
            if (fetchedMarkers.has(index)) return;
            sendMessage({
              type: 'GetPinInfoAction',
              index,
            });
          },
          viewUrl: `${origin}/specify/view/collectionobject/${collectionObjectId}/`,
        })
    );
    addMarkersToMap(leafletMap, layerGroup, markers);
  },
  PointDataAction({ index, localityData, state: { origin } }) {
    if (!markers || !occurrences) throw new Error("Markers aren't loaded");
    const formattedLocality = formatLocalityData(
      localityData,
      `${origin}/specify/view/collectionobject/${occurrences[index].collectionObjectId}/`,
      true
    );
    Object.values(markers[index])
      .flat()
      .map((marker) => marker.getPopup()?.setContent(formattedLocality));
  },
});

export type Field<T> = { readonly headerName: string; readonly value: T };

export type LocalityData = IR<Field<string | number>>;

export type OccurrenceData = {
  readonly collectionObjectId: number;
  readonly collectingEventId: number;
  readonly localityId: number;
  readonly localityData: LocalityData;
};

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
