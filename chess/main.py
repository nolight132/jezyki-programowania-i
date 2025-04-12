import pygame
import configparser
import os
import appdirs

# Initialize Pygame
pygame.init()

# Constants
SIZE = 60
UI_HEIGHT = 60 # Height of the UI bar
WIDTH, HEIGHT = 480, 480 + UI_HEIGHT

# Define themes
THEMES = {
    "default": {"white": (255, 255, 255), "black": (0, 0, 0), "background": (200, 200, 200)},
    "wood": {"white": (240, 217, 181), "black": (181, 136, 99), "background": (194, 178, 128)},
    "dark": {"white": (220, 220, 220), "black": (70, 70, 70), "background": (100, 100, 100)},
    "blue": {"white": (200, 225, 255), "black": (0, 0, 128), "background": (150, 150, 255)},
}

# Configuration file settings
APPNAME = "Chessboard"
APPAUTHOR = "nolight132"
CONFIG_FILE = "config.ini"

# Initialize pieces map
pieces_map = [[None for _ in range(8)] for _ in range(8)]


def load_config():
    """Load configuration from file, or create a default one if it doesn't exist."""
    config = configparser.ConfigParser()
    config_dir = appdirs.user_config_dir(APPNAME, APPAUTHOR)
    config_path = os.path.join(config_dir, CONFIG_FILE)

    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    if os.path.exists(config_path):
        config.read(config_path)
    else:
        # Create default config
        config["appearance"] = {"theme": "default"}
        save_config(config)  # Save the default config
    return config, config_path


def save_config(config):
    """Save the configuration to the file."""
    config_dir = appdirs.user_config_dir(APPNAME, APPAUTHOR)
    config_path = os.path.join(config_dir, CONFIG_FILE)
    with open(config_path, "w") as configfile:
        config.write(configfile)


# Load configuration
config, config_path = load_config()

# Get initial theme from config
current_theme = config.get("appearance", "theme", fallback="default")


def draw_board(screen, theme):
    """Draw the chessboard with the given theme colors."""
    white_color = theme["white"]
    black_color = theme["black"]

    for row in range(8):
        for col in range(8):
            color = white_color if (row + col) % 2 == 0 else black_color
            pygame.draw.rect(
                screen,
                color,
                (col * SIZE, row * SIZE + UI_HEIGHT, SIZE, SIZE)
            )


def draw_ui(screen, theme):
    """Draw the UI elements at the top of the screen."""
    pygame.draw.rect(screen, theme["background"], (0, 0, WIDTH, UI_HEIGHT))
    font = pygame.font.Font("fonts/pixel-font.ttf", 24)
    text_color = (0, 0, 0)

    screen.blit(font.render("1: Default", False, text_color), (10, 10))
    screen.blit(font.render("2: Wood", False, text_color), (130, 10))
    screen.blit(font.render("3: Dark", False, text_color), (225, 10))
    screen.blit(font.render("4: Blue", False, text_color), (320, 10))


# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessboard")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            theme_changed = False
            if event.key == pygame.K_1:
                current_theme = "default"
                theme_changed = True
            elif event.key == pygame.K_2:
                current_theme = "wood"
                theme_changed = True
            elif event.key == pygame.K_3:
                current_theme = "dark"
                theme_changed = True
            elif event.key == pygame.K_4:
                current_theme = "blue"
                theme_changed = True

            if theme_changed:
                config.set("appearance", "theme", current_theme)
                save_config(config)

    # Draw the UI
    draw_ui(screen, THEMES[current_theme])

    # Draw the chessboard
    draw_board(screen, THEMES[current_theme])

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
