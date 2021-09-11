#!/usr/bin/python

import sys
import pytube # python -m pip install git+https://github.com/pytube/pytube
import os
import re
import time
import random
import asyncio
import subprocess # pip install youtube-dl
from pprint import pprint

def parseBool(s: str, default: bool) -> bool:
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
  s = re.sub(r'\$', 'S', s)
  s = re.sub(r'\|', '-', s)
  return s
def youtubedl_escape(s: str) -> str:
  return re.sub(r"%", r"%%", s)

async def sh(cmd: str):
  P = asyncio.subprocess.PIPE
  process = await asyncio.create_subprocess_shell(cmd, stdout=P, stderr=P)
  stdout, stderr = await process.communicate()
  if (process.returncode != 0):
    raise Exception(stdout.decode('utf-8') + '\n' + stderr.decode('utf-8'))

video_count = 0

archive = {}
video_info_count = 0
video_info_count_lock = asyncio.Lock()
async def get_video_info_and_download(url: str, audio_only: bool, playlist_path: str, storage: dict):
  global connections, video_info_count, download_count
  if url in archive:
    file_name = archive[url]
  else:
    for j in range(8):
      await connections.acquire()
      try:
        youtube = pytube.YouTube(url)
        file_name = fs_escape(f'{youtube.title} [{youtube.author}]')
        archive[url] = file_name
        connections.release()
        break
      except:
        connections.release()
        if j == 7:
          raise
        await asyncio.sleep(2**j)
  await video_info_count_lock.acquire()
  video_info_count += 1
  video_info_count_lock.release()
  print(f'\n({video_info_count}/{video_count}) +{url} {file_name}', flush=True)

  if (file_name not in storage) or (not (storage[file_name] &
                                          (AUDIO_EXTENSIONS_WHITELIST if audio_only else VIDEO_EXTENSIONS_WHITELIST))):
    file_path = f'{playlist_path}{youtubedl_escape(file_name)}'
    c = download_media(url, audio_only, file_path)
    await c
  else:
    await download_count_lock.acquire()
    download_count += 1
    download_count_lock.release()

download_count = 0
download_count_lock = asyncio.Lock()
async def download_media(url: str, audio_only: bool, file_path: str):
  global connections, download_count
  cmd = 'youtube-dl'
  cmd += f' "{url}"'
  if audio_only:
    cmd += f' -f "bestaudio"'
    cmd += f' -x --audio-format "mp3"'
    cmd += f' --add-metadata --metadata-from-title "%(title)s"'
  else:
    cmd += f' -f "bestvideo[height<={max_video_height}]+bestaudio/best[height<={max_video_height}]/best"'
    cmd += f' --merge-output-format "mkv" --recode-video "mkv"' # debian is stupid and has decades old ffmpeg and doesn't let you recode into mp4
    cmd += f' --write-sub --write-auto-sub --sub-lang "en,cs,rechat" --embed-subs'
  cmd += f' -o "{file_path}.%(ext)s"'
  await download_count_lock.acquire()
  download_count += 1
  download_count_lock.release()
  print(f'\n({download_count}/{video_count}) {cmd}', flush=True)
  await connections.acquire()
  await sh(cmd)
  connections.release()

AUDIO_EXTENSIONS_WHITELIST = {'mp3'}
VIDEO_EXTENSIONS_WHITELIST = {'mkv'}

if len(sys.argv) == 1:
  exit('Not enough arguments!')
if len(sys.argv) == 2:
  input_url = sys.argv[1]
else:
  exit('Too many arguments!')

try:
  is_playlist = True
  playlist = pytube.Playlist(input_url)
  playlist_title = playlist.title
except Exception:
  is_playlist = False
  playlist = {input_url}
  playlist_title = ''

user_path = os.path.expanduser('~')
is_termux = user_path.find('com.termux') > -1
music_path = f'{user_path}/storage/music/' if is_termux else f'{user_path}/Music/'
downloads_path = f'{user_path}/storage/downloads/' if is_termux else f'{user_path}/Downloads/'

async def main():
  global connections, video_count, video_info_count, download_count
  playlist_name = ''
  if is_playlist:
    while playlist_name == '':
      playlist_name = input(f'Playlist name? [{playlist_title}]: ') or playlist_title

  audio_only = None
  while audio_only == None:
    audio_only = parseBool(input(f'Audio only? [Yn]: '), True)

  max_video_height = None
  while max_video_height == None:
    try:
      max_video_height = round(float(input(f'Max video height? [480]: ') or '480'))
    except ValueError:
      pass

  root_path = f'{music_path if audio_only else downloads_path}'
  playlist_path = f'{root_path}{playlist_name}/'
  try:
    os.mkdir(playlist_path)
  except FileExistsError:
    pass

  connections = asyncio.BoundedSemaphore(3)

  do_while = True
  while do_while:
    storage = {}
    for (dirpath, dirnames, filenames) in os.walk(root_path):
      for file_name in filenames:
        name, ext = file_name.rsplit('.', 1)
        if name not in storage:
          storage[name] = {ext}
        else:
          storage[name].add(ext)

    video_count = len(playlist)
    video_info_count = 0
    download_count = 0
    tasks = []
    shuffled_playlist = list(playlist)
    random.shuffle(shuffled_playlist)
    for url in shuffled_playlist:
      task = asyncio.ensure_future(get_video_info_and_download(url, audio_only, playlist_path, storage))
      tasks.append(task)

    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    errors = [t for t in tasks if t.exception() != None]
    error_count = len(errors)
    if error_count:
      pprint(errors)
      print(f'\n{download_count} downloads {error_count} errors', flush=True)
      do_while = parseBool(input(f'Continue? [Yn]: '), True)
    else:
      print(f'\n{download_count} downloads {error_count} errors', flush=True)
      input(f'Exit? [Y]: ')
      do_while = False

asyncio.run(main())
