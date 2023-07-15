import numpy as np
from map_creator import create_map
import sys



class CycleArray:
    '''cyclic numpy array'''
    def __init__(self, *args):
        self.arr = np.array(*args)
    def __getitem__(self, i):
        return self.arr[i % len(self.arr)]
    def __len__(self):
        return 2*30  # some very high number


def create_layered(
        filename=None,
        # config
        basesize = 200,
        blocklen = 20,
        min_wall_thickness = 1,  # on each side
        max_wall_thickness = 5 , # on each side
        wall_thickness_change_probability = 0.15,
        obstacle_growlen = 11,  # has be be less than sqrt(0.5) * blocklen - 2
        obstacle_size = 5,
        obstacle_side_switch_probability = 0.8,
        obstacle_direction_change_probability = 0.4,
        obstacle_freeze_probability = 1,
        block_wall = 1,
        block_corner = 1,
        block_obstacle = 1,
        block_freeze = 9,
        directions = None  # directions to build along
    ):
    directions = directions or CycleArray([2]*(basesize//blocklen-2) + [3] + [0]*(basesize//blocklen-2) + [3])

    # create the map matrix
    # 0: nothing, 1: normal, 3: unhookable, 33: start, 34: finish, 192: spwan
    size = np.array([basesize]*2)
    game = np.full((size[0],size[1],4), 1, dtype='B')

    # add content
    start_pos = np.array([blocklen,blocklen])
    pos = start_pos
    direction_i = 0
    rotations = CycleArray([(0,-1),(-1,0),(0,1),(1,0)])  # directions for rotations purposes
    newpos = pos + rotations[directions[direction_i]] * blocklen
    hellofromtheotherside = False  # side to grow obstacles from
    left_thickness = 1
    right_thickness = 1

    # clear way for first part
    forward = directions[direction_i]
    next_right = rotations[forward - 1]
    next_left = rotations[forward + 1]
    p1 = pos + next_left*blocklen//2
    p2 = pos + next_right*blocklen//2
    p3 = p1 + rotations[forward] * 3 * blocklen // 2
    p4 = p2 + rotations[forward] * 3 * blocklen // 2
    xa = min(p1[0],p2[0],p3[0],p4[0])
    xb = max(p1[0],p2[0],p3[0],p4[0])
    ya = min(p1[1],p2[1],p3[1],p4[1])
    yb = max(p1[1],p2[1],p3[1],p4[1])
    game[xa:xb,ya:yb,0] = 0

    # place one part of the way at a time until the border is reached or no directions are given
    while 0 <= newpos[0]+blocklen <= size[0] and 0 <= newpos[1]+blocklen <= size[1] and direction_i + 1 < len(directions):
        # directions
        forward = rotations[directions[direction_i]]
        left = rotations[directions[direction_i] - 1]
        right = rotations[directions[direction_i] + 1]

        last_dir = rotations[directions[direction_i - 1]]
        next_dir = rotations[directions[direction_i + 1]]
        less_left_start = all(last_dir == right)
        less_right_start = all(last_dir == left)
        less_left_end = all(next_dir == left)
        less_right_end = all(next_dir == right)
        left_start = 0 if less_right_start else (blocklen if less_left_start else blocklen//2)
        right_start = 0 if less_left_start else (blocklen if less_right_start else blocklen//2)
        left_end = blocklen if less_left_end else (2*blocklen if less_right_end else 3*blocklen//2)
        right_end = blocklen if less_right_end else (2*blocklen if less_left_end else 3*blocklen//2)

        # clear way for next
        next_right = rotations[directions[direction_i + 1] - 1]
        next_left = rotations[directions[direction_i + 1] + 1]
        p1 = newpos + next_left*blocklen//2
        p2 = newpos + next_right*blocklen//2
        p3 = p1 + next_dir * 3 * blocklen // 2
        p4 = p2 + next_dir * 3 * blocklen // 2
        xa = min(p1[0],p2[0],p3[0],p4[0])
        xb = max(p1[0],p2[0],p3[0],p4[0])
        ya = min(p1[1],p2[1],p3[1],p4[1])
        yb = max(p1[1],p2[1],p3[1],p4[1])
        game[xa:xb,ya:yb,0] = 0

        # calculate position
        pos_ = pos - forward * blocklen//2  # set pos further to make extension for corners possible
        newpos_ = newpos + forward * blocklen//2  # set newpos further to make extension for corners possible
        a = np.array([min(pos_[0], newpos_[0]),min(pos_[1], newpos_[1])])
        b = np.array([max(pos_[0], newpos_[0]),max(pos_[1], newpos_[1])]) + 1

        # create thick wall and add freeze
        i = 0
        for x in list(range(a[0], b[0], 1))[::forward[0] or 1]:
            for y in list(range(a[1], b[1], 1))[::forward[1] or 1]:
                # set blocks
                # left side
                if i >= left_start and i <= left_end:
                    x_ = x + left[0] * blocklen // 2
                    y_ = y + left[1] * blocklen // 2
                    xa = min(x_, x_ - left[0] * left_thickness)
                    xb = max(x_, x_ - left[0] * left_thickness)
                    ya = min(y_, y_ - left[1] * left_thickness)
                    yb = max(y_, y_ - left[1] * left_thickness)
                    game[xa:xb+1,ya:yb+1,0] = block_wall  # left side
                    tmpx = x_ - left[0] * left_thickness
                    tmpy = y_ - left[1] * left_thickness
                    tmp = game[tmpx-1:tmpx+2,tmpy-1:tmpy+2]
                    game[tmpx-1:tmpx+2,tmpy-1:tmpy+2] = np.where(tmp > 0, tmp, block_freeze)  # put left freeze around block, without overwriting
                    # set next thickness
                    p = wall_thickness_change_probability
                    left_thickness += np.random.choice([-1,0,1], 1, p=[p/2,1-p,p/2])[0]
                    if left_thickness > max_wall_thickness: left_thickness = max_wall_thickness
                    elif left_thickness < min_wall_thickness: left_thickness = min_wall_thickness
                # right side
                if i >= right_start and i <= right_end:
                    x_ = x + right[0] * blocklen // 2
                    y_ = y + right[1] * blocklen // 2
                    xa = min(x_, x_ - right[0] * right_thickness)
                    xb = max(x_, x_ - right[0] * right_thickness)
                    ya = min(y_, y_ - right[1] * right_thickness)
                    yb = max(y_, y_ - right[1] * right_thickness)
                    game[xa:xb+1,ya:yb+1,0] = block_wall  # right side
                    tmpx = x_ - right[0] * right_thickness
                    tmpy = y_ - right[1] * right_thickness
                    tmp = game[tmpx-1:tmpx+2,tmpy-1:tmpy+2]
                    game[tmpx-1:tmpx+2,tmpy-1:tmpy+2] = np.where(tmp > 0, tmp, block_freeze)  # put right freeze around block, without overwriting
                    # set next thickness
                    p = wall_thickness_change_probability
                    right_thickness += np.random.choice([-1,0,1], 1, p=[p/2,1-p,p/2])[0]
                    if right_thickness > max_wall_thickness: right_thickness = max_wall_thickness
                    elif right_thickness < min_wall_thickness: right_thickness = min_wall_thickness
                i += 1
        # generate left corners
        if less_left_end:
            for i in range(1,left_thickness+1):
                left_end_base = pos + forward * (left_end-blocklen//2) + left * blocklen//2
                start = left_end_base - left * i
                end = left_end_base - left * i + forward * (left_thickness-i)
                game[min(start[0],end[0]):max(start[0],end[0])+1, min(start[1],end[1]):max(start[1],end[1])+1, 0] = block_corner  # corner
                tmp = game[end[0]-1:end[0]+2,end[1]-1:end[1]+2]
                game[end[0]-1:end[0]+2,end[1]-1:end[1]+2] = np.where(tmp > 0, tmp, 9)  # put left freeze around block, without overwriting
        # generate right corners
        if less_right_end:
            for i in range(1,right_thickness+1):
                right_end_base = pos + forward * (right_end-blocklen//2) + right * blocklen//2
                start = right_end_base - right * i
                end = right_end_base - right * i + forward * (right_thickness-i)
                game[min(start[0],end[0]):max(start[0],end[0])+1, min(start[1],end[1]):max(start[1],end[1])+1, 0] = block_corner  # corner
                tmp = game[end[0]-1:end[0]+2,end[1]-1:end[1]+2]
                game[end[0]-1:end[0]+2,end[1]-1:end[1]+2] = np.where(tmp > 0, tmp, 9)  # put right freeze around block, without overwriting

        # create obstacle
        # TODO: allow obstacles in corners
        putfreeze = np.random.choice([True, False], 1, p=[obstacle_freeze_probability,1-obstacle_freeze_probability])[0]
        if not less_left_start and not less_right_start:  # dont create obstacles in corners
            # grow multiple obstacles at the same place to increase size
            for _ in range(obstacle_size):
                # set start position and grow direction
                if hellofromtheotherside:  # right
                    grow_direction = directions[direction_i] + 1
                    o_pos = pos - right * blocklen//2
                else:  # left
                    grow_direction = directions[direction_i] + 3
                    o_pos = pos - left * blocklen//2
                start = o_pos.copy()
                initial_grow_dir = rotations[grow_direction]
                o_pos += rotations[grow_direction]
                # grow obstacle
                while sum((o_pos-start)**2) < obstacle_growlen**2 and ((o_pos-start+rotations[grow_direction]) * initial_grow_dir >= 0).all():  # stop when going too far or when hitting a wall
                    game[o_pos[0],o_pos[1],0] = block_obstacle  # grow obstacle block
                    if putfreeze:
                        tmp = game[o_pos[0]-1:o_pos[0]+2,o_pos[1]-1:o_pos[1]+2]
                        game[o_pos[0]-1:o_pos[0]+2,o_pos[1]-1:o_pos[1]+2] = np.where(tmp > 0, tmp, block_freeze)  # put freeze around block, without overwriting
                    grow_direction += np.random.choice([-1,0,1], 1, p=[obstacle_direction_change_probability/2,1-obstacle_direction_change_probability,obstacle_direction_change_probability/2])[0]  # select random new grow direction
                    o_pos += rotations[grow_direction]
            # randomly switch side
            hellofromtheotherside ^= np.random.choice([True, False], 1, p=[obstacle_side_switch_probability,1-obstacle_side_switch_probability])[0]

        # update variables for next run
        direction_i += 1
        pos = newpos
        newpos = pos + rotations[directions[direction_i]] * blocklen


    # fill hole created for next
    next_right = rotations[directions[direction_i] - 1]
    next_left = rotations[directions[direction_i] + 1]
    p1 = pos + next_left*blocklen//2
    p2 = pos + next_right*blocklen//2
    p3 = p1 + next_dir * 3 * blocklen // 2
    p4 = p2 + next_dir * 3 * blocklen // 2
    xa = min(p1[0],p2[0],p3[0],p4[0])
    xb = max(p1[0],p2[0],p3[0],p4[0])
    ya = min(p1[1],p2[1],p3[1],p4[1])
    yb = max(p1[1],p2[1],p3[1],p4[1])
    game[xa:xb,ya:yb,0] = 1

    # create spawn and start line
    a = start_pos - blocklen//2 + 1
    b = start_pos + blocklen//2
    game[a[0]-1:b[0]+1,a[1]-1:b[1]+1,0] = 1  # add wall around spawn
    game[a[0]+1:b[0]-1,a[1]+1:b[1]-1,0] = 0  # remove stuff
    a += rotations[directions[0]]
    b += rotations[directions[0]]
    game[a[0]+1:b[0]-1,a[1]+1:b[1]-1,0] = 0  # remove stuff
    game[start_pos[0],start_pos[1],0] = 192  # create spawn
    start_line_start = start_pos + rotations[directions[0]] * (blocklen // 2) - rotations[directions[0] + 1] * (blocklen // 2 - 2)
    start_line_end = start_line_start + rotations[directions[0] + 1] * (blocklen - 4)
    a = np.array([min(start_line_start[0], start_line_end[0]),min(start_line_start[1], start_line_end[1])])
    b = np.array([max(start_line_start[0], start_line_end[0]),max(start_line_start[1], start_line_end[1])]) + 1
    game[a[0]:b[0],a[1]:b[1],0] = 33  # create start line
    tmp = start_pos + rotations[directions[0]] * blocklen//2

    # create finish line
    a = pos - blocklen//2 + 1
    b = pos + blocklen//2
    game[a[0]-1:b[0]+1,a[1]-1:b[1]+1,0] = 1  # add wall around finish area
    game[a[0]+1:b[0]-1,a[1]+1:b[1]-1,0] = 0  # remove stuff
    a -= forward
    b -= forward
    game[a[0]+1:b[0]-1,a[1]+1:b[1]-1,0] = 0  # remove stuff
    start_line_start = pos - forward * blocklen//2 + left * (blocklen // 2 - 2)
    start_line_end = start_line_start + right * (blocklen - 4)
    a = np.array([min(start_line_start[0], start_line_end[0]),min(start_line_start[1], start_line_end[1])])
    b = np.array([max(start_line_start[0], start_line_end[0]),max(start_line_start[1], start_line_end[1])]) + 1
    game[a[0]:b[0],a[1]:b[1],0] = 34  # create finish line

    # generate visual tile layers
    layer_unhookable = np.zeros(game.shape, dtype='B')
    layer_unhookable[:,:,0] = np.array(np.where(game[:,:,0] == 3, 8, 0), dtype='B')  # walls
    layer_desert = np.zeros(game.shape, dtype='B')
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 1, np.random.choice(np.array([7,64,65,70], dtype='B'), game[:,:,0].shape), 0), dtype='B')  # obstacles
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 9, 126, 0), dtype='B')  # freeze
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 33, 94, 0), dtype='B')  # start line
    layer_desert[:,:,0] += np.array(np.where(game[:,:,0] == 34, 94, 0), dtype='B')  # finish line

    # generate the map file
    create_map(game, [('generic_unhookable', layer_unhookable), ('desert_main', layer_desert)], filename=filename)



# generate a map when the script is called from the command line
if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_layered(filename=sys.argv[1])
    else:
        create_layered()
