# generate a teeworlds/ddnet map

# helpful documentation:
# * german map explanation: https://teeworlds-friends.de/thread/7563-roh-aufbau-einer-teeworlds-map/
# * ddnet map documentation: https://ddnet.tw/libtw2-doc/map/
# * teeworlds mapitem source: https://github.com/teeworlds/teeworlds/blob/master/src/game/mapitems.h
# * twl datafile items source: https://github.com/Malekblubb/twl/blob/master/include/twl/files/map/map_datafile_items.hpp


import sys, zlib
import numpy as np



def toByte(x):
    '''convert an int to bytes'''
    return x.to_bytes(4, 'little')


class Item:
    def __init__(self, id, type, data):
        self.id = id
        self.type = type  # can one of: Version, Info, Image, Envelopes, Group, Layer, Envpoint, ...
        self.data = data  # structure depends on type
    
    def __len__(self):
        '''return the length if converted to bytes'''
        return (len(self.data) + 2) * 4

    def toByte(self):
        '''converte to bytestring'''
        return toByte(self.type << 16 + self.id) + toByte(len(self.data) * 4) + b''.join(toByte(x) for x in self.data)


def save_map(items, data):
    '''generate a byte sequence from items and data, add required info and save it'''
    # compress data
    compressed_data = [zlib.compress(x) for x in data]

    # calculate itemtypes
    itemtypes = []
    items_considered_so_far = 0
    for itemtype in range(7):  # TODO: check if 7 is the correct number of item types
        count = len([x for x in items if x.type == itemtype])
        if count > 0:
            itemtypes.append((itemtype, items_considered_so_far, count))
        items_considered_so_far += count

    # calculate header
    item_area_size = sum(len(x) for x in items)
    data_area_size = sum(len(x) for x in compressed_data)
    # calculate the size by adding everything up (dont know why -16, maybe because not everything of the header is counted)
    size = 36 - 16 + 12*len(itemtypes) + 4*len(items) + 2*4*len(data) + item_area_size + data_area_size
    swaplen = 328  # this is just a value used by another map; TODO: fix
    header = [4, size, swaplen, len(itemtypes), len(items), len(data), item_area_size, data_area_size]

    # create byte result
    result = b'DATA'
    # add header
    for x in header:
        result += toByte(x)
    # add itemtypes info
    for x in itemtypes:
        for y in x:
            result += toByte(y)
    # add item offsets
    curr_offset = 0
    for x in items:
        result += toByte(curr_offset)
        curr_offset += len(x)
    # add compressed data offsets
    curr_offset = 0
    for x in compressed_data:
        result += toByte(curr_offset)
        curr_offset += len(x)
    # add uncompressed data lengths
    for x in data:
        result += toByte(len(x))
    # add items
    for item in items:
        result += item.toByte()
    # add compressed data
    for x in compressed_data:
        result += x

    # write
    with open('newmap.map', 'wb') as f:
        f.write(result)


def create_map(matrix):
    '''create the map items and data from a given matrix'''
    # ids should probably be unique per type
    # items should be ordered by type

    # add start items
    items = [Item(0, 0, [1]), Item(0, 1, [1] + [0xffffffff]*5)]  # add a `version 1` item at the beginning and an info block after

    # add group items
    # version, offset_x, offset_y, parallax_x, parallax_y, startlayer, numlayers, use_clipping, clip_x, clip_y, clip_w, clip_h, name
    # name_empty = [0x80808080, 0x80808080, 0x80808000]  # item name: nothing
    name_game = [3353472485, 0x80808080, 0x80808000]  # item name: 'Game', ...
    items += [
        Item(0, 4, [3, 0, 0, 100, 100, 0, 1, 0, 0, 0, 0, 0] + name_game)
    ]

    # add layer items
    # version, type (invalid, game, tiles, quads), flags, ...
    # * tiles: ..., version, width, height, type, color (rgba), colorenv, colorenv_offset, image, data, name
    # * quads: .., version, num_quads, data, image, name
    items += [
        # game layer
        Item(0, 5, [0,2,0, 3, matrix.shape[0], matrix.shape[1], 1, 0xff,0xff,0xff,0xff, 0xffffffff, 0, 0xffffffff, 0] + name_game + [0xffffffff]*5)
    ]

    # add end item
    items += [Item(0, 6, [])]  # add an empty envpoint item at the end

    # add generated data
    data = [matrix.tobytes()]

    # create bytestream and save it as map file
    save_map(items, data)


def generate_map():
    '''generate a matrix which represents the map'''
    # create the map matrix
    m = np.zeros((200,200,4), dtype='B')

    # add content
    m[0,:,0] = 1  # top wall
    m[-1,:,0] = 1  # ground wall
    m[:,0,0] = 1  # left wall
    m[:,-1,0] = 1  # right wall
    m[-2,99,0] = 192  # spawn
    m[5:-5,5:-5,0] = np.random.rand(190,190) > 0.95

    # generate the map file
    create_map(m)



# generate a map when the script is called from the command line
if __name__ == "__main__":
    generate_map()
