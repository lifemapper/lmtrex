# t-rex

The Lifemapper trex repository houses objects and common tools used within a
Lifemapper Broker installation that may also be useful for outside
contributors and the community as a whole.

Any community contributed tool through the
[lmtrex repository](https://github.com/lifemapper/lmtrex/) should
use these objects to ensure that new contributions are compatible with the
Lifemapper backend.

This work has been supported by NSF Awards NSF BIO-1458422, OCI-1234983.

## Debugging


To run flask in debug mode, first setup virtual environment for python at the 
top level of the repo, activate, then add dependencies from requirements.txt:

```zsh
cd ~/git/lmtrex
python3 -m venv venv
. venv/bin/activate
pip3 install flask requests pykew gunicorn
```

then start the flask application

```zsh
export FLASK_ENV=development
export FLASK_APP=lmtrex.flask_app.broker.routes
flask run
```

test on development port in browser: https://127.0.0.1:5000/api/v1/occ

## Deployment

To run the containers, generate `fullchain.pem` and `privkey.pem` (certificate
and the private key) using Let's Encrypt and put (or symlink) these files into the
`./lmtrex/config/` directory.

While in development, you can generate self-signed certificates:

```zsh
openssl req \
  -x509 -sha256 -nodes -newkey rsa:2048 -days 365 \
  -keyout ./lmtrex/config/privkey.pem \
  -out ./lmtrex/config/fullchain.pem
```

### Production

Run the containers:

```zsh
docker compose up -d
```

Broker is now available at [https://localhost/](https://localhost:443)

### Development

Run the containers:

```zsh
docker compose -f docker-compose.yml -f docker-compose.development.yml up
```

Broker is now available at [http://localhost/](http://localhost:443).

Webpack is watching for front-end file changes and rebuilds the bundle when
needed.

CherryPy is watching for back-end file changes and restarts the server when
needed.

#### (Optional) NPM dependencies

If you need to do front-end development, follow these steps:

Install npm and Node.js

Install front-end dependencies:

```
cd ./lmtrex/lmtrex/frontend/js_src
npm i
```

If any front-end changes were made, run `npm run typecheck` before
committing changes to verify validity of TypeScript types.

#### Configuring Debugger

Debugger configuration is IDE dependent. [Instructions for
PyCharm](https://kartoza.com/en/blog/using-docker-compose-based-python-interpreter-in-pycharm/)

`dev-back-end` container is running `debugpy` on port `5001`.

## Troubleshooting

To delete all containers, images, networks and volumes, stop any running
containers:

```zsh
docker compose stop
```

And run this command:

```zsh
# this ignores running container
docker system prune --all --volumes
```

### SSL certificates

SSL certificates are served from the base VM, and need apache to be renewed.  
These are administered by Letsencrypt using Certbot and are only valid for 90 days at
a time. When it is time for a renewal (approx every 60 days), bring the docker
containers down, and start apache. Renew the certificates, then stop apache,
and bring the containers up again.

```zsh
certbot certificates
docker compose stop
systemctl start httpd
certbot renew
systemctl stop httpd
docker compose up -d
```
