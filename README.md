# tw-utils

python scripts for teeworlds (requires python 3)

All results are saved to the current working directory.


## create map

Generate a teeworlds map:

    python create_random_blocks.py
    python create_spiral.py

Those scripts utilize `create_map.py` to build and save the map file


## save images

Extract all images saved in a teeworlds map (doesn't include referenced external images):

    python save_images.py PATH_TO_MAP
