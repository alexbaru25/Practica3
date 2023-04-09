import pygame
import sys, os
import socket
import pickle
import random
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 70
PLAYER_WIDTH = 50

BALL_COLOR = WHITE
BALL_SIZE = 10
FPS = 60
DELTA = 30

SIDES = ["left", "right"]
DISPAROS=[]
class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [10, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 10, SIZE[Y]//2]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 60:
            self.pos[Y] = 60
    

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self, pos,player):
        self.pos=pos
        self.velocity = 3
        self.player=player
    def get_pos(self):
        if self.player== RIGHT_PLAYER:
            self.pos[0]-=2*random.random()+2
        else:
            self.pos[0]+=2*random.random()+2
        return self.pos

    def update(self):
        self.pos[0]+= self.velocity
        #self.pos[Y] += self.velocity[Y]

    def bounce(self):#vamos
        self.velocity = -self.velocity

    def collide_player(self):
        self.bounce()
        print('ahiiiii')
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        #self.ball = Ball([-2,3])
        self.score = [11,11]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def get_ball(self,player):
        pos_jugador=self.players[player].get_pos()
        if player ==RIGHT_PLAYER: 
           self.ball=Ball([pos_jugador[0]-PLAYER_WIDTH ,pos_jugador[1]],RIGHT_PLAYER)
        else:
            self.ball=Ball([pos_jugador[0]+PLAYER_WIDTH ,pos_jugador[1]],LEFT_PLAYER)
        return self.ball

    def get_score(self):
        return self.score

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def moveUp(self, player):
        self.players[player].moveUp()

    def moveDown(self, player):
        self.players[player].moveDown()


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.player = player
      if player.get_side()==LEFT_PLAYER:
          self.image=pygame.image.load('marcianito_izda1.png')
          pygame.draw.rect(self.image, 'blue', [0,0,PLAYER_WIDTH, PLAYER_HEIGHT],-1)
      else:  
          self.image=pygame.image.load('marcianito_dcha1.png')
          pygame.draw.rect(self.image, 'green', [0,0,PLAYER_WIDTH, PLAYER_HEIGHT],-1)
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite):
    def __init__(self, ball,player):
        super().__init__()
        self.ball = ball
        self.player=player
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, 5])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        if self.player == LEFT_PLAYER:
           pos = [self.ball.get_pos()[0]-1000,self.ball.get_pos()[1]]
        else:
            pos = self.ball.get_pos()
        pos = self.ball.get_pos()
        print(pos)
        [self.rect.centerx, self.rect.centery] = pos

class Display():
    def __init__(self, game):
        self.hay_bola=False
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]

        #self.ball = BallSprite(self.game.get_ball())
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        #self.all_sprites.add(self.ball)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        running = True
        pygame.init()

    def analyze_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.stop()
                elif event.key == pygame.K_s:
                    self.game.moveUp(LEFT_PLAYER)
                elif event.key == pygame.K_x:
                    self.game.moveDown(LEFT_PLAYER)
                elif event.key == pygame.K_k:
                    self.game.moveUp(RIGHT_PLAYER)
                elif event.key == pygame.K_m:
                    self.game.moveDown(RIGHT_PLAYER)
                elif event.key == pygame.K_d:
                    self.ball = BallSprite(self.game.get_ball(LEFT_PLAYER),LEFT_PLAYER)
                    DISPAROS.append(self.ball)
                    self.all_sprites.add(self.ball)
                    self.hay_bola=True
                elif event.key == pygame.K_j:
                    self.ball = BallSprite(self.game.get_ball(RIGHT_PLAYER),RIGHT_PLAYER)
                    DISPAROS.append(self.ball)
                    self.all_sprites.add(self.ball)
                    self.hay_bola=True
        if self.hay_bola:
            for i in DISPAROS:
                if pygame.sprite.spritecollide(i, self.paddle_group, False):
                   if i.ball.get_pos()[0]>500:
                      i.ball.get_pos()[0]=2000
                      self.game.score[RIGHT_PLAYER]-=1
                      DISPAROS.remove(i)
                      self.all_sprites.remove(i)
                   elif i.ball.get_pos()[0]<500:
                      i.ball.get_pos()[0]=-2000
                      self.game.score[LEFT_PLAYER]-=1
                      DISPAROS.remove(i)
                      self.all_sprites.remove(i)
                else:
                     if i.ball.get_pos()[0]>800 or i.ball.get_pos()[0]<0:
                         self.all_sprites.remove(i)
        if self.game.score[RIGHT_PLAYER]==0:
            self.game.stop()
        if self.game.score[LEFT_PLAYER]==0:
            self.game.stop()
        self.all_sprites.update()



    def refresh(self):
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()

        for i in range(score[LEFT_PLAYER]):
            pygame.draw.rect(self.screen, GREEN, (10 + i * 31.5, 10, 20, 20))
        for i in range(score[RIGHT_PLAYER]):
            pygame.draw.rect(self.screen, RED, (675 - i * 31.5, 10, 20, 20))        
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
      pygame.quit()

class Network:
    def __init__(self): ##this will connect to the server initially
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1' #server ip #<---
        self.port = 5555   #server port #<---
        self.addr = (self.server, self.port)
        self.p = self.connect()
    def getP(self):
        return self.p
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)



def main():
    try:
        game = Game()
        display = Display(game)

        while game.is_running():
            display.analyze_events()
            display.refresh()
            display.tick()
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
