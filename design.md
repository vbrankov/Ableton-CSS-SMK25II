For start we'll just implement the Preset 1.

# Preset 1

The shift mode will select the functions of knobs and pads in non-shift mode. We will call these modes. There will be 16 modes, one for each pad. The top left pad will be mode 0, mode 1 will be the pad right of it and so on. Mode 8 will be the bottom left pad, and so on. The pad of the currently selected mode will be lit white.

Pressing a pad and holding it and then pressing another pad will make pads act as the first mode and knobs as the second mode. In this case, the colors of the selected pads will be red and blue instead of just white.

# Mode 0 - Session

There will be red box 7 wide and 2 tall. Pads will display clips in the red box. The rightmost column will represent scene. Pressing each pad will trigger the pad function, which will be selected with one of the knobs. Pads will have the same color as the Ableton track. If a pad is empty it will have a very dark shade of the track color. If a pad is starting it will flash two colors: its dark shade and the track color. If the pad is playing it will flash white and the color of the track. If the pad is recording it will flash red and the color of the track. Flashing doesn't have to be too fast, maybe every half a second or synchronize with the tempo.

Knob functions:

  - Red box vertical move. As the red box is moved, the colors of the pads follow.
  - Red box horizontal move.
  - Mode of the pads: play/stop, stop, record. As the knob is rotated, all the pads are unlit except the bottom left three pads which are lit to represent the mode selected. Once the knob stops rotating, the pads go bad to their usual colors.
  - Global quantization
  - Tempo
  - Metronome volume
  - Master volume
  - Undo/redo

# Mode 1 - Device

The knobs represent the blue hand knobs. The top row will select the device 1-8. The bottom row will be:

  - Pads 1-2: Bank blue hand by 8
  - Pads 3-4: Navitage devices by 8
  - Pads 5-6: Navigate tracks by 8
  - Pads 7-8: Undo/Redo

# Mode 2 - Sends

The knobs represent sends of the 8 tracks. The top row of the pads will select the send 1-8. The bottom row will be:

  - Pads 1-2: Navigate sends by 8
  - Pads 3-4: Unused
  - Pads 5-6: Navigate tracks by 8
  - Pads 7-8: Undo/Redo

# Mode 3 - Mix mode

The knobs represent the track volumes. The top row of the pads will mute or solo tracks, denpending on row mode selector. Bottom row of the pads will be:

  - Pads 1-2: Mode selector (Mute/Solo)
  - Pads 3-4: Unused
  - Pads 5-6: Navigate tracks by 8
  - Pads 7-8: Undo/Redo

When the mode changes, the top row will adjust colors. Muted or solo track will have the full color of the track, the remaining tracks will be the dark shade of the track.

# Mode 4 - Edit clip (pending)

Pads show clips in red box, 8 x 2. The rest of the mode has to be defined, but knobs should include:

  - Scroll red box
  - Dusplicate clip
  - Delete clip
  - Clip length
  - loop

# Mode 5 - Instruments and Devices

  - Knob 1: Navigate tracks. If past the last track, creates a new midi track.
  - Knob 2: Navigate browser hierarchy (folders, categories up/down)
  - Knob 3: Scroll items at current hierarchy level (one by one)
  - Knob 4: Fast scroll (jump by 8)
  - Knob 5: Navigate devices on current track
  - Knob 6: Reorder devices (move selected device left/right)
  - Knob 7: Unused
  - Knob 8: Undo/Redo

Pad 1 tapped alone adds the given instrument or device to the track. Pad 2 deletes the selected device. Holding a combination of other pads for a longer time, like a second, memorizes the instrument or device to the combination. A short press of the combination adds the given instrument or device.

# Mode 6 - Crossfader

  - Knob 1: Scroll tracks
  - Knob 8: Crossfader position

Top row pads: Assign tracks to A/B/None
Bottom row pads:

  - Pads 5-6: Navigate tracks by 8
  - Pads 7-8: Undo/Redo

# Mode 8 - Drums

All 16 pads will represent drums (C1-D#2, MIDI channel 10). Knobs will be the blue hand of the drums.

# Mode 9 - Drum Color

All 16 pads play drums. Holding a set of pads and rotating the first three knobs change: hue, saturation, brightness. Rotating the pads without holding pads changes color values for all pads. Hue rotates.

The color scheme of the drums will be tied to the selected instrument. If another instrument is selected, if colors weren't assigned to it, it gets assigned the last shown color selection. Going to mode 9 and rotating the knob 4 displays one of 16 last color layouts of instruments. So to copy a layout of another drum set we just need to select it, go to the new drum set and rotate knob 4 and the layout of the last instrument will be selected. As I wrote, that history size is 16. The colors and assignments are stored in a configuration file that Ableton allow CSS to have.