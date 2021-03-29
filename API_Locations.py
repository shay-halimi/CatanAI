# where the board begin
start_of_board_x = 165
start_of_board_y = 572

# crossroads start locations
start_cr = (int(start_of_board_x + terrain_size[0] * 1.5 - crossroad_size[0] / 2),
            int(start_of_board_y - ter_mid_height - crossroad_size[1] / 2))

def set_crossroads_locations(crossroads):
    y = start_cr[1]
    even = False
    step = -int(terrain_size[0] / 2)
    start = start_cr[0]
    for i in range(12):
        x = start
        if even:
            y += ter_top_height
        else:
            start += step
            y += ter_mid_height
        if i == 5:
            step *= -1
        for j in range(len(g_board.crossroads[i])):
            crossroads[i][j].api_location = (x, y)
            x += terrain_size[0]
        even = not even