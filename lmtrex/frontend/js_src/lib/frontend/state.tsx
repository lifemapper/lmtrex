import React from 'react';
import type { State } from 'typesafe-reducer';
import { generateReducer } from 'typesafe-reducer';

import { Section } from '../components/common';
import { ErrorMessage } from '../components/errorBoundary';
import { Loading } from '../components/loading';
import type { Component, RA } from '../config';
import commonText from '../localization/common';
import frontEndText from '../localization/frontend';
import {
  IssuesTable,
  NameTable,
  OccurrenceTable,
  SyftoriumLink,
} from './components';
import type { BrokerRecord } from './entry';
import { LeafletContainer } from './leaflet';
import { extractField } from './utils';

export type MainState = State<
  'MainState',
  {
    occurrence: RA<BrokerRecord> | undefined | 'loading';
    name: RA<BrokerRecord> | undefined | 'invalid' | 'loading';
  }
>;

export type ErrorState = State<
  'ErrorState',
  {
    title: string;
    message: Component | RA<Component>;
  }
>;

export type States = MainState | ErrorState;

export function ensureMainState(state: States): MainState {
  if (state.type === 'MainState') return state;
  else throw new Error(`Reducer called on ${state.type} state`);
}

export const stateReducer = generateReducer<Component | undefined, States>({
  ErrorState({ action: { title, message } }) {
    return <ErrorMessage title={title}>{message}</ErrorMessage>;
  },
  MainState({ action: { occurrence, name } }) {
    if (typeof occurrence === 'undefined' && typeof name === 'undefined')
      return (
        <ErrorMessage title={commonText('noDataErrorTitle')}>
          <p>{commonText('noDataErrorMessage')}</p>
        </ErrorMessage>
      );
    else if (
      occurrence === 'loading' ||
      name === 'loading' ||
      name === 'invalid'
    )
      return <Loading />;

    const scientificName =
      typeof name === 'undefined'
        ? undefined
        : extractField(name, 'gbif', 'dwc:scientificName');

    // TODO: go over "show ..." statements
    return (
      <main>
        <header>
          <h1>
            <img src="/static/img/specify_network_long.svg" alt="" />
            <span className="sr-only">{frontEndText('specifyNetwork')}</span>
          </h1>
          <h2>{scientificName ?? frontEndText('scientificNameUnknown')}</h2>
        </header>
        <div className="sections">
          {[
            <Section
              key="issues"
              anchor="issues"
              label={frontEndText('dataQuality')}
            >
              {typeof occurrence === 'object' ? (
                <IssuesTable occurrence={occurrence} />
              ) : undefined}
            </Section>,
            <Section
              key="occ"
              anchor="occ"
              label={frontEndText('collectionObject')}
            >
              {typeof occurrence === 'object' ? (
                <OccurrenceTable occurrence={occurrence} />
              ) : undefined}
            </Section>,
            <Section key="name" anchor="name" label={frontEndText('taxonomy')}>
              {typeof name === 'object' ? <NameTable name={name} /> : undefined}
            </Section>,
            <Section
              key="map"
              anchor="map"
              label={frontEndText('distribution')}
            >
              <LeafletContainer
                scientificName={scientificName}
                occurrence={occurrence}
              />
            </Section>,
            <Section
              key="stats"
              anchor="stats"
              label={frontEndText('syftoriumHeader')}
            >
              {typeof occurrence === 'object' ? (
                <SyftoriumLink occurrence={occurrence} />
              ) : undefined}
            </Section>,
          ].filter(
            (section): section is Component => typeof section === 'object'
          )}
        </div>
      </main>
    );
  },
});
