# Python Audio Visualizer

## 1. Project Overview

This project is a real-time audio visualizer built with Python.

The program captures audio from a microphone, processes the audio data, calculates its strength, and converts the audio information into visual elements on the screen using Pygame.

The main goal is to understand how raw microphone audio can be processed with Python and turned into a real-time visualization.

---

## 2. Main Technologies

* **Python** - Main programming language
* **NumPy** - Numerical and audio-data processing
* **SoundCard** - Capturing audio from the microphone
* **Pygame** - Creating the visual interface and animation

---

## 3. Complete Project Flow

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
Get Microphone
  |
  v
Start Audio Recorder
  |
  v
Capture Audio Frames
  |
  v
Process Audio Data
  |
  v
Convert Stereo Audio to Mono
  |
  v
Calculate Audio Volume
  |
  v
Convert Volume to Visual Value
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

## 4. Core Audio Pipeline

The most important pipeline of the project is:

```text
Microphone
    |
    v
Audio Frames
    |
    v
NumPy Processing
    |
    v
Audio Volume / Strength
    |
    v
Visual Value
    |
    v
Pygame
    |
    v
Screen
```

---

## 5. Current Code Concepts

### 5.1 Creating the Recorder

```python
with mic.recorder(samplerate=48000) as recorder:
```

This creates a microphone recording session.

* `mic` represents the microphone.
* `recorder()` creates a recording session.
* `samplerate=48000` means the audio is captured at 48,000 samples/frames per second.
* `as recorder` stores the recording-session object in the variable `recorder`.
* `with` manages the recording session and automatically cleans it up when the block finishes.

---

### 5.2 Capturing Audio

```python
audio = recorder.record(numframes=1024)
```

This captures 1,024 audio frames from the microphone.

The returned audio data is stored in the variable `audio`.

With a sample rate of 48,000 frames per second:

```text
48,000 frames = 1 second
1,024 frames ≈ 0.0213 seconds
```

So the program processes small chunks of audio continuously.

---

### 5.3 Converting Stereo to Mono

```python
audio = np.mean(audio, axis=1)
```

If the microphone provides two channels, such as left and right:

```text
Left    Right
0.2     0.4
0.3     0.5
0.1     0.2
```

`np.mean(..., axis=1)` calculates the average of the channels for each frame.

The result is one value per frame.

```text
Stereo Audio
     |
     v
Left + Right
     |
     v
Average
     |
     v
Mono Audio
```

---

## 6. Audio Volume Calculation

After converting the audio to mono, the project calculates the strength of the current audio chunk.

Example:

```python
volume = np.linalg.norm(audio)
```

`np.linalg.norm()` produces a single value representing the overall strength of the audio samples.

The value can then be scaled and used to control the height of a visualizer bar.

```text
Audio samples
     |
     v
Calculate volume
     |
     v
Scale volume
     |
     v
Bar height
```

---

## 7. Visualization

Pygame is responsible for displaying the processed audio information.

The basic visualizer works like this:

```text
Quiet sound
    |
    v
Short bar

Loud sound
    |
    v
Tall bar
```

The program continuously updates the bar according to the incoming audio.

---

## 8. Main Program Architecture

The project can eventually be organized like this:

```text
audio_visualizer/
|
├── main.py
|
├── audio/
|   ├── __init__.py
|   └── recorder.py
|
├── visualizer/
|   ├── __init__.py
|   └── display.py
|
├── config.py
|
├── requirements.txt
|
└── README.md
```

For the learning/development stage, keeping the project in a single `main.py` file is recommended.

The code can be separated into modules after the main visualizer is working.

---

## 9. Development Stages

### Stage 1 - Audio Capture

Learn and implement:

* Microphone selection
* SoundCard recorder
* Sample rate
* Audio frames
* NumPy arrays

### Stage 2 - Audio Processing

Learn and implement:

* Mono conversion
* Audio amplitude/volume
* NumPy operations
* Scaling values

### Stage 3 - Basic Visualization

Learn and implement:

* Pygame window
* Drawing rectangles
* Mapping volume to bar height
* Screen updates

### Stage 4 - Real-Time Loop

Learn and implement:

* Continuous audio capture
* Pygame event handling
* Frame rate
* Smooth updates
* Program shutdown

### Stage 5 - Advanced Visualization

Learn and implement:

* FFT
* Frequency analysis
* Multiple bars
* Waveforms
* Smoother animations

---

## 10. Future Improvements

Once the basic visualizer works, the project can be extended with:

* Multiple visualization bars
* Waveform visualization
* Frequency spectrum visualization
* FFT-based frequency analysis
* Smoother bar animation
* Bass/mid/treble visualization
* Better UI
* Different visual effects
* Music-file input instead of only microphone input
* Audio-reactive animations

These are extensions to the basic project and are not required for the first working version.

---

## 11. Current Progress

Completed concepts:

* [x] Microphone object
* [x] Audio recorder
* [x] Sample rate
* [x] Audio frame capture
* [x] Understanding `with`
* [x] Understanding `recorder.record()`
* [x] Understanding `np.mean()`
* [x] Understanding `axis=1`

Current stage:

```text
Microphone
    |
    v
Capture 1024 frames
    |
    v
Convert stereo to mono
    |
    v
>>> NEXT: Calculate audio volume
```

---

## 12. Final Goal

The finished basic project should continuously listen to audio from the microphone and display the audio strength visually in real time.

```text
             Microphone
                  |
                  v
            Capture Audio
                  |
                  v
             Process Audio
                  |
                  v
           Calculate Volume
                  |
                  v
           Generate Visuals
                  |
                  v
                Pygame
                  |
                  v
            Visual Display
                  |
                  └──────> Repeat
```

The final result will be a real-time Python audio visualizer that connects:

**Microphone → Audio Processing → NumPy → Visualization → Pygame → Screen**
