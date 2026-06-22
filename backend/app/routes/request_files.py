"""Helpers for routes that accept optional upload bodies."""

from __future__ import annotations

from typing import Any

from fastapi import Request


async def read_optional_upload(request: Request, field_names: tuple[str, ...] = ("file", "image")) -> tuple[bytes | None, str | None]:
    content_type = request.headers.get("content-type", "").lower()
    if "multipart/form-data" in content_type:
        try:
            form = await request.form()
        except Exception as exc:
            raise ValueError("Multipart parsing failed. Install python-multipart and retry the upload.") from exc
        upload: Any | None = None
        for name in field_names:
            candidate = form.get(name)
            if hasattr(candidate, "read"):
                upload = candidate
                break
        if upload is None:
            for candidate in form.values():
                if hasattr(candidate, "read"):
                    upload = candidate
                    break
        if upload is None:
            return None, None
        return await upload.read(), getattr(upload, "filename", None)

    body = await request.body()
    if not body:
        return None, None
    filename = request.headers.get("x-filename")
    return body, filename

