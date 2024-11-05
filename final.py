import time

import pygame
import sys
import subprocess
import button

# Khởi tạo Pygame
pygame.init()

# Cài đặt kích thước màn hình và màu sắc
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((800, 640))
pygame.display.set_caption("Main Menu")
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#load images
start_1_img = pygame.image.load('img/1_player.png').convert_alpha()
start_2_img = pygame.image.load('img/2_player.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()

#create button
start_1_button = button.Button(SCREEN_WIDTH // 2 - 130, 50, start_1_img, 1)
start_2_button= button.Button(SCREEN_WIDTH // 2 - 130, 200, start_2_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 130, 350, exit_img, 1)


# Hàm để hiển thị menu
def main_menu():
    run = True
    while run:
        screen.fill(BG)
        # add buttons
        if start_1_button.draw(screen):
            subprocess.Popen(["python", "demo.py"])
            time.sleep(1)  # Đợi 1 giây để đảm bảo game đã khởi động
            pygame.quit()
            sys.exit()
        if start_2_button.draw(screen):
            subprocess.Popen(["python", "pk_mode.py"])
            time.sleep(1)  # Đợi 1 giây để đảm bảo game đã khởi động
            pygame.quit()
            sys.exit()
        if exit_button.draw(screen):
            run = False

        # Kiểm tra sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        pygame.display.flip()

# Chạy menu chính
main_menu()
