"""Mode reference data for all controller modes."""


class ModeReference:
    """Provides reference information for all modes."""

    # Mode reference data
    MODES = {
        0: {  # Session Mode
            'name': 'Session',
            'description': 'Track control with clip launching',
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
            'description': 'Control device parameters (blue hand)',
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
            'description': 'Select modes and global navigation (hold MCP button)',
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
        5: {  # Browser Mode
            'name': 'Browser',
            'description': 'Navigate browser and manage devices',
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
