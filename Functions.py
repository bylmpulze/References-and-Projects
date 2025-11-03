import random as randomizer

#region restart
def restartenvironment ():
    global snake, direction, feedCordrnd, score, endgame
    snake = [[13, 13], [13, 14]]
    direction = 0
    feedCordrnd = [feedCordsRandomizer()]
    score = 0
    endgame = False


# Feedspawn around 39x25 pixels ( 975 )
def feedCordsRandomizer():
    while True:
        Coord = [randomizer.randint(0, 39), randomizer.randint(0, 39)]
        if Coord not in snake and Coord not in feedCordrnd:
            return Coord



