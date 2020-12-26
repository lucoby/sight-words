from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sight_words.sight_words import make_pdf

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/heartbeat")
async def heartbeat():
    return {"status": "alive"}


@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


@app.post("/")
async def post_root(request: Request, words: str = Form(...)):
    words = words.splitlines()
    filepath = make_pdf(*words)
    return FileResponse(filepath, filename="Sight Words.pdf")
