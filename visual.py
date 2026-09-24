import pygame
import soundcard as sc
import numpy as np

# Initialize Pygame
pygame.init()

# Step 3: Portrait player layout (OLED-ready zones)
WIDTH, HEIGHT = 400, 700
TOP_H, MID_H, BOT_H = 380, 120, 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

clock = pygame.time.Clock()

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

        # Draw background zones
        # Top: album placeholder (blank black for now)
        screen.fill((10, 10, 10))
        pygame.draw.rect(screen, (10, 10, 10), (0, 0, WIDTH, TOP_H))
        # Mid: text + progress zone (Step 5)
        pygame.draw.rect(screen, (16, 16, 16), (0, TOP_H, WIDTH, MID_H))
        # Bottom: bars + controls zone
        pygame.draw.rect(screen, (10, 10, 10), (0, TOP_H + MID_H, WIDTH, BOT_H))
        # Zone dividers
        pygame.draw.line(screen, (40, 40, 40), (0, TOP_H), (WIDTH, TOP_H))
        pygame.draw.line(screen, (40, 40, 40), (0, TOP_H + MID_H), (WIDTH, TOP_H + MID_H))

        # Draw visualizer bars (temp fit: 32 bars into 400px width, bottom zone)
        bar_w = WIDTH // 32
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

            # Calculate bar position (bottom zone, temp fit for Step 3)
            x = i * bar_w + 1
            y = (TOP_H + MID_H + BOT_H - 10) - height
            bar_draw_w = bar_w - 2

            # Draw bar
            pygame.draw.rect(
                screen,
                (0, 200, 255),
                (x, y, bar_draw_w, height)
            )

        # Update display
        pygame.display.flip()
        clock.tick(30)

pygame.quit()