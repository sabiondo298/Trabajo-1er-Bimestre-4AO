import numpy as np
import wave

# Note: No pygame initialization needed for WAV file generation

def generate_tone(frequency, duration, volume=0.5):
    """Generate a simple tone"""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    # Generate sine wave
    t = np.linspace(0, duration, num_samples, False)
    wave_data = np.sin(frequency * 2 * np.pi * t) * volume

    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)

    return wave_data.tobytes()

def create_sound_file(filename, frequency, duration, volume=0.5):
    """Create a WAV sound file"""
    sample_rate = 44100
    wave_data = generate_tone(frequency, duration, volume)

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data)

# Create sound effects
print("Creating sound effects...")

# Eat sound - short high-pitched beep
create_sound_file('eat.wav', 800, 0.1, 0.3)

# Death sound - descending tone
# For simplicity, just create a low tone
create_sound_file('death.wav', 200, 0.5, 0.4)

# Background music - longer, more complex tone (just a placeholder)
create_sound_file('background.wav', 440, 2.0, 0.1)

print("Sound files created: eat.wav, death.wav, background.wav")