# tw-utils

python scripts for teeworlds (requires python 3)

All results are saved to the current working directory.


## create map

Generate a teeworlds map (the filename argument is optional):

    python create_random_blocks.py [FILENAME]
    python create_spiral.py [FILENAME]

Those scripts utilize `create_map.py` to build and save the map file. The map is saved as `FILENAME.map`, with the default FILENAME being `newmap`.


## save images

Extract all images saved in a teeworlds map (doesn't include referenced external images):

    python save_images.py PATH_TO_MAP


## helpful teeworlds map-/datafile documentation:

* german map explanation: https://teeworlds-friends.de/thread/7563-roh-aufbau-einer-teeworlds-map/
* ddnet map documentation: https://ddnet.tw/libtw2-doc/map/
* teeworlds mapitem source: https://github.com/teeworlds/teeworlds/blob/master/src/game/mapitems.h
* twl datafile items source: https://github.com/Malekblubb/twl/blob/master/include/twl/files/map/map_datafile_items.hpp
* libtw2 datafile documentation: https://github.com/heinrich5991/libtw2/blob/master/doc/datafile.md
