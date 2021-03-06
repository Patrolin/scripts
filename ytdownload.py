#!/usr/bin/python

import sys
import pytube # python -m pip install git+https://github.com/pytube/pytube
import os
import re
import time
import subprocess # pip install youtube-dl

def parseBool(s: str, default=True) -> bool:
  s = s.strip()
  if s in {'Y', 'y'}:
    return True
  elif s in {'N', 'n'}:
    return False
  else:
    return None if s else default

NTFS_ESCAPE = r'[\/:*?"<>|]'
EXT_POSIX_ESCAPE = r'[/<>|*$]'
FOO_ESCAPE = r'[\/:*?<>*]'

def fs_escape(s: str) -> str:
  #return re.sub(NTFS_ESCAPE, '_', s) if os.name == 'nt' else re.sub(EXT_POSIX_ESCAPE, '_', s)
  s = re.sub(FOO_ESCAPE, '_', s)
  s = re.sub(r'"', '\'', s)
  s = re.sub(r'$', 'S', s)
  s = re.sub(r'\|', '-', s)
  return s

def download_url(url: str, path: str, i: int, N: int) -> None:
  global do_while
  cmd = 'youtube-dl'
  cmd += f' "{url}"'
  if audio_only:
    cmd += f' -f "best[height<={max_video_height}]/best"'
    cmd += f' -x --audio-format "mp3"' # youtube-dl is dumb and only supports exporting to mp3 # TODO: download only audio when possible
    cmd += f' --add-metadata --metadata-from-title "%(title)s"'
  else:
    cmd += f' -f "bestvideo[height<={max_video_height}]+bestaudio/best[height<={max_video_height}]/best"'
    cmd += f' --merge-output-format "mkv" --recode-video "mkv"' # debian is stupid and has decades old ffmpeg and doesn't let you recode into mp4
    cmd += f' --write-sub --write-auto-sub --sub-lang "en,cs,rechat" --embed-subs'
    #cmd += f' --write-thumbnail --embed-thumbnail' # debian's youtube-dl is terrible and has broken dependencies for mp4 and doesn't support mkv
  #cmd += f' -o "{path}%(title)s [%(channel)s].%(ext)s"'
  cmd += f' -o "{path}.%(ext)s"'
  #cmd += f' --download-archive ~/storage/downloads/video/{playlist_path}archive.txt' # termux doesn't implement asyncio, so this doesn't work either
  print(f'\n({i+1}/{N}) {cmd}', flush=True)
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
      playlist_path = input(f'\nPlaylist name? [{playlist_title}]: ') or playlist_title
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
  path = os.path.expanduser(path)
  playlist2 = playlist or {input_url}
  
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
    os.mkdir(path)
  except FileExistsError:
    pass
  try:
    with open(f'{path}qArchive.txt', 'r', encoding='utf8') as f:
      archive = {p[0]: (p[1][:-1] if p[1][-1] == '\n' else p[1]) for p in (x.split(' ', 1) for x in f.readlines())}
  except FileNotFoundError:
    archive = {}
  goto = True
  for i, url in enumerate(playlist2):
    if (url not in archive) or (archive[url] not in media) or (
        not (media[archive[url]] & (FFMPEG_AUDIO_EXTENSIONS if audio_only else FFMPEG_VIDEO_EXTENSIONS))):
      goto = False
      for j in range(8):
        try:
          youtube = pytube.YouTube(url)
          archive[url] = fs_escape(f'{youtube.title} [{youtube.author}]')
          goto = True
        except:
          print(f'({j+1}/8) Failed')
          time.sleep(2**j)
      if not goto:
        break
      print(f'({i+1}/{len(playlist2)}) +{url}')
  if not goto:
    continue
  with open(f'{path}qArchive.txt', 'w+', encoding='utf8') as f:
    f.writelines([f'{url} {name}\n' for (url, name) in archive.items()])
  media_delta = {}
  for i, url in enumerate(playlist2):
    if (archive[url] not in media) or (not (media[archive[url]] &
                                            (FFMPEG_AUDIO_EXTENSIONS if audio_only else FFMPEG_VIDEO_EXTENSIONS))):
      media_delta[url] = archive[url]
  do_while = False
  for i, url in enumerate(media_delta):
    download_url(url, f'{path}{media_delta[url]}', i, len(media_delta))
