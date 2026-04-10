import numpy as np
import wave

# Nota: No se necesita inicializar pygame para generar archivos WAV

def generar_tono(frecuencia, duracion, volumen=0.5):
    """Genera un tono simple"""
    frecuencia_muestreo = 44100
    num_muestras = int(frecuencia_muestreo * duracion)

    # Generar onda sinusoidal
    t = np.linspace(0, duracion, num_muestras, False)
    datos_onda = np.sin(frecuencia * 2 * np.pi * t) * volumen

    # Convertir a enteros de 16 bits
    datos_onda = (datos_onda * 32767).astype(np.int16)

    return datos_onda.tobytes()

def crear_archivo_sonido(nombre_archivo, frecuencia, duracion, volumen=0.5):
    """Crea un archivo WAV de sonido"""
    frecuencia_muestreo = 44100
    datos_onda = generar_tono(frecuencia, duracion, volumen)

    with wave.open(nombre_archivo, 'wb') as archivo_wav:
        archivo_wav.setnchannels(1)  # Mono
        archivo_wav.setsampwidth(2)  # 16 bits
        archivo_wav.setframerate(frecuencia_muestreo)
        archivo_wav.writeframes(datos_onda)

# Crear efectos de sonido
print("Creando efectos de sonido...")

# Sonido de comer - pitido corto y agudo
crear_archivo_sonido('eat.wav', 800, 0.1, 0.3)

# Sonido de muerte - tono descendente
# Para simplificar, usar un tono bajo
crear_archivo_sonido('death.wav', 200, 0.5, 0.4)

# No se genera música de fondo para evitar ruido estático constante

print("Archivos de sonido creados: eat.wav, death.wav")