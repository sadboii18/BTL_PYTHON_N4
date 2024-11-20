import random

import pygame
import os
import csv
import button

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

start_game = False

level_list = [10, 11]
level = random.choice(level_list)

# define player action variables
shoot1 = False
shoot2 = False

player1_char = "ahri"
player2_char = "samurai"

attack1=False
attack2=False

moving_left_player1 = False
moving_right_player1 = False

moving_left_player2 = False
moving_right_player2 = False

grenade = False
grenade_thrown = False

grenade2 = False
grenade_thrown2 = False
start_intro = True

# load music and sounds
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.1)


# load images

pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
flash_img = pygame.image.load(f'img/3.png').convert_alpha()
flash_img = pygame.transform.scale(flash_img, (50,50))
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
map1_img = pygame.image.load('img/map1.png').convert_alpha()
map2_img = pygame.image.load('img/map2.png').convert_alpha()
char_1_img = pygame.image.load('img/ahri/Idle/0.png').convert_alpha()
char_2_img = pygame.image.load('img/samurai/Idle/0.png').convert_alpha()

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bullet
bullet_img = pygame.image.load('img/icons/SpongeBullet.png').convert_alpha()
# grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo'	: ammo_box_img,
    'Grenade'	: grenade_box_img
}


# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
BLUE = (0, 122, 204)
LIGHT_BLUE = (173, 216, 230)

# define font
font = pygame.font.SysFont('Futura', 30)
FONT = pygame.font.Font(None, 40)

def draw_button(surface, text, rect, base_color, hover_color, text_color):
    """Draws a button and returns True if clicked."""
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    color = hover_color if is_hovered else base_color
    pygame.draw.rect(surface, color, rect)

    # Draw button text
    text_surf = FONT.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

    # Return if clicked
    if is_hovered and pygame.mouse.get_pressed()[0]:
        return True
    return False

def start_game_screen():
    screen.fill(BG)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width), 0))
        screen.blit(mountain_img, ((x * width), SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width), SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width), SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.effect_one=False
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death','Shoot','Attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -16
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision with floor
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0


        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def effect(self,scale,newAction,speed,sped,num):

        if self.frame_index >= len(self.animation_list[newAction])-1 and self.effect_one==False:
            skill1 = Effect(self.rect.centerx + (1 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction, scale,self.flip, speed,sped, 'fire', num)
            if self is player1:
                player1_small_group.add(skill1)
            else:
                player2_small_group.add(skill1)
            if num==0:
                skill2 = Effect(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction),
                                self.rect.top, self.direction, scale,self.flip, 5,sped, 'fire', num)
                player1_small_group.add(skill2)
                skill3 = Effect(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction),
                                self.rect.top, self.direction, scale, self.flip,10,sped, 'fire', num)
                player1_small_group.add(skill3)
            self.effect_one=True

    def shoot(self):

        if self is player1:

            if self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot_cooldown = 40
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                player1_bullet_group.add(bullet)
                # reduce ammo
                self.ammo -= 1
                shot_fx.play()
        else:
            if self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot_cooldown = 40
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                player2_bullet_group.add(bullet)
                # reduce ammo
                self.ammo -= 1
                shot_fx.play()



    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            elif self.action==4:
                self.frame_index = 0
                if self is player1:
                    global shoot1
                    shoot1=False
                else:
                    global shoot2
                    shoot2=False
            elif self.action == 5:
                if self is player1:
                    global attack1
                    attack1=False
                else:
                    global attack2
                    attack2=False
            else:
                self.frame_index=0
    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # iterate through each value in level data file
        i = 0
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile == 12:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile == 11:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 13:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15  :# create player
                        player1 = Soldier(f'{player1_char}', x * TILE_SIZE, y * TILE_SIZE, 1, 5, 40, 5)
                        health_bar1 = HealthBar(10, 10, player1.health, player1.health)
                    elif tile == 16:# create enemies
                        player2 = Soldier(f'{player2_char}', x * TILE_SIZE, y * TILE_SIZE, 1, 5, 40, 5)
                        health_bar2 = HealthBar(SCREEN_WIDTH - 150 - 10, 10, player2.health, player2.health)
                    elif tile == 17  :# create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18  :# create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19  :# create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20  :# create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player1, health_bar1, player2, health_bar2


    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        # check if the player has picked up the box
        for player in player_group:
            if pygame.sprite.collide_rect(self, player):
                # check what kind of box it was
                if self.item_type == 'Health':
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                elif self.item_type == 'Ammo':
                    player.ammo += 15
                elif self.item_type == 'Grenade':
                    player.grenades += 3
                # delete the item box
                self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Effect(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale,flip,speed,sped,type,num):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.flip=flip
        self.type=type
        self.sped=sped
        self.num=num
        img = pygame.image.load(f'img/{self.type}/{self.num}.png').convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width()) * scale, int(img.get_height()*scale)))
        img=pygame.transform.flip(img, self.flip, False)
        self.frame_index = 0
        self.image = img
        self.timer = 8
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.counter = 0

    def update(self):
        self.rect.x += (self.direction * self.sped)
        self.rect.y += (self.direction * self.speed)

        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        if self.num==3:
            self.timer -= 1
            if self.timer <= 0:
                self.kill()
        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player1, player2_small_group, False):
            if player1.alive:
                player1.health -= 15
                self.kill()

        if pygame.sprite.spritecollide(player2, player1_small_group, False):
            if player2.alive:
                player2.health -= 15
                self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed)
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player1, player2_bullet_group, False):
            if player1.alive:
                player1.health -= 20
                self.kill()

        if pygame.sprite.spritecollide(player2, player1_bullet_group, False):
            if player2.alive:
                player2.health -= 20
                self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.obstacle_list:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update grenade position
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            grenade_fx.play()
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            for player in player_group:
                if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        EXPLOSION_SPEED = 4
        # update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

# start_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 50, 200, 50)
# map_1_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 150, 200, 50)
# map_2_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 250, 200, 50)
# player1_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 350, 200, 50)
# player2_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 450, 200, 50)
exit_button = pygame.Rect(SCREEN_WIDTH/2 - 100, 550, 200, 50)

ahri_char1 = button.Button(SCREEN_WIDTH/2 + 110, 310, char_1_img, 1)
samurai_char1 = button.Button(SCREEN_WIDTH/2 + 210, 310, char_2_img, 1)

ahri_char2 = button.Button(SCREEN_WIDTH/2  + 110, 410, char_1_img, 1)
samurai_char2 = button.Button(SCREEN_WIDTH/2 + 210, 410, char_2_img, 1)
# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player1_bullet_group = pygame.sprite.Group()
player2_bullet_group = pygame.sprite.Group()
player1_small_group=pygame.sprite.Group()
player2_small_group=pygame.sprite.Group()
player2_big_group=pygame.sprite.Group()
player1_big_group=pygame.sprite.Group()





# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player1, health_bar1, player2, health_bar2 = world.process_data(world_data)
player_group.add(player1)
player_group.add(player2)



run = True
while run:

    clock.tick(FPS)
    # if start_game == False:
    #     screen.fill(BLACK)
    #     if draw_button(screen, "Start Game", start_button, BLUE, LIGHT_BLUE, WHITE) and len(player1_char) > 0 and len(player2_char) > 0:
    #         start_game = True
    #     if draw_button(screen, "Map 1", map_1_button, BLUE, LIGHT_BLUE, WHITE):
    #         level = 10
    #     if draw_button(screen, "Map 2", map_2_button, BLUE, LIGHT_BLUE, WHITE):
    #         level = 11
    #
    #     draw_button(screen, "Player 1", player1_button, BLUE, LIGHT_BLUE, WHITE)
    #     if ahri_char1.draw(screen):
    #         player1_char = "ahri"
    #     if samurai_char1.draw(screen):
    #         player1_char = "samurai"
    #     draw_button(screen, "Player 2", player2_button, BLUE, LIGHT_BLUE, WHITE)
    #     if ahri_char2.draw(screen):
    #         player2_char = "ahri"
    #     if samurai_char2.draw(screen):
    #         player2_char = "samurai"
    #     if draw_button(screen, "EXIT", exit_button, BLUE, LIGHT_BLUE, WHITE):
    #         run = False

    # else:
# update background
    draw_bg()
    # draw world map
    world.draw()
    # show player health
    health_bar1.draw(player1.health)
    # show ammo

    # player2 status
    # show player health
    health_bar2.draw(player2.health)
    # show ammo


    for player in player_group:
        player.update()
        player.draw()

    for enemy in enemy_group:
        enemy.update()
        enemy.draw()

    # update and draw groups
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()
    player1_bullet_group.update()
    player2_bullet_group.update()
    player1_small_group.update()
    player2_small_group.update()
    player1_big_group.update()
    player2_big_group.update()

    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)
    player1_bullet_group.draw(screen)
    player2_bullet_group.draw(screen)
    player1_small_group.draw(screen)
    player2_small_group.draw(screen)
    player1_big_group.draw(screen)
    player2_big_group.draw(screen)

    if start_intro == True:
        if intro_fade.fade():
            start_intro = False
            intro_fade.fade_counter = 0

    # update player actions
    if player1.alive:

        # Hanh dong ban cua nhan vat
        # if shoot1:
        #     player1.shoot()
        # # Hanh dong nem luu dan cua nhan vat
        # elif grenade and grenade_thrown == False and player1.grenades > 0:
        #     grenadeee = Grenade(player1.rect.centerx + (0.5 * player1.rect.size[0] * player1.direction), player1.rect.top, player1.direction)
        #     grenade_group.add(grenadeee)
        #     # reduce grenades
        #     player1.grenades -= 1
        #     grenade_thrown = True

        if shoot1:
            player1.update_action(4) # shoot
            player1.effect(2,4,0,9,1)
        elif attack1:
            player1.update_action(5) # attack
            player1.effect(1,5,0,7,0)

        elif player1.in_air:
            player1.update_action(2)  # 2: jump4
        elif moving_left_player1 or moving_right_player1:
            player1.update_action(1)  # 1: run
        else:
            player1.update_action(0)  # 0: idle

        player1.move(moving_left_player1, moving_right_player1)

    if player2.alive:


        if shoot2:
            player2.update_action(4)  # shoot
            player2.effect(1.5,4, 0,9, 4)
        elif attack2:
            player2.update_action(5)  # attack
            player2.effect(0.3,5,0,0,3)
        elif player2.in_air:
            player2.update_action(2)  # 2: jump
        elif moving_left_player2 or moving_right_player2:
            player2.update_action(1)  # 1: run
        else:
            player2.update_action(0)  # 0: idle

        player2.move(moving_left_player2, moving_right_player2)
    if  not player1.alive or not player2.alive:
        if death_fade.fade():
            if exit_button.draw(screen):
                run = False
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False

        # Player1
        # Khi giư phím
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left_player1 = True
            if event.key == pygame.K_d:
                moving_right_player1 = True
            if event.key == pygame.K_SPACE:
                shoot1 = True
                player1.effect_one=False
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_w and player1.alive:
                player1.jump = True
                jump_fx.play()
            if event.key == pygame.K_q:
                attack1=True
                player1.effect_one=False


        # Khi nhả phím
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left_player1 = False
            if event.key == pygame.K_d:
                moving_right_player1 = False
            # if event.key == pygame.K_SPACE:
            #     shoot1 = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

        # Player2
        # Khi giư phím
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left_player2 = True
            if event.key == pygame.K_RIGHT:
                moving_right_player2 = True
            if event.key == pygame.K_1:
                player2.effect_one=False
                shoot2 = True
            if event.key == pygame.K_2:
                player2.effect_one=False
                attack2 = True
            if event.key == pygame.K_UP and player2.alive:
                player2.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # Khi nhả phím
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left_player2 = False
            if event.key == pygame.K_RIGHT:
                moving_right_player2 = False

    pygame.display.update()

pygame.quit()
