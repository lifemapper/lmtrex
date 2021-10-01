import React from 'react';

import type { Component } from '../config';

export function Section({
  anchor,
  label,
  children,
}: {
  readonly anchor: string;
  readonly label: string;
  readonly children: Component | undefined;
}): Component | null {
  // eslint-disable-next-line unicorn/no-null
  return typeof children === 'undefined' ? null : (
    <section id={anchor}>
      <h3>{label}</h3>
      {children}
    </section>
  );
}
