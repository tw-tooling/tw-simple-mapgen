import sys, zlib


def toByte(x):
    return x.to_bytes(4, 'little')


def create_map():

    itemtypes = []
    items = []
    data = []

    # calculate the size by adding everything up (dont know why -16, maybe because not everything of the header is counted)
    item_area_size = 0  # TODO
    data_area_size = 0  # TODO
    size = 36 - 16 + 12*len(itemtypes) + 4*len(items) + 2*4*len(data) + item_area_size, data_area_size
    swaplen = 4192  # this is just a value used by another map; TODO: fix
    header = [4, size, swaplen, len(itemtypes), len(items), len(data), item_area_size, data_area_size]
    result = b'DATA'
    for x in header:
        result += toByte(x)

    # write
    with open('newmap.map', 'wb') as f:
        f.write(result)



if __name__ == "__main__":
    create_map()
