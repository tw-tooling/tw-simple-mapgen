# generate a teeworlds/ddnet map

# helpful documentation:
# * german map explanation: https://teeworlds-friends.de/thread/7563-roh-aufbau-einer-teeworlds-map/
# * ddnet map documentation: https://ddnet.tw/libtw2-doc/map/
# * teeworlds mapitem source: https://github.com/teeworlds/teeworlds/blob/master/src/game/mapitems.h
# * twl datafile items source: https://github.com/Malekblubb/twl/blob/master/include/twl/files/map/map_datafile_items.hpp
# * libtw2 datafile documentation: https://github.com/heinrich5991/libtw2/blob/master/doc/datafile.md


import sys, zlib
import numpy as np



class CycleArray:
    '''cyclic numpy array'''
    def __init__(self, *args):
        self.arr = np.array(*args)
    def __getitem__(self, i):
        return self.arr[i % len(self)]
    def __len__(self):
        return len(self.arr)


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
    swaplen =  36 - 16 + 12*len(itemtypes) + 4*len(items) + 2*4*len(data) + item_area_size  # size before data (-16, because it starts after `swaplen`)
    size = swaplen + data_area_size  # size of everything after `swaplen`
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


# --------------------------------------------- map content creation below ---------------------------------------------


def generate_random_blocks():
    # create the map matrix
    m = np.zeros((200,200,4), dtype='B')

    # add content
    m[0,:,0] = 1  # top wall
    m[-1,:,0] = 1  # ground wall
    m[:,0,0] = 1  # left wall
    m[:,-1,0] = 1  # right wall
    m[-2,99,0] = 192  # spawn
    m[5:-5,5:-5,0] = np.random.rand(190,190) > 0.95  # random blocks

    # generate the map file
    create_map(m)


def generate_spiral():
    # config
    basesize = 200
    blocklen = 15
    obstacle_size = 2
    obstacle_side_switch_probability = 0.8
    obstacle_direction_change_probability = 0.2
    obstacle_freeze_probability = 0.8

    # create the map matrix
    size = np.array([basesize]*2)
    m = np.zeros((size[0],size[1],4), dtype='B')

    # add content
    sidelen = 1
    pos = size//2-1  # set position to center
    direction = 0
    directions = CycleArray([(0,-1),(-1,0),(0,1),(1,0)])
    pos += sidelen * blocklen // 2  # start with a bit offset from center
    newpos = pos + directions[direction] * sidelen * blocklen
    hellofromtheotherside = False  # side to grow obstacles from
    while 0 <= newpos[0]+blocklen*2 <= m.shape[0] and 0 <= newpos[1]+blocklen*2 <= m.shape[1]:
        # calculate position
        a = np.array([min(pos[0], newpos[0]),min(pos[1], newpos[1])])
        b = np.array([max(pos[0], newpos[0]),max(pos[1], newpos[1])]) + 1

        # create freeze
        currdir = directions[direction]
        nextdir = directions[direction + 1]
        a_ = a - nextdir - np.absolute(currdir)
        b_ = b - nextdir + np.absolute(currdir)
        m[a_[0]:b_[0],a_[1]:b_[1],0] = 9  # outer freeze
        a_ = a + nextdir + np.absolute(currdir)
        b_ = b + nextdir - np.absolute(currdir)
        m[a_[0]:b_[0],a_[1]:b_[1],0] = np.where(m[a_[0]:b_[0],a_[1]:b_[1],0] > 0, m[a_[0]:b_[0],a_[1]:b_[1],0], 9)  # inner freeze (dont overwrite obstacles)

        # create wall
        m[a[0]:b[0],a[1]:b[1],0] = 1

        # create obstacles
        growlen = blocklen//2
        first = True
        for startx in list(range(a[0], b[0], blocklen))[::currdir[0] or 1]:
            for starty in list(range(a[1], b[1], blocklen))[::currdir[1] or 1]:
                # skip first to avoid obstacle collisions
                if first:
                    first = False
                    continue
                putfreeze = np.random.choice([True, False], 1, p=[obstacle_freeze_probability,1-obstacle_freeze_probability])[0]
                # grow multiple obstacles at the same place to increase size
                for _ in range(obstacle_size):
                    # set start position and grow direction
                    if hellofromtheotherside:
                        grow_direction = direction + 1
                        pos = np.array([startx,starty]) - nextdir * blocklen
                    else:
                        grow_direction = direction + 3
                        pos = np.array([startx,starty]).copy()
                    start = pos.copy()
                    initial_grow_dir = directions[grow_direction]
                    pos += directions[grow_direction]
                    # grow obstacle
                    while ((pos-start) * initial_grow_dir >= 0).all() and sum((pos-start)**2) < growlen**2:
                        m[pos[0],pos[1],0] = 1  # grow obstacle block
                        if putfreeze and ((pos-start+directions[grow_direction]) * initial_grow_dir >= 0).all():  # only put freeze when not inside the wall
                            m[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2] = np.where(m[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2] > 0, m[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2], 9)  # put freeze around block, without overwriting
                        grow_direction += np.random.choice([-1,0,1], 1, p=[obstacle_direction_change_probability/2,1-obstacle_direction_change_probability,obstacle_direction_change_probability/2])[0]  # select random new grow direction
                        pos += directions[grow_direction]
                # randomly switch side
                hellofromtheotherside ^= np.random.choice([True, False], 1, p=[obstacle_side_switch_probability,1-obstacle_side_switch_probability])[0]

        # update variables for next run
        direction = (direction + 1) % len(directions)  # % is only needed to keey the variable small for performance reasons
        if direction in [0,2]:
            sidelen += 1
        pos = newpos
        newpos = pos + directions[direction] * sidelen * blocklen

    # generate last spiral round
    while 0 <= newpos[0]+blocklen <= m.shape[0] and 0 <= newpos[1]+blocklen <= m.shape[1]:
        # calculate position
        a = np.array([min(pos[0], newpos[0]),min(pos[1], newpos[1])])
        b = np.array([max(pos[0], newpos[0]),max(pos[1], newpos[1])]) + 1

        # create freeze
        currdir = directions[direction]
        nextdir = directions[direction + 1]
        a_ = a + nextdir + np.absolute(currdir)
        b_ = b + nextdir - np.absolute(currdir)
        m[a_[0]:b_[0],a_[1]:b_[1],0] = np.where(m[a_[0]:b_[0],a_[1]:b_[1],0] > 0, m[a_[0]:b_[0],a_[1]:b_[1],0], 9)  # inner freeze (dont overwrite obstacles)

        # create wall
        m[a[0]:b[0],a[1]:b[1],0] = 1

        # update variables for next run
        direction = (direction + 1) % len(directions)  # `%` is only needed to keep the variable small for performance reasons
        if direction in [0,2]:
            sidelen += 1
        pos = newpos
        newpos = pos + directions[direction] * sidelen * blocklen

    # create freeze free spawn with start
    mid = size//2-1
    a = mid - blocklen//2 + 1
    b = mid + blocklen//2
    m[a[0]:b[0],a[1]:b[1],0] = 0
    m[mid[0],mid[1],0] = 192  # create spawn
    m[mid[0]-blocklen//2:mid[0]+blocklen//2+1,mid[1]+blocklen//2+1,0] = 33  # create start line
    finish_line_start = pos - directions[direction-1]*blocklen
    finish_line_end = finish_line_start + directions[direction]*blocklen
    a = np.array([min(finish_line_start[0], finish_line_end[0]),min(finish_line_start[1], finish_line_end[1])])
    b = np.array([max(finish_line_start[0], finish_line_end[0]),max(finish_line_start[1], finish_line_end[1])]) + 1
    m[a[0]:b[0],a[1]:b[1],0] = np.where(m[a[0]:b[0],a[1]:b[1],0] == 1, 1, 34)  # create finish line without overwriting blocks

    # generate outer walls/nothing
    m[blocklen,:,0] = 0  # top wall
    m[-blocklen-1,:,0] = 0  # ground wall
    m[:,blocklen,0] = 0  # left wall
    m[:,-blocklen-1,0] = 0  # right wall

    # generate the map file
    create_map(m)



# generate a map when the script is called from the command line
if __name__ == "__main__":
    generate_spiral()
