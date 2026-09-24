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

        volume = np.abs(audio).mean()

        bar_height = int(volume * 1000)
        bar_height = min(bar_height, 400)

        screen.fill((10, 10, 10))

        pygame.draw.rect(
            screen,
            (0, 200, 255),
            (350, 450 - bar_height, 100, bar_height)
        )

        pygame.display.flip()

pygame.quit()