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



def create_random_blocks(filename):
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
    create_map(m, filename)




# generate a map when the script is called from the command line
if __name__ == "__main__":
    filename = 'newmap.map'
    if len(sys.argv) > 1:
        filename = sys.argv[1] + '.map'
    create_random_blocks(filename)
