# SMK25II User Manual

## Mode Selection (Shift Mode)

Press **MCP button** to enter mode selection.

**Pads:**
- Pad 0 (top-left): Mode 0 - Session
- Pad 1: Mode 1 - (not implemented)
- Pad 2: Mode 2 - Device
- Pad 3-7: (not implemented)
- Pad 8: Mode 8 - Drums
- Pad 9-15: (not implemented)

**Knobs (Global Navigation):**
- Knob 1: Select track (left/right through tracks)
- Knob 2: Select scene (up/down through scenes)
- Knob 6: Selected track volume
- Knob 7: Master volume
- Knob 8: Undo/redo (left=undo, right=redo)

---

## Mode 0 - Session

**Pads (7×2 grid + scenes):**
- Columns 0-6: Clips in red box (7 wide × 2 tall)
  - Empty slot: dim track color
  - Stopped clip: track color
  - Playing clip: blend white + track color
  - Recording clip: blend red + track color
- Column 7: Scene launch (master track color)

**Knobs:**
- Knob 1: Red box horizontal scroll (left/right)
- Knob 2: Red box vertical scroll (up/down)
- Knob 3: Pad launch mode (play/stop, stop only, record)
  - Shows selection on bottom-left 3 pads while turning
  - Times out after 0.25 seconds
- Knob 4: Global quantization (0-13)
- Knob 5: Tempo (20-999 BPM, ±1 BPM per step)
- Knob 6: Metronome (right=on, left=off)
- Knob 7: Master volume (±2% per step)
- Knob 8: Undo/redo (left=undo, right=redo)

**Pad Launch Modes (Knob 3):**
- Mode 0: Play/Stop (toggle clips)
- Mode 1: Stop only (only stops, won't start)
- Mode 2: Record (arms track and records)

---

## Mode 2 - Device

**Top Row Pads (0-7):**
- Select device 1-8 on current track
- Selected device: blue
- Available device: dim white
- No device: off

**Bottom Row Pads (8-15):**
- Pad 8: Bank left (-8 parameters)
- Pad 9: Bank right (+8 parameters)
- Pad 10: Device left (-8 devices)
- Pad 11: Device right (+8 devices)
- Pad 12: Track left (-8 tracks)
- Pad 13: Track right (+8 tracks)
- Pad 14: Undo
- Pad 15: Redo

**Knobs:**
- Knobs 0-7: Control 8 device parameters (current bank)
  - Bank 0: Parameters 0-7
  - Bank 1: Parameters 8-15
  - etc.
  - ±2% of parameter range per step

**Notes:**
- Changing tracks resets to device 0, bank 0
- Non-automatable and quantized parameters are skipped
- Bottom row pads: orange (function pads), white (undo/redo)

---

## Mode 8 - Drums

**Pads:**
- All 16 pads: Drum notes C1-D#2 (MIDI notes 36-51)
- Channel: 10 (standard drum channel)
- Color: orange (all pads)

**Knobs:**
- Not yet implemented

---

## Hardware Notes

**Relative Knobs:**
- All knobs send only two values:
  - 0x7F (127): Clockwise rotation
  - 0x00 (0): Counter-clockwise rotation

**Pad Colors:**
- RGB format: R (lowest byte) | G<<8 | B<<16
- LED state: 0-127=off, 128-255=on

**MIDI Channels:**
- Session mode: Pads=13, Knobs=0
- Device mode: Pads=2, Knobs=2
- Drums mode: Pads=0
- Shift mode: Pads=15, Knobs=14

**Performance:**
- MIDI send interval: 1ms minimum between messages
- Caching prevents redundant updates
- Bulk mode available for faster initialization
