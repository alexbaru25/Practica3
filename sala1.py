#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:29:51 2023

@author: alumno
"""
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
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
ID=Value('i',0)
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
        print(self.pos)
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
        return self.pos

    def update(self):
        self.pos[0]+= self.velocity
 

    def collide_player(self,player):
        if player==RIGHT_PLAYER:
           self.pos[0]=+300
        else:
           self.pos[0]=-300

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self,manager):
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)])
        self.disparos=manager.list()
        self.score = manager.list([11,11])
        self.running = Value('i', 1)
        self.lock=Lock()
        
    def get_player(self, side):
        return self.players[side]

    def get_ball(self,player):
        self.lock.acquire()
        pos_jugador=self.players[player].get_pos()
        if player ==RIGHT_PLAYER: 
           self.disparos.append(Ball([pos_jugador[0]-PLAYER_WIDTH ,pos_jugador[1]],RIGHT_PLAYER))
        else:
            self.disparos.append(Ball([pos_jugador[0]+PLAYER_WIDTH ,pos_jugador[1]],LEFT_PLAYER))
        self.lock.release()
        
    def ball_collide(self, player):
        self.lock.acquire()
        self.score[player]-=1
        self.lock.release()
    
    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        self.players[player].moveUp()
        self.lock.release()
        
    def moveDown(self, player):
        self.lock.acquire()
        self.players[player].moveDown()
        self.lock.release()
        
    def get_info(self):
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_disparos': list(self.disparos),
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        return info
        
    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.disparos}>"
    
def player(side, conn, game):
    try:
        print(f"starting player {SIDES[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                    print(game.players[0].pos)
                    print(game.players[1].pos)
                    print(game.get_info())
                elif command == "down":
                    game.moveDown(side)
                elif command == "collide":
                    game.ball_collide(side)
                elif command == "disparo":
                    game.get_ball(side)
                elif command == "quit":
                    game.stop()
            conn.send(game.get_info())
 
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)

