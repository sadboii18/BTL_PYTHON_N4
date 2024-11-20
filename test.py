import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 122, 204)
LIGHT_BLUE = (173, 216, 230)

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, 40)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game with Start Screen")


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


def start_screen():
    """Display the start screen and wait for the button click."""
    start_button_rect = pygame.Rect(SCREEN_WIDTH/2 -100, 50, 200, 50)  # Button position and size
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Fill the screen
        screen.fill(WHITE)

        # Draw title
        title_surf = FONT.render("Welcome to the Game!", True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)

        # Draw start button
        if draw_button(screen, "Start Game", start_button_rect, BLUE, LIGHT_BLUE, WHITE):
            return  # Exit start screen when button is clicked

        # Update the display
        pygame.display.flip()


def main_game():
    """Main game loop."""
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen
        screen.fill(BLACK)

        # Example game content
        game_text = FONT.render("Game Running... Press X to Quit", True, WHITE)
        screen.blit(game_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


# Main program flow
start_screen()  # Show start screen
main_game()  # Start the game
