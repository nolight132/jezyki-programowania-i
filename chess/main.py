import pygame
import configparser
import os
import appdirs
import random

# Initialize Pygame
pygame.init()

# Constants
SIZE = 60  # Size of each square
UI_HEIGHT = 100  # Increased Height of the UI bar for more info
WIDTH, HEIGHT = 8 * SIZE, 8 * SIZE + UI_HEIGHT
BOARD_OFFSET_Y = UI_HEIGHT # Where the board starts vertically

# Define themes
THEMES = {
    "default": {"white": (255, 255, 255), "black": (0, 0, 0), "background": (200, 200, 200), "text": (0,0,0)},
    "wood": {"white": (240, 217, 181), "black": (181, 136, 99), "background": (194, 178, 128), "text": (50,50,30)},
    "dark": {"white": (220, 220, 220), "black": (70, 70, 70), "background": (100, 100, 100), "text": (230,230,230)},
    "blue": {"white": (200, 225, 255), "black": (0, 0, 128), "background": (150, 150, 255), "text": (0,0,50)},
}

# Configuration file settings
APPNAME = "Chessboard"
APPAUTHOR = "nolight132"
CONFIG_FILE = "config.ini"

# --- Piece Representation ---
pawn_pos = None
queen_positions = []
loaded_sprites = {}

# --- Game State ---
attack_status_message = ""

# --- Font Initialization ---
try:
    ui_font_small = pygame.font.Font("fonts/pixel-font.ttf", 18)
    ui_font_large = pygame.font.Font("fonts/pixel-font.ttf", 24)
except FileNotFoundError:
    # Use a common system font as fallback if custom font fails
    print("Warning: pixel-font.ttf not found. Using default system font.")
    ui_font_small = pygame.font.SysFont(None, 22)
    ui_font_large = pygame.font.SysFont(None, 30)


def load_config():
    """Load configuration from file, or create a default one if it doesn't exist."""
    config = configparser.ConfigParser()
    config_dir = appdirs.user_config_dir(APPNAME, APPAUTHOR)
    config_path = os.path.join(config_dir, CONFIG_FILE)

    os.makedirs(config_dir, exist_ok=True)

    if os.path.exists(config_path):
        config.read(config_path)
        # Ensure the required section exists
        if 'appearance' not in config:
            config['appearance'] = {'theme': 'default'}
            save_config(config) # Save if section was missing
    else:
        # Create default config
        config["appearance"] = {"theme": "default"}
        save_config(config) # Save the default config
    return config, config_path


def save_config(config):
    """Save the configuration to the file."""
    config_dir = appdirs.user_config_dir(APPNAME, APPAUTHOR)
    config_path = os.path.join(config_dir, CONFIG_FILE)
    try:
        with open(config_path, "w") as configfile:
            config.write(configfile)
    except IOError as e:
        print(f"Error saving configuration to {config_path}: {e}")


# Load configuration
config, config_path = load_config()

# Get initial theme from config
current_theme_name = config.get("appearance", "theme", fallback="default")
if current_theme_name not in THEMES:
    print(f"Warning: Theme '{current_theme_name}' not found in THEMES. Falling back to 'default'.")
    current_theme_name = "default"


def load_sprites():
    """Load piece sprites from the ./sprites/ directory."""
    global loaded_sprites
    piece_files = {'bP': 'black/pawn.png', 'wQ': 'white/queen.png'}
    sprite_dir = 'sprites'
    loaded_sprites = {} # Clear previous sprites

    for code, filename in piece_files.items():
        path = os.path.join(sprite_dir, filename)
        try:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (SIZE / 1.2, SIZE / 1.2))
            loaded_sprites[code] = image
            print(f"Loaded sprite: {path}")
        except pygame.error as e:
            print(f"Error loading sprite {path}: {e}")
            # Create a fallback surface (e.g., colored square) if loading fails
            fallback_surface = pygame.Surface((SIZE, SIZE))
            fallback_color = (255, 0, 0) if code == 'wQ' else (0, 255, 0)
            pygame.draw.rect(fallback_surface, fallback_color, (5, 5, SIZE / 1.2, SIZE / 1.2))
            loaded_sprites[code] = fallback_surface
        except FileNotFoundError:
            print(f"Error: Sprite file not found at {path}")
            fallback_surface = pygame.Surface((SIZE, SIZE))
            fallback_color = (255, 0, 255) # Magenta if file not found
            pygame.draw.rect(fallback_surface, fallback_color, (5, 5, SIZE-10, SIZE-10))
            loaded_sprites[code] = fallback_surface

    # Ensure required sprites are present, even if loading failed
    if 'bP' not in loaded_sprites:
        print("Error: Black Pawn sprite ('bP') could not be loaded.")
        # Potentially exit or handle more gracefully
    if 'wQ' not in loaded_sprites:
        print("Error: White Queen sprite ('wQ') could not be loaded.")
        # Potentially exit or handle more gracefully

def get_all_squares():
    """Returns a list of all possible (row, col) tuples on the board."""
    return [(r, c) for r in range(8) for c in range(8)]

def place_pieces(num_queens):
    """Randomly places 1 pawn and num_queens queens on unique squares."""
    global pawn_pos, queen_positions
    queen_positions = [] # Reset positions

    if num_queens < 0:
        num_queens = 0
    if num_queens + 1 > 64:
        print("Error: Cannot place more than 64 pieces.")
        num_queens = 63 # Max queens possible leaving one square for the pawn

    all_squares = get_all_squares()
    if len(all_squares) < num_queens + 1:
        print("Error logic placing pieces - not enough squares.")
        return # Avoid crashing

    chosen_squares = random.sample(all_squares, num_queens + 1)

    pawn_pos = chosen_squares[0]
    queen_positions = chosen_squares[1:]
    print(f"Placed pawn at: {pawn_pos}")
    print(f"Placed {len(queen_positions)} queens at: {queen_positions}")
    # Initial check after placing
    check_and_update_attack_status()

def randomize_pawn_position():
    """Finds a new random empty square for the pawn."""
    global pawn_pos
    if not queen_positions and not pawn_pos: # Nothing on board
        place_pieces(len(queen_positions))
        if not pawn_pos:
            print("Could not place pawn initially.")
            return

    occupied_squares = set(queen_positions)
    if pawn_pos:
        occupied_squares.add(pawn_pos)

    available_squares = [sq for sq in get_all_squares() if sq not in occupied_squares]

    if not available_squares:
        print("No available squares left to move the pawn.")
        return

    new_pawn_pos = random.choice(available_squares)
    pawn_pos = new_pawn_pos
    print(f"New pawn position: {pawn_pos}")
    check_and_update_attack_status()


def can_queen_attack(q_pos, p_pos):
    """Checks if a queen at q_pos attacks a pawn at p_pos, considering pieces in between."""
    if not p_pos or not q_pos:
        return False # Cannot attack if either piece is not on the board

    q_row, q_col = q_pos
    p_row, p_col = p_pos

    # Check if on the same row, column, or diagonal
    if q_row == p_row or q_col == p_col or abs(q_row - p_row) == abs(q_col - p_col):
        # Check for blocking pieces
        step_row = 0 if q_row == p_row else (1 if p_row > q_row else -1)
        step_col = 0 if q_col == p_col else (1 if p_col > q_col else -1)
        current_row, current_col = q_row + step_row, q_col + step_col

        while (current_row, current_col) != p_pos:
            if (current_row, current_col) in queen_positions:
                return False

            current_row += step_row
            current_col += step_col

        return True

    # Not on the same row, column, or diagonal
    return False

def check_and_update_attack_status():
    """Checks if the pawn is attacked and updates the status message."""
    global attack_status_message
    global attack_pieces_message
    if pawn_pos is None:
        attack_status_message = "No pawn on the board."
        return

    attacking_queens = []
    for q_pos in queen_positions:
        if can_queen_attack(q_pos, pawn_pos):
            attacking_queens.append(q_pos)

    if not attacking_queens:
        attack_status_message = "Pawn is SAFE."
        attack_pieces_message = ""
        attacker_coords = ""
    else:
        attacker_coords = ", ".join([f"{to_algebraic(pos)}" for pos in attacking_queens])
        attack_status_message = "Pawn is ATTACKED by queen(s) at:"
        attack_pieces_message = f"{attacker_coords}"
    print(attack_status_message)
    print(attacker_coords)


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
                (col * SIZE, row * SIZE + BOARD_OFFSET_Y, SIZE, SIZE) # Offset by UI height
            )

def draw_pieces(screen):
    """Draw the pawn and queens based on their positions."""
    if 'bP' not in loaded_sprites or 'wQ' not in loaded_sprites:
        print("Cannot draw pieces, sprites not loaded.")
        return

    # Draw Pawn
    if pawn_pos:
        p_row, p_col = pawn_pos
        pawn_sprite = loaded_sprites['bP']
        # Calculate centered position
        pawn_x = p_col * SIZE + (SIZE - pawn_sprite.get_width()) // 2
        pawn_y = p_row * SIZE + BOARD_OFFSET_Y + (SIZE - pawn_sprite.get_height()) // 2
        screen.blit(pawn_sprite, (pawn_x, pawn_y))

    # Draw Queens
    for q_row, q_col in queen_positions:
        queen_sprite = loaded_sprites['wQ']
        # Calculate centered position
        queen_x = q_col * SIZE + (SIZE - queen_sprite.get_width()) // 2
        queen_y = q_row * SIZE + BOARD_OFFSET_Y + (SIZE - queen_sprite.get_height()) // 2
        screen.blit(queen_sprite, (queen_x, queen_y))


def draw_ui(screen, theme):
    """Draw the UI elements at the top of the screen."""
    pygame.draw.rect(screen, theme["background"], (0, 0, WIDTH, UI_HEIGHT))
    text_color = theme["text"]

    # Theme instructions
    theme_text = "Themes: 1:Default 2:Wood 3:Dark 4:Blue"
    theme_render = ui_font_small.render(theme_text, True, text_color)
    screen.blit(theme_render, (10, 5))

    # Action instructions
    action_text = "'R': Randomize Pawn | Click Queen to Remove"
    action_render = ui_font_small.render(action_text, True, text_color)
    screen.blit(action_render, (10, 25))

    # Attack Status
    status_render = ui_font_large.render(attack_status_message, True, text_color)
    attack_pieces_render = ui_font_small.render(attack_pieces_message, True, text_color)
    status_rect = status_render.get_rect(center=(WIDTH // 2, 60)) # Center the status
    attack_pieces_rect = attack_pieces_render.get_rect(center=(WIDTH // 2, 80)) # Center the attack pieces message
    screen.blit(status_render, status_rect)
    screen.blit(attack_pieces_render, attack_pieces_rect)


def get_square_from_mouse(mouse_pos):
    """Converts mouse coordinates to board (row, col) if on the board."""
    mx, my = mouse_pos
    if my < BOARD_OFFSET_Y: # Click was in the UI area
        return None
    if mx < 0 or mx >= WIDTH or my >= HEIGHT: # Click outside window bounds (below board)
        return None

    row = (my - BOARD_OFFSET_Y) // SIZE
    col = mx // SIZE

    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    else:
        return None # Should not happen with checks above, but good practice


def to_algebraic(row_col_tuple):
    """Converts a (row, col) tuple to algebraic notation (e.g., (0, 0) -> 'a8')."""
    if row_col_tuple is None:
        return "N/A"

    row, col = row_col_tuple
    if not (0 <= row < 8 and 0 <= col < 8):
        return "Invalid"

    file = chr(ord('a') + col)
    rank = 8 - row

    return f"{file}{rank}"


# --- Initialization ---

# Get number of queens from user (run before pygame window opens)
while True:
    try:
        k_queens_str = input("Enter the number of queens (k) to place (5 max): ")
        k_queens = int(k_queens_str)
        if k_queens < 0:
            print("Number of queens cannot be negative. Please enter 0 or more.")
        elif k_queens > 5:
             print("Maximum number of queens is 5.")
        else:
            break # Valid input
    except ValueError:
        print("Invalid input. Please enter an integer.")

place_pieces(k_queens)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessboard")
load_sprites() # Initialize sprites after display is set
clock = pygame.time.Clock()

# --- Main Loop ---
running = True
while running:
    current_theme = THEMES[current_theme_name] # Get theme colors dict

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            theme_changed = False
            new_theme_name = current_theme_name
            if event.key == pygame.K_1:
                new_theme_name = "default"
                theme_changed = True
            elif event.key == pygame.K_2:
                new_theme_name = "wood"
                theme_changed = True
            elif event.key == pygame.K_3:
                new_theme_name = "dark"
                theme_changed = True
            elif event.key == pygame.K_4:
                new_theme_name = "blue"
                theme_changed = True
            elif event.key == pygame.K_r: # Randomize Pawn Position
                print("R key pressed - Randomizing pawn.")
                randomize_pawn_position()
                # Attack status is updated within randomize_pawn_position

            if theme_changed and new_theme_name in THEMES:
                current_theme_name = new_theme_name
                config.set("appearance", "theme", current_theme_name)
                save_config(config)
                print(f"Theme changed to: {current_theme_name}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                clicked_square = get_square_from_mouse(mouse_pos)

                if clicked_square:
                    print(f"Clicked on square: {clicked_square}")
                    # Check if a queen is on this square
                    if clicked_square in queen_positions:
                        print(f"Removing queen at {clicked_square}")
                        queen_positions.remove(clicked_square)
                        check_and_update_attack_status() # Re-verify after removal


    # --- Drawing ---
    # Draw the UI first (background for it)
    draw_ui(screen, current_theme)

    # Draw the chessboard
    draw_board(screen, current_theme)

    # Draw the pieces on top of the board
    draw_pieces(screen)

    # --- Update Display ---
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30) # Limit to 30 FPS


# --- Shutdown ---
pygame.quit()
print("Game window closed.")
