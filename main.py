import os
import pygame
import random
import threading
from pygame.locals import *
pygame.mixer.init()
pygame.font.init()
pygame.display.init()
# Retrieve the screen size
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h


WIDTH, HEIGHT =  int(screen_width*0.8), int(screen_height*0.8)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHOOTER MADNESS")

SHOOTING_SOUND = pygame.mixer.Sound(os.path.join('Assets','Gun+Silencer.mp3'))


BACKGROUND_IMAGE = pygame.image.load(os.path.join('Assets','space.jpg'))
BACKGROUND = pygame.transform.scale(BACKGROUND_IMAGE,(WIDTH,HEIGHT))

YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
RED_SPACE_SHIP = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))

YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACE_SHIP, (WIDTH/30, HEIGHT/15)), 90)
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACE_SHIP, (WIDTH/30, HEIGHT/15)), 270)
BULLET_IMAGE = pygame.image.load(os.path.join('Assets','bullet.png'))
BULLET = pygame.transform.scale(BULLET_IMAGE,(WIDTH/75,HEIGHT/50))

BULLET_IMAGE2 = pygame.image.load(os.path.join('Assets','bullet2.png'))
BULLET2 = pygame.transform.scale(BULLET_IMAGE2,(WIDTH/75,HEIGHT/50))

METEOR_IMAGE = pygame.image.load(os.path.join('Assets','meteor.png'))
METEOR = pygame.transform.scale(METEOR_IMAGE,(WIDTH/20,WIDTH/20))

ORB_IMAGE = pygame.image.load(os.path.join('Assets','orb.png'))
ORB = pygame.transform.scale(ORB_IMAGE,(WIDTH/30,WIDTH/30))
FPS = 60

METEOR_EXPLODES=[]
for i in range(21):
    METEOR_EXPLODES.append(pygame.transform.scale(pygame.image.load(os.path.join('Assets','meteor{}.png'.format(i))),(WIDTH/20,WIDTH/20)))


RED_WON = pygame.USEREVENT + 1
YELLOW_WON = pygame.USEREVENT + 2

RED_POWER = pygame.USEREVENT + 3
YELLOW_POWER = pygame.USEREVENT + 4


def draw_window(yellow, red, projectils1, projectils2,meteors,powerups):
    WIN.blit(BACKGROUND,(0,0))
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))


    for projectil in projectils1:
        WIN.blit(BULLET,(projectil.x,projectil.y))

    for projectil in projectils2:
        WIN.blit(BULLET2, (projectil.x, projectil.y))


    for meteor,addx,addy in meteors:
        WIN.blit(METEOR, (meteor.x-10, meteor.y-10))

    for powerup, addx, addy in powerups:
        WIN.blit(ORB,(powerup.x,powerup.y))


    pygame.display.update()

def movement_object(pressed_keys, object, boundaries, speed, keyup, keydown):
    ymin, ymax = boundaries
    if pressed_keys[keyup] and object.y > ymin:
        object.y -= speed
    if pressed_keys[keydown] and object.y < ymax:
        object.y += speed


def meteor_cracking(x,y):
    shooting_duration = 0.3  # Duration of the animation in seconds
    shooting_frames = int(shooting_duration * FPS)  # Number of frames in the animation
    frame_duration = shooting_duration / shooting_frames  # Duration of each frame

    shooting_frame = 0
    start_time = pygame.time.get_ticks()

    while shooting_frame < shooting_frames:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000

        if elapsed_time >= shooting_frame * frame_duration:
            WIN.blit(METEOR_EXPLODES[shooting_frame], (x, y))
            shooting_frame += 1

        pygame.display.update()
def shoot_from_object(pressed_keys, object,oposite_object,key,projectils,max_x,direction,can_shoot,whoshot,meteors):
    shooted=0
    for projectil in projectils:
        projectil.x+=direction
        if(abs(projectil.x-max_x)<5):
            projectils.remove(projectil)
        if oposite_object.colliderect(projectil):
            projectils.remove(projectil)
            if whoshot:
                pygame.event.post(pygame.event.Event(YELLOW_WON))
            else:
                pygame.event.post(pygame.event.Event(RED_WON))
        for meteor,x,y in meteors:
            if meteor.colliderect(projectil):
                xc=meteor.x
                yc=meteor.y
                meteors.remove((meteor,x,y))
                projectils.remove(projectil)
                threading.Thread(target=meteor_cracking, args=(xc,yc)).start()

    if can_shoot and pressed_keys[key]:
        projectil = pygame.Rect(object.x+object.width,object.y+object.height/2.3,WIDTH/75,HEIGHT/50)
        projectils.append(projectil)
        SHOOTING_SOUND.play()
        shooted=1
    return shooted

def update_shooting_counters(cnt_red,cnt_yellow):
    can_shoot_red=0
    can_shoot_yellow=0
    if not cnt_red:
        can_shoot_red=1
    else:
        cnt_red-=1
    if not cnt_yellow:
        can_shoot_yellow=1
    else:
        cnt_yellow-=1
    return cnt_yellow,can_shoot_yellow,cnt_red,can_shoot_red

def game_over(player):
    pygame.mixer.music.stop()

    font = pygame.font.Font(os.path.join('Assets','ARCADE_R.TTF'), 32)
    text = font.render("Player {} WON!".format(player),True,(255,0,0) if player == 2 else (225,225,0))
    run=1
    clock = pygame.time.Clock()
    while(run):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                run = 0
            if event.type == pygame.QUIT:
                return 0
        WIN.blit(text,(WIDTH / 3, HEIGHT / 3))
        pygame.display.update()
    return 2


def update_asteroids(asteroids,max_x,max_y,object1,object2):
    for meteor,addx,addy in asteroids:
        meteor.x+=addx
        meteor.y+=addy
        if(abs(meteor.x-max_x)<5 or abs(meteor.y-max_y)<5):
            asteroids.remove((meteor,addx,addy))
        if object1.colliderect(meteor) or object2.colliderect(meteor):
            if object2.colliderect(meteor):
                pygame.event.post(pygame.event.Event(YELLOW_WON))
            else:
                pygame.event.post(pygame.event.Event(RED_WON))
def update_powerups(powerups,max_x,max_y,object1,object2):
    for powerup,addx,addy in powerups:
        powerup.x+=addx
        powerup.y+=addy
        if (abs(powerup.x - max_x) < 5 or abs(powerup.y - max_y) < 5):
            powerups.remove((powerup, addx, addy))
        if object1.colliderect(powerup) or object2.colliderect(powerup):
            powerups.remove((powerup,addx,addy))
            if object2.colliderect(powerup):
                pygame.event.post(pygame.event.Event(RED_POWER))
            else:
                pygame.event.post(pygame.event.Event(YELLOW_POWER))
def driver_func():
    pygame.mixer_music.load(os.path.join('Assets', 'music.mp3'))
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    run = 1
    game_time=0
    become_harder=10
    adder=60

    yellow = pygame.Rect(WIDTH/100, HEIGHT/2,WIDTH/(33*1), HEIGHT/(20*1))
    yellow_projectils=[]
    can_shoot_yellow=True
    cnt_yellow=0
    yellow_powerup=0
    yellow_double=0


    red = pygame.Rect(WIDTH-WIDTH/100-WIDTH/30, HEIGHT/2,WIDTH/(33*1), HEIGHT/(20*1))
    red_projectils=[]
    can_shoot_red=True
    cnt_red=0
    red_powerup=0
    red_double=0

    asteroids=[] #(rect,how much to add x, how much to add y)
    ASTEROID_OFFSET=100
    spawn_asteroid=ASTEROID_OFFSET

    powerups=[]
    POWERUP_OFFSET=1000
    spawn_powerup = POWERUP_OFFSET

    while run:
        dt=clock.tick(FPS)

        if spawn_powerup>0:
            spawn_powerup-=1
        else:
            powerup = pygame.Rect(random.randint(200,700), random.randint(100,400),WIDTH/20,WIDTH/20)
            x=random.randint(-3,3)
            while not x:
                x=random.randint(-3,3)
            powerups.append((powerup,x,random.randint(-1,1)))
            spawn_powerup=POWERUP_OFFSET
            print(powerups)

        if(spawn_asteroid>0):
            spawn_asteroid-=1
        else:
            meteor = pygame.Rect(random.randint(200,700), random.randint(100,400),WIDTH/32,WIDTH/32)
            x=random.randint(-3,3)
            while not x:
                x=random.randint(-3,3)
            asteroids.append((meteor,x,random.randint(-1,1)))
            spawn_asteroid=ASTEROID_OFFSET

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
            if event.type == RED_WON:
                print("RED WON")
                run=game_over(2)
            if event.type == YELLOW_WON:
                print("YELLOW WON")
                run=game_over(1)
            if event.type == YELLOW_POWER:
                yellow_powerup=100
            if event.type == RED_POWER:
                red_powerup=100


        pressed_keys = pygame.key.get_pressed()
        movement_object(pressed_keys, yellow, (HEIGHT/30, HEIGHT-HEIGHT/30-HEIGHT/15), HEIGHT/150, K_w, K_s)
        movement_object(pressed_keys, red, (HEIGHT/30, HEIGHT-HEIGHT/30-HEIGHT/15), HEIGHT/150, K_UP, K_DOWN)

        if(not yellow_powerup and shoot_from_object(pressed_keys,yellow,red,K_SPACE,yellow_projectils,WIDTH,HEIGHT/150,can_shoot_yellow,1,asteroids)):
            cnt_yellow=30
        if(not red_powerup and shoot_from_object(pressed_keys,red,yellow,K_k,red_projectils,0,-HEIGHT/150,can_shoot_red,0,asteroids)):
            cnt_red=30

        if(yellow_powerup and shoot_from_object(pressed_keys,yellow,red,K_SPACE,yellow_projectils,WIDTH,HEIGHT/150,can_shoot_yellow,1,asteroids)):
            cnt_yellow=20
            yellow_powerup-=1
        if(red_powerup and shoot_from_object(pressed_keys,red,yellow,K_k,red_projectils,0,-HEIGHT/150,can_shoot_red,0,asteroids)):
            cnt_red=20
            red_powerup-=1

        if(powerups):
            update_powerups(powerups,WIDTH,HEIGHT,yellow,red)
        cnt_yellow,can_shoot_yellow,cnt_red,can_shoot_red=update_shooting_counters(cnt_red,cnt_yellow)
        update_asteroids(asteroids,WIDTH,HEIGHT,yellow,red)
        draw_window(yellow, red,yellow_projectils,red_projectils,asteroids,powerups)
        game_time+=dt/1000
        if(game_time>become_harder):
            ASTEROID_OFFSET*=2/3
            become_harder+=adder
        if(run==2):
            return 1
    return 0
def main_menu():
    pygame.mixer_music.load(os.path.join('Assets', 'music_main_menu.mp3'))
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    run=1
    bigger_text_play_game=0
    bigger_text_options=0

    font = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30))
    text = font.render("PLAY GAME", True, (224, 225, 0))
    text_body = pygame.Rect(WIDTH / 3, HEIGHT / 3, WIDTH / 3, WIDTH / 29)

    font_options = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30))
    text_options = font_options.render("OPTIONS", True, (224, 225, 0))
    text_body_options = pygame.Rect(WIDTH / 3 + WIDTH / 30, HEIGHT / 2.25, WIDTH / 3, WIDTH / 29)

    while(run):
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return 1

            if not bigger_text_play_game:
                font = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30))
                text = font.render("PLAY GAME", True, (224, 225, 0))
                text_body = pygame.Rect(WIDTH / 3, HEIGHT / 3, WIDTH / 3, WIDTH / 29)
            else:
                font = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30+WIDTH/100))
                text = font.render("PLAY GAME", True, (224, 225, 0))
                text_body = pygame.Rect(WIDTH / 3-WIDTH/20, HEIGHT / 3,WIDTH/3+WIDTH/6, HEIGHT / 10 )

            if not bigger_text_options:
                font_options = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30))
                text_options = font_options.render("OPTIONS", True, (224, 225, 0))
                text_body_options = pygame.Rect(WIDTH / 3 + WIDTH / 30, HEIGHT / 2.25, WIDTH / 3, WIDTH / 29)
            else:
                font_options = pygame.font.Font(os.path.join('Assets', 'ARCADE_R.TTF'), round(WIDTH / 30 + WIDTH/100))
                text_options = font_options.render("OPTIONS", True, (224, 225, 0))
                text_body_options = pygame.Rect(WIDTH / 3+ WIDTH / 20-WIDTH/20, HEIGHT / 2.25,WIDTH/3+WIDTH/6, HEIGHT / 10 )

            if text_body.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return 0 #playgame
                bigger_text_play_game=1
            else:
                bigger_text_play_game=0

            if text_body_options.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return 2 #options
                bigger_text_options=1
            else:
                bigger_text_options=0

        WIN.blit(BACKGROUND, (0, 0))
        WIN.blit(text, (text_body.x, text_body.y))
        WIN.blit(text_options, (text_body_options.x, text_body_options.y))
        pygame.display.update()

def options_window():
    pass
def main():
    while(1):
        window=main_menu()
        if window==0:
            term=driver_func()
            if not term:
                break
        elif window == 1:
            break
        elif window == 2:
            options_window()


    pygame.quit()
if __name__ == "__main__":
    main()
