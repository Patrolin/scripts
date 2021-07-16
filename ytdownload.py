#!/usr/bin/python

import sys
import pytube
import os
import re
import subprocess

def parseBool(s: str, default=True) -> bool:
  s = s.strip()
  if s in {'Y', 'y'}:
    return True
  elif s in {'N', 'n'}:
    return False
  else:
    return None if s else default

def fs_escape(s: str) -> str:
  return re.sub(r'[\/:*?"<>|]', '_', s) if os.name == 'nt' else s

def download_url(url: str, path: str) -> None:
  global do_while
  cmd = 'youtube-dl'
  cmd += f' "{url}"'
  if audio_only:
    cmd += f' -f "best[height<={max_video_height}]/best"'
    cmd += f' -x --audio-format "mp3"' # youtube-dl is dumb and only supports exporting to mp3
    cmd += f' --add-metadata --metadata-from-title "%(artist)s - %(title)s"'
  else:
    cmd += f' -f "bestvideo[height<={max_video_height}]+bestaudio/best[height<={max_video_height}]/best"'
    cmd += f' --merge-output-format "mkv" --recode-video "mkv"' # debian is stupid and has decades old ffmpeg and doesn't let you recode into mp4
    cmd += f' --write-sub --write-auto-sub --sub-lang "en,cs,rechat" --embed-subs'
    #cmd += f' --write-thumbnail --embed-thumbnail' # debian's youtube-dl is terrible and has broken dependencies for mp4 and doesn't support mkv
  cmd += f' -o "{path}%(title)s [%(channel)s].%(ext)s"'
  #cmd += f' --download-archive ~/storage/downloads/video/{playlist_path}archive.txt' # termux doesn't implement asyncio, so this doesn't work either
  print(f'\n{cmd}', flush=True)
  do_while |= subprocess.run(cmd, shell=True).returncode

FFMPEG_AUDIO_EXTENSIONS = {'mp3'}
FFMPEG_VIDEO_EXTENSIONS = {
    "3g2", "3gp", "3gp2", "asf", "avi", "cavs", "dvr-ms", "exr", "ffindex", "ffpreset", "flv", "gxf", "h261", "h263",
    "h264", "ifv", "ivf", "kux", "m2t", "m2ts", "m4v", "mkv", "mod", "mov", "mp4", "mpg", "mxf", "nut", "png", "tod",
    "vob", "webm", "wmv", "xmv", "y4m"
}

if len(sys.argv) == 1:
  exit('Not enough arguments!')
if len(sys.argv) == 2:
  input_url = sys.argv[1]
else:
  exit('Too many arguments!')

try:
  playlist = pytube.Playlist(input_url)
  playlist_title = playlist.title
except Exception:
  playlist = None
  playlist_title = ''

do_while = True
while do_while:
  playlist_path = ''
  if playlist:
    while playlist_path == '':
      playlist_path = input(f'Playlist name? [{playlist_title}]: ') or playlist_title
    playlist_path += '/'
  audio_only = None
  while audio_only == None:
    audio_only = parseBool(input(f'Audio only? [Yn]: '), True)
  max_video_height = None
  while max_video_height == None:
    try:
      max_video_height = round(float(input(f'Max video height? [480]: ') or '480'))
    except ValueError:
      pass
  
  if audio_only:
    path = f'~/storage/downloads/audio/{playlist_path}'
  else:
    path = f'~/storage/downloads/video/{playlist_path}'
  if not playlist:
    playlist = {input_url}
  
  media = {}
  try:
    with os.scandir(path) as d:
      for direntry in d:
        if direntry.is_file():
          name, ext = direntry.name.rsplit('.', 1)
          if name not in media:
            media[name] = {ext}
          else:
            media[name].add(ext)
  except FileNotFoundError:
    pass
  try:
    os.mkdir(os.path.expanduser(path))
  except FileExistsError:
    pass
  try:
    with open(f'{path}qArchive.txt', 'r', encoding='utf8') as f:
      archive = {p[0]: (p[1][:-1] if p[1][-1] == '\n' else p[1]) for p in (x.split(' ', 1) for x in f.readlines())}
  except FileNotFoundError:
    archive = {}
  archive_delta = {}
  for i, url in enumerate(playlist, 1):
    if (url not in archive) or (archive[url] not in media) or (
        not (media[archive[url]] & (FFMPEG_AUDIO_EXTENSIONS if audio_only else FFMPEG_VIDEO_EXTENSIONS))):
      youtube = pytube.YouTube(url)
      archive_delta[url] = fs_escape(f'{youtube.title} [{youtube.author}]')
      print(f'+{url} ({i}/{len(playlist)})')
  archive = archive | archive_delta
  with open(f'{path}qArchive.txt', 'w+', encoding='utf8') as f:
    f.writelines([f'{url} {name}\n' for (url, name) in archive.items()])
  do_while = False
  for url in archive_delta:
    download_url(url, path)
