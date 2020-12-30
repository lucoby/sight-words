from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sight_words.sight_words import make_slides, make_video

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/heartbeat")
async def heartbeat():
    return {"status": "alive"}


@app.get("/slides", name="slides", response_class=HTMLResponse)
async def get_slides(request: Request):
    return templates.TemplateResponse("slides.html", {"request": request, "title": "Slides"})


@app.post("/slides")
def post_slides(request: Request, title: str = Form(""), subtitle: str = Form(""), words: str = Form(...)):
    words = words.splitlines()
    filepath = make_slides(*words, title=title, subtitle=subtitle)
    return FileResponse(filepath, filename="Sight Words.pdf")


@app.get("/video", name="video", response_class=HTMLResponse)
async def get_video(request: Request):
    return templates.TemplateResponse("video.html", {"request": request, "title": "Video"})


@app.post("/video")
def post_video(request: Request, title: str = Form(""), subtitle: str = Form(""), words: str = Form(...)):
    words = words.splitlines()
    filepath, missing_words = make_video(*words, title=title, subtitle=subtitle)
    if len(missing_words) == 0:
        return FileResponse(filepath, filename="Sight Words.mp4")
    else:
        _, id, _ = filepath.split("/")
        return templates.TemplateResponse(
            "video.html",
            {
                "request": request,
                "title": "Video",
                "message": f"Audio is missing for these words: {','.join(missing_words)}.",
                "redirect": "Click here to download anyways.",
                "endpoint": "missing",
                "id": id,
            },
        )


@app.get("/missing/{id}", name="missing")
def get_missing(request: Request, id):
    filepath = f"temp/{id}/sight_words.mp4"
    path = Path(filepath).resolve()
    print(path.parents)
    print(Path("temp/"))
    if Path("temp/").resolve() in path.parents:
        return FileResponse(filepath, filename="Sight Words.mp4")
