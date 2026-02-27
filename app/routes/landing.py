"""GET / — landing page."""

import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.config import settings

router = APIRouter(tags=["landing"])

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)


@router.get("/", response_class=HTMLResponse)
async def landing_page():
    template = env.get_template("landing.html")
    html = template.render(base_url=settings.base_url)
    return HTMLResponse(content=html)


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    template = env.get_template("privacy.html")
    html = template.render(base_url=settings.base_url)
    return HTMLResponse(content=html)
