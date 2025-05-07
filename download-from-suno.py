import os

import requests
from rich.align import Align
from rich.live import Live
from rich.panel import Panel


def wget(url: str, filename=None):
    if filename is None:
        filename = url.split("/")[-1]
    p = Panel("", border_style="blue", title="[white]" + filename, title_align="left")
    with open(filename, "wb+") as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            with Live(p, refresh_per_second=20):
                for data in response.iter_content(chunk_size=4096):
                    tsize, _ = os.get_terminal_size()
                    tsize -= 6
                    dl += len(data)
                    f.write(data)
                    done = int(tsize * dl / total_length)
                    p.renderable = Align(
                        f"[{'=' * done}{' ' * (tsize - done)}]", "center"
                    )


def get_audio_name(content: str) -> str:
    if '\\"title\\":\\"' not in content:
        return "nom_pas_trouve"
    contains_name = content[content.index('\\"title\\":\\"') + 12 :]
    return contains_name[: contains_name.index('\\"')]


def get_audio_url(base_url: str) -> tuple:
    content = requests.get(base_url).text
    name = get_audio_name(content)
    if "og:audio" not in content:
        raise ValueError("No og:audio found !")
    url = None
    for e in content.split("og:audio"):
        if "https://cdn1.suno.ai" in e:
            url = (
                "https://cdn1.suno.ai"
                + e.split("https://cdn1.suno.ai")[1].split("\\")[0].split('"')[0]
            )
            break
    if url is None:
        raise ValueError("No link in content")
    return url, name


def download(base_url: str):
    audio_url, audio_name = get_audio_url(base_url)
    print(audio_name.encode())
    audio_name = audio_name.replace("\\u0026", "&").replace("\\n", "")
    filename = ""
    for char in audio_name:
        if char.lower() in "aàâbcdeéèêfghiîjklmnoôpqrstuùvwxyz0123456789_-=:.& ":
            filename += char
    filename += ".mp3"
    while os.path.isfile(filename):
        filename = "_" + filename
    wget(audio_url, filename)


def show_help(fname: str) -> int:
    print(f"Usage: {fname} music_url_1 [music_url_2 music_url_3...]")
    print("Download each music from suno.com")
    return 0


def main(fname: str, args: list) -> int:
    if not len(args):
        raise ValueError("An argument is required !")
    for arg in args:
        if arg in ("-h", "--help"):
            return show_help()
        if not arg.startswith("https://suno.com/song/"):
            raise ValueError("Url is not a valid Suno URL !")
        download(arg)
    return 0
