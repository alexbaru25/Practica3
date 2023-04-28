#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:29:51 2023

@author: alumno
"""
from multiprocessing.connection import Client
import traceback
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
class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side
        
    def set_pos(self, pos):
        self.pos = pos


    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self, pos,player):
        self.pos=[ None, None ]
        self.player = player
  
    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos = pos
    
    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.score = [11,11]
        self.running = True
        self.disparos=[]
        
    def get_player(self, side):
        return self.players[side]
    
    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)
        
    def get_ball(self,player):
        pos_jugador=self.players[player].get_pos()
        if player ==RIGHT_PLAYER: 
           self.ball=Ball([pos_jugador[0]-PLAYER_WIDTH ,pos_jugador[1]],RIGHT_PLAYER)
        else:
            self.ball=Ball([pos_jugador[0]+PLAYER_WIDTH ,pos_jugador[1]],LEFT_PLAYER)
        return self.ball

    def set_ball_pos(self, dispa):
        self.disparos=[]
        for i in dispa:
            self.disparos.append(i)
        print(self.disparos)
    def get_score(self):
        return self.score
    
    def set_score(self, score):
        self.score = score
    
    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos(gameinfo['pos_disparos'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
    
    def is_running(self):
        return self.running

    def stop(self):
        self.running = False


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
        print("la pos es",pos)
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
        pos = self.ball.get_pos()
        print(pos)
        [self.rect.centerx, self.rect.centery] = pos

class Display():
    def __init__(self, game):
        self.hay_bola=False
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        self.disparos=game.disparos
        #self.ball = BallSprite(self.game.get_ball())
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        for i in self.disparos:
            self.all_sprites.add(BallSprite(i,i.player))
        
        #self.all_sprites.add(self.ball)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        running = True
        pygame.init()

    def analyze_events(self,side):
        events=[]
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
                elif event.key == pygame.K_UP: 
                    events.append("up")
                elif event.key == pygame.K_SPACE:
                    events.append("disparo")
        print(events)            
        if self.hay_bola:
            for i in self.disparos:
                if pygame.sprite.spritecollide(i, self.paddle_group[side], False):
                       self.disparos.remove(i)
                       self.all_sprites.remove(i)
                       events.append("collide")
                   
        if self.game.score[side]==0:
            events.append("quit")
        return events


    def refresh(self):
        self.all_sprites.update()       
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

def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDES[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
