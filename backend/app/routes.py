from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import get_url, save_url
from app.models import ShortenRequest, ShortenResponse, UrlInfoResponse

router = APIRouter()


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create short URL",
)
def create_short_url(payload: ShortenRequest):
    """Generates a UUID, stores the link in DynamoDB and returns the shortened link."""
    short_code = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    original_url = str(payload.original_url)

    try:
        save_url(short_code=short_code, original_url=original_url, created_at=created_at)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store URL in DynamoDB: {str(exc)}",
        )

    short_url = f"{settings.BASE_URL.rstrip('/')}/{short_code}"

    return ShortenResponse(
        short_code=short_code,
        original_url=original_url,
        short_url=short_url,
    )


@router.get(
    "/urls/{short_code}",
    response_model=UrlInfoResponse,
    summary="Inspect shortened link metadata",
)
def get_short_url_info(short_code: str):
    """Queries DynamoDB and returns URL metadata as JSON."""
    try:
        item = get_url(short_code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query error: {str(exc)}",
        )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    return UrlInfoResponse(
        short_code=item["short_code"],
        original_url=item["original_url"],
        created_at=item["created_at"],
    )


@router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original target URL",
)
def redirect_to_original(short_code: str):
    """Redirects the client to the original URL using HTTP 307 Temporary Redirect."""
    try:
        item = get_url(short_code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query error: {str(exc)}",
        )

    if not item or "original_url" not in item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    return RedirectResponse(
        url=item["original_url"],
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
