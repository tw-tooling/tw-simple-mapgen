from create_layered import create_layered, CycleArray



create_layered(
    filename=None,
    # config
    basesize = 300,
    blocklen = 20,
    growlen = 11,  # has be be less than sqrt(0.5) * blocklen - 2
    min_wall_thickness = 1,  # on each side
    max_wall_thickness = 5 , # on each side
    wall_thickness_change_probability = 0.15,
    obstacle_size = 5,
    obstacle_side_switch_probability = 0.8,
    obstacle_direction_change_probability = 0.4,
    obstacle_freeze_probability = 1,
    block_wall = 1,
    block_corner = 1,
    block_obstacle = 1,
    block_freeze = 9,
    directions = [2,2,2,3,3,3,2,1,1,1,2,2,3,3,3,2,1,1,1,2,2,2,2]  # directions to build along
)
