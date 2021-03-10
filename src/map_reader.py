# read a teeworlds map

# for links to documentation see `map_creator.py`


import sys, zlib



def readInt(f):
    return int.from_bytes(f.read(4), byteorder='little')


def intsToStr(arr):
    return ''.join(chr(y-128) if y >= 128 else '\0' for x in arr for y in x.to_bytes(4, 'big'))


class Item:
    def __init__(self, f):
        type_and_id = readInt(f)
        # header (8)
        self.type = (type_and_id >> 16) & 0xffff
        self.id = type_and_id & 0xffff
        self.len = readInt(f)
        # print(f'{self.type = }, {self.id = }, {self.len = }')
        self.data = [readInt(f) for i in range(self.len//4)]

# class VersionItem(Item):
#     def __init__(self, f):
#         super().__init__(f)
#         # version (4)
#         self.version = readInt(f)

# class InfoItem(VersionItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # info (16)
#         self.author_index = readInt(f)
#         self.map_version_index = readInt(f)
#         self.credits_index = readInt(f)
#         self.license_index = readInt(f)

# class ImageItem(VersionItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # image (24)
#         self.width = readInt(f)
#         self.height = readInt(f)
#         self.external = readInt(f)
#         self.name = readInt(f)
#         self.data = readInt(f)

# class EnvelopesItem(VersionItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # envelopes (60)
#         self.channels = readInt(f)
#         self.start_point = readInt(f)
#         self.num_point = readInt(f)
#         self.name = tuple(readInt(f) for i in range(3))
#         self.syncron = readInt(f)
#         # TODO: check if smth is missing

# class GroupItem(VersionItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # group (60)
#         self.offset_x = readInt(f)
#         self.offset_y = readInt(f)
#         self.parallax_x = readInt(f)
#         self.parallax_y = readInt(f)
#         self.startlayer = readInt(f)
#         self.numlayers = readInt(f)
#         self.use_clipping = readInt(f)
#         self.clip_x = readInt(f)
#         self.clip_y = readInt(f)
#         self.clip_w = readInt(f)
#         self.clip_h = readInt(f)
#         self.name = tuple(readInt(f) for i in range(3))

# class LayerItem(VersionItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # layer
#         self.type = readInt(f)  # invalid, game, tiles, quads
#         self.flags = readInt(f)

# class TilemapLayerItem(LayerItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # tilemap layer
#         self.version = readInt(f)
#         self.width = readInt(f)
#         self.height = readInt(f)
#         self.flags = readInt(f)
#         self.color = tuple(readInt(f) for i in range(4))  # rgba
#         self.colorenv = readInt(f)
#         self.colorenv_offset = readInt(f)
#         self.image = readInt(f)
#         self.data = readInt(f)
#         self.name = tuple(readInt(f) for i in range(3))

# class QuadLayerItem(LayerItem):
#     def __init__(self, f):
#         super().__init__(f)
#         # tilemap layer ()
#         self.version = readInt(f)
#         self.num_quads = readInt(f)
#         self.data = readInt(f)
#         self.image = readInt(f)
#         self.name = [readInt(f) for i in range(3)]

# class EnvpointItem(Item):
#     def __init__(self, f):
#         super().__init__(f)
#         # envpoint (24)
#         envpoint_time = readInt(f)
#         envpoint_curvetype = readInt(f)
#         envpoint_values = tuple(readInt(f) for i in range(4))

# ITEM_TYPES = [VersionItem, InfoItem, ImageItem, EnvelopesItem, GroupItem, LayerItem, EnvpointItem, None, None]


def read(filename, verbose=False):
    with open(filename, "rb") as f:
        # read header
        signature = f.read(4)
        version, size, swaplen, num_itemtypes, num_items, num_rawdata, item_area_size, data_area_size = [readInt(f) for i in range(8)]
        if verbose: print(f'header: {version = }, {size = }, {swaplen = }, {num_itemtypes = }, {num_items = }, {num_rawdata = }, {item_area_size = }, {data_area_size = }')

        # read items info
        itemtypes = [tuple(readInt(f) for x in range(3)) for i in range(num_itemtypes)]  # (type, start, count)
        item_offsets = [readInt(f) for i in range(num_items)]
        # item_lengths = [b-a for a, b in zip(item_offsets, item_offsets[1:] + [item_area_size])]
        if verbose: print(f'{itemtypes = }')

        # read compressed data info
        compressed_data_offsets = [readInt(f) for i in range(num_rawdata)]
        compressed_data_lengths = [b-a for a, b in zip(compressed_data_offsets, compressed_data_offsets[1:] + [data_area_size])]
        uncompressed_data_lengths = [readInt(f) for i in range(num_rawdata)]

        # read items
        items = [Item(f) for i in range(num_items)]

        # read compressed data
        data = [zlib.decompress(f.read(l)) for l in compressed_data_lengths]

        # print info
        if verbose:
            print('item types:')
            for i, typename in enumerate(['version', 'info', 'image', 'envelopes', 'group', 'layer', 'envpoint']):
                print(f'{len([x for x in items if x.type == i]):4d} {typename}')
            print('items:')
            for item in items:
                print(f'{item.id:3d} {item.type}: {item.data}')
            print(f'data ({data_area_size} / {sum(uncompressed_data_lengths)}):')
            for x in data:
                print(f'{len(x):3d} - {x[:30]} ...')

        # done
        return items, data



if __name__ == "__main__":
    # check argument
    if len(sys.argv) != 2:
        print('one arg required')
        exit()

    # read map and print info
    read(sys.argv[1], verbose=True)
