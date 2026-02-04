import pygame
import random
import sys
import os

# ==================================================
# RUTAS
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

# ==================================================
# CONFIGURACIÓN
# ==================================================
WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRASS_GREEN = (0, 110, 0)

# ==================================================
# CLASE SPRITE ANIMADO (ROBUSTA)
# ==================================================
class AnimatedSprite:
    def __init__(self, path, frames, fps=6):
        self.sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = self.sheet.get_size()

        if sheet_w % frames != 0:
            raise ValueError(
                f"Sprite mal exportado: {path} ({sheet_w}px no divisible entre {frames})"
            )

        self.frame_width = sheet_w // frames
        self.frame_height = sheet_h
        self.frames = []

        for i in range(frames):
            frame = self.sheet.subsurface(
                (i * self.frame_width, 0, self.frame_width, self.frame_height)
            )
            self.frames.append(frame)

        self.index = 0
        self.image = self.frames[0]
        self.last_update = pygame.time.get_ticks()
        self.delay = 1000 // fps

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.delay:
            self.last_update = now
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

# ==================================================
# PANTALLA DE INICIO
# ==================================================
def start_screen(screen):
    font = pygame.font.Font(None, 28)
    screen.fill(BLACK)

    lines = [
        "TRESGÜERAS: OPERACIÓN CHIVO EXPIATORIO",
        "",
        "Tepotzotlán, Estado de México - 6:00 AM",
        "",
        "El sistema SWAT prometió revolucionar la empresa.",
        "8 meses después:",
        "- GPS sin funcionar",
        "- Reportes inexistentes",
        "- Facturación manual",
        "",
        "\"Para el viernes quiero UN nombre.\"",
        "\"O será el tuyo.\"",
        "",
        "FLECHAS  - Mover nave",
        "ESPACIO  - Rayo de baja justificada",
        "",
        "Presiona cualquier tecla para comenzar..."
    ]

    y = 80
    for line in lines:
        txt = font.render(line, True, WHITE)
        rect = txt.get_rect(center=(WIDTH // 2, y))
        screen.blit(txt, rect)
        y += 30

    pygame.display.flip()
    wait_for_key()

def wait_for_key():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                return

# ==================================================
# GAME OVER
# ==================================================
def game_over(screen, score):
    font = pygame.font.Font(None, 48)
    screen.fill(BLACK)

    screen.blit(font.render("GAME OVER", True, (200, 0, 0)),
                (WIDTH // 2 - 130, HEIGHT // 3))
    screen.blit(font.render(f"Puntaje final: {score}", True, WHITE),
                (WIDTH // 2 - 170, HEIGHT // 2))

    pygame.display.flip()
    wait_for_key()

# ==================================================
# INIT PYGAME
# ==================================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Operación Chivo Expiatorio")
clock = pygame.time.Clock()

# ==================================================
# CARGA DE SPRITES
# ==================================================
empleado_sprites = {
    "run": AnimatedSprite(os.path.join(ASSETS, "empleado", "run.png"), 4, fps=8),
    "happy": AnimatedSprite(os.path.join(ASSETS, "empleado", "happy.png"), 2, fps=4),
    "sad": AnimatedSprite(os.path.join(ASSETS, "empleado", "sad.png"), 2, fps=3),
}

SPRITE_W = empleado_sprites["run"].frame_width
SPRITE_H = empleado_sprites["run"].frame_height

# Nave (jugador) – fija
ovni_img = pygame.image.load(
    os.path.join(ASSETS, "jefe", "novel.png")
).convert_alpha()
ovni_img = pygame.transform.scale(ovni_img, (64, 64))

# Jefe fijo (HUD)
jefe_img = pygame.image.load(
    os.path.join(ASSETS, "jefe", "novel.png")
).convert_alpha()
jefe_img = pygame.transform.scale(jefe_img, (40, 40))

# ==================================================
# VARIABLES DE JUEGO
# ==================================================
player = pygame.Rect(WIDTH // 2 - 25, 10, 50, 50)
player_speed = 5

targets = []
score = 0
level = 1
goal = 10
current = 0
timer = 60

font = pygame.font.Font(None, 28)
space_pressed = False

grass = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)

# ==================================================
# INICIO
# ==================================================
start_screen(screen)
running = True

# ==================================================
# LOOP PRINCIPAL
# ==================================================
while running:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            space_pressed = True
        elif e.type == pygame.KEYUP and e.key == pygame.K_SPACE:
            space_pressed = False

    keys = pygame.key.get_pressed()
    player.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    player.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player_speed
    player.clamp_ip(screen.get_rect())

    # Spawn de empleados
    if random.randint(0, 45) == 0 and len(targets) < 8:
        speed = random.choice([-2, -1, 1, 2])
        targets.append({
            "rect": pygame.Rect(
                random.randint(0, WIDTH - SPRITE_W),
                HEIGHT - SPRITE_H - grass.height,
                SPRITE_W,
                SPRITE_H
            ),
            "speed": speed
        })

    # Estado emocional del empleado (por nivel)
    estado_empleado = "happy" if level <= 2 else "sad" if level <= 4 else "run"
    sprite = empleado_sprites[estado_empleado]
    sprite.update()

    # Movimiento empleados
    for t in targets[:]:
        t["rect"].x += t["speed"]
        if t["rect"].left <= 0 or t["rect"].right >= WIDTH:
            t["speed"] *= -1

    # Rayo
    if space_pressed:
        beam = pygame.Rect(player.centerx - 2, player.bottom, 4, HEIGHT)
        for t in targets[:]:
            if beam.colliderect(t["rect"]):
                targets.remove(t)
                score += 1
                current += 1

    # Timer / niveles
    timer -= 1 / FPS
    if timer <= 0:
        if current < goal:
            game_over(screen, score)
            break
        level += 1
        current = 0
        goal += 10
        timer = 60

    # ==================================================
    # DIBUJO
    # ==================================================
    screen.fill(BLACK)
    pygame.draw.rect(screen, GRASS_GREEN, grass)

    screen.blit(ovni_img, player)

    for t in targets:
        screen.blit(sprite.image, t["rect"])

    if space_pressed:
        pygame.draw.line(
            screen, YELLOW,
            (player.centerx, player.bottom),
            (player.centerx, HEIGHT), 2
        )

    # HUD
    screen.blit(jefe_img, (WIDTH - 80, 10))
    screen.blit(font.render(f"Nivel: {level}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Puntaje: {score}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Tiempo: {int(timer)}", True, WHITE), (10, 70))
    screen.blit(font.render(f"Objetivo: {current}/{goal}", True, WHITE), (10, 100))

    pygame.display.flip()

pygame.quit()
sys.exit()
