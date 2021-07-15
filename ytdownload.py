#!/usr/bin/python

import sys
import pytube
import subprocess

url = sys.argv[1]
playlist_title = pytube.Playlist(url).title

def truthiness(s: str, default=True) -> bool:
  s = s.strip()
  if s in {'Y', 'y'}:
    return True
  elif s in {'N', 'n'}:
    return False
  else:
    return None if s else default

do_while = True
while do_while:
  playlist_name = ''
  if playlist_title:
    while playlist_name == '':
      playlist_name = input(f'Playlist name? [{playlist_title}]: ') or playlist_title
  audio_only = None
  while audio_only == None:
    audio_only = truthiness(input(f'Audio only? [Yn]: '), True)
  max_video_height = None
  while max_video_height == None:
    try:
      max_video_height = round(float(input(f'Max video height? [480]: ') or '480'))
    except ValueError:
      pass
  cmd = 'youtube-dl'
  cmd += f' {url}'
  if audio_only:
    cmd += f' -f "best[height<={max_video_height}]/best"'
    cmd += f' -x --audio-format "mp3"' # youtube-dl is dumb and only supports exporting to mp3
    cmd += f' --add-metadata --metadata-from-title "%(artist)s - %(title)s"'
    cmd += f' -o "~/storage/downloads/audio/{playlist_name}"'
  else:
    cmd += f' -f "bestvideo[height<={max_video_height}]+bestaudio/best[height<={max_video_height}]/best"'
    cmd += f' --merge-output-format "mkv" --recode-video "mkv"' # debian is stupid and has decades old ffmpeg and doesn't let you recode into mp4
    cmd += f' --write-sub --write-auto-sub --sub-lang "en,cs,rechat" --embed-subs'
    #cmd += f' --write-thumbnail --embed-thumbnail' # debian's youtube-dl is terrible and has broken dependencies for mp4 and doesn't support mkv
    cmd += f' -o "~/storage/downloads/video/{playlist_name}"'
  #dowhile = subprocess.run(cmd, shell=True).returncode
  print(cmd)
