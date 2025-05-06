# FastAPI WebServer

This is a wrapper of a FAST API application with some additional features that might be useful for quick web development.

It features:
- Powerful environment and settings handling with dynamic module import like Django;
- Local Key-Value Cache database, powered by SQLite;
- Better logging configuration via `commons.logging`;
- Powerful database tools:
  - A Database Adapter to connect to any database on-the-fly;
  - A Data Migration Tool, to run `.sql` files, or migrate `json` data that runs automagically on server startup;
  - A FastAPI Dependency for the database (`webserver.core.ServerDatabase`)
  - A SQLite Cache Database + FastAPI dependency (`webserver.core.ServerCache`)
- An SMTP service, implemented on top of [fastapi-mail](https://pypi.org/project/fastapi-mail/);
- Internationalization (i18n) on top of [Babel](https://babel.pocoo.org/):
  - A FastAPI Dependency that discovers the locale based on HTTP Header `Accept-Language` (`webserver.core.AvailableLocale`)
- Front-end tools:
  - [SASS](https://sass-lang.com/) Compiler (`webserver.frontend.css`);
  - Server-Side Rendering via `Jinja2Template`;
- Static Files provider;
- CORS Support;
- TLS Support + [mkcert](https://github.com/FiloSottile/mkcert) certificates (local/development only)
- Content Proxies (`webserver.extras.proxies`):
  - Gravatar
  - GIPHY

## Roadmap

The following features are expected to be implemented in the future. Contribution is welcome.

- [ ] OCI-Compliant Image for Docker/Podman
- [ ] Logging and Tracing API (via OpenTelemetry)
- [ ] Authentication and Authorization
  - [ ] OAuth2 support
  - [ ] OpenID Connect support
  - [ ] Passkey support (via [Bitwarden passwordless](https://docs.passwordless.dev/guide/))
- [ ] Traffic Analyzer
  - [ ] (AI) Bot detector
  - [ ] VPN detector
  - [ ] Rate limiter
  - [ ] IP-based Access-Control List (ACL)
- [ ] Content Providers (HTTP client and proxy)
  - [ ] Google Fonts API> ⚠️ This is under active development and might not be ready for production environments.

## Testing

```shell
coverage run -m unittest && coverage html -d tests/coverage/html
```

## Build
```shell
uv build && twine upload dist/*
```

## Getting Started

Optionally, set up the environment variables. All environment variables can be found on `.env` file in the root of this repository.

```python
import webserver
from fastapi import APIRouter, FastAPI

router: APIRouter = APIRouter()
app: FastAPI = webserver.app


@router.get("/")
def index():
  return {"Hello World": f"from {webserver.settings.APP_NAME}"}


app.include_router(router)

if __name__ == "__main__":
  webserver.start()
```

This enables both local execution through `main` method as well as `fastapi (dev|run)` commands.
