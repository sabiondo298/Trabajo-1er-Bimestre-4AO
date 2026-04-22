# Slither Juan
Una recreacion simple del popular juego Slither.io usando Pygame.

## Caracteristicas

- **Multijugador**: Soporte para hasta 4 jugadores locales
- **Serpientes IA**: Serpientes controladas por computadora que compiten con los jugadores
- **Sistema de Puntuacion**: Puntos otorgados por comer comida
- **Controles Suaves**: Movimiento fluido para todos los jugadores
- **Deteccion de Colisiones**: Colisiones realistas de serpientes
- **Efectos de Sonido**: Retroalimentacion de audio (cuando los archivos de sonido estan disponibles)

## Controles

### Jugador 1 (Jugador Humano)
- W: Moverse Arriba
- A: Moverse Izquierda
- S: Moverse Abajo
- D: Moverse Derecha

### Jugador 2 (Serpiente Azul - IA por defecto)
- Flecha Arriba: Moverse Arriba
- Flecha Izquierda: Moverse Izquierda
- Flecha Abajo: Moverse Abajo
- Flecha Derecha: Moverse Derecha

### Jugador 3 (Serpiente Amarilla - IA por defecto)
- I: Moverse Arriba
- J: Moverse Izquierda
- K: Moverse Abajo
- L: Moverse Derecha

### Jugador 4 (Serpiente Morada - IA por defecto)
- Numpad 8: Moverse Arriba
- Numpad 4: Moverse Izquierda
- Numpad 5: Moverse Abajo
- Numpad 6: Moverse Derecha

## Como Jugar

1. Controla tu serpiente para comer las bolitas de comida roja o violeta
2. Tu serpiente crece mas cuanto mas comida comes
3. Evita chocar con otras  con tu caeza
4. El juego continua hasta que todos los jugadores humanos mueran
5. Intenta obtener la puntuacion mas alta!

## Requisitos

- Python 3.x
- Pygame library

## Instalacion

1. Instalar Pygame:
   ```
   pip install pygame
   ```

2. Para correr el juego:
   ```
   python slither/main.py
   ```

## Efectos de Sonido

Para habilitar los efectos de sonido, agrega los siguientes archivos WAV al directorio slither/:
- `eat.wav`: Sonido cuando comes comida
- `death.wav`: Sonido cuando una serpiente muere

## Personalizacion

Puedes modificar las siguientes constantes en slither/main.py:
- `WIDTH`, `HEIGHT`: Dimensiones de la pantalla
- `FPS`: Velocidad del juego
- `SNAKE_SPEED`: Que tan rapido se mueven las serpientes
- `MAX_FOOD`: Numero maximo de bolitas de comida
- `num_players`: Numero de jugadores (1-4)