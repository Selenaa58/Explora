import pygame, sys, os, random, json

pygame.init()
pygame.mixer.init()

# Music
pygame.mixer.music.load("musique_fond.mp3")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bienvenue sur Explora")
clock = pygame.time.Clock()

# Color
PLAYER_COLOR = (112, 66, 20)
ARTIFACT_COLOR = (255, 215, 0)
ARTIFACT_HIGHLIGHT = (0, 255, 255)
OBSTACLE_COLOR = (100, 100, 100)
STAR_COLOR = (255, 250, 255)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (0, 150, 0)
BUTTON_HOVER = (0, 200, 0)

font = pygame.font.Font(None, 32)
font_big = pygame.font.Font(None, 48)

player = pygame.Rect(50, 50, 40, 60)
speed = 5

SAVE_FILE = "save_game.json"
def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("current_salle", 0), data.get("points", 0), data.get("total_stars", 0)
            except:
                return 0, 0, 0
    return 0, 0, 0

def save_game(current_salle, points, total_stars):
    data = {"current_salle": current_salle, "points": points, "total_stars": total_stars}
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

current_salle, points, total_stars = load_game()

def load_background(name):
    try:
        img = pygame.image.load(os.path.join("images", name)).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.fill((50, 30, 20))
        return s

backgrounds = {
    "welcome": load_background("accueil.jpg"),
    "rules": load_background("fond_regles.jpg"),
    "game": load_background("fond_salle.jpg"),
    "final": load_background("fond_last.jpg")  # <- modifié pour la dernière image
}

def draw_button(rect, text, mouse_pos):
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    screen.blit(font.render(text, True, TEXT_COLOR), (rect.x + 10, rect.y + 10))

def generate_stars(n):
    return [pygame.Rect(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), 20, 20) for _ in range(n)]

salles = [
    {
        "artefacts": [pygame.Rect(600, 100, 40, 40), pygame.Rect(300, 400, 40, 40)],
        "collected": [False, False],
        "obstacles": [{"rect": pygame.Rect(200, 200, 100, 20), "dir": [2, 0]},
                      {"rect": pygame.Rect(500, 300, 150, 20), "dir": [0, 2]}],
        "questions": [{"question": "Quel dieu grec est le dieu du soleil ?", "bonne": "A", "choix": ["A - Apollon", "B - Zeus", "C - Hadès"]},
                      {"question": "Quel animal est associé à Poséidon ?", "bonne": "C", "choix": ["A - Lion", "B - Aigle", "C - Cheval"]}],
        "stars": generate_stars(3)
    },
    {
        "artefacts": [pygame.Rect(100, 100, 40, 40), pygame.Rect(650, 450, 40, 40)],
        "collected": [False, False],
        "obstacles": [{"rect": pygame.Rect(300, 250, 200, 20), "dir": [3, 0]},
                      {"rect": pygame.Rect(400, 400, 100, 20), "dir": [0, 3]}],
        "questions": [{"question": "Qui est le roi des dieux grecs ?", "bonne": "B", "choix": ["A - Hadès", "B - Zeus", "C - Poséidon"]},
                      {"question": "Quel peuple a construit les pyramides ?", "bonne": "C", "choix": ["A - Romains", "B - Grecs", "C - Égyptiens"]}],
        "stars": generate_stars(4)
    }
]

state = "welcome"
hit = False
message = ""
resume_button = None

while True:
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(backgrounds[state], (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game(current_salle, points, total_stars)
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "welcome" and start_button.collidepoint(event.pos):
                state = "rules"
            elif state == "rules" and start_button.collidepoint(event.pos):
                state = "game"
            elif state == "final" and restart_button.collidepoint(event.pos):
                current_salle = 0
                points = 0
                total_stars = 0
                player.topleft = (50, 50)
                state = "welcome"
                for salle in salles:
                    salle["collected"] = [False] * len(salle["collected"])
                    salle["stars"] = generate_stars(len(salle["stars"]))
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
            elif hit and resume_button and resume_button.collidepoint(event.pos):
                hit = False
                message = ""
                player.topleft = (50, 50)

        if event.type == pygame.KEYDOWN and state == "game" and not hit:
            salle = salles[current_salle]
            for i, rect in enumerate(salle["artefacts"]):
                if player.colliderect(rect) and not salle["collected"][i]:
                    if event.unicode.upper() == salle["questions"][i]["bonne"]:
                        salle["collected"][i] = True
                        points += 10
                        total_stars += 1
                        message = f"Artefact {i+1} collecté ! +10 pts, +1 étoile"
                    elif event.unicode.upper() in ["A", "B", "C"]:
                        message = "Mauvaise réponse !"

    # Écran d'accueil
    if state == "welcome":
        lines = ["Bienvenue, cher explorateur.",
                 "Chaque point doré que tu touches renferme un mystère…",
                 "Sauras-tu résoudre les énigmes qui t’attendent ?"]
        y_start = 210
        for i, line in enumerate(lines):
            surf = font.render(line, True, TEXT_COLOR)
            rect = surf.get_rect(center=(WIDTH//2, y_start + i*40))
            screen.blit(surf, rect)
        start_button = pygame.Rect(WIDTH//2 - 100, y_start + len(lines)*40 + 20, 200, 50)
        draw_button(start_button, "Suivant", mouse_pos)

    # Écran des règles
    elif state == "rules":
        lines = ["Voici les règles du jeu :",
                 "- Déplace-toi avec les flèches pour explorer les salles.",
                 "- Collecte les étoiles pour gagner des points.",
                 "- Résous les énigmes en appuyant sur A, B ou C.",
                 "- Évite les obstacles !"]
        y_start = 150
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, TEXT_COLOR), (50, y_start + i*40))
        start_button = pygame.Rect(WIDTH//2 - 100, 400, 200, 50)
        draw_button(start_button, "Commencer", mouse_pos)

    elif state == "game":
        salle = salles[current_salle]
        if not hit:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT]: dx = -speed
            if keys[pygame.K_RIGHT]: dx = speed
            if keys[pygame.K_UP]: dy = -speed
            if keys[pygame.K_DOWN]: dy = speed
            futur = player.move(dx, dy)
            if not any(futur.colliderect(o["rect"]) for o in salle["obstacles"]):
                player = futur

            for obs in salle["obstacles"]:
                obs["rect"].x += obs["dir"][0]
                obs["rect"].y += obs["dir"][1]
                if obs["rect"].left <= 0 or obs["rect"].right >= WIDTH: obs["dir"][0] *= -1
                if obs["rect"].top <= 0 or obs["rect"].bottom >= HEIGHT: obs["dir"][1] *= -1
                pygame.draw.rect(screen, OBSTACLE_COLOR, obs["rect"])
                if player.colliderect(obs["rect"]):
                    hit = True
                    message = "Vous avez été touché !"

            for i, rect in enumerate(salle["artefacts"]):
                color = ARTIFACT_HIGHLIGHT if player.colliderect(rect) and not salle["collected"][i] else ARTIFACT_COLOR
                if not salle["collected"][i]:
                    pygame.draw.rect(screen, color, rect)

            for star in salle["stars"][:]:
                pygame.draw.rect(screen, STAR_COLOR, star)
                if player.colliderect(star):
                    total_stars += 1
                    points += 5
                    salle["stars"].remove(star)
                    message = "+1 étoile +5 pts"

            for i, rect in enumerate(salle["artefacts"]):
                if player.colliderect(rect) and not salle["collected"][i]:
                    q = salle["questions"][i]
                    y = 100
                    screen.blit(font.render(q["question"], True, TEXT_COLOR), (50, y))
                    y += 40
                    for c in q["choix"]:
                        screen.blit(font.render(c, True, TEXT_COLOR), (70, y))
                        y += 30
                    screen.blit(font.render("Appuie sur A, B ou C", True, TEXT_COLOR), (50, y+10))

            if all(salle["collected"]) and not hit:
                message = "Salle complète ! Appuie sur Entrée pour passer à la suivante."
                if keys[pygame.K_RETURN]:
                    current_salle += 1
                    if current_salle >= len(salles):
                        state = "final"
                    else:
                        player.topleft = (50, 50)
                        message = ""

            pygame.draw.rect(screen, PLAYER_COLOR, player)

        else:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(180)
            s.fill((0, 0, 0))
            screen.blit(s, (0, 0))
            screen.blit(font_big.render("Vous avez été touché !", True, (255, 0, 0)), (200, 200))
            resume_button = pygame.Rect(WIDTH//2 - 100, 300, 200, 50)
            draw_button(resume_button, "Reprendre ?", mouse_pos)

        screen.blit(font.render(message, True, TEXT_COLOR), (20, 20))
        screen.blit(font.render(f"Points: {points} | Étoiles: {total_stars}", True, TEXT_COLOR), (20, 50))

    # Écran final
    elif state == "final":
        screen.blit(backgrounds["final"], (0, 0))
        screen.blit(font.render("Félicitations, cher explorateur !", True, TEXT_COLOR), (150, 200))
        screen.blit(font.render("Tu viens de remporter la partie !", True, TEXT_COLOR), (100, 250))
        restart_button = pygame.Rect(WIDTH//2 - 100, 400, 200, 50)
        draw_button(restart_button, "Recommencer", mouse_pos)

    pygame.display.flip()
    clock.tick(60)
