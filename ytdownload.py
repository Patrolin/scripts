from yt_dlp import YoutubeDL
import re
from typing import NamedTuple, cast
import asyncio
from os.path import expanduser, exists as fileexists
from sys import argv

# playlists
class VideoInfo(NamedTuple):
    title: str
    url: str

def url_param(key: str, url: str) -> str:
    match = re.search(f"[?&]{key}=([^&]+)", url)
    return match[1] if match != None else ""

def video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"

def playlist_url(playlist_id: str) -> str:
    return f"https://www.youtube.com/playlist?list={playlist_id}"

def exit_with_prompt(error: str, error_code: int = 1):
    if error: print(error)
    input("Press enter to exit...")
    exit(error_code)

# prompts
def promptBool(prefix: str, default: bool) -> bool:
    b: bool | None = None
    while b == None:
        b = parseBool(input(prefix), default)
    return b

def parseBool(s: str, default: bool) -> bool | None:
    s = s.strip()
    if s in {"Y", "y"}:
        return True
    elif s in {"N", "n"}:
        return False
    else:
        return None if s else default

def promptInt(prefix: str, default: int):
    v: int | None = None
    while v == None:
        v = parseInt(input(prefix), default)
    return v

def parseInt(s: str, default: int) -> int | None:
    s = s.strip()
    if s == "":
        return default
    try:
        return int(s)
    except ValueError:
        return None

# download
async def sh(cmd: str):
    P = asyncio.subprocess.PIPE
    process = await asyncio.create_subprocess_shell(cmd, stdout=P, stderr=P)
    stdout, stderr = await process.communicate()
    if (process.returncode != 0):
        raise Exception(stdout.decode('utf-8') + '\n' + stderr.decode('utf-8'))

#NTFS_ESCAPE = r'[\/:*?"<>|]'
FOO_ESCAPE = r'[\/:*?<>*]'

def fs_escape(s: str) -> str:
    #return re.sub(NTFS_ESCAPE, '_', s) if os.name == 'nt' else re.sub(EXT_POSIX_ESCAPE, '_', s)
    s = re.sub(FOO_ESCAPE, '_', s)
    s = re.sub(r'"', '\'', s)
    s = re.sub(r'\$', 'S', s)
    s = re.sub(r'\|', '-', s)
    return s

AUDIO_EXTENSION = "mp3"

def AUDIO_CMD(video_info: VideoInfo, file_path: str):
    acc = "yt-dlp"
    acc += f" {video_info.url}"
    acc += f" -f bestaudio"
    acc += f" -x --audio-format {AUDIO_EXTENSION}"
    acc += f" --add-metadata --metadata-from-title '%(title)s'"
    acc += f" -o \"{file_path}\""
    print(acc)
    return acc

VIDEO_EXTENSION = "mkv"

def VIDEO_CMD(video_info: VideoInfo, file_path: str, max_video_height: int):
    acc = "yt-dlp"
    acc += f" {video_info.url}"
    acc += f" -f \"bestvideo[height<={max_video_height}]+bestaudio/best[height<={max_video_height}]/best\""
    acc += f" --merge-output-format \"{VIDEO_EXTENSION}\" --recode-video {VIDEO_EXTENSION}"
    acc += f" --write-subs --write-auto-subs --embed-subs --compat-options no-keep-subs --sub-lang \"en,cs\""
    acc += f" -o \"{file_path}\""
    print(acc)
    return acc

user_path = expanduser("~")
is_termux = user_path.find("com.termux") > -1
music_path = f"{user_path}/storage/music" if is_termux else f"{user_path}/Music"
downloads_path = f"{user_path}/storage/downloads" if is_termux else f"{user_path}/Downloads"

async def download_video_if_not_exist(
    video_info: VideoInfo, playlist_name: str | None, \
    audio_only: bool, max_video_height: int, \
    n: int, maxN: int
):
    dir_path = (music_path if audio_only else downloads_path) + (f"/{playlist_name}" if playlist_name != None else "")

    def get_file_name(title: str) -> str:
        return f"{title}." + (AUDIO_EXTENSION if audio_only else VIDEO_EXTENSION)

    def get_file_path(file_name: str) -> str:
        return f"{dir_path}/{fs_escape(file_name)}"

    file_name = get_file_name(video_info.title)
    file_path = get_file_path(file_name)
    temp_file_path = get_file_path(get_file_name(f"{video_info.title}.temp"))

    def print_diff(new: bool):
        print(f" {' +'[new]} {file_name}{f' ({n}/{maxN})' if playlist_name != None else ''}")

    file_exists = fileexists(file_path) and not fileexists(temp_file_path)
    print_diff(not file_exists)
    if file_exists:
        return
    if audio_only:
        await sh(AUDIO_CMD(video_info, file_path))
    else:
        await sh(VIDEO_CMD(video_info, file_path, max_video_height))

TREAT_VIDEO_WITH_PLAYLIST_AS_PLAYLIST = False

async def main():
    if len(argv) == 1:
        exit_with_prompt('Not enough arguments!')
    if len(argv) == 2:
        url = argv[1]
    else:
        exit_with_prompt('Too many arguments!')

    playlist_name: str | None = None
    videos: list[VideoInfo] = []
    video_id = url_param("v", url)
    playlist_id = url_param("list", url)
    is_playlist = (playlist_id != "") if TREAT_VIDEO_WITH_PLAYLIST_AS_PLAYLIST else (video_id == "")
    if (is_playlist and playlist_id == "") or (not is_playlist and video_id == ""):
        exit_with_prompt(f"Error: invalid url; {url}")
    standardized_url: str = playlist_url(cast(str, playlist_id)) if is_playlist else video_url(cast(str, video_id))
    with YoutubeDL({"extract_flat": True, "quiet": True}) as yt:
        playlist_or_video = yt.extract_info(standardized_url, download=False)
        if is_playlist:
            playlist_name = playlist_or_video["title"]
            for video in playlist_or_video["entries"]:
                videos.append(VideoInfo(video["title"], video["url"]))
        else:
            videos.append(VideoInfo(playlist_or_video["title"], standardized_url))
    print(f" Playlist: {playlist_name}" if is_playlist else f" Video: {videos[0].title}")

    audio_only = promptBool(" Audio only? [Yn]: ", True)
    max_video_height = promptInt(" Max video height? [480]: ", 480) if not audio_only else 480

    #work_index_lock = asyncio.Lock()
    for i, v in enumerate(videos):
        try:
            await download_video_if_not_exist(v, playlist_name, audio_only, max_video_height, i + 1, len(videos))
        except Exception as err:
            print(err)
    exit_with_prompt("", 0)

if __name__ == "__main__":
    asyncio.run(main())
