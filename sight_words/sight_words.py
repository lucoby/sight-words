import os
from pathlib import Path
import random
import string
import ffmpeg
from pdf2image import convert_from_path
from pydub import AudioSegment
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from mw import mw

load_dotenv()

MERRIAM_WEBSTER_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")


def make_slides(*words, title="", subtitle=""):
    """Makes a pdf with one word on each page

    :param words: List of words to add to pdf
    :param title: Adds a title slide with this as the title
    :param subtitle: Adds this as a subtitle - only used if title is also included
    """
    return _make_slides(*words, title=title, subtitle=subtitle)


def _make_slides(*words, title="", subtitle="", workspace=None):
    if workspace is None:
        id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        workspace = f"temp/{id}"
        Path(workspace).mkdir()

    height, width = letter  # swapped for landscape
    filename = f"{workspace}/sight-words.pdf"
    c = canvas.Canvas(filename, pagesize=(width, height))
    pdfmetrics.registerFont(TTFont("Comic Sans", "resources/fonts/comic.ttf"))

    if title != "":
        c.setFont("Comic Sans", 72)
        c.drawCentredString(width / 2, height / 2, title)
        c.setFont("Comic Sans", 48)
        c.drawCentredString(width / 2, height / 2 - 50, subtitle)
        c.showPage()

    for word in words:
        add_word(c, word, width, height)

    c.save()
    return filename


def add_word(canvas, word, width, height):
    canvas.setFont("Comic Sans", 72)
    canvas.drawCentredString(width / 2, height / 2, word)
    canvas.showPage()


def make_video(*words, title="", subtitle=""):
    """Makes a video with one word on each slide and audio of the word being said

    :param words: List of words to add to pdf
    :param title: Adds a title slide to the video with this as the title
    :param subtitle: Adds this as a subtitle - only used if title is also included
    """
    id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    workspace = f"temp/{id}"
    Path(workspace).mkdir()

    slides = _make_slides(*words, title=title, subtitle=subtitle, workspace=workspace)

    audio = AudioSegment.silent(duration=0)
    if title != "":
        audio = AudioSegment.silent(duration=4000)

    mw_client = mw.MwClient(api_key=MERRIAM_WEBSTER_API_KEY)
    missing_words = []
    for word in words:
        try:
            audio += add_word_audio(mw_client, word)
        except RuntimeError:
            audio += AudioSegment.silent(duration=4000)
            missing_words.append(word)

    audio_file = f"{workspace}/audio.mp3"
    audio.export(audio_file, format="mp3")

    images = convert_from_path(slides)
    for i, image in enumerate(images):
        image.save(f"{workspace}/img{i:03d}.png")
    video = ffmpeg.input(f"{workspace}/img%03d.png", framerate=0.25).video
    audio = ffmpeg.input(audio_file).audio
    video_filename = f"{workspace}/sight_words.mp4"
    out = ffmpeg.output(audio, video, video_filename, r=20, loglevel="panic")
    out.run()
    return video_filename, missing_words


def add_word_audio(client, word):
    initial = AudioSegment.silent(duration=1000)
    word_filename = client.audio(word)
    word_audio = AudioSegment.from_mp3(word_filename)
    pause = AudioSegment.silent(duration=3000 - 2 * len(word_audio))
    return initial + word_audio + pause + word_audio
