# SMK25II User Manual

## Mode Selection (Shift Mode)

Press **MCP button** to enter mode selection.

**Pads:**
- Pad 0 (top-left): Mode 0 - Session
- Pad 1: Mode 1 - Device
- Pad 2: Mode 2 - Mix
- Pad 3: Mode 3 - Sends
- Pad 4-5: (not implemented)
- Pad 6: Mode 6 - Crossfader
- Pad 7: (not implemented)
- Pad 8: Mode 8 - Drums
- Pad 9: Mode 9 - Drum Color
- Pad 10-15: (not implemented)

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

## Mode 6 - Crossfader

**Top Row Pads (0-7):**
- Cycle crossfader assignment for 8 visible tracks
- Press to cycle: None → A → B → None
- None: dim track color
- A: red (left)
- B: blue (right)

**Bottom Row Pads (8-15):**
- Pad 8: Snap crossfader to A (left, red)
- Pad 9: Snap crossfader to center (dim white)
- Pad 10: Snap crossfader to B (right, blue)
- Pad 11: Unused (off)
- Pad 12-13: Track left/right by 8 (orange)
- Pad 14-15: Undo/redo (white)

**Knobs:**
- Knob 1: Scroll through tracks (same as track navigation)
- Knob 8: Control crossfader position
  - ±2% per step
  - Left (min) = A tracks only
  - Center = both A and B tracks
  - Right (max) = B tracks only

**Notes:**
- Red box highlights 8 visible tracks (8 wide × 1 tall)
- Red box moves when navigating tracks
- Tracks assigned to "None" always play regardless of crossfader position
- Perfect for DJ-style mixing and live transitions

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

## Mode 9 - Drum Color

Interactive drum pad mode with per-pad color editing and persistence.

**Pads:**
- Bottom row (8-15): Drum notes C1-G1 (MIDI notes 36-43)
- Top row (0-7): Drum notes G#1-D#2 (MIDI notes 44-51)
- Notes pass through directly to Ableton
- Channel: 9 (Channel 10)
- Colors: Individually editable per pad (persists per instrument)

**Knobs (HSV Controls):**
- Knob 0: Hue adjustment
  - On mode entry: adjusts all pads (until you press a pad or 0.5s passes)
  - After pressing pad(s): release → rotate knob within 0.5s to adjust those pads
  - After 0.5s of no pad presses: knobs do nothing (prevents accidents)
  - Hue wraps around (full color wheel)
  - ±2% per step

- Knob 1: Saturation adjustment
  - Same targeting behavior as Knob 0
  - Range: 0-100%
  - ±2% per step

- Knob 2: Brightness adjustment
  - Same targeting behavior as Knob 0
  - Range: 0-100%
  - ±2% per step

**Knobs (RGB Controls):**
- Knob 3: Red channel adjustment
  - Same targeting behavior as Knob 0
  - Adjusts red component directly
  - ±4% per step (2x speed)

- Knob 4: Green channel adjustment
  - Same targeting behavior as Knob 0
  - Adjusts green component directly
  - ±4% per step (2x speed)

- Knob 5: Blue channel adjustment
  - Same targeting behavior as Knob 0
  - Adjusts blue component directly
  - ±4% per step (2x speed)

**Knobs (Special Functions):**
- Knob 6: Match color
  - Moves all recently released pads towards the most recently pressed pad's color
  - Each rotation moves all HSV components 4% closer to target
  - Useful for making multiple pads share similar colors

- Knob 7: History navigation
  - Navigate through last 16 instrument color layouts
  - Useful for copying color schemes between drum instruments
  - Select instrument A → go to instrument B → rotate knob 7 → loads A's colors

**Color Persistence:**
- Colors are saved per instrument device
- File location: `~/.config/SMK25II/drum_colors.json`
- Human-readable JSON format
- Stores HSV values (hue, saturation, brightness) for each pad
- Maintains history of last 16 instruments

**Workflow:**
1. Enter Mode 9 (Drum Color)
2. To set initial colors for all pads:
   - Immediately after entering mode, rotate knobs 0-2 (HSV)
   - All pads change together (you have 0.5s before this expires)
3. To adjust specific pads:
   - Press the pad(s) you want to edit
   - Release them (you can see the colors now)
   - Within 0.5 seconds, rotate knobs:
     - Knobs 0-2: Adjust hue/saturation/brightness (HSV)
     - Knobs 3-5: Adjust red/green/blue (RGB, faster)
     - Knob 6: Match color to most recently pressed pad
   - Colors update in real-time and save automatically
4. Play pads to trigger drums and see their colors
5. Switch instruments - colors automatically update to that instrument's layout
6. Use knob 7 to copy color layouts between instruments

**Notes:**
- The 0.5-second window allows you to release pads one-by-one without losing the selection
- Hardware lights pads white when held - release them to see your color edits
- After 0.5s of inactivity, knobs do nothing (prevents accidental changes)
- Colors persist per instrument device across sessions
- Switching tracks/devices automatically loads that instrument's color layout
- Use HSV knobs (0-2) for intuitive color adjustments
- Use RGB knobs (3-5) for precise color matching or faster adjustments
- Match color (knob 6) helps create cohesive color schemes quickly

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
- Crossfader mode: Pads=5, Knobs=5
- Drums mode: Pads=0, Knobs=1
- Drum Color mode: Pads=9, Knobs=10
- Shift mode: Pads=15, Knobs=14

**Performance:**
- MIDI send interval: 1ms minimum between messages
- Caching prevents redundant updates
- Bulk mode available for faster initialization
