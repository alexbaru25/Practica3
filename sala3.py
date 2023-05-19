#Irma Alonso 
#Alejandro Barragán 
#Germán Sánchez


from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random
# Definición de colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

# Definición de constantes y dimensiones
X = 0
Y = 1
SIZE = (700, 510)

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
        # Inicialización de jugador con su posición inicial según el lado
        # de la pantalla en el que se encuentra
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [10, 270]
        else:
            self.pos = [SIZE[X] - 10, 270]

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
        # Inicialización de la pelota con su posición y velocidad inicial
        # También se almacena el jugador que la lanzó
        self.pos=pos
        self.velocity = 5
        self.player=player
        
    def get_pos(self):
        return self.pos

    def update(self):
        if self.player == 0:
            self.pos[0]+= self.velocity
        else:
            self.pos[0]-=self.velocity

    def collide_player(self,player):
        if player==RIGHT_PLAYER:
           self.pos[0]=+300
        else:
           self.pos[0]=-300

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self,manager):
        # Inicialización del juego con jugadores, puntuación y estado de ejecución
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)])   # Lista compartida de jugadores
        self.disparos=manager.dict({0:[]})  # Diccionario compartido de disparos
        self.score = manager.list([11,11])  # Lista compartida de puntuación
        self.running = Value('i', 1)  # Variable compartida para indicar el estado de ejecución del juego
        self.lock=Lock()     # Semaforo para sincronización
    
    #Devuelve un jugador específico según el lado indicado
    def get_player(self, side):
        return self.players[side]
    
    #Crea y devuelve una instancia de la clase Ball según el jugador especificado.
    #La posición de la pelota se determina en función de la posición del jugador y el lado.
    def get_ball(self,player):
        self.lock.acquire()
        pos_jugador=self.players[player].get_pos()
        lst=self.disparos[0]
        if player ==RIGHT_PLAYER: 
           lst.append(Ball([pos_jugador[0]-PLAYER_WIDTH ,pos_jugador[1]],RIGHT_PLAYER))
        else:
            lst.append(Ball([pos_jugador[0]+PLAYER_WIDTH ,pos_jugador[1]],LEFT_PLAYER))
        self.disparos[0]=lst
        print(self.disparos[0])
        self.lock.release()
        
    def ball_collide(self, player):
        self.lock.acquire()
        lista=self.disparos[0]
        if player == 1:
            for i in lista:
                if i.get_pos()[0]<715 and i.get_pos()[0]> 650 and self.players[player].get_pos()[1]==i.get_pos()[1]:
                    lista.remove(i)      # Elimina el disparo si colisiona con la paleta del jugador
                    self.score[player]-=1
        else:
            for i in lista:
                if i.get_pos()[0]<50 and i.get_pos()[0]> 0 and self.players[player].get_pos()[1]==i.get_pos()[1]:
                    lista.remove(i)      # Elimina el disparo si colisiona con la paleta del jugador  
                    self.score[player]-=1
        self.disparos[0]=lista   # Actualiza la lista de disparos después de la colisión
        self.lock.release()
    
    def get_score(self):
        return list(self.score)  # Devuelve una copia de la puntuación

    def is_running(self):
        return self.running.value == 1   # Devuelve True si el juego está en ejecución, False de lo contrario

    def stop(self):
        self.running.value = 0           # Detiene la ejecución del juego

    def moveUp(self, player):   # Mueve hacia arriba al jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()
        
    def moveDown(self, player):   # Mueve hacia abajo al jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
    
    def moveDisp(self):
        self.lock.acquire()
        
        lista=self.disparos[0]
        for i in lista:
            if i.get_pos()[0]>800 or i.get_pos()[0]<-300:
                lista.remove(i)         # Elimina los disparos que están fuera de la pantalla
        
        for i in range(len(lista)):
            q=lista[i]
            q.update()      # Actualiza la posición de cada disparo
            lista[i]=q      # Actualiza la lista de disparos después del movimiento
        self.disparos[0]=lista  # Actualiza la lista de disparos después del movimiento
        self.lock.release()
    
    
    
    def get_info(self):
       
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_disparos': self.disparos[0],
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        return info       # Devuelve un diccionario con la información del juego
        
    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.disparos[0]}>"
    
def player(side, conn, game):
    try:
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "collide":
                    game.ball_collide(side)
                elif command == "disparo":
                    game.get_ball(side)
                elif command == "quit":
                    game.stop()
            if side == 1:
                 game.moveDisp()             
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

