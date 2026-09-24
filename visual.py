import pygame
import soundcard as sc
import numpy as np

pygame.init()

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Music Visualizer")

speaker = sc.default_speaker()

mic = sc.get_microphone(
    speaker.name,
    include_loopback=True
)

running = True

with mic.recorder(samplerate=48000) as recorder:

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        audio = recorder.record(numframes=1024)

        audio = np.mean(audio, axis=1)

        fft = np.abs(np.fft.rfft(audio))

        bars = np.array_split(fft, 32)

        screen.fill((10, 10, 10))

        for i, bar in enumerate(bars):

             value = np.mean(bar)

             height = int(value * 5)
             height = min(height, 400)

             x = 20 + i * 24
             y = 450 - height

             pygame.draw.rect(
                 screen,
                (0, 200, 255),
                (x, y, 18, height)
             )

        pygame.display.flip()

pygame.quit()