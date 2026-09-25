# Python Audio Visualizer

## 1. Project Overview

This project is a real-time audio visualizer built with Python.

The program captures the audio currently playing on the computer, processes the audio data using NumPy, analyzes its frequency components using FFT, and displays the result as animated visualization bars using Pygame.

The project starts as a Python-based desktop visualizer. The long-term goal is to develop the visualization into a music-player style interface (reference image, no album art for now) on laptop screen, and later send the processed visualization data to an ESP32-C3 with an OLED display (on hold until screen arrives).

The main goal is to understand how real-time audio can be captured, processed, analyzed, and converted into visual information.

---

## 2. Main Technologies

- **Python 3.14.7** - Main programming language
- **NumPy 2.5.3** - Numerical and audio-data processing
- **SoundCard 0.4.6** - Capturing computer audio through loopback
- **pygame-ce 2.5.8** - Creating the visual interface and animation (replacement for pygame, no 3.14 wheel for pygame 2.6.1)
- **pyserial 3.5** - Laptop -> ESP32-C3 serial link (115200 baud)

Current hardware in hand:

- **ESP32-C3** - Main microcontroller (S3 ignored for now)
- **Laptop screen** - Temporary output (400x700 portrait player UI)

On-hold hardware (do NOT code yet):

- **OLED SSD1306 128x64 I2C** - Not yet received, will inform when available
- No album-art section for now (top zone stays blank black)

---

## 3. Current Project Flow

```text
START
  |
  v
Import Libraries
  |
  v
Initialize Pygame
  |
  v
Get Default Speaker
  |
  v
Create Loopback Audio Capture
  |
  v
Start Audio Recorder
  |
  v
Capture Audio Frames
  |
  v
Convert Stereo Audio to Mono
  |
  v
Apply Hann Window
  |
  v
Perform FFT
  |
  v
Convert FFT Magnitude to dB
  |
  v
Divide Frequencies into 32 Bands
  |
  v
Calculate Bar Values
  |
  v
Apply Bar Smoothing
  |
  v
Draw Visualizer
  |
  v
Update Screen
  |
  v
Repeat
  |
  +------ User quits? ------+
             |              |
            No             Yes
             |              |
             +---- Loop     v
                       Stop Recorder
                            |
                            v
                       Close Pygame
                            |
                            v
                           END
```

---

## 4. Target UI (reference image, no album for now)

Portrait player card `400x700`, black background:

- Top 0-380: blank black (album placeholder, skipped)
- Mid 380-500: Title `Perfect / Edsheeran`, time `0:30 / 4:25`, progress line + dot (fake timer)
- Bottom 500-700: 24 white mini-bars max 80px + dummy icons `shuffle, prev, play, next, repeat`

Audio chain unchanged: `48000Hz, 2048 frames, mono, Hann, RFFT, 2/N, dB, geomspace(20,20000), interp [-60,-5] -> [0,80], smooth +5/-3`.

Locked Step 2 (verified 2026-09-24, no code change): latency `42.67ms`, resolution `23.44Hz`, `1025 bins`, FFT ends `visual.py:83`, draw starts `:86`. Synthetic 440Hz -> peak 445Hz -12dB OK. Known: low log bands 1,2,4 have 0 bins (flicker risk, fix in Step 4 by merging).

C3 role (no OLED yet): receive `0xFF + 24 bytes` over USB-Serial 115200, blink onboard LED to bass. No FFT/WiFi/display on C3 yet.

## 5. 8-Step Plan (C3 only, OLED on hold)

1. Setup Check - DONE (see §6)
2. Lock Audio Pipeline - DONE (see §4 lock note)
3. Portrait Layout - DONE (400x700, zones 380/120/200, 32 bars temp-fit w=12, tick 30)
4. Bottom Mini Visualizer (32 -> 24 bars) - DONE (24 log bands, white, 0-80px, w12/gap4, width 396/400, empty bands [1,3])
5. Text + Progress + Dummy Controls - DONE (SysFont 32/22/16, fake 0:30/4:25 timer, progress dot, 5 dummy icons no click)
6. Serial Protocol on Laptop - DONE (0xFF+24B 0-80 @115200, auto-COM, display-only fallback, 750B/s, 0 COM ports found 2026-09-24)
7. C3 Firmware Without Screen
8. Integrate + Hold for OLED

## 6. Env Status - Step 1 DONE 2026-09-24

- Python 3.14.7, pip 26.2.1
- numpy 2.5.3, pygame-ce 2.5.8, soundcard 0.4.6, pyserial 3.5
- `visual.py` compiles OK, imports OK
- Speakers found: 2, default `Speakers (AB13X USB Audio)`
- Note: `pygame` 2.6.1 has no 3.14 wheel, use `pygame-ce` (`import pygame` still works)
