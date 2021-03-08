import sys, zlib


def toByte(x):
    return x.to_bytes(4, 'little')


class Item:
    def __init__(self, id, type, data):
        self.id = id
        self.type = type
        self.data = data
    
    def __len__(self):
        return (len(self.data) + 2) * 4

    def toByte(self):
        return toByte(self.type << 16 + self.id) + toByte(len(self.data) * 4) + b''.join(toByte(x) for x in self.data)


def save_map(items, data):
    # compress data
    compressed_data = [zlib.compress(x) for x in data]

    # calculate itemtypes
    itemtypes = []
    items_considered_so_far = 0
    for itemtype in range(7):  # TODO: check if 7 is correct
        count = len([x for x in items if x.type == itemtype])
        if count > 0:
            itemtypes.append((itemtype, items_considered_so_far, count))
        items_considered_so_far += count

    # calculate header
    item_area_size = sum(len(x) for x in items)
    data_area_size = sum(len(x) for x in compressed_data)
    # calculate the size by adding everything up (dont know why -16, maybe because not everything of the header is counted)
    size = 36 - 16 + 12*len(itemtypes) + 4*len(items) + 2*4*len(data) + item_area_size + data_area_size
    swaplen = 4192  # this is just a value used by another map; TODO: fix
    header = [4, size, swaplen, len(itemtypes), len(items), len(data), item_area_size, data_area_size]

    # create byte result
    result = b'DATA'
    # header
    for x in header:
        result += toByte(x)
    # itemtypes info
    for x in itemtypes:
        for y in x:
            result += toByte(y)
    # item offsets
    curr_offset = 0
    for x in items:
        result += toByte(curr_offset)
        curr_offset += len(x)
    # compressed data offsets
    curr_offset = 0
    for x in compressed_data:
        result += toByte(curr_offset)
        curr_offset += len(x)
    # uncompressed data offsets
    curr_offset = 0
    for x in data:
        result += toByte(curr_offset)
        curr_offset += len(x)
    # items
    for item in items:
        result += item.toByte()
    # compressed data
    for x in compressed_data:
        result += x

    # write
    with open('newmap.map', 'wb') as f:
        f.write(result)


def create_map():
    # ids should probably be unique per type
    # items should be ordered by type
    # layers: version, type (invalid, game, tiles, quads), flags, version, ...

    items = [Item(0, 0, [1])]  # add a `version 1` item at the beginning
    data = []

    # TODO

    items += [Item(0, 6, [])]  # add an empty envpoint? item at the end
    save_map(items, data)


if __name__ == "__main__":
    create_map()
