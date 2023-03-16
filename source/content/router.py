from http import HTTPStatus
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authentication.manager import current_active_user
from database.connection import get_async_session
from database.models import Content, User

from .constans import ALLOWED_CONTENT_TYPES, UPLOADED_CONTENT_PATH
from .schemas import ContentCreate, ContentRead, ContentUpdate
from .utils import get_content_or_404, open_contentfile, write_content

router = APIRouter(
    prefix='/contents',
    tags=['contents']
)


@router.post('/')
async def upload_content(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(None),
    content: UploadFile = File(...),
):
    """Позволяет пользователю загружать контент."""
    content_class, content_extension = content.content_type.split('/')
    content_path = (f'{UPLOADED_CONTENT_PATH}/'
                    f'{user.id}_{content_class}_{uuid4()}.{content_extension}')
    content_info = ContentCreate(
        title=title, description=description, tags=tags
    )

    if content.content_type in ALLOWED_CONTENT_TYPES:
        await write_content(content=content, content_path=content_path)
    else:
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail=(
                'Вы пытаетесь загрузить файл с неподдерживаемым типом данных.'
            )
        )

    new_content = Content(
        author_id=user.id,
        content_class=content_class,
        content_extension=content_extension,
        content_path=content_path,
        **content_info.dict(),
    )

    session.add(new_content)
    await session.commit()
    return 'Файл был успешно загружен.'


@router.get('/', response_model=List[ContentRead])
async def get_contents(session: AsyncSession = Depends(get_async_session)):
    """Позволяет пользователю просматривать весь контент."""
    query = select(Content).options(selectinload(Content.author))
    result = await session.execute(query)
    return result.scalars().all()


@router.get('/{content_id}', response_model=ContentRead)
async def get_content(
    content_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Позволяет пользователю просмотреть конкретный контент."""
    return await get_content_or_404(content_id, session)


@router.get('/streaming/{content_id}')
async def get_streaming_content(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Позволяет пользователю просмотреть конкретный контент в плеере."""
    content, status_code, content_length, headers, \
        content_type = await open_contentfile(request, content_id, session)

    response = StreamingResponse(
        content,
        media_type=content_type,
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers
    })
    return response


@router.patch('/{content_id}', response_model=ContentRead)
async def update_content(
    content_id: int,
    update_data: ContentUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Позволяет пользователю обновлять данные о контенте."""
    content = await get_content_or_404(content_id, session)
    data = update_data.dict(exclude_unset=True)

    for key, value in data.items():
        setattr(content, key, value)
    session.add(content)
    await session.commit()
    await session.refresh(content)
    return content


@router.delete('/{content_id}')
async def delete_content(
    content_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Позволяет пользователю удалять контент."""
    content = await get_content_or_404(content_id, session)
    await session.delete(content)
    await session.commit()
    return 'Файл был успешно удален.'
