"""Mode reference data for all controller modes."""


class ModeReference:
    """Provides reference information for all modes."""

    # Mode reference data
    MODES = {
        0: {  # Session Mode
            'name': 'Session',
            'description': 'Launch and control clips across 7 tracks and 2 scenes with global transport controls.',
            'knobs': [
                {'num': 0, 'name': 'Scroll Horizontal', 'detail': 'Move session box left/right'},
                {'num': 1, 'name': 'Scroll Vertical', 'detail': 'Move session box up/down'},
                {'num': 2, 'name': 'Pad Mode', 'detail': '0=Play/Stop, 1=Stop Only, 2=Record'},
                {'num': 3, 'name': 'Quantization', 'detail': 'Adjust clip trigger quantization'},
                {'num': 4, 'name': 'Tempo', 'detail': 'Adjust BPM (20-999)'},
                {'num': 5, 'name': 'Metronome', 'detail': 'Right=ON, Left=OFF'},
                {'num': 6, 'name': 'Master Volume', 'detail': 'Adjust master track volume'},
                {'num': 7, 'name': 'Undo/Redo', 'detail': 'Left=Undo, Right=Redo'},
            ],
            'pads': {
                'type': 'grid',  # Special grid layout
                'grid': [
                    ['Clip T1S1', 'Clip T2S1', 'Clip T3S1', 'Clip T4S1', 'Clip T5S1', 'Clip T6S1', 'Clip T7S1', 'Scene 1'],
                    ['Clip T1S2', 'Clip T2S2', 'Clip T3S2', 'Clip T4S2', 'Clip T5S2', 'Clip T6S2', 'Clip T7S2', 'Scene 2'],
                ],
                'notes': [
                    'Clip Pads (0-6, 8-14): Launch/stop clips on 7 tracks × 2 scenes. Color matches track.',
                    'Scene Pads (7, 15): Launch all clips in scene 1 or 2.',
                ],
                'legend': [
                    {'color': '#555', 'text': 'Dim = No clip'},
                    {'color': '#0f0', 'text': 'Bright = Has clip'},
                    {'color': '#fff', 'text': 'White blend = Playing'},
                    {'color': '#f00', 'text': 'Red blend = Recording'},
                ]
            }
        },
        1: {  # Device Mode
            'name': 'Device',
            'description': 'Control the 8 blue hand parameters of the selected device on the current track.',
            'knobs': [
                {'num': 0, 'name': 'Parameter 1', 'detail': 'Control 1st device parameter'},
                {'num': 1, 'name': 'Parameter 2', 'detail': 'Control 2nd device parameter'},
                {'num': 2, 'name': 'Parameter 3', 'detail': 'Control 3rd device parameter'},
                {'num': 3, 'name': 'Parameter 4', 'detail': 'Control 4th device parameter'},
                {'num': 4, 'name': 'Parameter 5', 'detail': 'Control 5th device parameter'},
                {'num': 5, 'name': 'Parameter 6', 'detail': 'Control 6th device parameter'},
                {'num': 6, 'name': 'Parameter 7', 'detail': 'Control 7th device parameter'},
                {'num': 7, 'name': 'Parameter 8', 'detail': 'Control 8th device parameter'},
            ],
            'pads': {
                'type': 'list',
                'items': [
                    {'num': 0, 'name': 'Device 1', 'detail': 'Select 1st device on track'},
                    {'num': 1, 'name': 'Device 2', 'detail': 'Select 2nd device on track'},
                    {'num': 2, 'name': 'Device 3', 'detail': 'Select 3rd device on track'},
                    {'num': 3, 'name': 'Device 4', 'detail': 'Select 4th device on track'},
                    {'num': 4, 'name': 'Device 5', 'detail': 'Select 5th device on track'},
                    {'num': 5, 'name': 'Device 6', 'detail': 'Select 6th device on track'},
                    {'num': 6, 'name': 'Device 7', 'detail': 'Select 7th device on track'},
                    {'num': 7, 'name': 'Device 8', 'detail': 'Select 8th device on track'},
                    {'num': 8, 'name': 'Bank Left', 'detail': 'Previous 8 parameters'},
                    {'num': 9, 'name': 'Bank Right', 'detail': 'Next 8 parameters'},
                    {'num': 10, 'name': 'Device -8', 'detail': 'Jump 8 devices back'},
                    {'num': 11, 'name': 'Device +8', 'detail': 'Jump 8 devices forward'},
                    {'num': 12, 'name': 'Track -8', 'detail': 'Jump 8 tracks left'},
                    {'num': 13, 'name': 'Track +8', 'detail': 'Jump 8 tracks right'},
                    {'num': 14, 'name': 'Undo', 'detail': 'Undo last action'},
                    {'num': 15, 'name': 'Redo', 'detail': 'Redo last undone action'},
                ],
                'notes': [
                    'Top row (0-7): Select one of 8 devices on current track. Blue = selected.',
                    'Bottom row (8-15): Navigate banks, devices, tracks, and undo/redo.',
                ]
            }
        },
        -1: {  # Shift Mode (Mode Selector)
            'name': 'Shift/Mode Selector',
            'description': 'Switch between modes and access global navigation controls by holding the MCP button.',
            'knobs': [
                {'num': 0, 'name': 'Select Track', 'detail': 'Navigate tracks left/right'},
                {'num': 1, 'name': 'Select Scene', 'detail': 'Navigate scenes up/down'},
                {'num': 2, 'name': 'Blue Hand', 'detail': 'Move device focus'},
                {'num': 3, 'name': 'Zoom', 'detail': 'Zoom in/out'},
                {'num': 4, 'name': 'Playhead', 'detail': 'Rewind/Fast forward'},
                {'num': 5, 'name': 'Loop Start', 'detail': 'Adjust loop start position'},
                {'num': 6, 'name': 'Loop Length', 'detail': 'Adjust loop length'},
                {'num': 7, 'name': 'Undo/Redo', 'detail': 'Left=Undo, Right=Redo'},
            ],
            'pads': {
                'type': 'mode_selector',
                'items': []  # Will be populated dynamically with mode names
            }
        },
        2: {  # Mix Mode
            'name': 'Mix',
            'description': 'Adjust track volumes and toggle mute/solo for 8 tracks at a time.',
            'knobs': [
                {'num': 0, 'name': 'Track 1 Volume', 'detail': 'Control volume for track 1'},
                {'num': 1, 'name': 'Track 2 Volume', 'detail': 'Control volume for track 2'},
                {'num': 2, 'name': 'Track 3 Volume', 'detail': 'Control volume for track 3'},
                {'num': 3, 'name': 'Track 4 Volume', 'detail': 'Control volume for track 4'},
                {'num': 4, 'name': 'Track 5 Volume', 'detail': 'Control volume for track 5'},
                {'num': 5, 'name': 'Track 6 Volume', 'detail': 'Control volume for track 6'},
                {'num': 6, 'name': 'Track 7 Volume', 'detail': 'Control volume for track 7'},
                {'num': 7, 'name': 'Track 8 Volume', 'detail': 'Control volume for track 8'},
            ],
            'pads': {
                'type': 'list',
                'items': [
                    {'num': 0, 'name': 'Track 1 Mute/Solo', 'detail': 'Toggle mute or solo for track 1'},
                    {'num': 1, 'name': 'Track 2 Mute/Solo', 'detail': 'Toggle mute or solo for track 2'},
                    {'num': 2, 'name': 'Track 3 Mute/Solo', 'detail': 'Toggle mute or solo for track 3'},
                    {'num': 3, 'name': 'Track 4 Mute/Solo', 'detail': 'Toggle mute or solo for track 4'},
                    {'num': 4, 'name': 'Track 5 Mute/Solo', 'detail': 'Toggle mute or solo for track 5'},
                    {'num': 5, 'name': 'Track 6 Mute/Solo', 'detail': 'Toggle mute or solo for track 6'},
                    {'num': 6, 'name': 'Track 7 Mute/Solo', 'detail': 'Toggle mute or solo for track 7'},
                    {'num': 7, 'name': 'Track 8 Mute/Solo', 'detail': 'Toggle mute or solo for track 8'},
                    {'num': 8, 'name': 'Mute Mode', 'detail': 'Switch to mute mode (orange when active)'},
                    {'num': 9, 'name': 'Solo Mode', 'detail': 'Switch to solo mode (orange when active)'},
                    {'num': 10, 'name': '—', 'detail': 'Unused'},
                    {'num': 11, 'name': '—', 'detail': 'Unused'},
                    {'num': 12, 'name': 'Track -8', 'detail': 'Jump 8 tracks left'},
                    {'num': 13, 'name': 'Track +8', 'detail': 'Jump 8 tracks right'},
                    {'num': 14, 'name': 'Undo', 'detail': 'Undo last action'},
                    {'num': 15, 'name': 'Redo', 'detail': 'Redo last undone action'},
                ],
                'notes': [
                    'Top row (0-7): Mute/Solo for 8 tracks. Color shows track color (bright=active, dim=inactive).',
                    'Bottom row: Pads 8-9 select mute/solo mode, 12-13 navigate tracks.',
                ]
            }
        },
        3: {  # Sends Mode
            'name': 'Sends',
            'description': 'Control send levels for 8 tracks to the selected return track.',
            'knobs': [
                {'num': 0, 'name': 'Track 1 Send', 'detail': 'Send level for track 1 to selected return'},
                {'num': 1, 'name': 'Track 2 Send', 'detail': 'Send level for track 2 to selected return'},
                {'num': 2, 'name': 'Track 3 Send', 'detail': 'Send level for track 3 to selected return'},
                {'num': 3, 'name': 'Track 4 Send', 'detail': 'Send level for track 4 to selected return'},
                {'num': 4, 'name': 'Track 5 Send', 'detail': 'Send level for track 5 to selected return'},
                {'num': 5, 'name': 'Track 6 Send', 'detail': 'Send level for track 6 to selected return'},
                {'num': 6, 'name': 'Track 7 Send', 'detail': 'Send level for track 7 to selected return'},
                {'num': 7, 'name': 'Track 8 Send', 'detail': 'Send level for track 8 to selected return'},
            ],
            'pads': {
                'type': 'list',
                'items': [
                    {'num': 0, 'name': 'Send 1', 'detail': 'Select send 1 (return track 1)'},
                    {'num': 1, 'name': 'Send 2', 'detail': 'Select send 2 (return track 2)'},
                    {'num': 2, 'name': 'Send 3', 'detail': 'Select send 3 (return track 3)'},
                    {'num': 3, 'name': 'Send 4', 'detail': 'Select send 4 (return track 4)'},
                    {'num': 4, 'name': 'Send 5', 'detail': 'Select send 5 (return track 5)'},
                    {'num': 5, 'name': 'Send 6', 'detail': 'Select send 6 (return track 6)'},
                    {'num': 6, 'name': 'Send 7', 'detail': 'Select send 7 (return track 7)'},
                    {'num': 7, 'name': 'Send 8', 'detail': 'Select send 8 (return track 8)'},
                    {'num': 8, 'name': 'Send -8', 'detail': 'Jump 8 sends back'},
                    {'num': 9, 'name': 'Send +8', 'detail': 'Jump 8 sends forward'},
                    {'num': 10, 'name': '—', 'detail': 'Unused'},
                    {'num': 11, 'name': '—', 'detail': 'Unused'},
                    {'num': 12, 'name': 'Track -8', 'detail': 'Jump 8 tracks left'},
                    {'num': 13, 'name': 'Track +8', 'detail': 'Jump 8 tracks right'},
                    {'num': 14, 'name': 'Undo', 'detail': 'Undo last action'},
                    {'num': 15, 'name': 'Redo', 'detail': 'Redo last undone action'},
                ],
                'notes': [
                    'Top row (0-7): Select which send/return track to control. Blue = selected.',
                    'Knobs control send levels for the selected send across 8 tracks.',
                ]
            }
        },
        5: {  # Browser Mode
            'name': 'Browser',
            'description': 'Navigate Ableton\'s browser, add/delete tracks, and manage devices on tracks.',
            'knobs': [
                {'num': 0, 'name': 'Navigate Tracks', 'detail': 'Move between tracks'},
                {'num': 1, 'name': 'Add/Delete Track', 'detail': 'Right=Add, Left=Delete'},
                {'num': 2, 'name': 'Navigate Hierarchy', 'detail': 'Right=Enter folder, Left=Exit'},
                {'num': 3, 'name': 'Scroll Items', 'detail': 'Browse items one by one'},
                {'num': 4, 'name': 'Navigate Devices', 'detail': 'Select device on track'},
                {'num': 5, 'name': 'Reorder Devices', 'detail': 'Move device left/right'},
                {'num': 6, 'name': 'Delete Device', 'detail': 'Remove selected device'},
                {'num': 7, 'name': 'Undo/Redo', 'detail': 'Left=Undo, Right=Redo'},
            ],
            'pads': {
                'type': 'list',
                'items': [
                    {'num': 0, 'name': 'Level 1 Indicator', 'detail': 'Lights when browsing level 1'},
                    {'num': 1, 'name': 'Level 2 Indicator', 'detail': 'Lights when browsing level 2'},
                    {'num': 2, 'name': 'Level 3 Indicator', 'detail': 'Lights when browsing level 3'},
                    {'num': 3, 'name': 'Level 4 Indicator', 'detail': 'Lights when browsing level 4'},
                    {'num': '4-15', 'name': 'Memorization', 'detail': 'Hold 1s + turn knob to save item, tap to load'},
                ],
                'notes': [
                    'Pads 0-3: Show current browser level (blue, green, red, yellow)',
                    'Pads 4-15: Memorize browser items to pad combinations',
                ]
            }
        },
        6: {  # Crossfader Mode
            'name': 'Crossfader',
            'description': 'Assign tracks to crossfader sides (A/B) and control the crossfader position.',
            'knobs': [
                {'num': 0, 'name': 'Navigate Tracks', 'detail': 'Scroll track window left/right'},
                {'num': 1, 'name': '—', 'detail': 'Unused'},
                {'num': 2, 'name': '—', 'detail': 'Unused'},
                {'num': 3, 'name': '—', 'detail': 'Unused'},
                {'num': 4, 'name': '—', 'detail': 'Unused'},
                {'num': 5, 'name': '—', 'detail': 'Unused'},
                {'num': 6, 'name': '—', 'detail': 'Unused'},
                {'num': 7, 'name': 'Crossfader', 'detail': 'Control crossfader position'},
            ],
            'pads': {
                'type': 'list',
                'items': [
                    {'num': 0, 'name': 'Track 1 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 1, 'name': 'Track 2 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 2, 'name': 'Track 3 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 3, 'name': 'Track 4 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 4, 'name': 'Track 5 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 5, 'name': 'Track 6 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 6, 'name': 'Track 7 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 7, 'name': 'Track 8 Assign', 'detail': 'Cycle: None → A → B → None'},
                    {'num': 8, 'name': 'Crossfader Left', 'detail': 'Snap crossfader to A (left)'},
                    {'num': 9, 'name': 'Crossfader Center', 'detail': 'Snap crossfader to center'},
                    {'num': 10, 'name': 'Crossfader Right', 'detail': 'Snap crossfader to B (right)'},
                    {'num': 11, 'name': '—', 'detail': 'Unused'},
                    {'num': 12, 'name': 'Track -8', 'detail': 'Jump 8 tracks left'},
                    {'num': 13, 'name': 'Track +8', 'detail': 'Jump 8 tracks right'},
                    {'num': 14, 'name': 'Undo', 'detail': 'Undo last action'},
                    {'num': 15, 'name': 'Redo', 'detail': 'Redo last undone action'},
                ],
                'notes': [
                    'Top row: Assign tracks to crossfader. Red=A, Blue=B, Dim=None.',
                    'Pads 8-10: Quick snap to left/center/right positions.',
                ]
            }
        },
        8: {  # Drums Mode
            'name': 'Drums',
            'description': 'Play drum sounds with velocity-sensitive pads colored by your saved presets.',
            'knobs': [
                {'num': 0, 'name': 'Device Param 1', 'detail': 'Control 1st parameter of drum device'},
                {'num': 1, 'name': 'Device Param 2', 'detail': 'Control 2nd parameter of drum device'},
                {'num': 2, 'name': 'Device Param 3', 'detail': 'Control 3rd parameter of drum device'},
                {'num': 3, 'name': 'Device Param 4', 'detail': 'Control 4th parameter of drum device'},
                {'num': 4, 'name': 'Device Param 5', 'detail': 'Control 5th parameter of drum device'},
                {'num': 5, 'name': 'Device Param 6', 'detail': 'Control 6th parameter of drum device'},
                {'num': 6, 'name': 'Device Param 7', 'detail': 'Control 7th parameter of drum device'},
                {'num': 7, 'name': 'Device Param 8', 'detail': 'Control 8th parameter of drum device'},
            ],
            'pads': {
                'type': 'grid',
                'grid': [
                    ['Note 44', 'Note 45', 'Note 46', 'Note 47', 'Note 48', 'Note 49', 'Note 50', 'Note 51'],
                    ['Note 36', 'Note 37', 'Note 38', 'Note 39', 'Note 40', 'Note 41', 'Note 42', 'Note 43'],
                ],
                'notes': [
                    'All 16 pads send MIDI notes to play drum sounds (notes 36-51).',
                    'Colors are loaded from saved settings (use Mode 9 to edit).',
                    'Knobs control device parameters (typically drum rack macros).',
                ]
            }
        },
        9: {  # Drum Color Mode
            'name': 'Drum Color',
            'description': 'Customize the color of each drum pad using HSV or RGB controls.',
            'knobs': [
                {'num': 0, 'name': 'Hue', 'detail': 'Adjust hue for selected pads'},
                {'num': 1, 'name': 'Saturation', 'detail': 'Adjust saturation for selected pads'},
                {'num': 2, 'name': 'Brightness', 'detail': 'Adjust brightness for selected pads'},
                {'num': 3, 'name': 'Red', 'detail': 'Adjust red channel for selected pads'},
                {'num': 4, 'name': 'Green', 'detail': 'Adjust green channel for selected pads'},
                {'num': 5, 'name': 'Blue', 'detail': 'Adjust blue channel for selected pads'},
                {'num': 6, 'name': 'Match Color', 'detail': 'Move selected pads toward last-pressed color'},
                {'num': 7, 'name': 'History', 'detail': 'Navigate through previous instrument layouts'},
            ],
            'pads': {
                'type': 'grid',
                'grid': [
                    ['Pad 0', 'Pad 1', 'Pad 2', 'Pad 3', 'Pad 4', 'Pad 5', 'Pad 6', 'Pad 7'],
                    ['Pad 8', 'Pad 9', 'Pad 10', 'Pad 11', 'Pad 12', 'Pad 13', 'Pad 14', 'Pad 15'],
                ],
                'notes': [
                    'Press and hold multiple pads, then turn knobs to edit their colors.',
                    'Colors are saved per instrument and automatically loaded in Mode 8.',
                    'Note: Enable "Track" on Port 2 in MIDI settings to hear sounds while editing.',
                ]
            }
        }
    }

    @classmethod
    def get_mode(cls, mode_number):
        """Get reference data for a mode."""
        return cls.MODES.get(mode_number, None)

    @classmethod
    def get_all_modes(cls):
        """Get all available mode numbers."""
        return sorted(cls.MODES.keys())
