from pathlib import Path

from fastapi import FastAPI
from starlette.templating import Jinja2Templates

from . import config, core
from logging import Logger, getLogger


# --- FastAPI app setup (executes before `core.fastapi_lifespan`)
settings: config.Settings = config.settings
app: FastAPI
templates: Jinja2Templates | None = None
_logger: Logger = getLogger(__file__)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.HTTP_ROOT_PATH}openapi.json",  # todo: make it optional
    generate_unique_id_function=core.generate_unique_route_id,
    lifespan=core.fastapi_lifespan
)

# Enable `/static` HTTP Path
if settings.http_static_enabled:
    from starlette.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(settings.static_folder.resolve())))

# Enable Jinja Templates
if settings.templates_enabled:
    templates = Jinja2Templates(directory=str(settings.templates_folder.resolve()))
else:
    _logger.info("HTML templates are not enabled. `webserver.templates` will be None.")

# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    from starlette.middleware.cors import CORSMiddleware

    # noinspection PyTypeChecker
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Setup SSL
if settings.enable_ssl:
    if not settings.SSL_CERTIFICATE and not settings.SSL_PRIVATE_KEY:
        certs_folder: Path = settings.resources_folder / 'certs'

        cert = (certs_folder / f"{settings.HOST}.pem")
        key = (certs_folder / f"{settings.HOST}-key.pem")

        if cert.exists() and key.exists():
            # assign existent certificates to the environment variable
            settings.SSL_CERTIFICATE = str(cert.resolve())
            settings.SSL_PRIVATE_KEY = str(key.resolve())
        else:
            # generates a certificate
            from commons.network.http import certs

            files = certs.get_cert(certs_folder, [settings.HOST])
            settings.SSL_CERTIFICATE = str(files.cert.resolve())
            settings.SSL_PRIVATE_KEY = str(files.key.resolve())


def start():
    """
    Start a local uvicorn server.
    """
    import uvicorn

    kwargs = {
        "app": "webserver:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "use_colors": settings.LOG_USE_COLORS,
        "log_config": settings.uvicorn_logging_config,
    }

    if settings.enable_ssl:
        kwargs["ssl_certfile"] = settings.ssl_certificate.resolve()
        kwargs["ssl_keyfile"] = settings.ssl_private_key.resolve()

    if settings.ENVIRONMENT == "local":
        kwargs["reload"] = True  # TODO: infinite-loop bug when log file is present project dir
    else:
        kwargs["workers"] = settings.WORKERS

    uvicorn.run(**kwargs)