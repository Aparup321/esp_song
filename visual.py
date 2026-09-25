import pygame
import soundcard as sc
import numpy as np

# Step 6: serial link to ESP32-C3 (optional, visualizer works without it)
try:
    import serial
    from serial.tools import list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

# Initialize Pygame
pygame.init()

# Step 3: Portrait player layout (OLED-ready zones)
WIDTH, HEIGHT = 400, 700
TOP_H, MID_H, BOT_H = 380, 120, 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Visualizer")

# Step 5: fonts + fake song timer (dummy metadata for now)
title_font = pygame.font.SysFont(None, 32)
artist_font = pygame.font.SysFont(None, 22)
time_font = pygame.font.SysFont(None, 16)
song_pos = 30.0  # start at 0:30 like reference image
SONG_TOTAL = 4 * 60 + 25  # 4:25

# Get speaker and microphone
speaker = sc.default_speaker()

mic = sc.get_microphone(
    speaker.name,
    include_loopback=True
)

running = True

# Store previous heights for smoothing
previous_heights = [0] * 24

# Step 6: open C3 serial if present, else run display-only
ser = None
if HAS_SERIAL:
    try:
        ports = list(list_ports.comports())
        # Prefer USB serial devices (CH340/CP210x/CDC) but fall back to first port
        c3_port = None
        for p in ports:
            desc = (p.description or "") + " " + (p.manufacturer or "")
            if any(k in desc for k in ("CH340", "CP210", "USB", "CDC", "Serial")):
                c3_port = p.device
                break
        if c3_port is None and ports:
            c3_port = ports[0].device
        if c3_port:
            ser = serial.Serial(c3_port, 115200, timeout=0)
            print(f"[serial] C3 link open: {c3_port} @115200")
        else:
            print("[serial] no COM port found, display-only mode")
    except Exception as e:
        print(f"[serial] open failed ({e}), display-only mode")
        ser = None

frame_count = 0

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

        # Create 24 logarithmic frequency ranges (Step 4: OLED-fit)
        frequency_ranges = np.geomspace(
            20,
            20000,
            25
        )

        bars = []

        # Divide frequencies into 24 bars
        for i in range(24):

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

        # Step 5: fake timer + text + progress (dummy, no real metadata yet)
        song_pos += 1.0 / 30.0
        if song_pos >= SONG_TOTAL:
            song_pos = 0.0
        mid_y = TOP_H
        title_surf = title_font.render("Perfect", True, (255, 255, 255))
        artist_surf = artist_font.render("Edsheeran", True, (170, 170, 170))
        screen.blit(title_surf, (20, mid_y + 8))
        screen.blit(artist_surf, (20, mid_y + 38))
        cur_m, cur_s = int(song_pos // 60), int(song_pos % 60)
        tot_m, tot_s = int(SONG_TOTAL // 60), int(SONG_TOTAL % 60)
        time_surf = time_font.render(f"{cur_m}:{cur_s:02d}", True, (150, 150, 150))
        total_surf = time_font.render(f"{tot_m}:{tot_s:02d}", True, (150, 150, 150))
        screen.blit(time_surf, (20, mid_y + 62))
        screen.blit(total_surf, (WIDTH - 50, mid_y + 62))
        # Progress line + dot
        px1, px2, py = 20, WIDTH - 20, mid_y + 92
        pygame.draw.line(screen, (60, 60, 60), (px1, py), (px2, py), 2)
        frac = song_pos / SONG_TOTAL
        dot_x = int(px1 + frac * (px2 - px1))
        pygame.draw.line(screen, (255, 255, 255), (px1, py), (dot_x, py), 2)
        pygame.draw.circle(screen, (255, 255, 255), (dot_x, py), 4)

        # Step 5: dummy controls row (no click logic yet)
        cy = TOP_H + MID_H + 40
        # shuffle (x-cross) at 60
        pygame.draw.line(screen, (150, 150, 150), (50, cy - 8), (70, cy + 8), 2)
        pygame.draw.line(screen, (150, 150, 150), (50, cy + 8), (70, cy - 8), 2)
        # prev at 130: bar + left triangle
        pygame.draw.rect(screen, (255, 255, 255), (112, cy - 10, 4, 20))
        pygame.draw.polygon(screen, (255, 255, 255), [(140, cy - 10), (140, cy + 10), (120, cy)])
        # play at 200: circle + triangle
        pygame.draw.circle(screen, (255, 255, 255), (200, cy), 20, 2)
        pygame.draw.polygon(screen, (255, 255, 255), [(194, cy - 10), (194, cy + 10), (210, cy)])
        # next at 270: right triangle + bar
        pygame.draw.polygon(screen, (255, 255, 255), [(260, cy - 10), (260, cy + 10), (280, cy)])
        pygame.draw.rect(screen, (255, 255, 255), (284, cy - 10, 4, 20))
        # repeat at 340: rect loop
        pygame.draw.rect(screen, (150, 150, 150), (328, cy - 8, 24, 16), 2)

        # Draw visualizer bars (Step 4: 24 white mini-bars, max 80px)
        bar_w, bar_gap, bar_margin = 12, 4, 8
        for i, bar in enumerate(bars):

            # Average value of this frequency range
            value = np.mean(bar)

            # Convert dB value into screen height (Step 4: mini-strip)
            height = int(
                np.interp(
                    value,
                    [-60, -5],
                    [0, 80]
                )
            )

            # Prevent bars from becoming taller than 80 pixels
            height = min(height, 80)

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

            # Calculate bar position (bottom zone, Step 4 fit)
            x = bar_margin + i * (bar_w + bar_gap)
            y = (TOP_H + MID_H + BOT_H - 10) - height

            # Draw bar (white for 1-bit OLED parity)
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (x, y, bar_w, height)
            )

        # Step 6: send packet to C3 (0xFF header + 24 bytes 0-80)
        if ser is not None:
            try:
                payload = bytes([max(0, min(80, int(v))) for v in previous_heights])
                ser.write(bytes([0xFF]) + payload)
                frame_count += 1
                if frame_count <= 3:
                    print(f"[serial] pkt {frame_count}: FF + {payload.hex(' ')}")
            except Exception as e:
                print(f"[serial] write failed ({e}), display-only mode")
                try:
                    ser.close()
                except Exception:
                    pass
                ser = None

        # Update display
        pygame.display.flip()
        clock.tick(30)

if ser is not None:
    try:
        ser.close()
    except Exception:
        pass

pygame.quit()