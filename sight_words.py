from clize import run
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def make_pdf(*words):
    """Makes a pdf with one word on each page

    :param words: List of words to add to pdf
    """
    height, width = letter  # swapped for landscape
    c = canvas.Canvas("sight-words.pdf", pagesize=(width, height))
    pdfmetrics.registerFont(TTFont("Comic Sans", "resources/fonts/comic.ttf"))

    for word in words:
        add_word(c, word, width, height)

    c.save()


def add_word(canvas, word, width, height):
    canvas.setFont("Comic Sans", 72)
    canvas.drawCentredString(width / 2, height / 2, word)
    canvas.showPage()


if __name__ == "__main__":
    run(make_pdf)
