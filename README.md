# SMK25II MIDI Remote Script for Ableton Live

A custom MIDI Remote Script for the SMK25II MIDI controller, designed for Ableton Live 12 Suite.

## Features

**Implemented Modes:**
- **Mode 0 - Session**: 7×2 clip launcher with scene launch, red box navigation, tempo/volume controls
- **Mode 2 - Device**: 8-device selection, parameter control with banking, device/track navigation
- **Mode 8 - Drums**: 16-pad drum grid (C1-D#2)

**Global Features:**
- Mode selection via MCP/Shift button
- Shift knobs for global navigation (track/scene selection, undo/redo, volumes)
- Dynamic LED colors based on clip/device state
- Efficient MIDI communication with caching and throttling

## Installation

1. Copy the entire `SMK25II` folder to your Ableton MIDI Remote Scripts directory:
   - **Windows**: `C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\`
   - **macOS**: `/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/`

2. Restart Ableton Live

3. In Ableton's Preferences → Link/Tempo/MIDI:
   - **IMPORTANT**: The SMK25II appears as three separate MIDI ports
   - **Enable all three SMK25II input sources** (turn on Track, Sync, and Remote for each)
   - **Set Control Surface to "SMK25II" ONLY on the first SMK25II port**
   - Leave Control Surface blank for the other two ports
   - This configuration is required for all modes to work correctly (especially Drum Color mode)

## Usage

See **[USER_MANUAL.md](USER_MANUAL.md)** for detailed controls reference.

**Quick Start:**
1. Press **MCP button** to select modes
2. Top-left pad (0) = Session mode
3. Third pad (2) = Device mode
4. Bottom-left pad (8) = Drums mode

## Project Structure

```
SMK25II/
├── __init__.py              # Entry point
├── MyController.py          # Main controller (mode management, MIDI routing)
├── Hardware.py              # Hardware abstraction (pads, knobs, LEDs)
├── ProtocolHandler.py       # SysEx protocol for SMK25II
├── MidiSender.py           # MIDI sending with throttling and caching
├── modes/
│   ├── base.py             # ModeBase abstract class
│   ├── session.py          # Session mode implementation
│   ├── device.py           # Device mode implementation
│   ├── drums.py            # Drums mode implementation
│   └── shift.py            # Shift/mode selector
├── design.md               # Design specifications
├── device.md               # SMK25II hardware documentation
└── USER_MANUAL.md          # User controls reference
```

## Architecture

The script uses a modular mode-based architecture:

- **ModeBase**: Abstract base class defining the mode interface
- Each mode implements: `configure()`, `update()`, `handle_pad()`, `handle_knob()`, `disconnect()`
- MyController handles mode switching and MIDI routing
- Hardware abstraction layer handles device-specific protocol

## Adding New Modes

1. Create new file in `modes/` directory (e.g., `modes/mix.py`)
2. Inherit from `ModeBase`
3. Implement the 5 required methods
4. Register in `MyController._init_modes()`
5. Add MIDI forwarding in `build_midi_map()` and `receive_midi()`

See existing modes for examples.

## Technical Details

**MIDI Communication:**
- Minimum 1ms interval between messages
- Caching prevents redundant updates
- SysEx protocol for hardware configuration
- Relative knob encoding: 0x7F=clockwise, 0x00=counter-clockwise

**Color Format:**
- RGB: R (lowest byte) | G<<8 | B<<16
- LED state: 0-127=off, 128-255=on

**Channels:**
- Session: Pads=13, Knobs=0
- Device: Pads=2, Knobs=2
- Drums: Pads=0
- Shift: Pads=15, Knobs=14

## Requirements

- Ableton Live 12 Suite
- SMK25II MIDI controller
- Python 2.7 (included with Ableton)

## Status

**Implemented:**
- ✅ Session mode (clip launching, scene launch, transport controls)
- ✅ Device mode (parameter control, device/track navigation)
- ✅ Drums mode (basic 16-pad grid)
- ✅ Mode selection and switching
- ✅ Global shift knobs

**Planned:**
- Mode 3 - Sends
- Mode 4 - Mix
- Mode 5 - Edit Clip
- Mode 6 - Instruments
- Mode 9 - Drum Color

## License

[Add your license here]

## Contributing

Contributions welcome! Please follow the existing code structure and ensure all files compile before submitting.

## Credits

Developed with Claude AI assistance.
