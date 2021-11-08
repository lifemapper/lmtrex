# t-rex

The Lifemapper trex repository houses objects and common tools used within a
Lifemapper Broker installation that may also be useful for outside
contributors and the community as a whole.

Any community contributed tool through the
[lmtrex repository](https://github.com/lifemapper/lmtrex/) should
use these objects to ensure that new contributions are compatible with the
Lifemapper backend.

This work has been supported by NSF Awards NSF BIO-1458422, OCI-1234983.

## Deployment

To run the containers, generate `fullchain.pem` and `privkey.pem` (certificate
and the private key) using Let's Encrypt and put these files into the
`./lmtrex/config/` directory.

While in development, you can generate self-signed certificates:

```zsh
openssl req \
  -x509 -sha256 -nodes -newkey rsa:2048 -days 365 \
  -keyout ./lmtrex/config/privkey.pem \
  -out ./lmtrex/config/fullchain.pem
```

To run the production container, or the development container with HTTPs
support, generate `fullchain.pem` and `privkey.pem` (certificate and the private
key) using Let's Encrypt and put these files into the `./lmtrex/config/`
directory.

### Production

Run the containers:

```zsh
docker compose -f docker-compose.production.yml up -d
```

Broker is now available at [https://localhost/](https://localhost:443)

### Development

Install npm and Node.js

Install front-end dependencies:

```
cd ./lmtrex/lmtrex/frontend/js_src
npm i
```

Run the containers:

```zsh
docker compose up
```

Broker is now available at [http://localhost/](http://localhost:443).

Webpack is watching for front-end file changes and rebuilds the bundle when
needed.

CherryPy is watching for back-end file changes and restarts the server when
needed.

If any front-end changes were made, run `npm run typecheck` before
committing changes to verify validity of TypeScript types.

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
a time.  When it is time for a renewal (approx every 60 days), bring the docker 
containers down, and start apache.  Renew the certificates, then stop apache, 
and bring the containers up again.

```zsh
certbot certificates 
docker compose stop
systemctl start httpd
certbot renew
systemctl stop httpd
docker compose up -d
```


