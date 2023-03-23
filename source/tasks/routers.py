from http import HTTPStatus

from fastapi import APIRouter, Depends

from authentication.manager import current_active_user
from database.models import User

from .tasks import send_email_uploads_report

router = APIRouter(
    prefix='/reports',
    tags=['reports']
)


@router.get('/uploads_report')
def get_uploads_report(user: User = Depends(current_active_user)):
    """Отправляем отчёт о загрузках пользователя с помощью Celery."""
    send_email_uploads_report.delay(user.username)
    return {
        'status': HTTPStatus.OK,
        'data': 'Письмо отправлено',
        'details': None
    }
