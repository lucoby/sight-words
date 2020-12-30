from clize import run
from sight_words.sight_words import make_slides, make_video


if __name__ == "__main__":
    run(make_slides, make_video)
