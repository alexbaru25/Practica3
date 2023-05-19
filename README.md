Juego Multijugador de Disparos

Este es un juego multijugador de disparos implementado en Python utilizando el módulo multiprocessing y pygame para la comunicación entre procesos.

Instrucciones de ejecución:

    Descarga todos los archivos del juego en tu máquina local.
    
    Abre una terminal y navega hasta el directorio donde se encuentran los archivos descargados.
    
    Ejecuta el siguiente comando para iniciar el servidor de juego:
          python sala3.py [dirección IP]
          
    El servidor estará en espera de dos jugadores para conectarse.
    
    Los jugadores pueden ejecutar el siguiente comando en terminales separadas para unirse al juego:
          python player3.py [dirección IP]
          
          
Una vez que se hayan unido dos jugadores, el juego comenzará. 
Cada jugador controlará una nave espacial en la pantalla y deberá evitar que los disparos pasen por su lado de la pantalla.
Los jugadores pueden mover sus naves hacia arriba y hacia abajo para esquivar o buscar disparar al rival.
El objetivo del juego es que un jugador venza al contrario eliminando la nave del contrario, eso se consigue acertando los disparos sobre el rival, cada disparo que impacta en el rival le resta una vida.
El juego continuará hasta que uno de los jugadores decida salir o alguno de ellos se quede sin vidas.

El juego cuenta con una versión local que se llama basic5.py
Por otra parte, ademas del sala3.py, player3.py y basic5.py el proyecto consta de un fondo para el juego background.png, y dos imágenes que son dos naves espaciales que representan a los jugadores marcianito_dcha1.png y marcianito_izda1.png
