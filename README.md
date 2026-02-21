# SMK25II MIDI Remote Script for Ableton Live

A custom MIDI Remote Script for the SMK25II MIDI controller, designed for Ableton Live 12 Suite.

## Features

**Implemented Modes:**
- **Mode 0 - Session**: 7×2 clip launcher with scene launch, red box navigation, tempo/volume controls
- **Mode 1 - Device**: 8-device selection, parameter control with banking, device/track navigation
- **Mode 2 - Mix**: Track volume control, mute/solo toggle, track navigation
- **Mode 3 - Sends**: Send control for 8 tracks, send selection, track navigation
- **Mode 5 - Browser/Instruments**: Device browser navigation with pad combination memorization
- **Mode 6 - Crossfader**: DJ-style crossfader control with A/B assignment
- **Mode 8 - Drums**: 16-pad drum grid (C1-D#2) with blue hand parameter control
- **Mode 9 - Drum Color**: Per-pad HSV color editing for drum pads

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

## Web-Based Reference Page

The script includes a built-in web server that provides a visual reference for all controller modes.

**Setup on iPhone/iPad (Full-Screen Mode):**
1. Find your PC's IP address (e.g., 192.168.1.X)
2. Open Safari on your device and go to `http://YOUR_PC_IP:8765`
3. Tap the **Share** button (square with arrow pointing up)
4. Scroll down and tap **"Add to Home Screen"**
5. Tap **"Add"**
6. Launch the app from your home screen - it will run full-screen without Safari UI!

**Desktop Browser:**
Simply navigate to `http://localhost:8765` or `http://YOUR_PC_IP:8765`

**Features:**
- Automatically displays reference for the current active mode
- Shows all 8 knob functions and 16 pad functions
- Updates in real-time when you switch modes
- Optimized for landscape orientation on mobile devices
- No app installation required - pure web-based

**Configuration:**
The web server port can be changed by editing `WEB_SERVER_PORT` in `MyController.py` (default: 8765)

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
- All mode pads: Channel 10 (Notes 36-51, CCs 36-51)
- Shift pads: Channel 10 (CCs 52-67)
- Session knobs: Channel 1 (CCs 21-28)
- Device knobs: Channel 3 (CCs 20-27)
- Mix knobs: Channel 4 (CCs 20-27)
- Sends knobs: Channel 5 (CCs 20-27)
- Browser knobs: Channel 6 (CCs 20-27)
- Crossfader knobs: Channel 7 (CCs 20-27)
- Drums knobs: Channel 2 (CCs 20-27)
- Drum Color knobs: Channel 11 (CCs 20-27)
- Shift knobs: Channel 15 (CCs 20-27)

## Requirements

- Ableton Live 12 Suite
- SMK25II MIDI controller
- Python 2.7 (included with Ableton)

## Status

**Implemented:**
- ✅ Session mode (clip launching, scene launch, transport controls)
- ✅ Device mode (parameter control, device/track navigation)
- ✅ Mix mode (volume, mute/solo, track navigation)
- ✅ Sends mode (send control, send selection, track navigation)
- ✅ Browser/Instruments mode (device browser navigation, pad memorization)
- ✅ Crossfader mode (DJ-style crossfader control)
- ✅ Drums mode (16-pad drum grid with parameter control)
- ✅ Drum Color mode (per-pad HSV color editing)
- ✅ Mode selection and switching (via MCP/Shift button)
- ✅ Global shift knobs (track/scene navigation, undo/redo, etc.)
- ✅ Web-based reference page (runs on port 8765)

**Planned:**
- Mode 4 - Edit Clip (clip editing and manipulation)

## License

[Add your license here]

## Contributing

Contributions welcome! Please follow the existing code structure and ensure all files compile before submitting.

## Credits

Developed with Claude AI assistance.
