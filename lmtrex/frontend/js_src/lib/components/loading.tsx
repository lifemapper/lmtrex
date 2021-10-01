import React from 'react';

import type { Component } from '../config';

const tagLines = [
  'Searching',
  'Running',
  'Exploring',
  'Hustling',
  'Gathering',
  'Hacking',
  'Pursuing',
  'Going after',
  'Assembling',
  'Fetching',
  'Grabbing',
  'Loading',
];

const getTagLine = (): string =>
  tagLines[Math.floor(Math.random() * tagLines.length)];

export function Loading(): Component {
  // Don't regenerate the tagline on reRenders
  const [tagLine] = React.useState(getTagLine());

  return (
    <div id="loader">
      <div>
        <span />
        <div className="logo-container">
          <div className="logo">
            <img
              src="/static/img/specify_network_square.svg"
              alt="Specify Network"
            />
          </div>
        </div>
        <h1>{tagLine}</h1>
      </div>
    </div>
  );
}
