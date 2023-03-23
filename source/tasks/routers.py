from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from authentication.manager import current_active_user
from database.connection import get_async_session
from database.models import User

from .tasks import send_email_uploads_report

router = APIRouter(
    prefix='/reports',
    tags=['reports']
)


@router.get('/uploads_report')
def get_uploads_report(user: User = Depends(current_active_user)):
    # 1400 ms - Клиент ждет
    # send_email_uploads_report(user=user, session=session)
    # 500 ms - Задача выполняется на фоне FastAPI в event loop'е или в другом треде
    # background_tasks.add_task(
    #     send_email_uploads_report,
    #     user=user
    # )
    # 600 ms - Задача выполняется воркером Celery в отдельном процессе
    send_email_uploads_report.delay(username=user.username)
    return {
        "status": HTTPStatus.OK,
        "data": 'Письмо отправлено',
        "details": None
    }
