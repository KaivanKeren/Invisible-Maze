import time
import pygame
import os
import random

# Ukuran maze
BASE_WIDTH = 7
BASE_HEIGHT = 7
TILE_SIZE = 50
FPS = 15
INITIAL_HEALTH = 5
TIMER_LIMIT = 30
LEVELS = 5

# Mengatur posisi harta karun dan pemain
def initialize_game(level):
    size = BASE_WIDTH + level * 2
    player_pos = [0, 0]
    treasure_pos = [size - 1, size - 1]
    health = INITIAL_HEALTH
    return player_pos, treasure_pos, health, size

# Membuat maze acak
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

# Menampilkan labirin di terminal
def display_maze(maze):
    print("Labirin (0 = jalan, 1 = dinding):")
    for row in maze:
        print(' '.join(map(str, row)))
    print()

# Menampilkan labirin dengan pygame
def display_maze_pygame(size, show_walls=True):
    pygame.init()
    screen = pygame.display.set_mode((size * TILE_SIZE, size * TILE_SIZE))
    pygame.display.set_caption("Invisible Maze")
    clock = pygame.time.Clock()
    
    colors = {
        'path': (200, 200, 200),
        'wall': (50, 50, 50),
        'player': (0, 128, 255),
        'treasure': (255, 223, 0),
        'health': (255, 0, 0),
        'background': (0, 0, 0),
        'timer': (0, 255, 0)
    }
    
    def draw_maze(maze, show_walls=True):
        for y in range(size):
             for x in range(size):
                if maze[y][x] == 1 and show_walls:
                    color = colors['wall']
                else:
                    color = colors['path']
                pygame.draw.rect(screen, color, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, colors['path'], pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)  # Grid overlay
    
    def draw_objects(player_pos, treasure_pos):
        pygame.draw.rect(screen, colors['player'], pygame.Rect(player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, colors['treasure'], pygame.Rect(treasure_pos[0] * TILE_SIZE, treasure_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    def draw_health(health):
        font = pygame.font.Font(None, 36)
        text = font.render(f'Health: {health}', True, colors['health'])
        screen.blit(text, (10, 10))
        pygame.draw.rect(screen, colors['health'], pygame.Rect(10, 50, 100, 20), 1)  # Health bar border
        pygame.draw.rect(screen, colors['health'], pygame.Rect(10, 50, 100 * (health / INITIAL_HEALTH), 20))  # Health bar fill
    
    def draw_timer(remaining_time):
        font = pygame.font.Font(None, 36)
        text = font.render(f'Time: {remaining_time}', True, colors['timer'])
        screen.blit(text, (size * TILE_SIZE - 120, 10))
    
    return screen, draw_maze, draw_objects, draw_health, draw_timer, clock

def play_level(level, reset_health=True):
    player_pos, treasure_pos, health, size = initialize_game(level)
    maze = generate_maze(size)
    
    # Menampilkan labirin untuk diingat
    print(f"Level {level} - Selamat datang di Invisible Maze!")
    print("Anda memiliki 30 detik untuk mengingat labirin sebelum dimulai.")
    display_maze(maze)
    time.sleep(30)
    
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print("Waktu untuk mengingat labirin telah habis. Labirin tidak terlihat sekarang.")
    print("Gunakan WASD untuk bergerak: W=Atas, S=Bawah, A=Kiri, D=Kanan")
    
    screen, draw_maze, draw_objects, draw_health, draw_timer, clock = display_maze_pygame(size, show_walls=False)
    
    if not reset_health:
        health = INITIAL_HEALTH  # Reset health if starting over due to Game Over
    
    start_time = time.time()
    running = True
    while running:
        elapsed_time = time.time() - start_time
        remaining_time = TIMER_LIMIT - int(elapsed_time)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit the game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if not move_player(player_pos, 'w', maze, size):
                        health -= 1
                elif event.key == pygame.K_s:
                    if not move_player(player_pos, 's', maze, size):
                        health -= 1
                elif event.key == pygame.K_a:
                    if not move_player(player_pos, 'a', maze, size):
                        health -= 1
                elif event.key == pygame.K_d:
                    if not move_player(player_pos, 'd', maze, size):
                        health -= 1
                
                if check_win(player_pos, treasure_pos):
                    print(f"Selamat! Kamu telah menyelesaikan Level {level}!")
                    return True
                
                if health <= 0:
                    print("Game Over!")
                    return False
        
        if remaining_time <= 0:
            print("Waktu habis!")
            return False
        
        screen.fill((0, 0, 0))
        draw_maze(maze)
        draw_objects(player_pos, treasure_pos)
        draw_health(health)
        draw_timer(remaining_time)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return False

# Menampilkan status permainan
def print_status(player_pos, treasure_pos, health, remaining_time):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print(f"Pemain berada di posisi: {player_pos}")
    print(f"Harta karun berada di posisi: {treasure_pos}")
    print(f"Kesehatan pemain: {health}")
    print(f"Waktu tersisa: {remaining_time}")

# Mengecek apakah posisi pemain sama dengan posisi harta karun
def check_win(player_pos, treasure_pos):
    return player_pos == treasure_pos

# Mengecek apakah posisi tujuan tidak menabrak dinding
def is_valid_move(new_pos, maze, size):
    x, y = new_pos
    return 0 <= x < size and 0 <= y < size and maze[y][x] == 0

# Menggerakkan pemain
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
        return False, True  # Move was invalid (hit a wall)

def play_level(level, reset_health=True):
    player_pos, treasure_pos, health, size = initialize_game(level)
    maze = generate_maze(size)
    
    screen, draw_maze, draw_objects, draw_health, draw_timer, clock = display_maze_pygame(size, show_walls=True)
    
    if not reset_health:
        health = INITIAL_HEALTH  # Reset health if starting over due to Game Over
    
    # Menampilkan labirin untuk diingat selama 30 detik
    print(f"Level {level} - Selamat datang di Invisible Maze!")
    print("Anda memiliki 30 detik untuk mengingat labirin sebelum dimulai.")
    
    start_time = time.time()
    memorization_time = 30
    
    while time.time() - start_time < memorization_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        
        remaining_time = memorization_time - int(time.time() - start_time)
        
        screen.fill((0, 0, 0))
        draw_maze(maze)
        draw_objects(player_pos, treasure_pos)
        draw_health(health)
        draw_timer(remaining_time)
        
        font = pygame.font.Font(None, 36)
        text = font.render(f"Memorize the maze! {remaining_time} seconds left", True, (255, 255, 255))
        screen.blit(text, (size * TILE_SIZE // 2 - text.get_width() // 2, size * TILE_SIZE - 50))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    print("Waktu untuk mengingat labirin telah habis. Labirin tidak terlihat sekarang.")
    print("Gunakan WASD untuk bergerak: W=Atas, S=Bawah, A=Kiri, D=Kanan")
    
    # Ubah maze menjadi tidak terlihat
    show_walls = False
    
    game_start_time = time.time()
    running = True
    wall_break_warning = ""
    while running:
        elapsed_time = time.time() - game_start_time
        remaining_time = TIMER_LIMIT - int(elapsed_time)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                valid_move = False
                wall_break = False
                if event.key == pygame.K_w:
                    valid_move, wall_break = move_player(player_pos, 'w', maze, size)
                elif event.key == pygame.K_s:
                    valid_move, wall_break = move_player(player_pos, 's', maze, size)
                elif event.key == pygame.K_a:
                    valid_move, wall_break = move_player(player_pos, 'a', maze, size)
                elif event.key == pygame.K_d:
                    valid_move, wall_break = move_player(player_pos, 'd', maze, size)
                
                if not valid_move:
                    health -= 1
                    if wall_break:
                        wall_break_warning = "Warning: You hit a wall!"
                else:
                    wall_break_warning = ""
                
                if check_win(player_pos, treasure_pos):
                    print(f"Selamat! Kamu telah menyelesaikan Level {level}!")
                    pygame.quit()
                    return True
                
                if health <= 0:
                    print("Game Over!")
                    pygame.quit()
                    return False
        
        if remaining_time <= 0:
            print("Waktu habis!")
            pygame.quit()
            return False
        
        screen.fill((0, 0, 0))
        draw_maze(maze, show_walls)
        draw_objects(player_pos, treasure_pos)
        draw_health(health)
        draw_timer(remaining_time)
        
        # Display wall break warning
        if wall_break_warning:
            font = pygame.font.Font(None, 36)
            text = font.render(wall_break_warning, True, (255, 0, 0))
            screen.blit(text, (size * TILE_SIZE // 2 - text.get_width() // 2, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return False

def main():
    level = 1
    while level <= LEVELS:
        # Pass reset_health=True for levels after 1, so health resets only on Level 1
        if play_level(level, reset_health=(level == 1)):
            level += 1
        else:
            print("Kembali ke Level 1...")
            level = 1
            time.sleep(5)

if __name__ == "__main__":
    main()
