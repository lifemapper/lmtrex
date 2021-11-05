# syntax=docker/dockerfile:1

FROM python:3.10.0rc2-alpine3.14 as back-end

LABEL maintainer="Specify Collections Consortium <github.com/specify>"

RUN addgroup -S specify -g 888 \
 && adduser -S specify -G specify -u 888

RUN mkdir -p /home/specify \
 && chown specify.specify /home/specify

RUN mkdir -p /scratch-path/log \
 && mkdir -p /scratch-path/sessions \
 && chown -R specify.specify /scratch-path

WORKDIR /home/specify
USER specify

COPY --chown=specify:specify ./requirements.txt .

RUN python -m venv venv \
 && venv/bin/pip install --no-cache-dir -r ./requirements.txt

COPY --chown=specify:specify ./lmtrex ./lmtrex
CMD ["./venv/bin/python", "-m", "lmtrex.config.broker"]


FROM node:16.10.0-buster as dev-front-end

LABEL maintainer="Specify Collections Consortium <github.com/specify>"

USER node
WORKDIR /home/node

RUN mkdir dist \
 && chown node:node dist

CMD ["npm", "run", "watch"]


FROM node:16.10.0-buster as front-end

LABEL maintainer="Specify Collections Consortium <github.com/specify>"

USER node
WORKDIR /home/node

COPY --chown=node:node lmtrex/frontend/js_src/package*.json ./
RUN npm install

RUN mkdir dist \
 && chown node:node dist

COPY --chown=node:node lmtrex/frontend/js_src .

RUN npm run build
