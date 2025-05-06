from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response
from webserver.core import ServerCache

gravatar_router: APIRouter = APIRouter(prefix="/proxy")
giphy_router: APIRouter = APIRouter(prefix="/proxy")


@gravatar_router.get("/avatar/{encoded_email}")
def gravatar_proxy(request: Request, cache: ServerCache, encoded_email: str, size: int = 32):
    from commons.media import gravatar, Image, mimetypes
    from commons.database import CacheEntry

    response: Response = Response(status_code=400, content="Image size must be between 32 and 1024.")
    cache_entry: Optional[CacheEntry] = None
    cache_hit: bool = False
    key = f"{encoded_email}+{size}"

    with cache:
        max_age: int = timedelta(days=30).max.seconds

        if size and (32 <= size <= 1024):  # check min 32 and max 1024
            cache_entry = cache.get(key)
            if (request.headers.get("Cache-Control") == "no-cache") or (not cache_entry) or (cache_entry and cache_entry.expired):
                if cache_entry:
                    cache.invalidate(cache_entry.id)

                image: Image = gravatar.avatar(encoded_email, size)

                if image:
                    cache_entry = cache.set(key, value=image.read(), max_age=max_age)
        else:
            cache_hit = True

        if cache_entry:
            response = Response(cache_entry.data, media_type=mimetypes.IMAGE_WEBP,
                                headers={
                                    "Age": f"{int((datetime.now() - cache_entry.created_at).total_seconds())}",
                                    "X-Cache": "HIT" if cache_hit else "MISS",
                                    "Cache-Control": f"max-age={cache_entry.max_age}",
                                    "Date": cache_entry.created_at.isoformat(),
                                    "Content-Disposition": f'inline; filename="Gravatar-{key}.webp"',
                                    "Content-Source": "Gravatar"
                                })

    return response


@giphy_router.get("/gif/{giphy_id}")
def giphy_proxy(request: Request, cache: ServerCache, giphy_id: str):
    from commons.database import CacheEntry
    from commons.media import giphy, Image, mimetypes

    response: Response = Response(status_code=404)
    cache_entry: Optional[CacheEntry] = None
    cache_hit: bool = False
    key = f"{giphy_id}"

    with cache:
        max_age: int = timedelta(days=180).max.seconds

        cache_entry = cache.get(key)
        if (request.headers.get("Cache-Control") == "no-cache") or (not cache_entry) or (cache_entry and cache_entry.expired):
            if cache_entry:
                cache.invalidate(cache_entry.id)

            image: Image = giphy.gif(giphy_id)

            if image:
                cache_entry = cache.set(key, value=image.read(), max_age=max_age)
        else:
            cache_hit = True

        if cache_entry:
            response = Response(cache_entry.data, media_type=mimetypes.IMAGE_GIF,
                                headers={
                                    "Age": f"{int((datetime.now() - cache_entry.created_at).total_seconds())}",
                                    "X-Cache": "HIT" if cache_hit else "MISS",
                                    "Cache-Control": f"max-age={cache_entry.max_age}",
                                    "Date": cache_entry.created_at.isoformat(),
                                    "Content-Disposition": f'inline; filename="Giphy-{key}.gif"',
                                    "Content-Source": "Giphy"
                                })

    return response
