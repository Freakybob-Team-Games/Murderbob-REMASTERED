import os
try:
    import pygame
except ImportError:
    print("pygame is not installed. Installing...")
    os.system('pip install pygame')
    import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
MOVE_SPEED = 4
BULLET_SPEED = 10
WHITE = (255, 255, 255)
WAVE_DELAY = 4000
INITIAL_WAVE_DELAY = 10000
START_DELAY = 10000
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
RED = pygame.Color('red')
PERK_SPAWN_INTERVAL = random.randint(10000, 15000)
MAX_PERKS_ON_SCREEN = 2
LOW_HEALTH_THRESHOLD = 40
LAST_PERK_SPAWN = 0
SPEED_PERK_USE_TIME = 5000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MurderBob - REMASTERED")


font = pygame.font.SysFont('Arial', 24)
player_hurt_img = pygame.image.load("Assets/playerHURT.png")
player_img = pygame.image.load("Assets/Freakybob.png")
enemy_img = pygame.image.load("Assets/ScarySquirtward.png")

special_leaf = pygame.image.load("Assets/special_leaf.jpg")
speed_perk_img = pygame.image.load("Assets/speed_perk.png")
gun = pygame.image.load("Assets/gun.png")
player_img = pygame.transform.scale(player_img, (52, 52))
enemy_img = pygame.transform.scale(enemy_img, (32, 32))
jumpscare_img = pygame.image.load("Assets/game_overJUMPSCARE.png")
jumpscare_sound = pygame.mixer.Sound("Assets/jumpscare.mp3")
merchant_screen_image = pygame.image.load('Assets/merchant_screen.png')


player_img = pygame.transform.scale(player_img, (52, 52))
enemy_img = pygame.transform.scale(enemy_img, (32, 32))

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
            self.original_speed = MOVE_SPEED
            self.image = player_img
            self.width, self.height = self.image.get_size()
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
            self.health = 100
            self.max_health = 100
            self.speed = MOVE_SPEED
            self.last_hurt_time = 0
            self.hurt_cooldown = 1000
            self.original_image = self.image
            self.speed_perk_active = False

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
            side = random.randint(1, 4)
            if side == 1:  # top
                x = random.randint(0, WIDTH - self.width)
                y = -self.height
            elif side == 2:  # right
                x = WIDTH
                y = random.randint(0, HEIGHT - self.height)
            elif side == 3:  # bottom
                x = random.randint(0, WIDTH - self.width)
                y = HEIGHT
            else:  # left
                x = -self.width
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






class Gun:
    def __init__(self, player):
        self.original_image = pygame.transform.scale(gun, (51, 31))
        self.image = self.original_image
        self.width, self.height = self.image.get_size()
        self.player = player
        self.angle = 0

    def update(self, mouse_x, mouse_y):
        dx = mouse_x - (self.player.x + self.player.width // 2)
        dy = mouse_y - (self.player.y + self.player.height // 2)
        self.angle = math.atan2(dy, dx)


        self.image = pygame.transform.rotate(self.original_image, -math.degrees(self.angle))
        self.width, self.height = self.image.get_size()

    def get_barrel_tip(self):
        radius = 40
        barrel_x = self.player.x + self.player.width // 2 + radius * math.cos(self.angle)
        barrel_y = self.player.y + self.player.height // 2 + radius * math.sin(self.angle)
        return barrel_x, barrel_y

    def draw(self, screen):
        x, y = self.get_barrel_tip()
        screen.blit(self.image, (x - self.width // 2, y - self.height // 2))
        
class Perk:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        if self.type == 0:
            self.original_image = pygame.transform.scale(special_leaf, (31, 31))
        elif self.type == 1:
            self.original_image = pygame.transform.scale(speed_perk_img, (31, 31))
        self.image = self.original_image
        self.width, self.height = self.image.get_size()
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def intersects(self, player_x, player_y):
        return (self.x < player_x + 52 and self.x + self.width > player_x and 
                self.y < player_y + 52 and self.y + self.height > player_y)
    

    def apply_perk(self, player):
        if self.type == 0:
            if player.health < 100:
                player.health = min(100, player.health + 20)
        elif self.type == 1:
            if not player.speed_perk_active:
                player.speed_perk_active = True
                player.speed = player.original_speed * 1.5
                pygame.time.set_timer(pygame.USEREVENT + 1, SPEED_PERK_USE_TIME)
        
        

class Boss(Enemy):
    def __init__(self, speed, health_rect):
        super().__init__(speed, health_rect)
        self.health = 300
        self.max_health = 300
        self.image = pygame.image.load("Assets/boss_fight.png")
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.width, self.height = self.image.get_size()
        self.x, self.y = self.spawn_enemy(health_rect)
        self.last_attack_time = 0
        self.attack_pattern = 0
        self.attack_cooldown = 2000

    def move_towards(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def attack(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            if self.attack_pattern == 0:
                self.shoot_projectiles(player)
            elif self.attack_pattern == 1:
                self.charge_attack(player)
            else:
                self.special_attack(player)
            self.last_attack_time = current_time

    def shoot_projectiles(self, player):
        for _ in range(3):
            angle = random.uniform(-math.pi, math.pi)
            projectile = Bullet(self.x, self.y, player.x + random.randint(-10, 10), player.y + random.randint(-10, 10))
            bullets.append(projectile)

    def charge_attack(self, player):

        charge_direction = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(charge_direction) * 5
        self.y += math.sin(charge_direction) * 5

        if self.get_rect().colliderect(player.get_rect()):
            player.health -= 20 

    def special_attack(self, player):
        # I'll add this later too
        player.health -= 1

    def draw_health_bar(self, screen):
        health_bar_width = 100
        health_bar_height = 20
        health_bar_x = self.x
        health_bar_y = self.y - 20
        health_bar_color = (255, 0, 0)
        health_bar_border_color = (0, 0, 0)
        pygame.draw.rect(screen, health_bar_border_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        health_bar_fill_width = int((self.health / self.max_health) * health_bar_width)
        pygame.draw.rect(screen, health_bar_color, (health_bar_x, health_bar_y, health_bar_fill_width, health_bar_height))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True
        return False

    def update_attack_pattern(self):
        if self.health < self.max_health * 0.3:
            self.attack_pattern = 2
        elif self.health < self.max_health * 0.6:
            self.attack_pattern = 1
        else:
            self.attack_pattern = 0
player = Player()
gun = Gun(player)
bullets = []
enemies = []
running = True
clock = pygame.time.Clock()
perks = []
wave = 1
enemies_remaining = 0
wave_active = False
wave_start_time = pygame.time.get_ticks()
current_wave_delay = INITIAL_WAVE_DELAY
game_start_time = pygame.time.get_ticks()

def start_wave():
    global wave, enemies_remaining, wave_active, wave_start_time, game_start_time
    


    if wave == 15:
        enemies.clear()
        enemies.append(Boss(1.5 + (wave * 0.2), pygame.Rect(0, screen.get_height() - 50, 100, 50)))
        enemies_remaining = 1
    else:
        num_enemies = wave * 1
        num_enemies = int(num_enemies)
        enemy_speed = 1.7 + (wave * 0.1)
        enemies.clear()

        health_image = pygame.image.load('Assets/health.png')
        health_rect = pygame.Rect(0, screen.get_height() - health_image.get_height() + 5, health_image.get_width(), health_image.get_height())

        for _ in range(num_enemies):
            enemies.append(Enemy(enemy_speed, health_rect))

        enemies_remaining = num_enemies

    wave_active = True
    wave_start_time = pygame.time.get_ticks()
    wave += 1

def game_over():
    pygame.mixer.stop()
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, WHITE)
    wave_text = font.render(f"You made it to wave {wave}!!", True, WHITE)

    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text, text_rect)
    wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(wave_text, wave_rect)

    pygame.display.flip()
    pygame.time.wait(3000)
 
def shoot_bullet(gun, bullets, target_x, target_y):
    bullet_x, bullet_y = gun.get_barrel_tip()
    bullets.append(Bullet(bullet_x, bullet_y, target_x, target_y))
   
while running:
    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            mouse_x, mouse_y = pygame.mouse.get_pos()
            shoot_bullet(gun, bullets, mouse_x, mouse_y)
            gunshot.play()
        elif event.type == pygame.USEREVENT:
            player.reset_image()
        elif event.type == pygame.USEREVENT + 1:  
            player.speed_perk_active = False
            player.speed = player.original_speed

    current_time = pygame.time.get_ticks()
    

    if len(perks) < MAX_PERKS_ON_SCREEN and current_time - LAST_PERK_SPAWN > PERK_SPAWN_INTERVAL:
        perk_x = random.randint(0, WIDTH - 20)
        perk_y = random.randint(0, HEIGHT - 20)
        
        if player.health / player.max_health < 0.4:
            perk_type = 0 if random.random() < 0.7 else 1
        else:
            perk_type = random.randint(0, 1)

        perks.append(Perk(perk_x, perk_y, perk_type))
        LAST_PERK_SPAWN = current_time

    for perk in perks[:]:
        perk.draw(screen)
        if perk.intersects(player.x, player.y):
            perk.apply_perk(player)
            perks.remove(perk)  


    if wave_active and enemies_remaining == 0:
        wave_active = False
        current_wave_delay = WAVE_DELAY
        wave_start_time = pygame.time.get_ticks()
    elif not wave_active and pygame.time.get_ticks() - wave_start_time >= current_wave_delay:
        start_wave()
        
    health_image = pygame.image.load('Assets/health.png')
    health_rect = pygame.Rect(0, screen.get_height() - health_image.get_height() + 5, health_image.get_width(), health_image.get_height())

    player.move(keys, health_rect)
    bullets = [bullet for bullet in bullets if bullet.update()]

    for enemy in enemies[:]:
        if isinstance(enemy, Boss):
            enemy.move_towards(player)
            enemy.update_attack_pattern()

            enemy.draw_health_bar(screen) 
            enemy.attack(player) 
        

            for bullet in bullets[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(10)
                    bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        enemies_remaining -= 1
        else:
            enemy.move_towards(player)
            if enemy.get_rect().colliderect(player.get_rect()):
                player.health -= 7
                player.hurt()
                enemies.remove(enemy)
                enemies_remaining -= 1



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
    else:
        wave_countdown_text = font.render("Survive!!", True, WHITE)


    if player.health <= 0:
        game_over()
        break

    player.draw(screen)
    screen.blit(wave_countdown_text, (10, 10))
    for bullet in bullets:
        bullet.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)


    gun.update(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
    gun.draw(screen)
    if wave == 1:
        wave_text = font.render(f"Wave: {wave}", True, WHITE)
    else:
        wave_text = font.render(f"Wave: {wave - 1}", True, WHITE)
    screen.blit(wave_text, (10, 30))
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    health_image.blit(health_text, (28, 30))
    screen.blit(health_image, (0, screen.get_height() - health_image.get_height() + 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
