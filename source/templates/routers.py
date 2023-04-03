from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from content.routers import get_contents

router = APIRouter(
    prefix='/pages',
    tags=['pages']
)

templates = Jinja2Templates(directory='templates')


@router.get('/index/{limit}/{offset}')
def get_index_page(request: Request, contents=Depends(get_contents)):
    return templates.TemplateResponse(
        'index.html',
        {"request": request, 'contents': contents}
    )

    