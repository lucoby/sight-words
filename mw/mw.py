from pathlib import Path
import requests
import pprint as pp


class MwClient:
    def __init__(self, api_key=""):
        self.api_key = api_key

    def learner(self, word):
        return requests.get(
            f"https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={self.api_key}"
        ).json()

    def audio(self, word: str, language_code="en", country_code="us", format="mp3"):
        local_filename = f"temp/audio/{word}.{format}"
        if Path(local_filename).exists():
            return local_filename

        word_response = self.learner(word)
        base_filename = ""
        for r in word_response:
            if "hwi" in r and "prs" in r["hwi"] and r["hwi"]["hw"] == word and "sound" in r["hwi"]["prs"][0]:
                base_filename = r["hwi"]["prs"][0]["sound"]["audio"]
                break

        subdirectory = ""
        if base_filename == "":
            raise RuntimeError(f"Failed to find audio: {word}")
        elif base_filename.startswith("bix"):
            subdirectory = "bix"
        elif base_filename.startswith("gg"):
            subdirectory = "gg"
        elif not base_filename[0].isalpha():
            subdirectory = "number"
        else:
            subdirectory = base_filename[0]

        base_audio_url = "https://media.merriam-webster.com/audio/prons"
        r = requests.get(
            f"{base_audio_url}/{language_code}/{country_code}/{format}/{subdirectory}/{base_filename}.{format}"
        )

        with open(local_filename, "wb") as f:
            f.write(r.content)

        return local_filename
