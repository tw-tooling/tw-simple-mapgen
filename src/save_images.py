import sys
from map_reader import read
from PIL import Image
from pathlib import Path


def save_images(filename):
    items, data = read(filename)

    # save images
    for item in items:
        if item.type == 2:  # image
            version, width, height, external, name_index, data_index = item.data
            name = data[name_index][:-1].decode("utf-8")
            if external == 0:
                print(f'saving {name}')
                img = Image.frombytes('RGBA', (width, height), data[data_index], 'raw')
                with open(Path(filename).stem + '_' + name + '.png', 'wb') as f:
                    img.save(f)
            else:
                print(f'skipping {name} (external)')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python save_images.py FILENAME')
        exit()
    save_images(sys.argv[1])
