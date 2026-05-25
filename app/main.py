from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.calculator import calculate_productivity
from app.schemas import ExcavatorInput, ExcavatorResult

app = FastAPI(
    title="Excavator Productivity App",
    description="Прототип системы расчета производительности карьерного экскаватора",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def read_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/calculate", response_model=ExcavatorResult)
def calculate(data: ExcavatorInput):
    return calculate_productivity(data)