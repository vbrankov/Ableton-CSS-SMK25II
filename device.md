The goal of this project is to create Ableton Live Control Surface Script (CSS) for the midi device SMK25II.

# Device

SMK25II is a midi controller with 8 infinite knobs, 16 velocity and pressure sensitive rgb illuminated pads and 25 piano keys in two octaves. The knobs and pads are fully configurable. In addition, there is a button MCP which we'll call "Shift" in the following test. It enables secondary function of knobs and pads and it is sticky. The user has to press it again to leave the "Shift" mode. In addition to all this, the controller has 8 presets, each of which enables a different configuration for each knob and pad including its shift mode. The pads are organized in two rows of 8 pads each, each column of pads right below each knob. The bottom row of pads has icons below it: play, pause, record, rewind, fast forward, left, right, undo. The row of knobs has labels each one: mode, oct, latch, gate, swing, tempo, rate, transpose.

Each knob has the following values configurable. The number before the name is the offset of the parameter. Each value is 8 bit unless otherwise stated. Enumerated values are encoded as integers in the order presented.

  0 Type: CC, Aftertouch, Note, CW
  1 Speed: Slowest, Slow, Normal, Fast, Fastest
  2 Channel: 1 to 16
  3 CC: 0 - 127
  4 Min: 0 - 127
  5 Max: 0 - 127

## Relative Knob Encoding

When a knob is configured as relative (Type: CW), it sends only two CC values:
- 0x00 (0): Counter-clockwise rotation
- 0x7F (127): Clockwise rotation

Each rotation increment produces one of these values, regardless of the Speed setting.

Each pad has the following values configurable:

  0 Type: Note, CC Toggle, Momentary, Program, MCP, Custom, Comb MCP
  1 Channel: 1 to 16
  2 Note: 0 (C -1) to 127 (B 9)
  3 MinVel: 0 - 127
  4 MaxVel: 0 - 127
  5 Color: RGB 24bit. Red is the lowest bit.
  8 Led: 0 - 255. 0 - 127 off, 128 - 255 on
  9 Sysex: 520-bit message

# Sysex Protocol

Sysex messages are used to configure the device. The message format is byte sequence of the following format:

  - Header, which is usually F0 00 32 09 49 00 40 02. Messages for setting color have 59 in the header instead of 49. Messages for setting SysEx for pads have 49 04 in the header instead of 49 00.
  - Parameter address, which is represented as 4 7-bit numbers. Lowest bits come first.
  - Value length in bits, which is represented as 4 7-bit numbers. The length is stored multiplied by 2. So for a value of length 8-bits the length is 10 00 00 00.
  - Value, stored as 7-bit sequence. An 8-bit value has to be stored as two 7-bit sequences, where the second sequence uses only the first bit.
  - 8-bit crc number which is concatenated with the value so that it starts right after the last bit of the value. For example, the value FF with CRC 61 is stored as 7F 83 01.
  - Footer: F7

There are many parameters but this document will explain only what is interesting for our project. The address of the parameters for the knob 1 in preset 1 is 1E. That means that the message which sets Type to Aftertouch is:

    F0 00 32 09 49 00 00 40 02 1E 00 00 00 10 00 00 00 01 34 03 F7

The starting address knobs 2 is 6 plus starting address for knob 1, so 24. 8 knobs are stored next to each other followed by the configuration for knobs in the shift mode. Therefore the base address for knob 1 in shift mode is 4E.

The starting address for pad 1 is 7E which comes right after the last knob in the shift mode. All pad configurations follow one another just like for knobs, so each pad configuration is 74 memory addresses apart. Similarily to the knobs, pad configurations in the shift mode follow the pad configurations in the non shift mode.

Preset configurations are spaced 2504 addresses apart. So the memory address for knob 1 in preset 2 is encoded as 66 13 (7-bit values) which is 2504 memory addresses away from 1E. There are 8 presets.

Examples:

  - Set color of pad 1 preset 1 to red:

      F0 00 32 09 59 00 00 40 02 03 01 00 00 30 00 00 00 7F 01 00 28 07 F7

  - Set color of pad 2 preset 3 to green:

      F0 00 32 09 59 00 00 40 02 15 15 00 00 30 00 00 00 00 7E 03 48 05 F7
  
  - Set sysex:

      F0 00 32 09 49 04 00 40 02 07 01 00 00 10 08 00 00 01
      7C 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      00 4C 01 F7

## Setting Pad SysEx (COMB_MCP)

When a pad is configured as type "Comb MCP" (type 6), it can send a custom MIDI message sequence when pressed. This is configured via the sysex field (offset 9 from pad base address).

**SysEx Payload Format:**
- The sysex field is 520 bits (65 bytes)
- The first byte is the **length** of the MIDI message to send
- Remaining bytes are the actual MIDI message bytes
- MIDI bytes can be any 8-bit value (0x00-0xFF), including values > 127 like 0xF0

**Example:** To send dual-channel drum notes (for playback on ch0 and tracking on ch9):
```
Length: 12 (0x0C) - we're sending 12 MIDI bytes
MIDI message:
  0x90, 0x24, 0x7F  # Note-on channel 0, note 36, velocity 127
  0x99, 0x24, 0x7F  # Note-on channel 9, note 36, velocity 127
  0x90, 0x24, 0x00  # Note-off channel 0, note 36
  0x99, 0x24, 0x00  # Note-off channel 9, note 36

Sysex bytes: [0x0C, 0x90, 0x24, 0x7F, 0x99, 0x24, 0x7F, 0x90, 0x24, 0x00, 0x99, 0x24, 0x00]
```

**Encoding Process:**
1. Build the sysex payload as a list of bytes (length + MIDI message)
2. Convert to a 520-bit integer (little-endian: first byte = bits 0-7)
3. Encode the integer as 75 7-bit blocks (520 bits ÷ 7 ≈ 75)
4. Add CRC (combined = value | (crc << 520))
5. Send via SysEx message with header `F0 00 32 09 49 04 00 40 02`

**Message Structure:**
- Header: `F0 00 32 09 49 04 00 40 02` (note: routing is 3 bytes, not 4)
- Address: 4 7-bit blocks (pad base address + 9)
- Length: 4 7-bit blocks (always 520 * 2 = 1040)
- Value: 77 7-bit blocks (75 for value + 2 for CRC)
- Footer: `F7`

# CRC

CRC computation every 7-bit value starting with the sixth value, excluding the F7 and CRC itself. The sixth value is right rotated by 4 bits, the next value by 5 bits and so on. The sum is then taken modulo 256 and subtracted from 0xff.

# More capabilities

The device has built-in chord and arpeggio subsystem.