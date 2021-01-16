from PIL import Image, ImageDraw, ImageFont
import Board
from Resources import Resource

print("hello to api")
background = Image.open('images/src/background.jpg')
sheep = Image.open('images/src/Sheep.jpg')
wheat = Image.open('images/src/Wheat.jpg').resize(sheep.size)
wood = Image.open('images/src/Wood.jpg').resize(sheep.size)
dessert = Image.open('images/src/Dessert.jpg').resize(sheep.size)
clay = Image.open('images/src/Clay.jpg').resize(sheep.size)
iron = Image.open('images/src/Iron.jpg').resize(sheep.size)
yellow = Image.open('images/src/yellow.jpg').resize(sheep.size)
mask_circle = Image.open('images/src/circle_mask.jpg').resize(sheep.size).convert('L')
mask = Image.open('images/src/mask.jpg').resize(sheep.size).convert('L')
temp = background.copy()
temp.paste(sheep, (100, 100), mask)
temp.paste(wheat, (400, 100), mask)
temp.paste(wood, (700, 100), mask)
temp.paste(dessert, (100, 400), mask)
temp.paste(clay, (400, 400), mask)
temp.paste(iron, (700, 400), mask)
temp.save('images/dst/result2.jpg', quality=95)
temp = yellow.copy()
draw = ImageDraw.Draw(temp)
font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', 48)
draw.multiline_text((81, 108), '12', fill=0, font=font)
temp.save('images/dst/text.jpg', quality=95)
twelve = Image.open("images/src/12.jpg")


board = Board.Board()

my_background = Image.open('images/src/background.jpg')


def show_terrain():
    temp_img = my_background.copy()
    y = 50
    for line in range(5):
        x = 50
        if line == 0:
            x += 228
        if line == 1:
            x += 114
        if line == 2:
            x += 0
        if line == 3:
            x += 114
        if line == 4:
            x += 228
        for terrain in board.map[line]:
            if terrain.resource == Resource.IRON:
                temp_img.paste(iron, (x, y), mask)
            if terrain.resource == Resource.SHEEP:
                temp_img.paste(sheep, (x, y), mask)
            if terrain.resource == Resource.CLAY:
                temp_img.paste(clay, (x, y), mask)
            if terrain.resource == Resource.WHEAT:
                temp_img.paste(wheat, (x, y), mask)
            if terrain.resource == Resource.WOOD:
                temp_img.paste(wood, (x, y), mask)
            if terrain.resource == Resource.DESSERT:
                temp_img.paste(dessert, (x, y), mask)
            if terrain.num != 7:
                number = yellow.copy().resize(sheep.size)
                draw = ImageDraw.Draw(number)
                if terrain.num == 6 or terrain.num == 8:
                    draw.multiline_text((81, 108), str(terrain.num), fill=(255, 0, 0), font=font)
                else:
                    draw.multiline_text((81, 108), str(terrain.num), fill=(0,0,0), font=font)
                number.save('images/dst/temp.jpg')
                number = Image.open('images/dst/temp.jpg')
                temp_img.paste(number, (x,y), mask_circle)
            x += 228
        y += 196
    temp_img.save('images/dst/result5.jpg', quality=95)


def show_crossroads():
    for i in range(12):
        pass


show_terrain()
