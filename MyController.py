"""Main controller for SMK25II MIDI Remote Script."""

import Live
from _Framework.ControlSurface import ControlSurface
from .Hardware import Hardware
from .WebServer import WebServer
from .modes import SessionMode, DrumsMode, DrumColorMode, ShiftMode, DeviceMode, MixMode, SendsMode, CrossfaderMode, BrowserMode

# Mode definitions (0-15)
MODE_SESSION = 0
MODE_DEVICE = 1
MODE_MIX = 2
MODE_SENDS = 3
MODE_EDIT_CLIP = 4
MODE_INSTRUMENTS = 5
MODE_6 = 6
MODE_7 = 7
MODE_DRUMS = 8
MODE_DRUM_COLOR = 9
MODE_10 = 10
MODE_11 = 11
MODE_12 = 12
MODE_13 = 13
MODE_14 = 14
MODE_15 = 15

# Mode names for web display
MODE_NAMES = {
    MODE_SESSION: "Session",
    MODE_DEVICE: "Device",
    MODE_MIX: "Mix",
    MODE_SENDS: "Sends",
    MODE_EDIT_CLIP: "Edit Clip",
    MODE_INSTRUMENTS: "Browser",
    MODE_6: "Crossfader",
    MODE_7: "Mode 7",
    MODE_DRUMS: "Drums",
    MODE_DRUM_COLOR: "Drum Color",
    MODE_10: "Mode 10",
    MODE_11: "Mode 11",
    MODE_12: "Mode 12",
    MODE_13: "Mode 13",
    MODE_14: "Mode 14",
    MODE_15: "Mode 15",
}

# Web server settings (User-configurable)
WEB_SERVER_PORT = 8765  # Change this if port is already in use

# Shift knob settings
SHIFT_KNOB_CHANNEL = 14  # Channel 15
SHIFT_KNOB_BASE_CC = 20  # CC 20-27

# Shift knob functions
SHIFT_KNOB_SCROLL_H = 0
SHIFT_KNOB_SCROLL_V = 1
SHIFT_KNOB_BLUE_HAND = 2
SHIFT_KNOB_ZOOM = 3
SHIFT_KNOB_PLAYHEAD = 4
SHIFT_KNOB_LOOP_START = 5
SHIFT_KNOB_LOOP_LENGTH = 6
SHIFT_KNOB_UNDO_REDO = 7


class MyController(ControlSurface):
    """Main controller class for SMK25II."""

    def __init__(self, c_instance):
        super(MyController, self).__init__(c_instance)
        self.log_message("=" * 80)
        self.log_message("SMK25II: NEW SESSION STARTING")
        self.log_message("=" * 80)
        self.log_message("SMK25II: Initializing...")

        # Hardware abstraction
        self._hw = Hardware(c_instance.send_midi, self.log_message)
        self._hardware_initialized = False

        # Web server for browser-based status display
        self._web_server = WebServer(WEB_SERVER_PORT, self, self.log_message)
        self._web_server.start()

        # Mode management
        self._current_mode_number = MODE_SESSION
        self._current_mode = None
        self._shift_mode = None
        self._modes = {}

        # Initialize modes
        self._init_modes()

        self.log_message("SMK25II: Initialization complete.")

    def _init_modes(self):
        """Initialize all mode instances."""
        self.log_message("Initializing modes...")

        # Create mode instances
        self._modes[MODE_SESSION] = SessionMode(self, self._hw, MODE_SESSION)
        self._modes[MODE_DEVICE] = DeviceMode(self, self._hw, MODE_DEVICE)
        self._modes[MODE_MIX] = MixMode(self, self._hw, MODE_MIX)
        self._modes[MODE_SENDS] = SendsMode(self, self._hw, MODE_SENDS)
        self._modes[MODE_INSTRUMENTS] = BrowserMode(self, self._hw, MODE_INSTRUMENTS)
        self._modes[MODE_6] = CrossfaderMode(self, self._hw, MODE_6)
        self._modes[MODE_DRUMS] = DrumsMode(self, self._hw, MODE_DRUMS)
        self._modes[MODE_DRUM_COLOR] = DrumColorMode(self, self._hw, MODE_DRUM_COLOR)
        # Add more modes here as they're implemented

        # Create shift mode
        self._shift_mode = ShiftMode(self, self._hw)

        self.log_message(f"Initialized {len(self._modes)} modes.")

    def update(self):
        """Called by Live after __init__."""
        super(MyController, self).update()

        if not self._hardware_initialized:
            self._hardware_initialized = True
            self._init_hardware()

    def _init_hardware(self):
        """Initialize hardware on first update."""
        self.log_message("Initializing hardware...")

        # Enable bulk mode for faster init
        self._hw.set_bulk_mode(True)

        # Configure all modes once (hardware setup)
        for mode in self._modes.values():
            mode.configure()

        # Configure shift mode pads
        self._shift_mode.configure()
        self._shift_mode.update()

        # Switch to initial mode (just updates colors)
        self.switch_mode(self._current_mode_number)

        # Disable bulk mode
        self._hw.set_bulk_mode(False)

        # Request MIDI map rebuild to ensure routing is set up
        self.request_rebuild_midi_map()

        self.log_message("Hardware initialized.")

    # =========================================================================
    # Mode management
    # =========================================================================

    def get_current_mode(self):
        """Get current mode number."""
        return self._current_mode_number

    def get_status(self):
        """Get current controller status for web display."""
        status = {
            'mode': {
                'number': self._current_mode_number,
                'name': MODE_NAMES.get(self._current_mode_number, f"Mode {self._current_mode_number}")
            },
            'browser': {
                'level1': '',
                'level2': '',
                'level3': '',
                'level4': '',
                'active_level': 0
            },
            'pad_colors': [],
            'pad_labels': []
        }

        # Get browser-specific status if in browser mode
        if self._current_mode_number == MODE_INSTRUMENTS and self._current_mode:
            if hasattr(self._current_mode, 'get_status'):
                browser_status = self._current_mode.get_status()
                status['browser'] = browser_status

        # Get pad colors from current mode
        if self._current_mode and hasattr(self._current_mode, 'get_pad_colors'):
            pad_colors = self._current_mode.get_pad_colors()
            # Convert to CSS hex format
            status['pad_colors'] = [self._rgb_to_hex(c) for c in pad_colors]

        # Get pad labels from current mode (dynamic names like track/scene names)
        if self._current_mode and hasattr(self._current_mode, 'get_pad_labels'):
            status['pad_labels'] = self._current_mode.get_pad_labels()

        # Get knob labels from current mode (dynamic parameter names)
        status['knob_labels'] = []
        if self._current_mode and hasattr(self._current_mode, 'get_knob_labels'):
            status['knob_labels'] = self._current_mode.get_knob_labels()

        return status

    def _rgb_to_hex(self, rgb):
        """Convert hardware RGB format to CSS hex string."""
        if rgb is None or rgb == 0:
            return '#1a1a1a'  # Default dark gray
        r = (rgb >> 0) & 0xFF
        g = (rgb >> 8) & 0xFF
        b = (rgb >> 16) & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"

    def set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        """Set the session highlight (red box) in Ableton."""
        self._c_instance.set_session_highlight(
            track_offset, scene_offset, width, height, include_return_tracks
        )

    def switch_mode(self, mode_number):
        """Switch to a different mode."""
        # Don't skip if current_mode is None (initial setup)
        if mode_number == self._current_mode_number and self._current_mode is not None:
            return

        # Disconnect current mode
        if self._current_mode:
            self._current_mode.disconnect()

        # Get new mode instance (or create placeholder if not implemented)
        if mode_number in self._modes:
            self._current_mode = self._modes[mode_number]
        else:
            self.log_message(f"Mode {mode_number} not implemented, using placeholder")
            # Could create a PlaceholderMode here
            self._current_mode = None

        self._current_mode_number = mode_number

        # Just update colors - hardware is already configured
        if self._current_mode:
            self._current_mode.update()

        # Update shift page to show current mode
        self._shift_mode.update()

    # =========================================================================
    # MIDI handling
    # =========================================================================

    def receive_midi(self, midi_bytes):
        """Handle incoming MIDI."""
        if not midi_bytes or len(midi_bytes) < 2:
            return

        # Parse MIDI message
        status = midi_bytes[0]
        msg_type = status & 0xF0
        channel = status & 0x0F

        if len(midi_bytes) >= 2:
            data1 = midi_bytes[1]
        if len(midi_bytes) >= 3:
            data2 = midi_bytes[2]

        # Note On/Off
        if msg_type in [0x90, 0x80]:
            velocity = data2 if msg_type == 0x90 else 0
            note = data1

            # All pads on channel 9 (standard MIDI drum channel)
            if channel == 9:
                # Check if this is a shift pad (notes 52-67)
                if 52 <= note <= 67:
                    # Shift mode pads
                    pad_index = note - 52
                    self._shift_mode.handle_pad(pad_index, velocity)
                elif self._current_mode_number in [MODE_DRUMS, MODE_DRUM_COLOR]:
                    # Drum modes: Map notes to pad indices (rows are swapped)
                    # Notes 36-43 (lower notes) → pad indices 8-15 (bottom row)
                    # Notes 44-51 (higher notes) → pad indices 0-7 (top row)
                    if 36 <= note <= 43:
                        pad_index = note - 36 + 8  # Bottom row
                    elif 44 <= note <= 51:
                        pad_index = note - 44  # Top row
                    else:
                        pad_index = -1

                    if 0 <= pad_index < 16 and self._current_mode:
                        self._current_mode.handle_pad(pad_index, velocity)
                else:
                    # Regular modes: Simple pad index mapping (notes 36-51)
                    if 36 <= note <= 51:
                        pad_index = note - 36
                        if self._current_mode:
                            self._current_mode.handle_pad(pad_index, velocity)

        # CC (knobs)
        elif msg_type == 0xB0:
            cc = data1
            value = data2

            # Shift knobs
            if channel == SHIFT_KNOB_CHANNEL:
                knob_index = cc - SHIFT_KNOB_BASE_CC
                if 0 <= knob_index < 8:
                    self.handle_shift_knob(knob_index, value)
            # Device mode knobs (channel 2, CC 20-27)
            elif channel == 2 and 20 <= cc <= 27 and self._current_mode_number == MODE_DEVICE:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Session mode knobs (channel 0, CC 21-28)
            elif channel == 0 and 21 <= cc <= 28 and self._current_mode_number == MODE_SESSION:
                knob_index = cc - 21
                self._current_mode.handle_knob(knob_index, value)
            # Drum mode knobs (channel 1, CC 20-27)
            elif channel == 1 and 20 <= cc <= 27 and self._current_mode_number == MODE_DRUMS:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Mix mode knobs (channel 3, CC 20-27)
            elif channel == 3 and 20 <= cc <= 27 and self._current_mode_number == MODE_MIX:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Sends mode knobs (channel 4, CC 20-27)
            elif channel == 4 and 20 <= cc <= 27 and self._current_mode_number == MODE_SENDS:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Browser/Instruments mode knobs (channel 5, CC 20-27)
            elif channel == 5 and 20 <= cc <= 27 and self._current_mode_number == MODE_INSTRUMENTS:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Crossfader mode knobs (channel 6, CC 20-27)
            elif channel == 6 and 20 <= cc <= 27 and self._current_mode_number == MODE_6:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)
            # Drum Color mode knobs (channel 10, CC 20-27)
            elif channel == 10 and 20 <= cc <= 27 and self._current_mode_number == MODE_DRUM_COLOR:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)

    def build_midi_map(self, midi_map_handle):
        """Build MIDI map for Live."""

        # Forward pads (channel 9) - all pads send notes
        # Notes 36-51 for regular mode pads
        for note in range(36, 52):
            Live.MidiMap.forward_midi_note(
                self._c_instance.handle(),
                midi_map_handle,
                9,  # Channel 9 (standard MIDI drums)
                note
            )

        # Notes 52-67 for shift pads (on shifted hardware page)
        for note in range(52, 68):
            Live.MidiMap.forward_midi_note(
                self._c_instance.handle(),
                midi_map_handle,
                9,  # Channel 9
                note
            )

        # Forward knobs for each mode
        knob_channels = [
            (0, 21, 29),   # Session mode (CCs 21-28)
            (1, 20, 28),   # Drums mode
            (2, 20, 28),   # Device mode
            (3, 20, 28),   # Mix mode
            (4, 20, 28),   # Sends mode
            (5, 20, 28),   # Browser mode
            (6, 20, 28),   # Crossfader mode
            (10, 20, 28),  # Drum Color mode
            (14, 20, 28),  # Shift knobs
        ]

        for channel, cc_start, cc_end in knob_channels:
            for cc in range(cc_start, cc_end):
                Live.MidiMap.forward_midi_cc(
                    self._c_instance.handle(),
                    midi_map_handle,
                    channel,
                    cc
                )

    # =========================================================================
    # Shift knob handlers (global navigation)
    # =========================================================================

    def handle_shift_knob(self, knob_index, value):
        """Handle shift knob turns (global navigation)."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        if knob_index == SHIFT_KNOB_SCROLL_H:
            self._shift_scroll_horizontal(delta)
        elif knob_index == SHIFT_KNOB_SCROLL_V:
            self._shift_scroll_vertical(delta)
        elif knob_index == SHIFT_KNOB_BLUE_HAND:
            self._shift_blue_hand(delta)
        elif knob_index == SHIFT_KNOB_ZOOM:
            self._shift_zoom(delta)
        elif knob_index == SHIFT_KNOB_PLAYHEAD:
            self._shift_playhead(delta)
        elif knob_index == SHIFT_KNOB_LOOP_START:
            self._shift_loop_start(delta)
        elif knob_index == SHIFT_KNOB_LOOP_LENGTH:
            self._shift_loop_length(delta)
        elif knob_index == SHIFT_KNOB_UNDO_REDO:
            self._shift_undo_redo(delta)

    def _decode_relative_value(self, value):
        """Decode relative CC value to delta."""
        # Hardware sends ONLY two values:
        # 0x7F (127) = clockwise
        # 0x00 (0) = counter-clockwise
        if value == 0x7F:
            return 1  # Clockwise
        elif value == 0x00:
            return -1  # Counter-clockwise
        else:
            # Should never happen, log error
            self.log_message(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    def _shift_scroll_horizontal(self, delta):
        """Select track (shift knob 1)."""
        song = self.song()
        tracks = song.visible_tracks
        view = song.view

        # Find current track index
        try:
            current_index = list(tracks).index(view.selected_track)
        except (ValueError, AttributeError):
            current_index = 0

        # Move to next/prev track
        new_index = current_index + delta
        new_index = max(0, min(len(tracks) - 1, new_index))

        if new_index < len(tracks):
            view.selected_track = tracks[new_index]

    def _shift_scroll_vertical(self, delta):
        """Select scene (shift knob 2)."""
        song = self.song()
        scenes = song.scenes
        view = song.view

        # Find current scene index
        try:
            current_index = list(scenes).index(view.selected_scene)
        except (ValueError, AttributeError):
            current_index = 0

        # Move to next/prev scene
        new_index = current_index + delta
        new_index = max(0, min(len(scenes) - 1, new_index))

        if new_index < len(scenes):
            view.selected_scene = scenes[new_index]

    def _shift_blue_hand(self, delta):
        """Move blue hand (device focus)."""
        # TODO: Implement blue hand movement
        pass

    def _shift_zoom(self, delta):
        """Zoom in/out."""
        # TODO: Implement zoom
        pass

    def _shift_playhead(self, delta):
        """Rewind/fast forward playhead."""
        song = self.song()
        current_pos = song.current_song_time
        # Move by 1 bar per step
        bars_per_step = 1
        seconds_per_bar = 60.0 / song.tempo * 4  # Assuming 4/4
        new_pos = max(0, current_pos + delta * seconds_per_bar)
        song.current_song_time = new_pos

    def _shift_loop_start(self, delta):
        """Adjust loop start position."""
        song = self.song()
        if song.loop:
            loop_start = song.loop_start
            # Move by 1 beat per step
            beats_per_step = 1
            seconds_per_beat = 60.0 / song.tempo
            new_start = max(0, loop_start + delta * seconds_per_beat)
            # Don't move past loop end
            if new_start < song.loop_start + song.loop_length:
                song.loop_start = new_start

    def _shift_loop_length(self, delta):
        """Adjust loop length."""
        song = self.song()
        if song.loop:
            loop_length = song.loop_length
            # Adjust by 1 bar per step
            bars_per_step = 1
            seconds_per_bar = 60.0 / song.tempo * 4
            new_length = max(seconds_per_bar, loop_length + delta * seconds_per_bar)
            song.loop_length = new_length

    def _shift_undo_redo(self, delta):
        """Undo/redo operations."""
        song = self.song()
        if delta < 0:
            if song.can_undo:
                song.undo()
        else:
            if song.can_redo:
                song.redo()

    # =========================================================================
    # Cleanup
    # =========================================================================

    def disconnect(self):
        """Cleanup when script is unloaded."""
        self.log_message("SMK25II: Disconnecting...")

        # Disconnect current mode
        if self._current_mode:
            self._current_mode.disconnect()

        # Stop web server
        if self._web_server:
            self._web_server.stop()

        super(MyController, self).disconnect()
        self.log_message("SMK25II: Disconnected.")
