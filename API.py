from PIL import Image, ImageDraw, ImageFont
import Board
from DevStack import DevStack
import Player
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

# current proportion
cr_pr = 0.635 * 0.95
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
start_cr = (int(start_of_board_x + terrain_size[0] * 1.5 - crossroad_size[0] / 2),
            int(start_of_board_y - ter_mid_height - crossroad_size[1] / 2))

# associating players with colors
players = {1: {"background": yellow, "str": "yellow", "color": (255, 242, 0), "name": "none"},
           2: {"background": red, "str": "red", "color": (255, 0, 0), "name": "none"},
           3: {"background": green, "str": "green", "color": (35, 177, 77), "name": "none"},
           4: {"background": blue, "str": "blue", "color": (0, 162, 232)}, "name": "none"}

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

# dice location
line_space = int((50 / cr_pr) * proportion)
start_print_dice = (int((906 / cr_pr) * proportion), int((121 / (0.635 * 0.95)) * proportion))
die1_loc = (start_print_dice[0], start_print_dice[1])
die2_loc = (start_print_dice[0], start_print_dice[1] + line_space)
dice_loc = (start_print_dice[0], start_print_dice[1] + line_space * 2)

# board for testing
g_board = Board.Board()


# creating the terrain in the start of the game and saving it in images/temp/background.jpg
def show_terrain(map):
    # open starting image of background
    curr_img = background.copy()
    # setting the y location of the start of the terrain
    y = start_of_board_y
    # printing the terrain
    for line in range(5):
        x = start_of_board_x
        if line == 0 or line == 4:
            x += terrain_size[0]
        if line == 1 or line == 3:
            x += int(terrain_size[0] / 2)

        for terrain in map[line]:

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
                curr_num_img.save('images/temp/temp.jpg')
                curr_num_img = Image.open('images/temp/temp.jpg')
                curr_img.paste(curr_num_img, (x, y), number_mask)
            x += terrain_size[0]
        y += ter_top_mid_height
    curr_img.save('images/temp/background.jpg', quality=95)


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


def set_roads_locations(roads, crossroads):
    i = 0
    xor = False
    for line in roads:
        up = 0
        down = 0
        if i == 5:
            xor = True
        for road in line:
            x1 = crossroads[i][up].api_location[0] + int(crossroad_size[0] / 2)
            y1 = crossroads[i][up].api_location[1] + int(crossroad_size[1] / 2)
            x2 = crossroads[i + 1][down].api_location[0] + int(crossroad_size[0] / 2)
            y2 = crossroads[i + 1][down].api_location[1] + int(crossroad_size[1] / 2)
            road.api_location = (x1, y1, x2, y2)
            if i % 2:
                up += 1
                down += 1
            else:
                if (up == down) != xor:
                    down += 1
                else:
                    up += 1
        i += 1


def print_crossroads(crossroads):
    for line in crossroads:
        for cr in line:
            print_crossroad(cr)


def print_crossroad(cr):
    curr_img = Image.open("images/temp/background.jpg")
    if cr.ownership:
        color = players[cr.ownership]["background"].copy()
        if cr.building == 1:
            curr_img.paste(color, cr.api_location, village_mask)
        if cr.building == 2:
            curr_img.paste(color, cr.api_location, city_mask)
    curr_img.save("images/temp/background.jpg")


def print_road(road):
    curr_img = Image.open("images/temp/background.jpg")
    if road.owner:
        draw = ImageDraw.Draw(curr_img)
        draw.line(road.api_location, fill=players[road.owner]["color"], width=10)
    curr_img.save("images/temp/background.jpg")


def print_roads(roads):
    for line in roads:
        for road in line:
            print_road(road)


def next_turn(name):
    curr_img = Image.open("images/temp/background.jpg")
    curr_img.save("images/dst/game1/" + name + ".jpg")


def print_dice(dice, name):
    curr_img = Image.open("images/dst/game1/" + name + ".jpg")
    draw = ImageDraw.Draw(curr_img)
    draw.multiline_text(die1_loc, "First Die : " + str(dice.dice1), fill=(0, 0, 0), font=font)
    draw.multiline_text(die2_loc, "Second Die : " + str(dice.dice2), fill=(0, 0, 0), font=font)
    draw.multiline_text(dice_loc, "Sum of Dice : " + str(dice.sum), fill=(0, 0, 0), font=font)
    curr_img.save("images/dst/game1/" + name + ".jpg")


# first line location
line_x = 1100
line_y = 500


def dev_stack_test():
    a = DevStack()
    print(a.deck)


def player_test():
    cur_game=Game.Game()
    playerA = Player.Player(1)
    add_resources_test(playerA)
    print(playerA.resources)
    cur_game.buy_dev_card(playerA)
    playerA.buy_devops()
    assert len(playerA.devCards) == 1




def add_resources_test(player):
    for resource in Resource:
        if resource is not Resource.DESSERT:
            player.add_resources(resource, 6)


def print_inf(names, img):
    curr_img = Image.open("images/dst/game1/" + img + ".jpg")
    draw = ImageDraw.Draw(curr_img)
    draw.multiline_text((line_x, line_y), "hello world", fill=(0, 0, 0), font=font)
    i = 0
    for name in names:
        draw.multiline_text((line_x + 400 * i, line_y + 1 * line_space),
                            name + ":\n\n    Points:\n\n    Wheat:\n\n    Sheep:\n\n    Iron:\n\n    Wood:\n\n    "
                                   "Clay:\n\n    Active knights:\n\n    Sleeping nights:\n\n    Longest road:\n\n"
                                   "    Victory points:\n\n    Road builder:\n\n    Monopoly:\n\n    Year of "
                                   "prosper:\n\n",
                            fill=(0, 0, 0), font=font)
        i += 1
    curr_img.save("images/dst/game1/" + img + ".jpg")


def game_test():
    show_terrain(g_board.map)
    set_crossroads_locations(g_board.crossroads)
    print_crossroads(g_board.crossroads)
    set_roads_locations(g_board.roads, g_board.crossroads)
    print_roads(g_board.roads)
    print_inf(("shay", "shaked", "sheleg"), "turn8")
    dev_stack_test()
    player_test()

print("hello world")
game_test()
