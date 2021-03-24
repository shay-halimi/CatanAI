from PIL import Image, ImageDraw, ImageFont
import Board
import DevStack
import Game
from Resources import Resource

# where the board begin
start_of_board_x = 165
start_of_board_y = 572

# start image
background = Image.open('images/src/background.jpg')

# terrain images and their mask
sheep = Image.open('images/src/Sheep.jpg')
wheat = Image.open('images/src/Wheat.jpg')
wood = Image.open('images/src/Wood.jpg')
dessert = Image.open('images/src/Dessert.jpg')
clay = Image.open('images/src/Clay.jpg')
iron = Image.open('images/src/Iron.jpg')
# mask
terrain_mask = Image.open('images/src/mask.jpg').convert('L')

# the proportion of the board relative to original size
proportion = 0.635 * 0.95

# resizing the terrain and its mask by the proportion index
terrain_size = int(sheep.size[0] * proportion), int(sheep.size[1] * proportion)
sheep = sheep.resize(terrain_size)
wheat = wheat.resize(terrain_size)
wood = wood.resize(terrain_size)
dessert = dessert.resize(terrain_size)
clay = clay.resize(terrain_size)
iron = iron.resize(terrain_size)
terrain_mask = terrain_mask.resize(terrain_size)

# height of parts of the terrain after resizing
ter_top_mid_height = int(Image.open('images/src/sizeForY.jpg').size[1] * proportion)
ter_top_height = int(60 * proportion)
ter_mid_height = ter_top_mid_height - ter_top_height

# players colors backgrounds, crossroads masks and locations
yellow = Image.open('images/src/yellow square.jpg')
blue = Image.open('images/src/blue square.jpg')
red = Image.open('images/src/red square.jpg')
green = Image.open('images/src/green square.jpg')
# masks
village_mask = Image.open('images/src/village mask.jpg').convert('L')
city_mask = Image.open('images/src/city mask.jpg').convert('L')

# resizing players backgrounds and crossroads masks by the proportion index
crossroad_size = int(yellow.size[0] * proportion), int(yellow.size[1] * proportion)
yellow = yellow.resize(crossroad_size)
blue = blue.resize(crossroad_size)
red = red.resize(crossroad_size)
green = green.resize(crossroad_size)
village_mask = village_mask.resize(crossroad_size)
city_mask = city_mask.resize(crossroad_size)

# crossroads start locations
start_cr = (int(start_of_board_x + terrain_size[0] * 1.5 - crossroad_size[0] / 2)
            , int(start_of_board_y - ter_mid_height - crossroad_size[1] / 2))

# associating players with colors
players = {1: (yellow, "yellow"), 2: (red, "red"), 3: (green, "green"), 4: (blue, "blue")}

# production number image, its mask, font and location
number_img = Image.open('images/src/yellow.jpg')
# mask
number_mask = Image.open('images/src/circle_mask.jpg').convert('L')
# font
font_size = int(48 * proportion)
font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', font_size)
# location
num_loc = (int(81 * proportion), int(108 * proportion))

# resizing production number and its mask by the terrain size
number_img = number_img.resize(terrain_size)
number_mask = number_mask.resize(terrain_size)

# natural crossroad image
crossroad = Image.open('images/src/crossroad.jpg')

# board for testing
g_board = Board.Board()


def show_terrain(board):
    curr_img = background.copy()
    y = start_of_board_y
    for line in range(5):
        x = start_of_board_x
        if line == 0 or line == 4:
            x += terrain_size[0]
        if line == 1 or line == 3:
            x += int(terrain_size[0] / 2)
        for terrain in board.map[line]:

            if terrain.resource == Resource.IRON:
                curr_img.paste(iron, (x, y), terrain_mask)
            if terrain.resource == Resource.SHEEP:
                curr_img.paste(sheep, (x, y), terrain_mask)
            if terrain.resource == Resource.CLAY:
                curr_img.paste(clay, (x, y), terrain_mask)
            if terrain.resource == Resource.WHEAT:
                curr_img.paste(wheat, (x, y), terrain_mask)
            if terrain.resource == Resource.WOOD:
                curr_img.paste(wood, (x, y), terrain_mask)
            if terrain.resource == Resource.DESSERT:
                curr_img.paste(dessert, (x, y), terrain_mask)

            if terrain.num != 7:
                curr_num_img = number_img.copy()
                draw = ImageDraw.Draw(curr_num_img)
                if terrain.num == 6 or terrain.num == 8:
                    draw.multiline_text(num_loc, str(terrain.num), fill=(255, 0, 0), font=font)
                else:
                    draw.multiline_text(num_loc, str(terrain.num), fill=(0, 0, 0), font=font)
                curr_num_img.save('images/dst/temp.jpg')
                curr_num_img = Image.open('images/dst/temp.jpg')
                curr_img.paste(curr_num_img, (x, y), number_mask)
            x += terrain_size[0]
        y += ter_top_mid_height
    curr_img.save('images/dst/result5.jpg', quality=95)


def show_crossroads(temp_img):
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
            c_r = red.copy()
            temp_img.paste(c_r, (x, y), village_mask)
            x += terrain_size[0]
        even = not even
    temp_img.save('images/dst/crossroads2.jpg')


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


def print_crossroads(crossroads, temp_img):
    for line in crossroads:
        for cr in line:
            if cr.ownership:
                c_r = players[cr.ownership][0].copy()
                temp_img.paste(c_r, cr.api_location, village_mask)
    temp_img.save('images/dst/crossroads3.jpg')

def DevStackTest():
    a=DevStack()
    print(a.stack)

show_terrain(g_board)
background = Image.open('images/dst/result5.jpg')
show_crossroads(background)
background = Image.open('images/dst/result5.jpg')
set_crossroads_locations(g_board.crossroads)
Board.test_crossroads(g_board.crossroads)
print_crossroads(g_board.crossroads, background)
