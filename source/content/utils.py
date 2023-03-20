from http import HTTPStatus
from pathlib import Path
from typing import IO

import aiofiles
from fastapi import Depends, HTTPException, UploadFile
from fastapi.requests import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import get_async_session
from database.models import Content


async def write_content(content: UploadFile, content_path: str):
    """Cохраняет загружаемый контент локально."""
    async with aiofiles.open(content_path, 'wb') as uploaded_content:
        data = await content.read()
        await uploaded_content.write(data)


async def get_content_or_404(
    content_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Позволяет получить контент по id или выдает 404 ошибку."""
    query = select(Content).where(Content.id == content_id).options(
        selectinload(Content.author)
    )

    result = await session.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Запрошенный контент не найден.'
        )
    return content


async def get_contents_with_limit_offset(
    session: AsyncSession,
    limit: int = None,
    offset: int = None
):
    """Возвращает результат лимитированного запроса контента."""
    query = select(Content).options(selectinload(Content.author))
    result = await session.execute(query)

    if limit and not offset:
        result = result.scalars().all()[:limit]
    elif not limit and offset:
        result = result.scalars().all()[offset:]
    elif limit and offset:
        limit += offset
        result = result.scalars().all()[offset:limit]
    else:
        result = result.scalars().all()
    return result


def ranged(
        content: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
):
    """Вычисляет конкретное место с кототорого необходимо
    начать воспроизведение контента."""

    consumed = 0
    content.seek(start)

    while True:
        data_length = min(
            block_size, end - start - consumed
        ) if end else block_size
        if data_length <= 0:
            break
        data = content.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(content, 'close'):
        content.close()


async def open_contentfile(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Открывает конкретный файл с контентом.Позволяет делать
    это с необходимого места воспроизведения."""

    content = await get_content_or_404(content_id, session)

    content_type = content.content_class + '/' + content.content_extension
    content_path = Path(content.content_path)

    content = content_path.open('rb')
    content_size = content_path.stat().st_size
    content_length = content_size
    status_code = HTTPStatus.OK
    headers = {}
    content_range = request.headers.get('range')

    if content_range:
        content_range = content_range.strip().lower()
        content_ranges = content_range.split('=')[-1]
        range_start, range_end, *_ = map(
            str.strip, (content_ranges + '-').split('-')
        )
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(
            content_size - 1, int(range_end)
        ) if range_end else content_size - 1
        content_length = (range_end - range_start) + 1
        content = ranged(content, start=range_start, end=range_end + 1)
        status_code = HTTPStatus.PARTIAL_CONTENT
        headers['Content-Range'] = \
            f'bytes {range_start}-{range_end}/{content_size}'

    return content, status_code, content_length, headers, content_type
