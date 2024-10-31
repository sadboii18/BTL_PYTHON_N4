import os
import random

import pygame
from pygame.transform import grayscale

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

#Dinh nghia cac bien trong GAME
GRAVITY = 0.75
TILE_SIZE = 40

#set framerate
clock = pygame.time.Clock()
FPS = 60

#Dinh nghia cac hanh dong nhan vat
shoot1 = False
shoot2 = False

moving_left_player1 = False
moving_right_player1 = False

moving_left_player2 = False
moving_right_player2 = False

grenade = False
grenade_thrown = False

grenade2 = False
grenade_thrown2 = False

#Tai hinh anh
#Luu dan
grenade_img = pygame.image.load('../assets/img/icons/grenade.png').convert_alpha()

#Vien dan
bullet_img = pygame.image.load('../assets/img/icons/bullet.png').convert_alpha()


#Cac hop tiep vien
health_box_img = pygame.image.load('../assets/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('../assets/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('../assets/img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'	: health_box_img,
    'Ammo'		: ammo_box_img,
    'Grenade'	: grenade_box_img
}
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


# Nhan vat
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

        # Cac hanh dong cua nhan vat
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # Load tung hinh anh trong folder hanh dong nhan vat de tao ra chuyen dong nhan vat
            num_of_frames = len(os.listdir(f'../assets/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'../assets/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

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

        # di chuyen trai, phai, nhay cua nhan vat
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
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Trong luc
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Kiem tra khi nhan vat cham mat dat
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # Cap nhat vi trỉ nhan vat
        self.rect.x += dx
        self.rect.y += dy

    def player_shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            player_bullet_group.add(bullet)
            # Giam dan khi ban
            self.ammo -= 1
    def enemy_shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            enemy_bullet_group.add(bullet)
            # Giam dan khi ban
            self.ammo -= 1

    def ai(self):
        if self.alive and (player1.alive or player2.alive):
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if (self.vision.colliderect(player1.rect) and player1.alive) or (self.vision.colliderect(player2.rect) and player2.alive):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot
                self.enemy_shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    pygame.draw.rect(screen, RED, self.vision)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # Cap nhat trang thai nhan vat (dang dung, nhay hay di chuyen)
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # reset frame index hinh anh khi load ra ngoai mang frame
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Kiem tra neu hanh dong hien tai co khac voi hanh dong truoc do khong?
        if new_action != self.action:
            self.action = new_action
            # Cap nhat lai trang thai
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


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #check if the player has picked up the box
        for player in player_group:
            if pygame.sprite.collide_rect(self, player):
                #check what kind of box it was
                if self.item_type == 'Health':
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                elif self.item_type == 'Ammo':
                    player.ammo += 15
                elif self.item_type == 'Grenade':
                    player.grenades += 3
                #delete the item box
                self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #Chuyen dong cua vien dan
        self.rect.x += (self.direction * self.speed)
        #Kiem tra neu vien dan bay ra ngoai man hinh
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #Kiem tra dan co va cham voi nhan vat
        if pygame.sprite.spritecollide(player1, enemy_bullet_group, False):
            if player1.alive:
                print("Player1 bị trúng đạn")
                player1.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(player2, enemy_bullet_group, False):
            if player2.alive:
                print("Player1 bị trúng đạn")
                player2.health -= 5
                self.kill()
        #Kiem tra doi tuong enemy1 co bi trung dan ko
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, player_bullet_group, False):
                if enemy.alive:
                    print("enemy bi trung dan")
                    enemy.health -= 25
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

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #Kiem tra luu dan khi roi xuong mat dat
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        #Khi luu dan va cham voi tuong, vat the trong game
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        #Cap nhat vi tri cua luu dan
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            for player in player_group:
                if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'../assets/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

#create sprite groups
enemy_group = pygame.sprite.Group()
player_bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

player1 = Soldier('player', 100, 200, 1.5, 2, 20, 5)
player2 = Soldier('player', 0, 200, 1.5, 2, 20, 5)
enemy1 = Soldier('enemy', 200, 200, 1.5, 1, 100, 0)
enemy2 = Soldier('enemy', 500, 200, 1.5, 1, 100, 0)
health_bar1 = HealthBar(10, 10, player1.health, player1.health)
health_bar2 = HealthBar(10, 90, player2.health, player2.health)

item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 260)
item_box_group.add(item_box)

enemy_group.add(enemy1)
enemy_group.add(enemy2)

player_group.add(player1)
player_group.add(player2)



run = True
while run:

    clock.tick(FPS)

    draw_bg()


    #player1 status
    # show player health
    health_bar1.draw(player1.health)
    # show ammo
    draw_text('AMMO: ', font, WHITE, 10, 35)
    for x in range(player1.ammo):
        screen.blit(bullet_img, (90 + (x * 10), 40))
    # show grenades
    draw_text('GRENADES: ', font, WHITE, 10, 60)
    for x in range(player1.grenades):
        screen.blit(grenade_img, (135 + (x * 15), 60))


    # player2 status
    # show player health
    health_bar2.draw(player2.health)
    # show ammo
    draw_text('AMMO: ', font, WHITE, 10, 120)
    for x in range(player2.ammo):
        screen.blit(bullet_img, (90 + (x * 10), 120))
    # show grenades
    draw_text('GRENADES: ', font, WHITE, 10, 150)
    for x in range(player2.grenades):
        screen.blit(grenade_img, (135 + (x * 15), 150))


    for player in player_group:
        player.update()
        player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.draw()
        enemy.update()

    # update and draw groups
    player_bullet_group.update()
    player_bullet_group.draw(screen)

    enemy_bullet_group.update()
    enemy_bullet_group.draw(screen)

    grenade_group.update()
    grenade_group.draw(screen)


    explosion_group.update()
    explosion_group.draw(screen)

    item_box_group.update()
    item_box_group.draw(screen)



    if player1.alive:
        # Hanh dong ban cua nhan vat
        if shoot1:
            player1.player_shoot()

        #Hanh dong nem luu dan cua nhan vat
        elif grenade and grenade_thrown == False and player1.grenades > 0:
            grenadeee = Grenade(player1.rect.centerx + (0.5 * player1.rect.size[0] * player1.direction), \
                              player1.rect.top, player1.direction)
            grenade_group.add(grenadeee)
            # reduce grenades
            player1.grenades -= 1
            grenade_thrown = True
        if player1.in_air:
            player1.update_action(2)  # 2: jump
        elif moving_left_player1 or moving_right_player1:
            player1.update_action(1)  # 1: run
        else:
            player1.update_action(0)  # 0: idle
        player1.move(moving_left_player1, moving_right_player1)

    if player2.alive:
        # shoot bullets
        if shoot2:
            player2.player_shoot()

        elif grenade2 and grenade_thrown2 == False and player2.grenades > 0:
            grenadeee = Grenade(player2.rect.centerx + (0.5 * player2.rect.size[0] * player2.direction),\
                              player2.rect.top, player2.direction)
            grenade_group.add(grenadeee)
            # reduce grenades
            player2.grenades -= 1
            grenade_thrown2 = True
        if player2.in_air:
            player2.update_action(2)  # 2: jump
        elif moving_left_player2 or moving_right_player2:
            player2.update_action(1)  # 1: run
        else:
            player2.update_action(0)  # 0: idle
        player2.move(moving_left_player2, moving_right_player2)

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False

        #Player1
        #Khi giư phím
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left_player1 = True
            if event.key == pygame.K_d:
                moving_right_player1 = True
            if event.key == pygame.K_SPACE:
                shoot1 = True
            if event.key == pygame.K_w and player1.alive:
                player1.jump = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_ESCAPE:
                run = False


        #Khi nhả phím
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left_player1 = False
            if event.key == pygame.K_d:
                moving_right_player1 = False
            if event.key == pygame.K_SPACE:
                shoot1 = False
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
            if event.key == pygame.K_DOWN:
                shoot2 = True
            if event.key == pygame.K_EQUALS:
                grenade2 = True
            if event.key == pygame.K_UP and player2.alive:
                player2.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Khi nhả phím
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left_player2 = False
            if event.key == pygame.K_RIGHT:
                moving_right_player2 = False
            if event.key == pygame.K_DOWN:
                shoot2 = False
            if event.key == pygame.K_EQUALS:
                grenade2 = False
                grenade_thrown2 = False






    pygame.display.update()

pygame.quit()