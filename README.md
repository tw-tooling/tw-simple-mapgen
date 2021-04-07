# tw-utils

Python scripts including a gores map generator for teeworlds.

You can download the map generator application for windows [here](https://github.com/JonasLoos/tw-utils/releases/download/v0.1/tw-mapgen-windows.exe) (no installation required).

layered | spiral
--- | ---
![Map 1](https://user-images.githubusercontent.com/33965649/113918790-22136980-97e3-11eb-92ba-0c47300ed3e8.png) | ![Map 2](https://user-images.githubusercontent.com/33965649/113918826-2a6ba480-97e3-11eb-8a58-32b703fe92c6.png)

The scripts require Python 3.
All results are saved to the current working directory if no other path is specified.


## start gui (from source)

    python automapper.py


## create map

Generate a teeworlds map (the filename argument is optional):

```sh
    python create_random_blocks.py [FILENAME]
    python create_spiral.py [FILENAME]
    python create_layered.py [FILENAME]

    # if you want to set custom directions and config, change `create_something.py` and run
    python create_something.py
```

Those scripts utilize `create_map.py` to build and save the map file. The map is saved as `FILENAME`, with the default FILENAME being `newmap.map`.


## save images

Extract all images saved in a teeworlds map to the working directory (doesn't include referenced external images):

    python save_images.py PATH_TO_MAP


## generate gui application with pyinstaller

    pyinstaller tw-mapgen.py --onefile


## helpful teeworlds map-/datafile documentation:

* german map explanation: https://teeworlds-friends.de/thread/7563-roh-aufbau-einer-teeworlds-map/
* ddnet map documentation: https://ddnet.tw/libtw2-doc/map/
* teeworlds mapitem source: https://github.com/teeworlds/teeworlds/blob/master/src/game/mapitems.h
* twl datafile items source: https://github.com/Malekblubb/twl/blob/master/include/twl/files/map/map_datafile_items.hpp
* libtw2 datafile documentation: https://github.com/heinrich5991/libtw2/blob/master/doc/datafile.md
