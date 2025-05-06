from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from fastpluggy.core.dependency import get_templates

home_router = APIRouter()


@home_router.get("/admin", response_class=HTMLResponse)
def fast_pluggy_home(request: Request, templates=Depends(get_templates)):
    """
    Home page route that renders the index.html.j2 template.
    """

    # Render the template for the home page
    return templates.TemplateResponse("index.html.j2", {
        "request": request
    })


