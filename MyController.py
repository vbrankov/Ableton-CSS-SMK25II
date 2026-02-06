"""Main controller for SMK25II MIDI Remote Script."""

import Live
from _Framework.ControlSurface import ControlSurface
from .Hardware import Hardware
from .modes import SessionMode, DrumsMode, ShiftMode, DeviceMode, MixMode, SendsMode, CrossfaderMode

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
        self.log_message("SMK25II: Initializing...")

        # Hardware abstraction
        self._hw = Hardware(c_instance.send_midi, self.log_message)
        self._hardware_initialized = False

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
        self._modes[MODE_6] = CrossfaderMode(self, self._hw, MODE_6)
        self._modes[MODE_DRUMS] = DrumsMode(self, self._hw, MODE_DRUMS)
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

        # Configure shift mode pads
        self._shift_mode.configure()
        self._shift_mode.update()

        # Switch to initial mode
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

        self.log_message(f"Switching mode: {self._current_mode_number} -> {mode_number}")

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

        # Configure and activate new mode
        if self._current_mode:
            self._current_mode.configure()
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

            # Shift page pads (mode selection)
            if channel == 15:  # SHIFT_PAD_CHANNEL
                pad_index = note - 36  # SHIFT_PAD_BASE_NOTE
                if 0 <= pad_index < 16:
                    self._shift_mode.handle_pad(pad_index, velocity)
            # Device mode pads (channel 2)
            elif channel == 2 and self._current_mode_number == MODE_DEVICE:
                pad_index = note - 36
                if 0 <= pad_index < 16:
                    self._current_mode.handle_pad(pad_index, velocity)
            # Session mode pads (channel 13)
            elif channel == 13 and self._current_mode_number == MODE_SESSION:
                pad_index = note - 36
                if 0 <= pad_index < 16:
                    self._current_mode.handle_pad(pad_index, velocity)
            # Mix mode pads (channel 3)
            elif channel == 3 and self._current_mode_number == MODE_MIX:
                pad_index = note - 36
                if 0 <= pad_index < 16:
                    self._current_mode.handle_pad(pad_index, velocity)
            # Sends mode pads (channel 4)
            elif channel == 4 and self._current_mode_number == MODE_SENDS:
                pad_index = note - 36
                if 0 <= pad_index < 16:
                    self._current_mode.handle_pad(pad_index, velocity)
            # Crossfader mode pads (channel 5)
            elif channel == 5 and self._current_mode_number == MODE_6:
                pad_index = note - 36
                if 0 <= pad_index < 16:
                    self._current_mode.handle_pad(pad_index, velocity)
            # Drums mode pads (channel 0) - pass through to Ableton, not handled here

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
            # Crossfader mode knobs (channel 5, CC 20-27)
            elif channel == 5 and 20 <= cc <= 27 and self._current_mode_number == MODE_6:
                knob_index = cc - 20
                self._current_mode.handle_knob(knob_index, value)

    def build_midi_map(self, midi_map_handle):
        """Build MIDI map for Live."""
        # Import Live MIDI map functions
        script_handle = self._c_instance.handle()

        # Forward shift pad notes for mode selection
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                15,  # SHIFT_PAD_CHANNEL
                36 + i  # SHIFT_PAD_BASE_NOTE + i
            )

        # Forward shift knob CCs
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                SHIFT_KNOB_CHANNEL,
                SHIFT_KNOB_BASE_CC + i
            )

        # Forward session mode pads and knobs
        # Session pads (channel 13, notes 36-51)
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                13,  # TRACK_CTRL_CHANNEL
                36 + i
            )

        # Session knobs (channel 0, CC 21-28)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                0,  # SESSION_KNOB_CHANNEL
                21 + i  # SESSION_KNOB_BASE_CC + i
            )

        # Drums pads (channel 0, notes 36-51) - NOT forwarded, pass through to Ableton
        # These notes go directly to Ableton for drum triggering

        # Device mode pads (channel 2, notes 36-51)
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                2,  # DEVICE_PAD_CHANNEL
                36 + i
            )

        # Device mode knobs (channel 2, CC 20-27)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                2,  # DEVICE_KNOB_CHANNEL
                20 + i
            )

        # Drum mode knobs (channel 1, CC 20-27)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                1,  # DRUM_KNOB_CHANNEL
                20 + i
            )

        # Mix mode pads (channel 3, notes 36-51)
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                3,  # MIX_PAD_CHANNEL
                36 + i
            )

        # Mix mode knobs (channel 3, CC 20-27)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                3,  # MIX_KNOB_CHANNEL
                20 + i
            )

        # Sends mode pads (channel 4, notes 36-51)
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                4,  # SENDS_PAD_CHANNEL
                36 + i
            )

        # Sends mode knobs (channel 4, CC 20-27)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                4,  # SENDS_KNOB_CHANNEL
                20 + i
            )

        # Crossfader mode pads (channel 5, notes 36-51)
        for i in range(16):
            Live.MidiMap.forward_midi_note(
                script_handle,
                midi_map_handle,
                5,  # CROSSFADER_PAD_CHANNEL
                36 + i
            )

        # Crossfader mode knobs (channel 5, CC 20-27)
        for i in range(8):
            Live.MidiMap.forward_midi_cc(
                script_handle,
                midi_map_handle,
                5,  # CROSSFADER_KNOB_CHANNEL
                20 + i
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
            self.log_message(f"Selected track: {tracks[new_index].name}")

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
            self.log_message(f"Selected scene: {new_index + 1}")

    def _shift_blue_hand(self, delta):
        """Move blue hand (device focus)."""
        self.log_message(f"Blue hand: {delta}")
        # TODO: Implement blue hand movement

    def _shift_zoom(self, delta):
        """Zoom in/out."""
        self.log_message(f"Zoom: {delta}")
        # TODO: Implement zoom

    def _shift_playhead(self, delta):
        """Rewind/fast forward playhead."""
        song = self.song()
        current_pos = song.current_song_time
        # Move by 1 bar per step
        bars_per_step = 1
        seconds_per_bar = 60.0 / song.tempo * 4  # Assuming 4/4
        new_pos = max(0, current_pos + delta * seconds_per_bar)
        song.current_song_time = new_pos
        self.log_message(f"Playhead: {new_pos:.2f}s")

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
                self.log_message(f"Loop start: {new_start:.2f}s")

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
            self.log_message(f"Loop length: {new_length:.2f}s")

    def _shift_undo_redo(self, delta):
        """Undo/redo operations."""
        song = self.song()
        if delta < 0:
            if song.can_undo:
                song.undo()
                self.log_message("Undo")
        else:
            if song.can_redo:
                song.redo()
                self.log_message("Redo")

    # =========================================================================
    # Cleanup
    # =========================================================================

    def disconnect(self):
        """Cleanup when script is unloaded."""
        self.log_message("SMK25II: Disconnecting...")

        # Disconnect current mode
        if self._current_mode:
            self._current_mode.disconnect()

        super(MyController, self).disconnect()
        self.log_message("SMK25II: Disconnected.")
