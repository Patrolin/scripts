import os
import time
from PIL import Image
from zipfile import ZipFile


def tile(path: str, w: int = 3, h: int = 1):
    w, h = int(w), int(h)
    img: Image = Image.open(path)
    width, height = img.size
    if w < h:
        img = img.resize((w*height//h, height))
    else:
        img = img.resize((width, h*width//w))
    width, height = img.size
    wide = width/w
    tall = height/h
    path, _, file = path.rpartition('/')
    name, _, extension = file.rpartition('.')

    with ZipFile(f'{path}/{name}.zip', mode='w') as zippy:
        for a, b in enumerate(range(1, h+1)):
            for i, j in enumerate(range(1, w+1)):
                temp = f'out_{a}_{i}.{extension}'
                img.crop((round(i*wide), round(a*tall), round(j*wide), round(b*tall))).save(temp)
                zippy.write(temp)
                os.remove(temp)
                time.sleep(0.1)


if __name__ == '__main__':
    tile(*input('Image: ').split(' '))
