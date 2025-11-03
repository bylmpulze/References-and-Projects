import random as randomizer
import snake


# Feedspawn around 39x25 pixels ( 975 )
def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 27), randomizer.randint(0, 27)]
        if Coord not in snake.snake and Coord not in snake.feedCordrnd:
            return Coord
        




