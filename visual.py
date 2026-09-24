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

        # Calculate audio volume
        volume = np.linalg.norm(audio)
        volume_level = int(volume * 100)

        print(volume_level)

        # Convert audio to frequency data
        fft = np.abs(np.fft.rfft(audio))

        # Divide frequency data into 32 bars
        frequencies = np.fft.rfftfreq(len(audio), 1 / 48000)

        frequency_ranges = np.geomspace(20, 20000, 33)

        bars = []

        for i in range(32):
            low = frequency_ranges[i]
            high = frequency_ranges[i + 1]

            mask = (frequencies >= low) & (frequencies < high)

            if np.any(mask):
                bars.append(fft[mask])
            else:
                bars.append(np.array([0]))

        screen.fill((10, 10, 10))

        # Draw the visualizer bars
        for i, bar in enumerate(bars):

            value = np.mean(bar)
            #compress large FFT values
            value = np.log1p(value)

            height = int(value * 100)
            height = min(height, 400)

            # Smooth the movement
            if height > previous_heights[i]:
                previous_heights[i] += 5
            else:
                previous_heights[i] -= 3

            previous_heights[i] = max(0, previous_heights[i])
            height = previous_heights[i]

            x = 20 + i * 24
            y = 450 - height

            pygame.draw.rect(
                screen,
                (0, 200, 255),
                (x, y, 18, height)
            )

        pygame.display.flip()

pygame.quit()