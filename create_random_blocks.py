import numpy as np
from map_creator import create_map
import sys



def create_random_blocks(filename=None):
    # create the map matrix
    game = np.zeros((200,200,4), dtype='B')
    tiles = np.zeros((200,200,4), dtype='B')

    # add content
    game[0,:,0] = 1  # top wall
    game[-1,:,0] = 1  # ground wall
    game[:,0,0] = 1  # left wall
    game[:,-1,0] = 1  # right wall
    game[-2,99,0] = 192  # spawn
    game[5:-5,5:-5,0] = np.random.rand(190,190) > 0.95  # random blocks
    tiles[0,:,0] = 1  # top wall
    tiles[-1,:,0] = 1  # ground wall
    tiles[:,0,0] = 1  # left wall
    tiles[:,-1,0] = 1  # right wall

    # generate the map file
    create_map(game, [('generic_unhookable', tiles)], filename=filename)



# generate a map when the script is called from the command line
if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_random_blocks(sys.argv[1])
    else:
        create_random_blocks()
