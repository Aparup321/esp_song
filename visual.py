import pygame
import soundcard as sc
import numpy as np

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Music Visualizer")

# Get speaker and microphone
speaker = sc.default_speaker()

mic = sc.get_microphone(
    speaker.name,
    include_loopback=True
)

running = True

# Store previous heights for smoothing
previous_heights = [0] * 32

with mic.recorder(samplerate=48000) as recorder:

    while running:

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Capture audio
        audio = recorder.record(numframes=2048)

        # Convert stereo audio to mono
        audio = np.mean(audio, axis=1)

        # Create Hann window
        window = np.hanning(len(audio))

        # Apply window to audio
        windowed_audio = audio * window

        # Perform FFT
        fft = np.abs(np.fft.rfft(windowed_audio))

        # Normalize FFT magnitude
        fft = fft * (2 / len(audio))

        # Convert magnitude to decibels
        fft = 20 * np.log10(np.maximum(fft, 1e-10))

        # Get frequency of each FFT bin
        frequencies = np.fft.rfftfreq(
            len(audio),
            1 / 48000
        )

        # Create 32 logarithmic frequency ranges
        frequency_ranges = np.geomspace(
            20,
            20000,
            33
        )

        bars = []

        # Divide frequencies into 32 bars
        for i in range(32):

            low = frequency_ranges[i]
            high = frequency_ranges[i + 1]

            mask = (
                (frequencies >= low) &
                (frequencies < high)
            )

            if np.any(mask):
                bars.append(fft[mask])
            else:
                bars.append(np.array([0]))

        # Draw background
        screen.fill((10, 10, 10))

        # Draw visualizer bars
        for i, bar in enumerate(bars):

            # Average value of this frequency range
            value = np.mean(bar)

            # Convert dB value into screen height
            height = int(
                np.interp(
                    value,
                    [-60, -5],
                    [0, 400]
                )
            )

            # Prevent bars from becoming taller than 400 pixels
            height = min(height, 400)

            # Smooth bar movement
            if height > previous_heights[i]:
                previous_heights[i] += 5
            else:
                previous_heights[i] -= 3

            # Prevent negative height
            previous_heights[i] = max(
                0,
                previous_heights[i]
            )

            height = previous_heights[i]

            # Calculate bar position
            x = 20 + i * 24
            y = 450 - height

            # Draw bar
            pygame.draw.rect(
                screen,
                (0, 200, 255),
                (x, y, 18, height)
            )

        # Update display
        pygame.display.flip()

pygame.quit()