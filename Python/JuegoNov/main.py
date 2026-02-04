import pygame
import random
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# =========================
# CONFIGURACIÓN GENERAL
# =========================
WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (120, 120, 120)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
GRASS_GREEN = (0, 100, 0)

# =========================
# CLASE SPRITE ANIMADO
# =========================
class AnimatedSprite:
    def __init__(self, path, frames, fps=6):
        self.sheet = pygame.image.load(path).convert_alpha()

        sheet_width, sheet_height = self.sheet.get_size()

        if sheet_width % frames != 0:
            raise ValueError(
                f"El sprite {path} no es divisible entre {frames} frames.\n"
                f"Ancho imagen: {sheet_width}"
            )

        self.frame_width = sheet_width // frames
        self.frame_height = sheet_height

        self.frames = []
        self.index = 0
        self.last_update = pygame.time.get_ticks()
        self.delay = 1000 // fps

        for i in range(frames):
            frame = self.sheet.subsurface(
                (i * self.frame_width, 0, self.frame_width, self.frame_height)
            )
            self.frames.append(frame)

        self.image = self.frames[0]

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.delay:
            self.last_update = now
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

# =========================
# PANTALLA DE INICIO
# =========================
def start_screen(screen):
    font = pygame.font.Font(None, 28)
    screen.fill(BLACK)

    text = [
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
        "El Ing. Novela recibe la llamada:",
        "\"Para el viernes quiero UN nombre.\"",
        "\"O será el tuyo.\"",
        "",
        "FLECHAS  - Mover OVNI de evaluación",
        "ESPACIO  - Rayo de Baja Justificada",
        "",
        "Presiona cualquier tecla para comenzar..."
    ]

    y = 80
    for line in text:
        render = font.render(line, True, WHITE)
        rect = render.get_rect(center=(WIDTH // 2, y))
        screen.blit(render, rect)
        y += 30

    pygame.display.flip()
    wait_for_key()

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

# =========================
# GAME OVER
# =========================
def game_over(screen, score):
    font = pygame.font.Font(None, 50)
    screen.fill(BLACK)

    screen.blit(font.render("GAME OVER", True, RED),
                (WIDTH // 2 - 120, HEIGHT // 3))
    screen.blit(font.render(f"Puntaje: {score}", True, WHITE),
                (WIDTH // 2 - 120, HEIGHT // 2))

    pygame.display.flip()
    wait_for_key()

# =========================
# INICIO PYGAME
# =========================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Operación Chivo Expiatorio")
clock = pygame.time.Clock()

# =========================
# SPRITES
# =========================
empleado_sprites = {
    "run": AnimatedSprite(
        os.path.join(ASSETS_DIR, "empleado", "run.png"), 64, 64, 4, fps=8
    ),
    "happy": AnimatedSprite(
        os.path.join(ASSETS_DIR, "empleado", "happy.png"), 64, 64, 2, fps=4
    ),
    "sad": AnimatedSprite(
        os.path.join(ASSETS_DIR, "empleado", "sad.png"), 64, 64, 2, fps=3
    ),
}

jefe_sprites = {
    "happy": pygame.image.load(
        os.path.join(ASSETS_DIR, "jefe", "happy.png")
    ).convert_alpha(),
    "sad": pygame.image.load(
        os.path.join(ASSETS_DIR, "jefe", "sad.png")
    ).convert_alpha(),
    "angry": pygame.image.load(
        os.path.join(ASSETS_DIR, "jefe", "angry.png")
    ).convert_alpha(),
}

ovni = pygame.image.load("assets/jefe/angry.png").convert_alpha()
ovni = pygame.transform.scale(ovni, (50, 50))

# =========================
# VARIABLES DE JUEGO
# =========================
player = pygame.Rect(WIDTH // 2 - 25, 10, 50, 50)
player_speed = 5

targets = []
score = 0
current_level = 1
abduction_target = 10
current_score = 0
countdown_timer = 60

font = pygame.font.Font(None, 30)
space_pressed = False

grass = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)

# =========================
# INICIAR JUEGO
# =========================
start_screen(screen)
running = True

# =========================
# LOOP PRINCIPAL
# =========================
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    keys = pygame.key.get_pressed()
    player.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    player.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player_speed
    player.clamp_ip(screen.get_rect())

    # Generar empleados
    if random.randint(0, 50) == 0:
        targets.append(pygame.Rect(random.randint(0, WIDTH - 64), HEIGHT - 64, 64, 64))

    # Estados emocionales
    if current_level <= 2:
        estado_empleado = "happy"
    elif current_level <= 5:
        estado_empleado = "sad"
    else:
        estado_empleado = "run"

    if countdown_timer < 15:
        estado_jefe = "angry"
    elif current_score < abduction_target // 2:
        estado_jefe = "sad"
    else:
        estado_jefe = "happy"

    sprite = empleado_sprites[estado_empleado]
    sprite.update()

    # RAYO
    if space_pressed:
        beam = pygame.Rect(player.centerx - 2, player.bottom, 4, HEIGHT)
        for t in targets[:]:
            if beam.colliderect(t):
                targets.remove(t)
                score += 1
                current_score += 1

    # TIMER
    countdown_timer -= 1 / FPS
    if countdown_timer <= 0:
        if current_score < abduction_target:
            game_over(screen, score)
            break
        else:
            current_level += 1
            current_score = 0
            abduction_target += 10
            countdown_timer = 60

    # =========================
    # DIBUJO
    # =========================
    screen.fill(BLACK)

    pygame.draw.rect(screen, GRASS_GREEN, grass)
    screen.blit(ovni, player)

    for t in targets:
        screen.blit(sprite.image, t)

    if space_pressed:
        pygame.draw.line(screen, YELLOW,
                         (player.centerx, player.bottom),
                         (player.centerx, HEIGHT), 2)

    screen.blit(jefe_sprites[estado_jefe], (WIDTH - 100, 10))

    screen.blit(font.render(f"Nivel: {current_level}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Puntaje: {score}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Tiempo: {int(countdown_timer)}", True, WHITE), (10, 70))
    screen.blit(font.render(f"Objetivo: {current_score}/{abduction_target}", True, WHITE), (10, 100))

    pygame.display.flip()

pygame.quit()
