import os
import pygame

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

#define game variables
GRAVITY = 0.75

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define player action variables
shoot1 = False
shoot2 = False

moving_left_player1 = False
moving_right_player1 = False

moving_left_player2 = False
moving_right_player2 = False


bullet_img = pygame.image.load('../assets/img/icons/bullet.png').convert_alpha()

#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))



class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
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

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
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
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

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
            else:
                self.frame_index = 0

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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player1, bullet_group, False):
            if player1.alive and player1.char_type != player2.char_type:
                print("Player1 bị trúng đạn")
                player1.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(player2, bullet_group, False):
            if player2.alive:
                print("Player2 bị trúng đạn")
                player2.health -= 5
                self.kill()
        #Kiem tra doi tuong enemy1 co bi trung dan ko
        if pygame.sprite.spritecollide(enemy1, bullet_group, False):
            if enemy1.alive:
                print("enemy bi trung dan")
                enemy1.health -= 25
                self.kill()



#create sprite groups
bullet_group = pygame.sprite.Group()

player1 = Soldier('player', 200, 200, 3, 5, 20)
player2 = Soldier('player', 300, 200, 3, 5, 20)
enemy1 = Soldier('enemy', 400, 200, 3, 5, 20)



run = True
while run:

    clock.tick(FPS)

    draw_bg()
    player1.update()
    player2.update()
    enemy1.update()

    player1.draw()
    player2.draw()
    enemy1.draw()

    # update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)

    player2.move(moving_left_player2, moving_right_player2)
    player1.move(moving_left_player1, moving_right_player1)

    if player1.alive:
        # shoot bullets
        if shoot1:
            player1.shoot()
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
            player2.shoot()
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

        # Player2
        # Khi giư phím
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left_player2 = True
            if event.key == pygame.K_RIGHT:
                moving_right_player2 = True
            if event.key == pygame.K_DOWN:
                shoot2 = True
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






    pygame.display.update()

pygame.quit()