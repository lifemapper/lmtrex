import '../../css/table.css';

import React from 'react';

import type { Component, IR, RA } from '../config';
import frontEndText from '../localization/frontend';
import type { BrokerRecord } from './entry';
import { mapFields } from './fieldMapper';
import { Response } from './formatTable';
import { extractField } from './utils';

export function SyftoriumLink({
  occurrence,
}: {
  occurrence: RA<BrokerRecord>;
}): Component | null {
  const fields = [
    {
      source: occurrence,
      aggregator: 'idb',
      field: 'dwc:institutionCode',
      name: 'institution_code',
    },
    {
      source: occurrence,
      aggregator: 'idb',
      field: 'dwc:collectionCode',
      name: 'collection_code',
    },
    {
      source: occurrence,
      aggregator: 'idb',
      field: 'gbif:publishingOrgKey',
      name: 'publishing_org_key',
    },
  ].map(
    ({ source, aggregator, field, name }) =>
      [name, extractField(source, aggregator, field)] as const
  );

  const hashedFields = Object.fromEntries(fields);
  const queryString = fields
    .filter(
      (field): field is [string, string] => typeof field[0] !== 'undefined'
    )
    .map(([name, value]) => `${name}=${value}`)
    .join('&');

  if (fields.some(([_name, value]) => typeof value === 'undefined'))
    // eslint-disable-next-line unicorn/no-null
    return null;

  return (
    <p>
      {frontEndText('syftoriumMessage')(
        hashedFields.institution_code ?? '',
        hashedFields.collection_code ?? ''
      )}{' '}
      <a href={`/stats/?${queryString}`}>here</a>.
    </p>
  );
}

export function Table({
  className = '',
  header,
  children,
}: {
  className?: string;
  header?: Component | RA<Component>;
  children: RA<Component>;
}): Component {
  return (
    <table className={className}>
      {header && (
        <thead>
          <tr>{header}</tr>
        </thead>
      )}
      <tbody>{children}</tbody>
    </table>
  );
}

export function Row({
  header,
  title,
  cells,
  className = '',
}: {
  header: string;
  title?: string;
  cells: RA<Component | string>;
  className?: string;
}) {
  return (
    <tr className={className}>
      <th scope="row" title={title}>
        {header}
      </th>
      {cells.map((column, index) => (
        <td key={index}>{column}</td>
      ))}
    </tr>
  );
}

export function IssuesTable({
  occurrence,
}: {
  occurrence: RA<BrokerRecord>;
}): Component | null {
  const issues = occurrence.filter(
    ({ record }) => Object.keys(record['s2n:issues'] as IR<string>).length > 0
  );
  // eslint-disable-next-line unicorn/no-null
  return issues.length === 0 ? null : (
    <Table className="issues">
      {issues.map(({ provider, record }) => (
        <Row
          key={provider.code}
          header={frontEndText('reportedBy')(provider.label)}
          cells={[
            <ul key="list">
              {Object.entries(record['s2n:issues'] as IR<string>).map(
                ([key, value]) => (
                  <li key={key}>
                    {value} ({key})
                  </li>
                )
              )}
            </ul>,
          ]}
        />
      ))}
    </Table>
  );
}

export function OccurrenceTable({
  occurrence,
}: {
  occurrence: RA<BrokerRecord>;
}): Component {
  const specimenId = extractField(
    occurrence,
    'mopho',
    'mopho:specimen.specimen_id',
    false
  );
  const formattedSpecimenId =
    typeof specimenId === 'undefined'
      ? extractField(occurrence, 'mopho', 's2n:view_url', false)
      : mapFields({
          'mopho:specimen.specimen_id': [specimenId],
        })[0].cells[0];

  const alteredResponse = occurrence
    .filter((record) => record.provider.code !== 'mopho')
    .map((response) => ({
      ...response,
      record: {
        ...response.record,
        'mopho:specimen.specimen_id': formattedSpecimenId,
      },
    }));

  return <Response responses={alteredResponse} />;
}

export function NameTable({ name }: { name: RA<BrokerRecord> }): Component {
  return <Response responses={name} />;
}
