import '../static/css/loader.css';

import type { RA } from './config';
import { showMap } from './leafletUtils';

const urlParameters = new URLSearchParams(window.location.search);

export const getQueryParameter = (
  name: string,
  validator: (value: string) => boolean
): string =>
  validator(urlParameters.get(name) ?? '') ? urlParameters.get(name) ?? '' : '';

export const splitJoinedMappingPath = (string: string): RA<string> =>
  string.split('.');

export const loader = async (
  task: () => Promise<string | unknown>,
  callback?: () => void
): Promise<void> =>
  task()
    .then((innerHtml) => {
      if (typeof innerHtml === 'string')
        document.getElementsByTagName('main')[0].innerHTML = innerHtml;
      document.body.classList.remove('loading');
      document.getElementById('loader')?.remove();
      callback?.();
    })
    .catch((error) => {
      console.error(error);
      document.body.innerHTML = `
        Unexpected error occurred:<br>
        ${error.toString()}
      `;
    });

/*
 * A generator of promises that can be resolved even before they are created
 *
 * Usage:
 * const [resolve, getPromise] = inversePromise<boolean>();
 * resolve(false);
 * getPromise().then(console.log)
 */
export function inversePromise<T>(): [
  ((value: T) => void) | undefined,
  () => Promise<T>
] {
  let resolve: ((value: T) => void) | undefined;
  let data: T | undefined;
  let resolved = false;
  const promise: T | Promise<T> = new Promise<T>((resolveValue) => {
    resolve = resolveValue;
  });

  return [
    resolve,
    async () =>
      new Promise<T>(async (resolve) => {
        if (!resolved) data = await promise;
        resolved = true;
        resolve(data);
      }),
  ];
}
