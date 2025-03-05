import time
import pygame
import random
import pygame.mixer

# Initialize the mixer
pygame.mixer.init()

# Game settings
MASTER_VOLUME = 0.5
BASE_WIDTH = 5
BASE_HEIGHT = 5
TILE_SIZE = 60
FPS = 30
INITIAL_HEALTH = 5
TIMER_LIMIT = 30
LEVELS = 3

# Load sound effects
hit_wall_sound = pygame.mixer.Sound('./sound/hit_wall.mp3')
treasure_sound = pygame.mixer.Sound('./sound/treasure.mp3')
win_sound = pygame.mixer.Sound('./sound/win.mp3')
game_over_sound = pygame.mixer.Sound('./sound/game_over.mp3')
time_up_sound = pygame.mixer.Sound('./sound/time_up.mp3')
backsound = pygame.mixer.Sound('./sound/backsound.mp3')


# Colors
COLORS = {
    'background': (15, 15, 30),
    'path': (70, 70, 100),
    'wall': (40, 40, 60),
    'player': (0, 200, 255),
    'treasure': (255, 215, 0),
    'health': (255, 50, 50),
    'timer': (50, 255, 50),
    'text': (200, 200, 200),
    'menu_highlight': (255, 255, 255),
    'menu_normal': (150, 150, 150)
}

# Initialize Pygame fonts
pygame.font.init()
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_LARGE = pygame.font.Font(None, 48)

def initialize_game(level):
    size = BASE_WIDTH + level * 2
    player_pos = [0, 0]
    treasure_pos = [size - 1, size - 1]
    health = INITIAL_HEALTH
    return player_pos, treasure_pos, health, size

def generate_maze(size):
    maze = [[1] * size for _ in range(size)]
    stack = [(0, 0)]
    maze[0][0] = 0

    while stack:
        x, y = stack[-1]
        stack.pop()
        neighbors = []
        
        for dx, dy in [(2, 0), (0, 2), (-2, 0), (0, -2)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and maze[ny][nx] == 1:
                if maze[ny - dy // 2][nx - dx // 2] == 1:
                    neighbors.append((nx, ny))
        
        if neighbors:
            stack.append((x, y))
            nx, ny = random.choice(neighbors)
            maze[ny][nx] = 0
            maze[ny - (ny - y) // 2][nx - (nx - x) // 2] = 0
            stack.append((nx, ny))
    
    return maze

def display_maze_pygame(size):
    screen_width = size * TILE_SIZE + 200  # Extra space for UI elements
    screen_height = size * TILE_SIZE + 100  # Extra space for UI elements
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Invisible Maze Adventure")
    clock = pygame.time.Clock()
    
    def draw_maze(maze, show_walls=True):
        for y in range(size):
            for x in range(size):
                rect = pygame.Rect(x * TILE_SIZE + 50, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
                if maze[y][x] == 1 and show_walls:
                    pygame.draw.rect(screen, COLORS['wall'], rect)
                else:
                    pygame.draw.rect(screen, COLORS['path'], rect)
                pygame.draw.rect(screen, COLORS['background'], rect, 1)  # Grid lines
    
    def draw_objects(player_pos, treasure_pos):
        player_rect = pygame.Rect(player_pos[0] * TILE_SIZE + 50, player_pos[1] * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
        treasure_rect = pygame.Rect(treasure_pos[0] * TILE_SIZE + 50, treasure_pos[1] * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
        
        pygame.draw.rect(screen, COLORS['player'], player_rect)
        pygame.draw.rect(screen, COLORS['treasure'], treasure_rect)
        
        # Add some visual flair
        pygame.draw.circle(screen, COLORS['background'], player_rect.center, TILE_SIZE // 4)
        pygame.draw.rect(screen, COLORS['background'], treasure_rect.inflate(-20, -20))
    
    # Healt bar
    def draw_health(health):
        text = FONT_MEDIUM.render(f'Health: {health}', True, COLORS['health'])
        screen.blit(text, (screen_width + 200, 60))
        
        health_bar_rect = pygame.Rect(screen_width + 200, 100, 250, 20)
        pygame.draw.rect(screen, COLORS['health'], health_bar_rect, 2)
        health_fill_rect = health_bar_rect.copy()
        health_fill_rect.width = health_fill_rect.width * (health / INITIAL_HEALTH)
        pygame.draw.rect(screen, COLORS['health'], health_fill_rect)
    
    def draw_timer(remaining_time):
        text = FONT_MEDIUM.render(f'Time: {remaining_time}', True, COLORS['timer'])
        screen.blit(text, (screen_width + 200, 140))
        
        timer_bar_rect = pygame.Rect(screen_width + 200, 180, 250, 20)
        pygame.draw.rect(screen, COLORS['timer'], timer_bar_rect, 2)
        timer_fill_rect = timer_bar_rect.copy()
        timer_fill_rect.width = timer_fill_rect.width * (remaining_time / TIMER_LIMIT)
        pygame.draw.rect(screen, COLORS['timer'], timer_fill_rect)
    
    def draw_level(level):
        text = FONT_LARGE.render(f'Level {level}', True, COLORS['text'])
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, 10))
    
    return screen, draw_maze, draw_objects, draw_health, draw_timer, draw_level, clock

def play_level(level, reset_health=True):
    player_pos, treasure_pos, health, size = initialize_game(level)
    maze = generate_maze(size)
    
    screen, draw_maze, draw_objects, draw_health, draw_timer, draw_level, clock = display_maze_pygame(size)
    
    if not reset_health:
        health = INITIAL_HEALTH
    
    # Memorization phase
    start_time = time.time()
    memorization_time = 30
    
    while time.time() - start_time < memorization_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Improved pause menu
                    pause_result = show_pause_menu(screen, level)
                    if pause_result == "quit":
                        return "quit"
                    elif pause_result == "restart":
                        return False
        
        remaining_time = memorization_time - int(time.time() - start_time)
        
        screen.fill(COLORS['background'])
        draw_maze(maze, show_walls=True)
        draw_objects(player_pos, treasure_pos)
        draw_health(health)
        draw_timer(remaining_time)
        draw_level(level)
        
        text = FONT_MEDIUM.render(f"Memorize the maze! {remaining_time} seconds left", True, COLORS['text'])
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() - 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Gameplay phase
    game_start_time = time.time()
    running = True
    wall_break_warning = ""
    
    while running:
        elapsed_time = time.time() - game_start_time
        remaining_time = max(0, TIMER_LIMIT - int(elapsed_time))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Improved pause menu
                    pause_result = show_pause_menu(screen, level)
                    if pause_result == "quit":
                        return "quit"
                    elif pause_result == "restart":
                        return False
                elif event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    valid_move, wall_break = move_player(player_pos, pygame.key.name(event.key), maze, size)
                    if not valid_move:
                        health -= 1
                        wall_break_warning = "Ouch! You hit a wall!" if wall_break else ""
                    else:
                        wall_break_warning = ""
                    
                    if check_win(player_pos, treasure_pos):
                        show_win_screen(screen, level)
                        return True
                    
                    if health <= 0:
                        show_game_over_screen(screen)
                        return False
        
        if remaining_time <= 0:
            show_time_up_screen(screen)
            return False
        
        screen.fill(COLORS['background'])
        draw_maze(maze, show_walls=False)
        draw_objects(player_pos, treasure_pos)
        draw_health(health)
        draw_timer(remaining_time)
        draw_level(level)
        
        if wall_break_warning:
            text = FONT_MEDIUM.render(wall_break_warning, True, COLORS['health'])
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() - 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False

def move_player(player_pos, direction, maze, size):
    new_pos = player_pos.copy()
    if direction == 'w':
        new_pos[1] -= 1
    elif direction == 's':
        new_pos[1] += 1
    elif direction == 'a':
        new_pos[0] -= 1
    elif direction == 'd':
        new_pos[0] += 1
    
    if is_valid_move(new_pos, maze, size):
        player_pos[:] = new_pos
        return True, False  # Move was valid, no wall break
    else:
        hit_wall_sound.play()  # Play sound when hitting a wall
        return False, True  # Move was invalid (hit a wall)

def is_valid_move(new_pos, maze, size):
    x, y = new_pos
    return 0 <= x < size and 0 <= y < size and maze[y][x] == 0

def check_win(player_pos, treasure_pos):
    if player_pos == treasure_pos:
        treasure_sound.play()  # Play sound when treasure is found
        return True
    return False

def show_win_screen(screen, level):
    win_sound.play()
    screen.fill(COLORS['background'])
    text1 = FONT_LARGE.render(f"Congratulations!", True, COLORS['text'])
    text2 = FONT_MEDIUM.render(f"You completed Level {level}", True, COLORS['text'])
    screen.blit(text1, (screen.get_width() // 2 - text1.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(text2, (screen.get_width() // 2 - text2.get_width() // 2, screen.get_height() // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(3000)

def show_game_over_screen(screen):
    game_over_sound.play()  # Play sound when the game is over
    screen.fill(COLORS['background'])
    text = FONT_LARGE.render("Game Over!", True, COLORS['health'])
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def show_time_up_screen(screen):
    screen.fill(COLORS['background'])
    text = FONT_LARGE.render("Time's Up!", True, COLORS['timer'])
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    
def set_volume(volume):
    """Set volume for all sound effects and background music"""
    global MASTER_VOLUME
    MASTER_VOLUME = max(0, min(1, volume))
    hit_wall_sound.set_volume(MASTER_VOLUME)
    treasure_sound.set_volume(MASTER_VOLUME)
    win_sound.set_volume(MASTER_VOLUME)
    game_over_sound.set_volume(MASTER_VOLUME)
    time_up_sound.set_volume(MASTER_VOLUME)
    backsound.set_volume(MASTER_VOLUME * 0.7)
    
def show_pause_menu(screen, current_level):
    """
    Display an interactive pause menu with multiple options
    
    Menu options:
    - Continue
    - Restart Level
    - Volume Control
    - Quit Game
    """
    menu_options = [
        "Continue",
        "Restart Level",
        "Volume",
        "Quit Game"
    ]
    selected_option = 0
    volume_slider = MASTER_VOLUME

    while True:
        screen.fill(COLORS['background'])
        
        # Title
        title = FONT_LARGE.render("Pause Menu", True, COLORS['text'])
        title_rect = title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
        screen.blit(title, title_rect)

        # Render menu options
        for i, option in enumerate(menu_options):
            color = COLORS['menu_highlight'] if i == selected_option else COLORS['menu_normal']
            text = FONT_MEDIUM.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + i * 50))
            screen.blit(text, text_rect)

        # Volume slider when Volume is selected
        if menu_options[selected_option] == "Volume":
            slider_rect = pygame.Rect(screen.get_width() // 2 - 150, screen.get_height() // 2 + 200, 300, 20)
            pygame.draw.rect(screen, COLORS['menu_normal'], slider_rect)
            
            # Volume indicator
            indicator_x = slider_rect.x + int(volume_slider * slider_rect.width)
            indicator_rect = pygame.Rect(indicator_x - 10, slider_rect.y - 10, 20, 40)
            pygame.draw.rect(screen, COLORS['menu_highlight'], indicator_rect)

            # Volume percentage text
            vol_text = FONT_SMALL.render(f"Volume: {int(volume_slider * 100)}%", True, COLORS['text'])
            vol_text_rect = vol_text.get_rect(center=(screen.get_width() // 2, slider_rect.y - 30))
            screen.blit(vol_text, vol_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Exit pause menu and continue game
                    return None
                
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Handle menu selection
                    if menu_options[selected_option] == "Continue":
                        return None
                    
                    if menu_options[selected_option] == "Restart Level":
                        return "restart"
                    
                    if menu_options[selected_option] == "Quit Game":
                        return "quit"
                
                # Volume control when Volume option is selected
                if menu_options[selected_option] == "Volume":
                    if event.key == pygame.K_LEFT:
                        volume_slider = max(0, volume_slider - 0.1)
                        set_volume(volume_slider)
                    
                    if event.key == pygame.K_RIGHT:
                        volume_slider = min(1, volume_slider + 0.1)
                        set_volume(volume_slider)

        # return None

def main():
    pygame.init()
    # Initialize volume
    set_volume(MASTER_VOLUME)
    
    # Start background music
    backsound.play(-1)  # -1 means loop indefinitely
    
    level = 1
    running = True
    while running and level <= LEVELS:
        result = play_level(level, reset_health=(level == 1))
        if result == "quit":
            running = False
        elif result:
            level += 1
        else:
            print("Back to Level 1...")
            level = 1
            time.sleep(2)
    
    pygame.quit()


if __name__ == "__main__":
    main()