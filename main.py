import pygame, sys, os, random

pygame.init()

# ---- Configuration ----
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bienvenue sur Explora")
clock = pygame.time.Clock()

# Couleurs
BG, PLAYER_COLOR, ARTIFACT_COLOR = (50,30,20), (50,100,200), (255,215,0)
ARTIFACT_HIGHLIGHT, OBSTACLE_COLOR, STAR_COLOR = (255,255,0), (100,100,100), (255,255,255)
TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER = (255,255,255), (0,150,0), (0,200,0)

# Police
font = pygame.font.Font(None,32)
font_big = pygame.font.Font(None,48)

# Joueur
player = pygame.Rect(50,50,40,60)
speed = 5

# Sauvegarde
SAVE_FILE = "savegame.txt"
def load_game(): 
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE,"r") as f:
            line=f.readline().strip()
            if line:
                return [int(x) for x in line.split("|")]
    return [0,0,0]
def save_game(salle, pts, stars):
    with open(SAVE_FILE,"w") as f:
        f.write(f"{salle}|{pts}|{stars}")

current_salle, points, total_stars = load_game()

# ---- Charger image trophée ----
trophy_img = pygame.image.load("trophy.png")  # Assure-toi d'avoir trophy.png dans le dossier
trophy_img = pygame.transform.scale(trophy_img,(200,200))

# Fonctions utilitaires
def draw_button(rect, text, mouse_pos):
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen,color,rect)
    screen.blit(font.render(text,True,TEXT_COLOR),(rect.x+10,rect.y+10))

def generate_stars(n):
    return [pygame.Rect(random.randint(50,WIDTH-50), random.randint(50,HEIGHT-50),20,20) for _ in range(n)]

# ---- Salles ----
salles = [
    {"artefacts":[pygame.Rect(600,100,40,40),pygame.Rect(300,400,40,40)],
     "collected":[False,False],
     "obstacles":[{"rect":pygame.Rect(200,200,100,20),"dir":[2,0]},{"rect":pygame.Rect(500,300,150,20),"dir":[0,2]}],
     "questions":[{"question":"Quel dieu grec est le dieu du soleil ?","bonne":"A","choix":["A - Apollon","B - Zeus","C - Hadès"]},
                  {"question":"Quel animal est associé à Poséidon ?","bonne":"C","choix":["A - Lion","B - Aigle","C - Cheval"]}],
     "stars":generate_stars(3)},
    {"artefacts":[pygame.Rect(100,100,40,40),pygame.Rect(650,450,40,40)],
     "collected":[False,False],
     "obstacles":[{"rect":pygame.Rect(300,250,200,20),"dir":[3,0]},{"rect":pygame.Rect(400,400,100,20),"dir":[0,3]}],
     "questions":[{"question":"Qui est le roi des dieux grecs ?","bonne":"B","choix":["A - Hadès","B - Zeus","C - Poséidon"]},
                  {"question":"Quel peuple a construit les pyramides ?","bonne":"C","choix":["A - Romains","B - Grecs","C - Égyptiens"]}],
     "stars":generate_stars(4)}
]

# ---- Variables ----
state = "welcome"  # welcome → rules → game → final
game_over = False
message=""

# ---- Boucle principale ----
while True:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(BG)

    # ---- Événements ----
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            save_game(current_salle, points, total_stars)
            pygame.quit(); sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            if state=="welcome" and start_button.collidepoint(event.pos):
                state="rules"
            elif state=="rules" and start_button.collidepoint(event.pos):
                state="game"
            elif state=="final" and restart_button.collidepoint(event.pos):
                current_salle=0; points=0; total_stars=0
                state="welcome"; player.topleft=(50,50)
        if event.type==pygame.KEYDOWN and state=="game" and not game_over:
            salle=salles[current_salle]
            for i, rect in enumerate(salle["artefacts"]):
                if player.colliderect(rect) and not salle["collected"][i]:
                    if event.unicode.upper()==salle["questions"][i]["bonne"]:
                        salle["collected"][i]=True; points+=10; total_stars+=1
                        message=f"Artefact {i+1} collecté ! +10 pts, +1 étoile"
                    elif event.unicode.upper() in ["A","B","C"]: message="Mauvaise réponse !"

    # ---- Écran de bienvenue ----
    if state=="welcome":
        welcome_lines = ["Bienvenue, explorateur.",
                         "Chaque porte que tu franchiras cache un secret…",
                         "Sauras-tu résoudre les énigmes qui t’attendent ?"]
        y_start=150
        for i,line in enumerate(welcome_lines):
            txt_surf=font.render(line,True,TEXT_COLOR)
            txt_rect=txt_surf.get_rect(center=(WIDTH//2, y_start+i*40))
            screen.blit(txt_surf, txt_rect)
        start_button=pygame.Rect(WIDTH//2-100,y_start+len(welcome_lines)*40+20,200,50)
        draw_button(start_button,"Suivant",mouse_pos)

    # ---- Écran règles ----
    elif state=="rules":
        rules_lines = ["Règles mystérieuses :",
                       "- Déplace-toi avec les flèches pour explorer les salles.",
                       "- Collecte les étoiles pour gagner des points.",
                       "- Résous les énigmes en appuyant sur A, B ou C.",
                       "- Évite les obstacles mobiles !"]
        y_start=100
        for i,line in enumerate(rules_lines):
            txt_surf=font.render(line,True,TEXT_COLOR)
            txt_rect=txt_surf.get_rect(topleft=(50, y_start+i*40))
            screen.blit(txt_surf, txt_rect)
        start_button=pygame.Rect(WIDTH//2-100,400,200,50)
        draw_button(start_button,"Commencer",mouse_pos)

    # ---- Écran jeu ----
    elif state=="game":
        salle=salles[current_salle]
        if not game_over:
            # Déplacement joueur
            keys=pygame.key.get_pressed(); dx=dy=0
            if keys[pygame.K_LEFT]: dx=-speed
            if keys[pygame.K_RIGHT]: dx=speed
            if keys[pygame.K_UP]: dy=-speed
            if keys[pygame.K_DOWN]: dy=speed
            future_player=player.move(dx,dy)
            if not any(future_player.colliderect(obs["rect"]) for obs in salle["obstacles"]):
                player=future_player

            # Obstacles
            for obs in salle["obstacles"]:
                obs["rect"].x+=obs["dir"][0]; obs["rect"].y+=obs["dir"][1]
                if obs["rect"].left<=0 or obs["rect"].right>=WIDTH: obs["dir"][0]*=-1
                if obs["rect"].top<=0 or obs["rect"].bottom>=HEIGHT: obs["dir"][1]*=-1
                pygame.draw.rect(screen,OBSTACLE_COLOR,obs["rect"])
                if player.colliderect(obs["rect"]):
                    game_over=True; message="Vous avez été touché !"

            # Artefacts
            for i,rect in enumerate(salle["artefacts"]):
                color=ARTIFACT_HIGHLIGHT if player.colliderect(rect) and not salle["collected"][i] else ARTIFACT_COLOR
                if not salle["collected"][i]: pygame.draw.rect(screen,color,rect)

            # Étoiles
            for star in salle["stars"][:]:
                pygame.draw.rect(screen,STAR_COLOR,star)
                if player.colliderect(star): total_stars+=1; points+=5; salle["stars"].remove(star); message="+1 étoile +5 pts"

            # Vérifier fin salle
            if all(salle["collected"]) and not game_over:
                message="Salle complète ! Appuie sur Entrée pour passer à la suivante."
                if keys[pygame.K_RETURN]:
                    current_salle+=1
                    if current_salle>=len(salles): state="final"
                    else: player.topleft=(50,50); message=""

            # Joueur
            pygame.draw.rect(screen,PLAYER_COLOR,player)

        # Texte et boutons
        screen.blit(font.render(message,True,TEXT_COLOR),(20,20))
        screen.blit(font.render(f"Points: {points} | Étoiles: {total_stars}",True,TEXT_COLOR),(20,50))

    # ---- Écran final ----
    elif state=="final":
        screen.blit(font.render("Bravo, cher explorateur !",True,TEXT_COLOR),(200,150))
        screen.blit(font.render("Voici ton cadeau :",True,TEXT_COLOR),(200,200))
        screen.blit(trophy_img,(WIDTH//2-100,250))
        restart_button=pygame.Rect(WIDTH//2-100,500,200,50)
        draw_button(restart_button,"Recommencer",mouse_pos)

    pygame.display.flip()
    clock.tick(60)
