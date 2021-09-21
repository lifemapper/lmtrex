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
              (grayscale = layerGroup === 'baseLayer') =>
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

type ViewRecordAction = Action<'ViewRecordAction', { index: number }>;

export type OutgoingMessage =
  | LoadedAction
  | GetPinInfoAction
  | ViewRecordAction;

let markers: RA<MarkerGroups> | undefined;
let localities: RA<LocalityData> | undefined;
const fetchedMarkers = new Set<number>();

export const dispatch = generateDispatch<IncomingMessageExtended>({
  BasicInformationAction: ({ leafletLayers }) => {
    updateLeafletTileServers(parseLayersFromJson(leafletLayers));
  },
  async LocalOccurrencesAction({ localityData, state: { sendMessage } }) {
    localities = localityData;
    const [leafletMap, layerGroup] = await getMap();
    markers = localityData.map((localityData, index) =>
      getMarkersFromLocalityData({
        localityData,
        markerClickCallback() {
          if (fetchedMarkers.has(index)) return;
          sendMessage({
            type: 'GetPinInfoAction',
            index,
          });
        },
        index,
      })
    );
    addMarkersToMap(leafletMap, layerGroup, markers);
  },
  PointDataAction({ index, localityData }) {
    if (!Array.isArray(markers) || !localities)
      throw new Error("Markers aren't loaded");
    const formattedLocality = formatLocalityData(localityData, index, true);
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
  readonly fetchMoreData: () => Promise<LocalityData | false>;
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
    localityData: RA<LocalityData>;
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
  };
};
