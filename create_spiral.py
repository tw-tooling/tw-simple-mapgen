import numpy as np
from map_creator import create_map
import sys



class CycleArray:
    '''cyclic numpy array'''
    def __init__(self, *args):
        self.arr = np.array(*args)
    def __getitem__(self, i):
        return self.arr[i % len(self)]
    def __len__(self):
        return len(self.arr)



def create_spiral(filename=None):
    # config
    basesize = 200
    blocklen = 15
    obstacle_size = 2
    obstacle_side_switch_probability = 0.8
    obstacle_direction_change_probability = 0.2
    obstacle_freeze_probability = 0.8

    # create the map matrix
    # 0: nothing, 1: normal, 3: unhookable, 33: start, 34: finish, 192: spwan
    size = np.array([basesize]*2)
    game = np.zeros((size[0],size[1],4), dtype='B')

    # add content
    sidelen = 1
    pos = size//2-1  # set position to center
    direction = 0
    directions = CycleArray([(0,-1),(-1,0),(0,1),(1,0)])
    pos += sidelen * blocklen // 2  # start with a bit offset from center
    newpos = pos + directions[direction] * sidelen * blocklen
    hellofromtheotherside = False  # side to grow obstacles from
    while 0 <= newpos[0]+blocklen*2 <= size[0] and 0 <= newpos[1]+blocklen*2 <= size[1]:
        # calculate position
        a = np.array([min(pos[0], newpos[0]),min(pos[1], newpos[1])])
        b = np.array([max(pos[0], newpos[0]),max(pos[1], newpos[1])]) + 1

        # create freeze
        currdir = directions[direction]
        nextdir = directions[direction + 1]
        a_ = a - nextdir - np.absolute(currdir)
        b_ = b - nextdir + np.absolute(currdir)
        game[a_[0]:b_[0],a_[1]:b_[1],0] = np.where(game[a_[0]:b_[0],a_[1]:b_[1],0] > 0, game[a_[0]:b_[0],a_[1]:b_[1],0], 9)  # outer freeze (dont overwrite obstacles)
        a_ = a + nextdir + np.absolute(currdir)
        b_ = b + nextdir - np.absolute(currdir)
        game[a_[0]:b_[0],a_[1]:b_[1],0] = np.where(game[a_[0]:b_[0],a_[1]:b_[1],0] > 0, game[a_[0]:b_[0],a_[1]:b_[1],0], 9)  # inner freeze (dont overwrite obstacles)

        # create wall
        game[a[0]:b[0],a[1]:b[1],0] = 1

        # make wall thick
        # TODO

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
                    while ((pos-start+directions[grow_direction]) * initial_grow_dir >= 0).all() and sum((pos-start)**2) < growlen**2:  # stop when going too far or when hitting the wall
                        game[pos[0],pos[1],0] = 1  # grow obstacle block
                        if putfreeze:
                            game[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2] = np.where(game[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2] > 0, game[pos[0]-1:pos[0]+2,pos[1]-1:pos[1]+2], 9)  # put freeze around block, without overwriting
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
    while 0 <= newpos[0]+blocklen <= size[0] and 0 <= newpos[1]+blocklen <= size[1]:
        # calculate position
        a = np.array([min(pos[0], newpos[0]),min(pos[1], newpos[1])])
        b = np.array([max(pos[0], newpos[0]),max(pos[1], newpos[1])]) + 1

        # create freeze
        currdir = directions[direction]
        nextdir = directions[direction + 1]
        a_ = a + nextdir + np.absolute(currdir)
        b_ = b + nextdir - np.absolute(currdir)
        game[a_[0]:b_[0],a_[1]:b_[1],0] = np.where(game[a_[0]:b_[0],a_[1]:b_[1],0] > 0, game[a_[0]:b_[0],a_[1]:b_[1],0], 9)  # inner freeze (dont overwrite obstacles)

        # create wall
        game[a[0]:b[0],a[1]:b[1],0] = 1

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
    game[a[0]:b[0],a[1]:b[1],0] = 0
    game[mid[0],mid[1],0] = 192  # create spawn
    game[mid[0]-blocklen//2:mid[0]+blocklen//2+1,mid[1]+blocklen//2+1,0] = 33  # create start line
    finish_line_start = pos - directions[direction-1]*blocklen
    finish_line_end = finish_line_start + directions[direction]*blocklen
    a = np.array([min(finish_line_start[0], finish_line_end[0]),min(finish_line_start[1], finish_line_end[1])])
    b = np.array([max(finish_line_start[0], finish_line_end[0]),max(finish_line_start[1], finish_line_end[1])]) + 1
    game[a[0]:b[0],a[1]:b[1],0] = np.where(np.isin(game[a[0]:b[0],a[1]:b[1],0], [1,3]), game[a[0]:b[0],a[1]:b[1],0], 34)  # create finish line without overwriting blocks

    # generate outer walls/nothing
    game[blocklen,:,0] = 0  # top wall
    game[-blocklen-1,:,0] = 0  # ground wall
    game[:,blocklen,0] = 0  # left wall
    game[:,-blocklen-1,0] = 0  # right wall

    # generate visual tile layers
    layer_unhookable = np.zeros(game.shape, dtype='B')
    layer_unhookable[:,:,0] = np.array(np.where(game[:,:,0] == 3, 8, 0), dtype='B')  # walls
    layer_desert = np.zeros(game.shape, dtype='B')
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 1, np.random.choice(np.array([6,7,64,65], dtype='B'), game[:,:,0].shape), 0), dtype='B')  # obstacles
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 9, 126, 0), dtype='B')  # freeze
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 33, 94, 0), dtype='B')  # start line
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 34, 94, 0), dtype='B')  # finish line

    # generate the map file
    create_map(game, [('generic_unhookable', layer_unhookable), ('desert_main', layer_desert)], filename=filename)



# generate a map when the script is called from the command line
if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_spiral(sys.argv[1])
    else:
        create_spiral()
