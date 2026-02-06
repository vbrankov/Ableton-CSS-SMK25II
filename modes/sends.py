"""Sends mode for SMK25II - control track send levels."""

import Live
from .base import ModeBase
from ..Hardware import (
    PAD_TYPE_NOTE,
    COLOR_WHITE, COLOR_OFF, COLOR_DIM_WHITE,
    COLOR_ORANGE, COLOR_BLUE, COLOR_GREEN
)

# Pad configuration
SENDS_PAD_CHANNEL = 4  # Channel 5 (0-indexed)
SENDS_PAD_BASE_NOTE = 36  # C1

# Knob configuration
SENDS_KNOB_CHANNEL = 4  # Channel 5
SENDS_KNOB_BASE_CC = 20  # CC 20-27

# Pad indices
TOP_ROW_START = 0  # Send selection pads 0-7
BOTTOM_ROW_START = 8  # Function pads 8-15

# Bottom row functions
PAD_SEND_LEFT = 8
PAD_SEND_RIGHT = 9
PAD_UNUSED_1 = 10
PAD_UNUSED_2 = 11
PAD_TRACK_LEFT = 12
PAD_TRACK_RIGHT = 13
PAD_UNDO = 14
PAD_REDO = 15


class SendsMode(ModeBase):
    """Sends mode - control track send levels."""

    def __init__(self, controller, hardware, mode_number):
        super(SendsMode, self).__init__(controller, hardware, mode_number)
        self._track_offset = 0  # Track offset for 8-track window
        self._send_index = 0  # Selected send (0-7)
        self._track_listeners = []  # Track-related listeners

    def configure(self):
        """Configure hardware for sends mode."""
        self.log("Configuring sends mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all 16 pads as notes
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=SENDS_PAD_CHANNEL,
                note=SENDS_PAD_BASE_NOTE + i,
                shifted=False
            )

        # Set all LEDs to ON (255)
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs as relative (CW type)
        self._configure_sends_knobs()

        # Add listeners for track changes
        self._add_track_listeners()

        # Set initial red box position
        self._controller.set_session_highlight(
            self._track_offset,  # track_offset
            0,  # scene_offset
            8,  # width (8 tracks)
            1,  # height (1 scene)
            False  # include_return_tracks
        )

        # Initial update
        self.update()

        self.log("Sends mode configured.")

    def _configure_sends_knobs(self):
        """Configure 8 knobs for send levels."""
        self.log("Configuring sends knobs...")
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=SENDS_KNOB_CHANNEL,
                cc=SENDS_KNOB_BASE_CC + i,
                shifted=False
            )

    def update(self):
        """Update pad colors and knob mappings."""
        song = self.song()
        tracks = song.visible_tracks

        # Update top row (send selection pads 0-7)
        for i in range(8):
            if i == self._send_index:
                # Currently selected send
                color = COLOR_BLUE
            else:
                # Other sends
                color = COLOR_DIM_WHITE

            self._hw.set_pad_color(i, color, shifted=False)

        # Update bottom row (function pads 8-15)
        # Send navigation pads
        self._hw.set_pad_color(PAD_SEND_LEFT, COLOR_GREEN, shifted=False)
        self._hw.set_pad_color(PAD_SEND_RIGHT, COLOR_GREEN, shifted=False)

        # Unused pads
        self._hw.set_pad_color(PAD_UNUSED_1, COLOR_OFF, shifted=False)
        self._hw.set_pad_color(PAD_UNUSED_2, COLOR_OFF, shifted=False)

        # Track navigation pads
        self._hw.set_pad_color(PAD_TRACK_LEFT, COLOR_ORANGE, shifted=False)
        self._hw.set_pad_color(PAD_TRACK_RIGHT, COLOR_ORANGE, shifted=False)

        # Undo/redo pads
        self._hw.set_pad_color(PAD_UNDO, COLOR_WHITE, shifted=False)
        self._hw.set_pad_color(PAD_REDO, COLOR_WHITE, shifted=False)

    def handle_pad(self, pad_index, velocity):
        """Handle pad press in sends mode."""
        if velocity == 0:  # Release
            return

        song = self.song()

        # Top row: send selection (0-7)
        if 0 <= pad_index <= 7:
            self._send_index = pad_index
            self.log(f"Selected send {self._send_index}")
            self.update()

        # Bottom row: functions (8-15)
        elif pad_index == PAD_SEND_LEFT:
            self._navigate_sends(-8)

        elif pad_index == PAD_SEND_RIGHT:
            self._navigate_sends(8)

        elif pad_index == PAD_TRACK_LEFT:
            self._navigate_tracks(-8)

        elif pad_index == PAD_TRACK_RIGHT:
            self._navigate_tracks(8)

        elif pad_index == PAD_UNDO:
            if song.can_undo:
                song.undo()
                self.log("Undo")

        elif pad_index == PAD_REDO:
            if song.can_redo:
                song.redo()
                self.log("Redo")

    def handle_knob(self, knob_index, value):
        """Handle knob turn in sends mode - control send level."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        song = self.song()
        tracks = song.visible_tracks
        track_idx = self._track_offset + knob_index

        if track_idx < len(tracks):
            track = tracks[track_idx]

            # Get mixer device and sends
            if hasattr(track, 'mixer_device'):
                mixer = track.mixer_device
                sends = mixer.sends

                if self._send_index < len(sends):
                    send_param = sends[self._send_index]

                    current = send_param.value
                    param_range = send_param.max - send_param.min
                    step_size = param_range * 0.02  # 2% per step
                    new_value = max(send_param.min, min(send_param.max, current + delta * step_size))
                    send_param.value = new_value

                    self.log(f"Track {track.name}: send {self._send_index} = {new_value:.2f}")

    def _navigate_sends(self, delta):
        """Navigate sends by delta amount."""
        song = self.song()

        # Get number of available sends (return tracks)
        num_sends = len(song.return_tracks)

        # Don't navigate if there are no sends
        if num_sends == 0:
            return

        new_index = self._send_index + delta
        new_index = max(0, min(num_sends - 1, new_index))  # Limit to available sends

        if new_index != self._send_index:
            self._send_index = new_index
            self.update()
            self.log(f"Send index: {self._send_index}")

    def _navigate_tracks(self, delta):
        """Navigate tracks by delta amount."""
        song = self.song()
        tracks = song.visible_tracks

        new_offset = self._track_offset + delta
        new_offset = max(0, min(len(tracks) - 8, new_offset)) if len(tracks) > 8 else 0

        if new_offset != self._track_offset:
            self._track_offset = new_offset

            # Update red box to follow track offset
            self._controller.set_session_highlight(
                self._track_offset,  # track_offset
                0,  # scene_offset
                8,  # width (8 tracks)
                1,  # height (1 scene)
                False  # include_return_tracks
            )

            self.update()

    def _decode_relative_value(self, value):
        """Decode relative CC value to delta."""
        if value == 0x7F:
            return 1  # Clockwise
        elif value == 0x00:
            return -1  # Counter-clockwise
        else:
            self.log(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    def _add_track_listeners(self):
        """Add listeners for track changes."""
        song = self.song()

        # Listen for track list changes
        def tracks_changed():
            self.log("Tracks changed")
            self._remove_track_listeners()
            self._add_track_listeners()
            self.update()

        song.add_visible_tracks_listener(tracks_changed)
        self._track_listeners.append(('visible_tracks', tracks_changed))

    def _remove_track_listeners(self):
        """Remove track listeners."""
        song = self.song()

        for listener_info in self._track_listeners:
            listener_type = listener_info[0]

            if listener_type == 'visible_tracks':
                _, listener = listener_info
                song.remove_visible_tracks_listener(listener)

        self._track_listeners = []

    def disconnect(self):
        """Cleanup when leaving sends mode."""
        self.log("Disconnecting sends mode...")
        self._remove_track_listeners()
