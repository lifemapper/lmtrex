import '../../css/main.css';

import React from 'react';
import ReactDOM from 'react-dom';

import ErrorBoundary from './errorBoundary';

export function app(Component: React.Element): void {
  ReactDOM.render(
    <React.StrictMode>
      <ErrorBoundary>
        <Component />
      </ErrorBoundary>
    </React.StrictMode>,
    document.getElementById('root')
  );
}
