
#include <Arduino.h>
#include <stdint.h>

#ifndef LED_PIN
  #ifdef LED_BUILTIN
    #define LED_PIN LED_BUILTIN
  #else
    #define LED_PIN 8  // C3 onboard blue LED / RGB boards
  #endif
#endif

const uint8_t N_BARS = 24;
const uint8_t HDR = 0xFF;
const uint8_t BASS_N = 6;       // bars 0-5 = low freqs
const uint8_t BASS_THRESH = 8; // 0-80 scale, your music peaks ~15 so 8 catches the beat
uint8_t bars[N_BARS];
uint8_t idx = 0;
bool inPacket = false;
unsigned long lastLog = 0;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  // Boot self-test: blink 5 times so you can SEE which LED this code controls
  for (uint8_t k = 0; k < 5; k++) {
    digitalWrite(LED_PIN, HIGH); delay(150);
    digitalWrite(LED_PIN, LOW); delay(150);
  }
  Serial.begin(115200);
  // USB CDC: wait briefly for host, don't block forever
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) { delay(10); }
  Serial.println("[c3] ready, waiting FF + 24B @115200");
}

void loop() {
  while (Serial.available()) {
    uint8_t b = (uint8_t)Serial.read();
    if (!inPacket) {
      if (b == HDR) { inPacket = true; idx = 0; }
      continue;
    }
    if (idx < N_BARS) {
      bars[idx++] = (b > 80) ? 80 : b;
      if (idx >= N_BARS) {
        inPacket = false;
        onPacket();
      }
    } else {
      inPacket = (b == HDR); idx = 0;
    }
  }
}

void onPacket() {
  uint16_t sum = 0;
  for (uint8_t i = 0; i < BASS_N; i++) sum += bars[i];
  uint8_t bass = sum / BASS_N;
  digitalWrite(LED_PIN, bass > BASS_THRESH ? HIGH : LOW);
  unsigned long now = millis();
  if (now - lastLog > 500) {
    lastLog = now;
    Serial.print("[c3] bass=");
    Serial.print(bass);
    Serial.print(" avg_all=");
    uint16_t s = 0;
    for (uint8_t i = 0; i < N_BARS; i++) s += bars[i];
    Serial.println(s / N_BARS);
  }
}
