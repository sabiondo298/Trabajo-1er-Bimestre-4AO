import pygame
import random
import math
import os

# Inicializar Pygame
pygame.init()
try:
    pygame.mixer.init()
    audio_disponible = True
except pygame.error:
    print("Audio no disponible. Ejecutando sin sonido.")
    audio_disponible = False

# Constantes
ANCHO, ALTO = 1400, 720
FPS = 60
VELOCIDAD_GUSANO = 3
TAMAÑO_COMIDA = 5
TAMAÑO_INICIAL_GUSANO = 10
COMIDA_MAXIMA = 100

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
PURPURA = (128, 0, 128)
CIAN = (0, 255, 255)
NARANJA = (255, 165, 0)
ROSA = (255, 192, 203)
LIMA = (50, 205, 50)
MAGENTA = (255, 0, 255)

# Colores de jugadores para IA
COLORES_JUGADORES = [VERDE, AZUL, AMARILLO, PURPURA]

# Colores disponibles para personalización
COLORES_DISPONIBLES = [
    ("Verde", VERDE),
    ("Naranja", NARANJA),
    ("Rosa", ROSA),
    ("Lima", LIMA),
    ("Rojo", ROJO),
    ("Magenta", MAGENTA),
    ("Cian", CIAN),
    ("Blanco", BLANCO)
]

# Configurar la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Slither.io Clon")
reloj = pygame.time.Clock()

# Cargar sonidos
if audio_disponible:
    try:
        sonido_comer = pygame.mixer.Sound('eat.wav')
        sonido_muerte = pygame.mixer.Sound('death.wav')
        musica_fondo = pygame.mixer.Sound('background.wav')
        musica_fondo.play(-1)  # Reproducir música de fondo en bucle
    except:
        print("Archivos de sonido no encontrados. Ejecutando sin sonido.")
        sonido_comer = None
        sonido_muerte = None
        musica_fondo = None
else:
    sonido_comer = None
    sonido_muerte = None
    musica_fondo = None

class Gusano:
    def __init__(self, x, y, color, es_ia=False):
        self.cuerpo = [(x, y)]
        self.direccion = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = color
        self.puntuacion = 0
        self.vivo = True
        self.es_ia = es_ia
        self.comida_objetivo = None
        self.punto_objetivo = None

    def mover(self):
        if not self.vivo:
            return

        cabeza = self.cuerpo[0]
        dx, dy = self.direccion

        # Calcular nueva posición de la cabeza
        nueva_cabeza = (cabeza[0] + dx * VELOCIDAD_GUSANO, cabeza[1] + dy * VELOCIDAD_GUSANO)

        # Envolver en los bordes de la pantalla
        nueva_cabeza = (nueva_cabeza[0] % ANCHO, nueva_cabeza[1] % ALTO)

        self.cuerpo.insert(0, nueva_cabeza)

        # Eliminar cola a menos que esté creciendo
        if len(self.cuerpo) > TAMAÑO_INICIAL_GUSANO + self.puntuacion:
            self.cuerpo.pop()

    def crecer(self):
        self.puntuacion += 1

    def dibujar(self, pantalla):
        if not self.vivo:
            return

        for i, segmento in enumerate(self.cuerpo):
            # Hacer la cabeza un poco más grande y de otro color
            tamaño = TAMAÑO_COMIDA + 2 if i == 0 else TAMAÑO_COMIDA
            color = self.color if i == 0 else tuple(max(0, c - 50) for c in self.color)
            pygame.draw.circle(pantalla, color, (int(segmento[0]), int(segmento[1])), tamaño)

    def revisar_colision(self, otros_gusanos, lista_comida):
        if not self.vivo:
            return

        cabeza = self.cuerpo[0]

        # Revisar colisión con otros gusanos
        for gusano in otros_gusanos:
            if gusano == self or not gusano.vivo:
                continue

            for i, segmento in enumerate(gusano.cuerpo):
                distancia = math.hypot(cabeza[0] - segmento[0], cabeza[1] - segmento[1])
                if distancia < TAMAÑO_COMIDA + 5:
                    # Si golpeas la cabeza de otro gusano y eres más grande, puedes comerlo
                    if i == 0:  # Colisión de cabeza
                        if len(self.cuerpo) > len(gusano.cuerpo) * 1.2:  # Debes ser significativamente más grande
                            gusano.vivo = False
                            self.puntuacion += gusano.puntuacion // 2  # Gana la mitad de su puntuación
                            if sonido_muerte:
                                sonido_muerte.play()
                        elif len(gusano.cuerpo) > len(self.cuerpo) * 1.2:
                            # Te comen
                            self.vivo = False
                            gusano.puntuacion += self.puntuacion // 2
                            if sonido_muerte:
                                sonido_muerte.play()
                    else:  # Colisión de cuerpo - siempre mortal
                        self.vivo = False
                        if sonido_muerte:
                            sonido_muerte.play()
                    return

        # Revisar colisión con comida
        for comida in lista_comida[:]:
            if math.hypot(cabeza[0] - comida[0], cabeza[1] - comida[1]) < TAMAÑO_COMIDA + 5:
                lista_comida.remove(comida)
                self.crecer()
                if sonido_comer:
                    sonido_comer.play()
                # Resetear punto objetivo para IA después de comer
                if self.es_ia:
                    self.punto_objetivo = None

    def movimiento_ia(self, lista_comida, todos_gusanos):
        if not self.es_ia or not self.vivo:
            return

        cabeza = self.cuerpo[0]

        # Revisar gusanos peligrosos cercanos
        peligro_cerca = False
        for gusano in todos_gusanos:
            if gusano == self or not gusano.vivo:
                continue
            if len(gusano.cuerpo) > len(self.cuerpo) * 1.1:  # Gusano más grande es peligroso
                cabeza_gusano = gusano.cuerpo[0]
                distancia_peligro = math.hypot(cabeza[0] - cabeza_gusano[0], cabeza[1] - cabeza_gusano[1])
                if distancia_peligro < 100:  # Peligrosamente cerca
                    peligro_cerca = True
                    # Alejarse del peligro
                    dx = cabeza[0] - cabeza_gusano[0]
                    dy = cabeza[1] - cabeza_gusano[1]
                    distancia = math.hypot(dx, dy)
                    if distancia > 0:
                        self.direccion = (dx / distancia, dy / distancia)
                    break

        if not peligro_cerca:
            # Si no hay punto objetivo o está cerca del actual, elegir nuevo
            if self.punto_objetivo is None or math.hypot(cabeza[0] - self.punto_objetivo[0], cabeza[1] - self.punto_objetivo[1]) < 20:
                # Buscar comida dentro del radio de 80 píxeles
                comida_en_radio = []
                for comida in lista_comida:
                    distancia = math.hypot(cabeza[0] - comida[0], cabeza[1] - comida[1])
                    if distancia <= 80:
                        comida_en_radio.append((distancia, comida))
                
                if comida_en_radio:
                    # Elegir una comida aleatoria dentro del radio
                    self.punto_objetivo = random.choice(comida_en_radio)[1]
                else:
                    # Elegir punto aleatorio en radio de 80 píxeles
                    angulo = random.uniform(0, 2 * math.pi)
                    radio = 80
                    self.punto_objetivo = (cabeza[0] + radio * math.cos(angulo), cabeza[1] + radio * math.sin(angulo))

            # Moverse hacia el punto objetivo
            dx = self.punto_objetivo[0] - cabeza[0]
            dy = self.punto_objetivo[1] - cabeza[1]
            distancia = math.hypot(dx, dy)

            if distancia > 0:
                self.direccion = (dx / distancia, dy / distancia)
        else:
            # Movimiento aleatorio si hay peligro cercano
            peligro_cercano = False
            for gusano in todos_gusanos:
                if gusano == self or not gusano.vivo:
                    continue
                if len(gusano.cuerpo) > len(self.cuerpo):
                    cabeza_gusano = gusano.cuerpo[0]
                    distancia_peligro = math.hypot(cabeza[0] - cabeza_gusano[0], cabeza[1] - cabeza_gusano[1])
                    if distancia_peligro < 80:
                        peligro_cercano = True
                        # Alejarse del peligro
                        dx = cabeza[0] - cabeza_gusano[0]
                        dy = cabeza[1] - cabeza_gusano[1]
                        distancia = math.hypot(dx, dy)
                        if distancia > 0:
                            self.direccion = (dx / distancia, dy / distancia)
                        break

            if not peligro_cercano and random.random() < 0.1:  # Cambiar dirección ocasionalmente
                self.direccion = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

def crear_comida():
    return (random.randint(0, ANCHO), random.randint(0, ALTO))

def dibujar_puntuacion(pantalla, gusanos):
    fuente = pygame.font.Font(None, 24)
    for i, gusano in enumerate(gusanos):
        if gusano.vivo:
            tipo_jugador = "IA" if gusano.es_ia else "Humano"
            texto_puntuacion = fuente.render(f"Jugador {i+1} ({tipo_jugador}): {gusano.puntuacion}", True, gusano.color)
            pantalla.blit(texto_puntuacion, (10, 10 + i * 30))

def dibujar_fin_juego(pantalla, gusanos):
    # Superposición semitransparente
    superposicion = pygame.Surface((ANCHO, ALTO))
    superposicion.set_alpha(128)
    superposicion.fill(NEGRO)
    pantalla.blit(superposicion, (0, 0))

    # Texto de fin de juego
    fuente_grande = pygame.font.Font(None, 72)
    fuente_media = pygame.font.Font(None, 48)
    fuente_pequeña = pygame.font.Font(None, 36)

    texto_fin = fuente_grande.render("FIN DEL JUEGO", True, BLANCO)
    pantalla.blit(texto_fin, (ANCHO//2 - texto_fin.get_width()//2, ALTO//2 - 150))

    # Tabla de puntuaciones
    texto_tabla = fuente_media.render("Tabla de puntuaciones", True, BLANCO)
    pantalla.blit(texto_tabla, (ANCHO//2 - texto_tabla.get_width()//2, ALTO//2 - 80))

    # Ordenar gusanos por puntuación
    gusanos_ordenados = sorted(gusanos, key=lambda g: g.puntuacion, reverse=True)

    for i, gusano in enumerate(gusanos_ordenados):
        tipo_jugador = "IA" if gusano.es_ia else "Humano"
        nombre_color = ["Verde", "Azul", "Amarillo", "Púrpura"][COLORES_JUGADORES.index(gusano.color) if gusano.color in COLORES_JUGADORES else 0]
        texto_puntuacion = fuente_pequeña.render(f"{i+1}. {nombre_color} ({tipo_jugador}): {gusano.puntuacion}", True, gusano.color)
        pantalla.blit(texto_puntuacion, (ANCHO//2 - texto_puntuacion.get_width()//2, ALTO//2 - 40 + i * 30))

    # Instrucciones de opciones
    texto_opciones = fuente_pequeña.render("R: Reiniciar | M: Menú | ESC: Salir", True, BLANCO)
    pantalla.blit(texto_opciones, (ANCHO//2 - texto_opciones.get_width()//2, ALTO - 50))

def dibujar_pantalla_victoria(pantalla, puntuacion_jugador):
    # Superposición semitransparente
    superposicion = pygame.Surface((ANCHO, ALTO))
    superposicion.set_alpha(128)
    superposicion.fill(NEGRO)
    pantalla.blit(superposicion, (0, 0))

    # Texto de victoria
    fuente_grande = pygame.font.Font(None, 72)
    fuente_media = pygame.font.Font(None, 48)
    fuente_pequeña = pygame.font.Font(None, 36)

    texto_victoria = fuente_grande.render("¡GANASTE!", True, (255, 215, 0))
    pantalla.blit(texto_victoria, (ANCHO//2 - texto_victoria.get_width()//2, ALTO//2 - 150))

    # Puntuación
    texto_puntuacion = fuente_media.render(f"Puntuación: {puntuacion_jugador}", True, BLANCO)
    pantalla.blit(texto_puntuacion, (ANCHO//2 - texto_puntuacion.get_width()//2, ALTO//2 - 50))

    # Instrucciones de opciones
    texto_opciones = fuente_pequeña.render("R: Reiniciar | M: Menú | ESC: Salir", True, BLANCO)
    pantalla.blit(texto_opciones, (ANCHO//2 - texto_opciones.get_width()//2, ALTO - 50))

def dibujar_menu_principal(pantalla):
    try:
        # Cargar la imagen del menú
        imagen_menu = pygame.image.load('menuslither.png')
        # Redimensionar la imagen al tamaño de la ventana
        imagen_menu = pygame.transform.scale(imagen_menu, (ANCHO, ALTO))
        # Dibujar la imagen
        pantalla.blit(imagen_menu, (0, 0))
    except:
        # Si la imagen no se encuentra, mostrar pantalla negra
        pantalla.fill(NEGRO)
        fuente_media = pygame.font.Font(None, 48)
        texto_error = fuente_media.render("Error: menuslither.png no encontrado", True, BLANCO)
        pantalla.blit(texto_error, (ANCHO//2 - texto_error.get_width()//2, ALTO//2))

    pygame.display.flip()

def dibujar_pantalla_personalizacion(pantalla, indice_color_seleccionado):
    try:
        # Cargar la imagen de personalización
        imagen_personalizacion = pygame.image.load('personalizarslither.png')
        # Redimensionar la imagen al tamaño de la ventana
        imagen_personalizacion = pygame.transform.scale(imagen_personalizacion, (ANCHO, ALTO))
        # Dibujar la imagen
        pantalla.blit(imagen_personalizacion, (0, 0))
    except:
        # Si la imagen no se encuentra, mostrar pantalla negra
        pantalla.fill(NEGRO)
        fuente_media = pygame.font.Font(None, 48)
        texto_error = fuente_media.render("Error: personalizarslither.png no encontrado", True, BLANCO)
        pantalla.blit(texto_error, (ANCHO//2 - texto_error.get_width()//2, ALTO//2))

    pygame.display.flip()

def menu_principal():
    """Bucle del menú principal"""
    while True:
        dibujar_menu_principal(pantalla)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "jugar"
                elif event.key == pygame.K_2:
                    return "personalizar"
                elif event.key == pygame.K_3:
                    return "salir"
        
        reloj.tick(FPS)

def personalizar_jugador():
    """Pantalla de personalización de color"""
    color_seleccionado = 0
    
    while True:
        dibujar_pantalla_personalizacion(pantalla, color_seleccionado)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_8:
                    indice = event.key - pygame.K_1
                    if indice < len(COLORES_DISPONIBLES):
                        color_seleccionado = indice
                elif event.key == pygame.K_RETURN:
                    return COLORES_DISPONIBLES[color_seleccionado][1]
                elif event.key == pygame.K_ESCAPE:
                    return None
        
        reloj.tick(FPS)

def bucle_juego(color_jugador):
    """Bucle principal del juego"""
    # Crear jugadores
    gusanos = []
    num_jugadores = 4

    for i in range(num_jugadores):
        x = random.randint(100, ANCHO - 100)
        y = random.randint(100, ALTO - 100)
        es_ia = i >= 1  # Primer jugador es humano, los demás son IA
        color = color_jugador if i == 0 else COLORES_JUGADORES[i]
        gusanos.append(Gusano(x, y, color, es_ia))

    lista_comida = [crear_comida() for _ in range(50)]

    ejecutando = True
    estado_juego = "jugando"  # "jugando", "fin_juego", "victoria"

    while ejecutando:
        reloj.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "salir"
            elif event.type == pygame.KEYDOWN and estado_juego != "jugando":
                if event.key == pygame.K_r:
                    # Reiniciar juego
                    return "jugar"
                elif event.key == pygame.K_m:
                    # Volver al menú
                    return "menu"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_3:
                    # Salir
                    return "salir"

        if estado_juego == "jugando":
            # Manejar entrada del jugador
            teclas = pygame.key.get_pressed()

            # Controles Jugador 1 (WASD) - permitir movimiento diagonal
            if not gusanos[0].es_ia and gusanos[0].vivo:
                dx = 0
                dy = 0
                if teclas[pygame.K_a]:
                    dx = -1
                if teclas[pygame.K_d]:
                    dx = 1
                if teclas[pygame.K_w]:
                    dy = -1
                if teclas[pygame.K_s]:
                    dy = 1
                if dx != 0 or dy != 0:
                    longitud = math.hypot(dx, dy)
                    gusanos[0].direccion = (dx / longitud, dy / longitud)

            # Controles Jugador 2 (Flechas)
            if len(gusanos) > 1 and not gusanos[1].es_ia and gusanos[1].vivo:
                if teclas[pygame.K_LEFT]:
                    gusanos[1].direccion = (-1, 0)
                elif teclas[pygame.K_RIGHT]:
                    gusanos[1].direccion = (1, 0)
                elif teclas[pygame.K_UP]:
                    gusanos[1].direccion = (0, -1)
                elif teclas[pygame.K_DOWN]:
                    gusanos[1].direccion = (0, 1)

            # Controles Jugador 3 (IJKL)
            if len(gusanos) > 2 and not gusanos[2].es_ia and gusanos[2].vivo:
                if teclas[pygame.K_j]:
                    gusanos[2].direccion = (-1, 0)
                elif teclas[pygame.K_l]:
                    gusanos[2].direccion = (1, 0)
                elif teclas[pygame.K_i]:
                    gusanos[2].direccion = (0, -1)
                elif teclas[pygame.K_k]:
                    gusanos[2].direccion = (0, 1)

            # Controles Jugador 4 (Teclado numérico)
            if len(gusanos) > 3 and not gusanos[3].es_ia and gusanos[3].vivo:
                if teclas[pygame.K_KP4]:
                    gusanos[3].direccion = (-1, 0)
                elif teclas[pygame.K_KP6]:
                    gusanos[3].direccion = (1, 0)
                elif teclas[pygame.K_KP8]:
                    gusanos[3].direccion = (0, -1)
                elif teclas[pygame.K_KP5]:
                    gusanos[3].direccion = (0, 1)

            # Movimiento de IA
            for gusano in gusanos:
                if gusano.es_ia:
                    gusano.movimiento_ia(lista_comida, gusanos)

            # Mover todos los gusanos
            for gusano in gusanos:
                gusano.mover()

            # Revisar colisiones
            for gusano in gusanos:
                gusano.revisar_colision(gusanos, lista_comida)

            # Generar nueva comida
            while len(lista_comida) < COMIDA_MAXIMA:
                lista_comida.append(crear_comida())

            # Revisar condición de victoria
            if gusanos[0].vivo:
                otros_vivos = sum(1 for g in gusanos[1:] if g.vivo)
                if otros_vivos == 0:
                    estado_juego = "victoria"
            else:
                # Revisar si todos los humanos están muertos (fin del juego)
                humano_vivo = any(not gusano.es_ia and gusano.vivo for gusano in gusanos)
                if not humano_vivo:
                    estado_juego = "fin_juego"

        # Dibujar todo
        pantalla.fill(NEGRO)

        # Dibujar comida
        for comida in lista_comida:
            pygame.draw.circle(pantalla, ROJO, (int(comida[0]), int(comida[1])), TAMAÑO_COMIDA)

        # Dibujar gusanos
        for gusano in gusanos:
            gusano.dibujar(pantalla)

        # Dibujar puntuaciones
        dibujar_puntuacion(pantalla, gusanos)

        # Dibujar pantalla de fin del juego o victoria si es necesario
        if estado_juego == "fin_juego":
            dibujar_fin_juego(pantalla, gusanos)
        elif estado_juego == "victoria":
            dibujar_pantalla_victoria(pantalla, gusanos[0].puntuacion)

        pygame.display.flip()

    return "salir"

def sesion_principal():
    """Sesión principal que maneja navegación del menú"""
    color_jugador = VERDE
    
    while True:
        resultado = menu_principal()
        
        if resultado == "salir":
            pygame.quit()
            break
        elif resultado == "jugar":
            resultado = bucle_juego(color_jugador)
            if resultado == "salir":
                pygame.quit()
                break
            elif resultado == "personalizar":
                nuevo_color = personalizar_jugador()
                if nuevo_color:
                    color_jugador = nuevo_color
        elif resultado == "personalizar":
            nuevo_color = personalizar_jugador()
            if nuevo_color:
                color_jugador = nuevo_color

def principal():
    sesion_principal()

if __name__ == "__main__":
    principal()
