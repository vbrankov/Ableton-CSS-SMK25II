# SMK25II User Manual

## Mode Selection (Shift Mode)

Press **MCP button** to enter mode selection.

**Pads:**
- Pad 0 (top-left): Mode 0 - Session
- Pad 1: Mode 1 - Device
- Pad 2: Mode 2 - Mix
- Pad 3: Mode 3 - Sends
- Pad 4-7: (not implemented)
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

## Mode 1 - Device

**Top Row Pads (0-7):**
- Select device 1-8 on current track
- Selected device: blue
- Available device: dim white
- No device: off

**Bottom Row Pads (8-15):**
- Pad 8-9: Bank left/right (yellow)
- Pad 10-11: Device left/right by 8 (cyan)
- Pad 12-13: Track left/right by 1 (magenta)
- Pad 14-15: Undo/redo (white)

**Knobs:**
- Knobs 0-7: Control 8 device parameters (current bank)
  - Skips "Device On" parameter at index 0
  - Bank 0: Parameters 1-8
  - Bank 1: Parameters 9-16
  - ±2% of parameter range per step (continuous params)
  - ±1 per step (quantized params like switches)

**Notes:**
- Changing tracks resets to device 0, bank 0
- Appointed device gets controlled (may differ from selected device)

---

## Mode 2 - Mix

**Top Row Pads (0-7):**
- Toggle mute or solo for 8 visible tracks
- Mode selector determines mute/solo behavior
- Active (muted/soloed): full track color
- Inactive: dim track color
- No track: off

**Bottom Row Pads (8-15):**
- Pad 8: Mute mode (orange when active, dim when inactive)
- Pad 9: Solo mode (orange when active, dim when inactive)
- Pad 10-11: Unused (off)
- Pad 12-13: Track left/right by 8 (orange)
- Pad 14-15: Undo/redo (white)

**Knobs:**
- Knobs 0-7: Control track volumes for 8 visible tracks
  - ±2% of volume range per step

**Notes:**
- Red box highlights 8 visible tracks (8 wide × 1 tall)
- Red box moves when navigating tracks
- Auto-updates when tracks change or mute/solo state changes

---

## Mode 3 - Sends

**Top Row Pads (0-7):**
- Select which send to control (Send A-H)
- Selected send: blue
- Other sends: dim white

**Bottom Row Pads (8-15):**
- Pad 8-9: Send left/right by 8 (green)
- Pad 10-11: Unused (off)
- Pad 12-13: Track left/right by 8 (orange)
- Pad 14-15: Undo/redo (white)

**Knobs:**
- Knobs 0-7: Control selected send level for 8 visible tracks
  - ±2% of send range per step

**Notes:**
- Red box highlights 8 visible tracks (8 wide × 1 tall)
- Red box moves when navigating tracks
- Select send with top row pads, then adjust levels with knobs

---

## Mode 8 - Drums

**Pads:**
- Bottom row (8-15): Drum notes C1-G1 (MIDI notes 36-43)
- Top row (0-7): Drum notes D2-B2 (MIDI notes 44-51)
- Notes pass through directly to Ableton (no script interception)
- Channel: 0 (Channel 1)
- Color: orange (all pads)

**Knobs:**
- Knobs 0-7: Control first device parameters (typically Instrument Rack macros)
  - Skips "Device On" parameter
  - Controls parameters 1-8 of first device on track
  - ±2% per step (continuous), ±1 per step (quantized)

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
- Mix mode: Pads=3, Knobs=3
- Sends mode: Pads=4, Knobs=4
- Drums mode: Pads=0, Knobs=1
- Shift mode: Pads=15, Knobs=14

**Performance:**
- MIDI send interval: 1ms minimum between messages
- Caching prevents redundant updates
- Bulk mode available for faster initialization
