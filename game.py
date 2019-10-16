from neat import nn, population
import pygame
import field
import food
import snake
import math
import sys
import pickle

rendering = True
blockSize = 32  # size of blocks
width = 12  # size of field width in blocks
height = 12
screenSize = (width * blockSize, height * blockSize)
speed = 1  # milliseconds per step
bg_color = 0x000000
snake_color = 0xFFFFFF

best_fitness = 0

# Initialize pygame and open a window
pygame.init()
screen = pygame.display.set_mode(screenSize)


pygame.time.set_timer(pygame.USEREVENT, speed)
clock = pygame.time.Clock()
scr = pygame.surfarray.pixels2d(screen)

dx = 1
dy = 0
generation_number = 0


def get_game_matrix(scr):
    global bg_color
    global snake_color
    res_matrix = []

    for i, x in enumerate(scr):
        res_arr = []
        if (i % blockSize == 0):
            for j, y in enumerate(x):
                if j % blockSize == 0:
                    if scr[i][j] == snake_color:
                        res_arr += [1]
                    elif scr[i][j] == bg_color:
                        res_arr += [0]
                    else:
                        res_arr += [2]
            res_matrix += [res_arr]

    # print res_matrix
    return res_matrix


def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    return obj


def positivy(x):
    if x > 0:
        return x
    else:
        return 0


def left(orientation):
    (dx, dy) = orientation
    if (dx, dy) == (-1, 0):
        dx, dy = 0, 1
    elif (dx, dy) == (0, 1):
        dx, dy = 1, 0
    elif (dx, dy) == (1, 0):
        dx, dy = 0, -1
    elif (dx, dy) == (0, -1):
        (dx, dy) = (-1, 0)
    return (dx, dy)


def right(orientation):
    (dx, dy) = orientation
    if (dx, dy) == (-1, 0):
        (dx, dy) = (0, -1)
    elif (dx, dy) == (0, -1):
        (dx, dy) = (1, 0)
    elif (dx, dy) == (1, 0):
        (dx, dy) = (0, 1)
    elif (dx, dy) == (0, 1):
        (dx, dy) = (-1, 0)

    return (dx, dy)


def get_inputs(game_matrix, position, orientation):  # (dx,dy)
    dx, dy = orientation
    # print "orientation",dx,dy
    position_x, position_y = position
    # print "position",position_x,position_y
    dist_straight_wall = 0
    dist_straight_food = 0
    dist_straight_tail = 0

    dist_left_wall = 0
    dist_left_food = 0
    dist_left_tail = 0

    dist_right_wall = 0
    dist_right_food = 0
    dist_right_tail = 0
    # print len(game_matrix) ,"rows"
    # print len(game_matrix[0]) ,"cols"
    # print game_matrix
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]):
        dist_straight_wall += 1
        position_x += dx
        position_y += dy
    # dist_straight_wall -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 2:
        dist_straight_food += 1
        position_x += dx
        position_y += dy
    # dist_straight_food -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 1 or (position_x, position_y) == position:
        dist_straight_tail += 1
        position_x += dx
        position_y += dy
    # dist_straight_tail -= 1

    position_x, position_y = position
    (dx, dy) = left(orientation)
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]):
        dist_left_wall += 1
        position_x += dx
        position_y += dy
    # dist_left_wall -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 2:
        dist_left_food += 1
        position_x += dx
        position_y += dy
    # dist_left_food -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 1 or (position_x, position_y) == position:
        dist_left_tail += 1
        position_x += dx
        position_y += dy
    # dist_left_tail -= 1

    position_x, position_y = position
    (dx, dy) = right(orientation)
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]):
        dist_right_wall += 1
        position_x += dx
        position_y += dy
    # dist_right_wall -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 2:
        dist_right_food += 1
        position_x += dx
        position_y += dy
    # dist_right_food -= 1
    position_x, position_y = position
    while position_x >= 0 and position_x < len(game_matrix) and position_y >= 0 and position_y < len(game_matrix[0]) and \
            game_matrix[position_x][position_y] != 1 or (position_x, position_y) == position:
        dist_right_tail += 1
        position_x += dx
        position_y += dy

    return [dist_straight_wall, dist_straight_food, dist_straight_tail, dist_left_wall, dist_left_food, dist_left_tail,
            dist_right_wall, dist_right_food, dist_right_tail]


def eval_fitness(genomes):
    global best_fitness
    global screen
    global width
    global height
    global blockSize
    global scr
    global generation_number
    global pop
    global bg_color
    global snake_color
    # global dx
    # global dy
    # global speed
    genome_number = 0
    for g in genomes:

        net = nn.create_feed_forward_phenotype(g)
        dx = 1
        dy = 0
        score = 0.0
        speed = 200
        hunger = 100
        # Create the field, the snake and a bit of food
        theField = field.Field(screen, width, height, blockSize, bg_color)
        theFood = food.Food(theField)
        theSnake = snake.Snake(theField, snake_color, 5)
        pygame.time.set_timer(pygame.USEREVENT, speed)
        snake_head_x, snake_head_y = theSnake.body[0]
        dist = math.sqrt((snake_head_x - theFood.x) ** 2 + (snake_head_y - theFood.y) ** 2)
        error = 0
        while True:

            event = pygame.event.wait()

            if event.type == pygame.QUIT:  # window closed
                print("Quittin")
                save_object(pop, 'population.dat')  ## export population
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT:  # timer elapsed
                matrix = get_game_matrix(scr)
                # print matrix
                head_x, head_y = theSnake.body[0]
                head_x += dx
                head_y += dy
                inputs = get_inputs(matrix, (head_x, head_y), (dx, dy))
                previous_state = inputs[1] < inputs[0]
                if inputs[4] < inputs[3]:
                    inputs[4] = 1
                else:
                    inputs[4] = 0

                if inputs[7] < inputs[6]:
                    inputs[4] = 1
                else:
                    inputs[4] = 0
                outputs = net.serial_activate(inputs)
                direction = outputs.index(max(outputs))
                if direction == 0:  # dont turn
                    # print "Straight"
                    pass

                if direction == 1:  # turn left
                    # print "Left"
                    (dx, dy) = left((dx, dy))
                if direction == 2:  # turn right
                    # print "Right"
                    (dx, dy) = right((dx, dy))

                hunger -= 1
                if not theSnake.move(dx, dy) or hunger <= 0:
                    break
                else:
                    inputs = get_inputs(matrix, (head_x, head_y), (dx, dy))
                    current_state = inputs[1] < inputs[0]

                    if inputs[1] <= 0:
                        inputs[1] = 1
                    if inputs[0] <= 0:
                        inputs[0] = 1
                    if inputs[2] <= 0:
                        inputs[2] = 1
                    wall, bread, tail, wall_left, bread_left, tail_left, wall_right, bread_right, tail_right = (inputs)
                    score += math.sqrt((theFood.x - theSnake.body[0][0]) ** 2 + (theFood.y - theSnake.body[0][1]) ** 2)
                    pass

            if theSnake.body[0] == (theFood.x, theFood.y):
                theSnake.grow()
                speed -= 5
                theFood = food.Food(theField)  # make a new piece of food
                score += 5
                hunger += 100
            if rendering:
                theField.draw()
                theFood.draw()
                theSnake.draw()
                pygame.display.update()
                # nao sei se isso ajuda :s parece que só ta lento mesmo
                # clock.tick(0)

            if event.type == pygame.KEYDOWN:  # key pressed
                if event.key == pygame.K_LEFT:
                    dx = -1
                    dy = 0
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                    dy = 0
                elif event.key == pygame.K_DOWN:
                    dx = 0
                    dy = 1
                elif event.key == pygame.K_UP:
                    dx = 0
                    dy = -1

        # Game over!
        if rendering:
            for i in range(0, 10):
                theField.draw()
                theFood.draw()
                theSnake.draw(damage=(i % 2 == 0))
                pygame.display.update()

        # pygame.time.wait(100)
        score = positivy(score) + 1
        g.fitness = positivy((-1 / (math.sqrt(score + 1))) + 1)
        best_fitness = max(best_fitness, g.fitness)
        print("Generation " + str(generation_number) + "\tGenome " + str(genome_number) + "\tFitness " + str(g.fitness) + "\tBest fitness " + str(best_fitness) + "\tError " + str(error) + "\tScore " + str(score) )
        genome_number += 1
    generation_number += 1
    if generation_number % 20 == 0:
        save_object(pop, 'population.dat')
        print("Exporting population")
        # export population
        # save_object(pop,'population.dat')
        # export population

pop = population.Population('config')
if len(sys.argv) > 1:
    pop = load_object(sys.argv[1])
    print("Reading popolation from " + sys.argv[1])
pop.run(eval_fitness, 10000)
