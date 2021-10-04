# t-rex

The Lifemapper t-rex repository houses objects and common tools used within a
Lifemapper Broker and Resolver installation that may also be useful for outside
contributors and the community as a whole.

Any community contributed tool through the
[T-Rex Python Repository](https://github.com/lifemapper/t-rex/) should
use these objects to ensure that new contributions are compatible with the
Lifemapper backend.

This work has been supported by NSF Awards NSF BIO-1458422, OCI-1234983.

## Deployment

To run the production container, or the development container with HTTPs
support, generate `fullchain.pem` and `privkey.pem` (certificate and the private
key) using Let's Encrypt and put these files into the `./lmtrex/config/`
directory.

### Production

Run the container:

```zsh
docker-compose -f docker-compose.production.yml up -d
```

Broker is now available at [https://localhost/](https://localhost:443)

### Development

#### Without HTTPs support

Run HTTP only version:

```zsh
docker-compose up -d
```

#### With HTTPs support

Generate self-signed certificates:

```zsh
openssl req \
  -x509 -sha256 -nodes -newkey rsa:2048 -days 365 \
  -keyout ./lmtrex/config/privkey.pem \
  -out ./lmtrex/config/fullchain.pem
```

Run the containers:

```zsh
docker-compose -f docker.compose.https.yml up -d
```

#### After deployment

Broker is now available at [http://localhost/](http://localhost:80).

Webpack is watching for front-end file changes and rebuilds the bundle when
needed.

CherryPy is watching for back-end file changes and restarts the server when
needed.

If any front-end changes were made, run `npm run typecheck` before
committing changes to verify validity of TypeScript types.
