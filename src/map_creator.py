# generate a teeworlds/ddnet map


import sys, zlib
import numpy as np
from collections import defaultdict



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
        return toByte((self.type << 16) + self.id) + toByte(len(self.data) * 4) + b''.join(toByte(x) for x in self.data)


def save_map(items, data, filename):
    '''generate a byte sequence from items and data, add required info and save it'''
    # compress data
    compressed_data = [zlib.compress(x) for x in data]

    # calculate itemtypes
    itemtypes = []
    items_considered_so_far = 0
    itemtypes_dict = defaultdict(lambda:0)
    for item in items:
        itemtypes_dict[item.type] += 1
    for i, count in sorted(itemtypes_dict.items()):
        itemtypes.append((i, items_considered_so_far, count))
        items_considered_so_far += count
    # for itemtype in range(7):  # TODO: check if 7 is the correct number of item types
    #     count = len([x for x in items if x.type == itemtype])
    #     if count > 0:
    #         itemtypes.append((itemtype, items_considered_so_far, count))
    #     items_considered_so_far += count

    # calculate header
    item_area_size = sum(len(x) for x in items)
    data_area_size = sum(len(x) for x in compressed_data)
    swaplen =  36 - 16 + 12*len(itemtypes) + 4*len(items) + 2*4*len(data) + item_area_size  # size before data (-16, because it starts after `swaplen`)
    size = swaplen + data_area_size  # size of everything after `swaplen`
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
    filename = filename if filename else 'newmap.map'
    with open(filename, 'wb') as f:
        f.write(result)


def create_map(game_matrix, tile_layers=[], filename=None):
    '''create the map items and data from a given matrix'''
    # ids should probably be unique per type
    # items should be ordered by type

    # add start items
    items = [Item(0, 0, [1]), Item(0, 1, [1] + [0xffffffff]*5)]  # add a `version 1` item at the beginning and an info block after

    # add image items
    # version, width, height, external, name, data
    for i, (imagename, matrix) in enumerate(tile_layers):
        items += [Item(i, 2, [1, 1024, 1024, 1, i, 0xffffffff])]

    # add group items
    # version, offset_x, offset_y, parallax_x, parallax_y, startlayer, numlayers, use_clipping, clip_x, clip_y, clip_w, clip_h, name
    name_empty = [0x80808080, 0x80808080, 0x80808000]  # item name: nothing
    name_game = [3353472485, 0x80808080, 0x80808000]  # item name: 'Game', ...
    items += [
        Item(0, 4, [3, 0, 0, 100, 100, 0, 1+len(tile_layers), 0, 0, 0, 0, 0] + name_game)
    ]

    # add layer items
    # version, type (invalid, game, tiles, quads), flags, ...
    # * tiles: ..., version, width, height, flags (Tiles,Game,Tele,Speedup,Front,Switch,Tune), color [r,g,b,a], colorenv, colorenv_offset, image, data, name
    # * quads: .., version, num_quads, data, image, name
    items += [
        # game layer
        Item(0, 5, [0, 2, 0, 3, game_matrix.shape[0], game_matrix.shape[1], 1, 255, 255, 255, 255, 0xffffffff, 0, 0xffffffff, len(tile_layers)] + name_game + [0xffffffff]*5)
    ]
    for i, (imagename, matrix) in enumerate(tile_layers,1):
        # tile layers
        items += [Item(i, 5, [0, 2, 0, 3, matrix.shape[0], matrix.shape[1], 0, 255, 255, 255, 255, 0xffffffff, 0, i-1, len(tile_layers)+i] + name_empty + [0xffffffff]*5)]

    # add end item
    items += [Item(0, 6, [])]  # add an empty envpoint item at the end

    # add ddnet special items
    # items += [
    #     Item(0, 0xfffe, [1, 0, 1, 0xffffffff, 0, 0]),
    #     Item(0xfffe, 0xffff, [1041966870, 395065720, 2614735130, 3762359768])
    # ]

    # add generated data
    data = []
    for imagename, matrix in tile_layers:
        data += [bytes(imagename+'\0','utf-8')]  # image names
    data += [game_matrix.tobytes()]  # game layer
    for imagename, matrix in tile_layers:
        data += [matrix.tobytes()]  # tiles layers

    # create bytestream and save it as map file
    save_map(items, data, filename)
