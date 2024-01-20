import pygame
import pymunk
import sys
import random
import os
import math
import time

from network import Network

net = Network()


# Initialize Pygame
pygame.init()

# Set up the screen
width, height = 1200, 760
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Suika Game")

bg = pygame.image.load("blits/background.jpg").convert()
bg = pygame.transform.scale(bg, (width, height))

# Set up the clock
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, -500)

# ORDER: CHERRY, STRAWBERRY, GRAPE, DEKOPON, ORANGE, APPLE, PEAR, PEACH, PINEAPPLE, MELON, WATERMELON
listOfFruits = ["blueberry", "raspberry", "grapes", "banana", "orange", "apple", "lemon", "pomegranate", "plum", "melon"] # i removed the pineapple lol

suikaDictionary = {
    "blueberry": {
        "mass": 5,
        "radius": 10,
        "color": (68,76,148),
        "score": 1
    },
    "raspberry": {
        "mass": 10,
        "radius": 15,
        "color": (232,34,50),
        "score": 3
    },
    "grapes": {
        "mass": 20,
        "radius": 23,
        "color": (190,240,113),
        "score": 4
    },
    "banana": {
        "mass": 40,
        "radius": 30,
        "color": (255,230,73),
        "score": 7
    },
    "orange": {
        "mass": 50,
        "radius": 45,
        "color": (254,102,10),
        "score": 10
    },
    "apple": {
        "mass": 80,
        "radius": 60,
        "color": (229,10,0),
        "score": 15
    },
    "lemon": {
        "mass": 100,
        "radius": 80,
        "color": (223,245,0),
        "score": 26
    },
    "pomegranate": {
        "mass": 120,
        "radius": 100,
        "color": (185,20,35),
        "score": 49
    },
    "pineapple": {
        "mass": 140,
        "radius": 140,
        "color": (247, 225, 63),
        "score": 63
    },
    "plum": {
        "mass": 150,
        "radius": 150,
        "color": (103,27,134),
        "score": 87
    },
    "melon": {
        "mass": 170,
        "radius": 170,
        "color": (167,211,56),
        "score": 145
    },
}

images = {
    fruit: pygame.transform.scale(
        pygame.image.load(f"blits/{fruit}.png").convert_alpha(), (suikaDictionary[fruit]["radius"] * 2, suikaDictionary[fruit]["radius"] * 2)
    ) 
    for fruit in listOfFruits
}

grayscale_images = {
    fruit: pygame.transform.scale(
        pygame.image.load(f"blits/{fruit}_grayscale.png").convert_alpha(), (suikaDictionary[fruit]["radius"] * 2, suikaDictionary[fruit]["radius"] * 2)
    ) 
    for fruit in listOfFruits
}


def send_data(score, fruits, garbage):
    if len(fruits) == 0:
        fruit_data = "n"
    else:
        fruit_data = '|'.join(f"{fruit.index}/{round(fruit.position[0], 3)}/{round(fruit.position[1], 3)}/{round(fruit.body.angle, 2)}" for fruit in fruits) 

    if len(garbage) == 0:
        garbage_data = "n"
    else:
        garbage_data = str(garbage[0])

    data = str(net.id) + ":" + str(score) + "_" + fruit_data + "_" + garbage_data
    return data

class PreFruit:
    def __init__(self, x, y, type):
        self.type = type
        self.mass = suikaDictionary[type]["mass"]
        self.radius = suikaDictionary[type]["radius"]
        self.color = suikaDictionary[type]["color"]
        self.image = images[type]

        pre_fruit_moment = pymunk.moment_for_circle(float('inf'), 0, 0)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, 0)

        self.shape.collision_type = 1  # Set a unique collision type for the static body
        self.shape.elasticity = 0
    
    def update(self, x, y):
        self.body.position = x, y

    def draw(self, screen):
        # Draw the pre-fruit
        pre_fruit_pos = int(self.body.position.x), height - int(self.body.position.y)
        screen.blit(self.image, (pre_fruit_pos[0] - self.radius, pre_fruit_pos[1] - self.radius))
    
    def release(self, space):
        return Fruit(self.type, space, self.body.position[0], self.body.position[1])

class Fruit:
    def __init__(self, type, space, x, y):
        # Create a watermelon (Suika) sprite
        self.type = type
        self.index = listOfFruits.index(type)
        self.mass = suikaDictionary[type]["mass"]
        self.radius = suikaDictionary[type]["radius"]
        self.color = suikaDictionary[type]["color"]
        self.image = images[type]

        suika_moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, suika_moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
      
        self.shape.collision_type = 5
        self.shape.user_data = self
        self.shape.elasticity = 0
        self.shape.friction = 0.9
        
        space.add(self.body, self.shape)

    def draw(self, screen):
        # Draw the watermelon with rotation
        suika_pos = int(self.body.position.x), height - int(self.body.position.y)
        rotated_image = pygame.transform.rotate(self.image, -self.body.angle * 180 / 3.14)
        rotated_rect = rotated_image.get_rect(center=suika_pos)
        screen.blit(rotated_image, rotated_rect.topleft)

    @property
    def position(self):
        return self.body.position
    
class GarbageFruit:
    def __init__(self, type, space, x, y):
        # Create a watermelon (Suika) sprite
        self.type = type
        self.index = listOfFruits.index(type)
        self.mass = suikaDictionary[type]["mass"] + 40
        self.radius = suikaDictionary[type]["radius"]
        self.color = (128,128,128)
        self.image = grayscale_images[type]

        suika_moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, suika_moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
      
        self.shape.collision_type = 5
        self.shape.user_data = self
        self.shape.elasticity = 0
        self.shape.friction = 0.9
        
        space.add(self.body, self.shape)

    def draw(self, screen):
        # Draw the watermelon with rotation
        suika_pos = int(self.body.position.x), height - int(self.body.position.y)
        rotated_image = pygame.transform.rotate(self.image, -self.body.angle * 180 / 3.14)
        rotated_rect = rotated_image.get_rect(center=suika_pos)
        screen.blit(rotated_image, rotated_rect.topleft)

    @property
    def position(self):
        return self.body.position

class Container:
    def __init__(self, containerWidth: int, containerHeight: int, x=None, y=None):
        self.w = containerWidth
        self.h = containerHeight
        # self.id = saosmaosa

        if not (x or y):
            # Center the container if x and y are not provided
            self.HorizontalDist = (width - containerWidth) / 2
            self.VerticalDist = (height - containerHeight) / 2
        else:
            # Use provided x and y values
            self.HorizontalDist = x
            self.VerticalDist = y

        # Standard ratio is 1w : 1.25h
        left_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_wall_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        # left wall
        left_wall_shape = pymunk.Segment(left_wall_body, (self.HorizontalDist, height - self.VerticalDist),
                                         (self.HorizontalDist, height - self.VerticalDist - self.h), 5)
        left_wall_shape.friction = 0.5
        space.add(left_wall_body, left_wall_shape)

        # right wall
        right_wall_shape = pymunk.Segment(right_wall_body, (self.w + self.HorizontalDist, height - self.VerticalDist),
                                          (self.w + self.HorizontalDist, height - self.VerticalDist - self.h), 5)
        right_wall_shape.friction = 0.5
        space.add(right_wall_body, right_wall_shape)

        # floor
        self.floor = pymunk.Segment(space.static_body, (self.HorizontalDist, height - self.VerticalDist - self.h),
                                    (self.w + self.HorizontalDist, height - self.VerticalDist - self.h), 5)
        space.damping = 0.8
        space.add(self.floor)

    def draw(self, screen):
        pygame.draw.line(screen, "white", (self.HorizontalDist, self.VerticalDist),
                        (self.HorizontalDist, self.VerticalDist + self.h), 5)
        
        pygame.draw.line(screen, "white", (self.HorizontalDist + self.w, self.VerticalDist),
                        (self.HorizontalDist + self.w, self.VerticalDist + self.h), 5)
        
        pygame.draw.line(screen, "white", (self.HorizontalDist, self.VerticalDist + self.h),
                        (self.w + self.HorizontalDist, self.VerticalDist + self.h), 5)


    @property
    def width(self):
        return self.w

    @property
    def height(self):
        return self.h

class Particle:
    def __init__(self, x, y, color, size):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity = (random.uniform(3, 10) * random.choice([-1, 1]), random.uniform(3, 10) * random.choice([-1, 1]))
        self.life = 255 # number of frames the particle will exist

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        self.life -= 1

    def draw(self, screen):
        opacity = max(self.life, 0)
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2], opacity), (int(self.x), int(self.y)), self.size)

class Snow:
    def __init__(self):
        # Define snowflake properties
        self.snowflake_radius = 2
        self.snowflake_color = (250, 250, 255)
        self.iterations = 0

        self.snowflakes = []

    def update(self):
        self.iterations += 1
        
        if self.iterations % 9 == 1:
            self.snowflakes.append((random.randint(0, width), random.randint(0, height)))

        self.snowflakes = [(x, y + 1) for (x, y) in self.snowflakes if y < height]

    def drawSnowflakes(self, screen):
        for i, (x, y) in enumerate(self.snowflakes):
            if y > height + 10:
                self.snowflakes.pop(i)
            else:
                pygame.draw.circle(screen, self.snowflake_color, (x, y), self.snowflake_radius)

class Scoreboard:
    def __init__(self, container):
        self.font = pygame.font.Font("slime.ttf", round(container.height / 30)) 
        self.x, self.y = container.HorizontalDist + container.width + 15, container.VerticalDist + 50 
        self.score = 0
        self.tick = 0

    def draw(self, screen):
        self.tick += 0.05

        score_text = self.font.render(str(self.score), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.x + len(str(self.score)) * 10, self.y + 10 * math.sin(self.tick)))
        
        screen.blit(score_text, score_rect.topleft)

class ComboHandler:
    def __init__(self):
        self.comboNumber = 0
        self.lastCombo = 0
        self.font = self.font = pygame.font.Font("slime.ttf", 50)
        self.shownNumbers = []       

    def incrementCombo(self, number, x, y, color, size):
        self.comboNumber += number
        self.shownNumbers.append([self.comboNumber, 
                                    [x + random.choice([-50, 30]), y - 30], 
                                        255,
                                            color,
                                                size
                                            ])
        self.lastCombo = 0

    def update(self):
        self.lastCombo += 1
        
        # reset combo
        if self.lastCombo > 500:
            self.comboNumber = 0

        # update opacity
        for i, item in enumerate(self.shownNumbers):
            if item[2] == 0:
                self.shownNumbers.pop(i)
            else:  
                item[1][1] -= 0.5
                item[2] -= 3

    def show(self, screen):
        for number, [x, y], opacity, color, size in self.shownNumbers:
            self.font = pygame.freetype.Font("slime.ttf", size)

            self.font.render_to(screen, (x, y), f"{number}", (color[0], color[1], color[2], opacity))

container = Container(containerWidth=450, containerHeight=690, x=60, y=50)
scoreboard = Scoreboard(container)

container2 = Container(containerWidth=450, containerHeight=690, x=640, y=50)
scoreboard2 = Scoreboard(container2)

snow = Snow()
combo_tracker = ComboHandler()

particles = []
garbage = []

# circle = pygame.image.load("blits/circle.png").convert_alpha()
# circle = pygame.transform.scale(circle, (container.HorizontalDist - 40, 1.07026144 * (container.HorizontalDist - 40)))

# merging
def merge_fruits(fruit1, fruit2, scoreboard, particles):
    
    if fruit1 in activeFruits and fruit2 in activeFruits:
        # add score
        scoreboard.score += suikaDictionary[fruit1.type]["score"]

        # midpoint
        new_x = (fruit1.position.x + fruit2.position.x) / 2
        new_y = (fruit1.position.y + fruit2.position.y) / 2

        # average velocity
        average_velocity_x = (fruit1.body.velocity.x + fruit2.body.velocity.x) / 2
        average_velocity_y = (fruit1.body.velocity.y + fruit2.body.velocity.y) / 2
    
        for _ in range(5):
            particle_color = fruit1.color
            particle_size = random.randint(5, 10)
            particles.append(Particle(new_x, height - new_y, particle_color, particle_size))

        # Get the index of the next fruit type
        current_type_index = listOfFruits.index(fruit1.type)
        next_type_index = current_type_index + 1 if fruit1.type != "melon" else 0 # back to blueberry

        # spawneth new fruit and apply velocity
        new_fruit = Fruit(listOfFruits[next_type_index], space, new_x, new_y)
        new_fruit.body.velocity = (average_velocity_x, average_velocity_y)

        activeFruits.append(new_fruit)

        # only send garbage fruit if neither are garbage fruit
        if not(isinstance(fruit1, GarbageFruit) or isinstance(fruit2, GarbageFruit)):     
            if combo_tracker.lastCombo <= 3000:
                combo_tracker.incrementCombo(1, new_x, height - new_y, new_fruit.color, new_fruit.radius * 2)
                scoreboard.score += (combo_tracker.comboNumber - 1) * 2

            # send garbage fruit
            garbage.append(listOfFruits.index(fruit1.type))

        # kill them all
        space.remove(fruit1.body, fruit1.shape)
        space.remove(fruit2.body, fruit2.shape)

        activeFruits.remove(fruit1)
        activeFruits.remove(fruit2)

def collision_handler(arbiter, space, data):
  # collision handler
  fruit_a = arbiter.shapes[0].user_data
  fruit_b = arbiter.shapes[1].user_data

  if fruit_a.type == fruit_b.type:
    merge_fruits(fruit_a, fruit_b, scoreboard, particles)

def determine_x(mouse_x, container, pre_fruit):
    if mouse_x < container.HorizontalDist + pre_fruit.radius:
        x = container.HorizontalDist + pre_fruit.radius
    elif mouse_x > container.HorizontalDist + container.width - pre_fruit.radius:
        x = container.HorizontalDist + container.width - pre_fruit.radius
    else:
        x = mouse_x
    
    return x

handler = space.add_collision_handler(5, 5)
handler.post_solve = collision_handler


# RUN FUNCTION

wait_for_next = 0

pre_fruit = PreFruit(width//2, container.VerticalDist, random.choice(listOfFruits[:3])) # fruit to be dropped (in sky)

next_fruit = PreFruit(container.HorizontalDist + container.width + 35, container.VerticalDist + 90, random.choice(listOfFruits[:3])) # next fruit

global activeFruits
activeFruits = []

# animal crossing goes first bc its the best lmao
# pygame.mixer.music.load("music/animalcrossing.mp3")
# pygame.mixer.music.set_volume(0.1)
# pygame.mixer.music.play()

game_over = False

# Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and wait_for_next == 0:
            activeFruits.append(pre_fruit.release(space))
            scoreboard.score += 1
            wait_for_next = 60
            
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if wait_for_next > 1:
        wait_for_next -= 1
    elif wait_for_next == 1:
        x = determine_x(mouse_x, container, pre_fruit)
        pre_fruit = PreFruit(x, height - container.VerticalDist, next_fruit.type)
        next_fruit = PreFruit(container.HorizontalDist + container.width + 35, container.VerticalDist + 90, random.choice(listOfFruits[:3]))
        wait_for_next -= 1

    # Update Pymunk
    dt = 1.0 / 60.0
    space.step(dt)

    combo_tracker.lastCombo += 1

    # Draw the screen
    screen.blit(bg, (0, 0))
    
    s = pygame.Surface((container.width,container.height))  # the size of your rect
    s.set_alpha(50)                # alpha level
    s.fill((104,255,155))           # this fills the entire surface
    screen.blit(s, (container.HorizontalDist,container.VerticalDist))    # (0,0) are the top-left coordinates

    s = pygame.Surface((container2.width,container2.height))  # the size of your rect
    s.set_alpha(20)                # alpha level
    s.fill((255,0,0))           # this fills the entire surface
    screen.blit(s, (container2.HorizontalDist,container2.VerticalDist))    # (0,0) are the top-left coordinates

    next_fruit.draw(screen)

    if wait_for_next == 0:
        x = determine_x(mouse_x, container, pre_fruit)
    
        pre_fruit.draw(screen)
        pre_fruit.update(x, height - container.VerticalDist)

    for fruit in activeFruits:
        if fruit.body.position[1] < 0:
            time.sleep(1)
            game_over = True
            break

        fruit.draw(screen)
    
    for i, particle in enumerate(particles):
        if not 0 < particle.x < width or not 0 < particle.y < height:
            particles.pop(i)
            continue
        if particle.life < 0:
            particles.pop(i)
            continue

        particle.update()
        particle.draw(screen)

    container.draw(screen)
    scoreboard.draw(screen)

    # change score2 like this: scoreboard2.score = x

    reply = net.send(send_data(scoreboard.score, activeFruits, garbage))
    garbage = []

    # parse_data function 
    incoming_score, fruits, incoming_garbage = reply.split(":")[1].split("_")

    scoreboard2.score = incoming_score

    if incoming_garbage != "n":
        newGarbageFruit = GarbageFruit(type =   listOfFruits[int(incoming_garbage)], 
                                        space =  space, 
                                        x =      random.randint(container.HorizontalDist, container.width + container.HorizontalDist), 
                                        y=       container.height + container.VerticalDist)
        activeFruits.append(newGarbageFruit)

    if fruits != "n":
        try:
            for fruit_data in fruits.split("|"):
                fruit_index, fruit_x, fruit_y, angle = fruit_data.split("/")
                
                fruit = listOfFruits[int(fruit_index)]

                pos = float(fruit_x)+580, height - float(fruit_y)
                
                rotated_image = pygame.transform.rotate(images[fruit], -float(angle) * 180 / 3.14)
                rotated_rect = rotated_image.get_rect(center=pos)
                screen.blit(rotated_image, rotated_rect.topleft)

        except Exception as error:
            print(error)
            print(fruits)

    container2.draw(screen)
    scoreboard2.draw(screen)

    snow.update()
    snow.drawSnowflakes(screen)

    combo_tracker.update()
    combo_tracker.show(screen)

    # # random music for the rest lol
    # if not pygame.mixer.music.get_busy():
    #     pygame.mixer.music.load("music/" + random.choice(os.listdir('music')))
    #     pygame.mixer.music.set_volume(0.1)
    #     pygame.mixer.music.play()

    pygame.display.flip()
    clock.tick(60)