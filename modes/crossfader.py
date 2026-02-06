"""Crossfader mode for SMK25II - assign tracks to crossfader and control position."""

import Live
from .base import ModeBase
from ..Hardware import (
    PAD_TYPE_NOTE,
    COLOR_WHITE, COLOR_OFF, COLOR_DIM_WHITE,
    COLOR_ORANGE, COLOR_BLUE, COLOR_RED
)

# Pad configuration
CROSSFADER_PAD_CHANNEL = 5  # Channel 6 (0-indexed)
CROSSFADER_PAD_BASE_NOTE = 36  # C1

# Knob configuration
CROSSFADER_KNOB_CHANNEL = 5  # Channel 6
CROSSFADER_KNOB_BASE_CC = 20  # CC 20-27

# Pad indices
TOP_ROW_START = 0  # Track assignment pads 0-7
BOTTOM_ROW_START = 8  # Function pads 8-15

# Bottom row functions
PAD_CROSSFADER_LEFT = 8
PAD_CROSSFADER_CENTER = 9
PAD_CROSSFADER_RIGHT = 10
PAD_UNUSED = 11
PAD_TRACK_LEFT = 12
PAD_TRACK_RIGHT = 13
PAD_UNDO = 14
PAD_REDO = 15

# Crossfader assignments (Ableton API values)
CROSSFADER_A = 0
CROSSFADER_NONE = 1
CROSSFADER_B = 2


class CrossfaderMode(ModeBase):
    """Crossfader mode - assign tracks and control crossfader position."""

    def __init__(self, controller, hardware, mode_number):
        super(CrossfaderMode, self).__init__(controller, hardware, mode_number)
        self._track_offset = 0  # Track offset for 8-track window
        self._track_listeners = []  # Track-related listeners

    def configure(self):
        """Configure hardware for crossfader mode."""
        self.log("Configuring crossfader mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all 16 pads as notes
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=CROSSFADER_PAD_CHANNEL,
                note=CROSSFADER_PAD_BASE_NOTE + i,
                shifted=False
            )

        # Set all LEDs to ON (255)
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs as relative (CW type)
        self._configure_crossfader_knobs()

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

        self.log("Crossfader mode configured.")

    def _configure_crossfader_knobs(self):
        """Configure knobs for crossfader mode."""
        self.log("Configuring crossfader knobs...")
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=CROSSFADER_KNOB_CHANNEL,
                cc=CROSSFADER_KNOB_BASE_CC + i,
                shifted=False
            )

    def update(self):
        """Update pad colors and knob mappings."""
        song = self.song()
        tracks = song.visible_tracks

        # Update top row (track assignment pads 0-7)
        for i in range(8):
            track_idx = self._track_offset + i
            if track_idx < len(tracks):
                track = tracks[track_idx]
                track_color = self._get_track_color_rgb(track)

                # Get crossfader assignment
                if hasattr(track, 'mixer_device'):
                    assignment = track.mixer_device.crossfade_assign

                    # Color based on assignment
                    if assignment == CROSSFADER_A:
                        color = COLOR_RED  # A side - red (left)
                    elif assignment == CROSSFADER_B:
                        color = COLOR_BLUE  # B side - blue (right)
                    else:  # CROSSFADER_NONE
                        color = self._dim_color(track_color)  # Dim track color
                else:
                    color = self._dim_color(track_color)
            else:
                # No track at this index
                color = COLOR_OFF

            self._hw.set_pad_color(i, color, shifted=False)

        # Update bottom row (function pads 8-15)
        # Crossfader position shortcuts
        self._hw.set_pad_color(PAD_CROSSFADER_LEFT, COLOR_RED, shifted=False)  # A side (left, red)
        self._hw.set_pad_color(PAD_CROSSFADER_CENTER, COLOR_DIM_WHITE, shifted=False)  # Center
        self._hw.set_pad_color(PAD_CROSSFADER_RIGHT, COLOR_BLUE, shifted=False)  # B side (right, blue)

        # Unused pad
        self._hw.set_pad_color(PAD_UNUSED, COLOR_OFF, shifted=False)

        # Track navigation pads
        self._hw.set_pad_color(PAD_TRACK_LEFT, COLOR_ORANGE, shifted=False)
        self._hw.set_pad_color(PAD_TRACK_RIGHT, COLOR_ORANGE, shifted=False)

        # Undo/redo pads
        self._hw.set_pad_color(PAD_UNDO, COLOR_WHITE, shifted=False)
        self._hw.set_pad_color(PAD_REDO, COLOR_WHITE, shifted=False)

    def handle_pad(self, pad_index, velocity):
        """Handle pad press in crossfader mode."""
        if velocity == 0:  # Release
            return

        song = self.song()
        tracks = song.visible_tracks

        # Top row: track crossfader assignment (0-7)
        if 0 <= pad_index <= 7:
            track_idx = self._track_offset + pad_index
            if track_idx < len(tracks):
                track = tracks[track_idx]

                if hasattr(track, 'mixer_device'):
                    mixer = track.mixer_device
                    current = mixer.crossfade_assign

                    # Cycle through: None → A → B → None
                    if current == CROSSFADER_NONE:
                        mixer.crossfade_assign = CROSSFADER_A
                        self.log(f"Track {track.name}: assigned to A")
                    elif current == CROSSFADER_A:
                        mixer.crossfade_assign = CROSSFADER_B
                        self.log(f"Track {track.name}: assigned to B")
                    else:  # CROSSFADER_B
                        mixer.crossfade_assign = CROSSFADER_NONE
                        self.log(f"Track {track.name}: unassigned")

                    self.update()

        # Bottom row: functions (8-15)
        elif pad_index == PAD_CROSSFADER_LEFT:
            # Snap crossfader to left (A side)
            master_track = song.master_track
            if hasattr(master_track, 'mixer_device'):
                crossfader_param = master_track.mixer_device.crossfader
                crossfader_param.value = crossfader_param.min
                self.log("Crossfader: A (left)")

        elif pad_index == PAD_CROSSFADER_CENTER:
            # Snap crossfader to center
            master_track = song.master_track
            if hasattr(master_track, 'mixer_device'):
                crossfader_param = master_track.mixer_device.crossfader
                center = (crossfader_param.min + crossfader_param.max) / 2.0
                crossfader_param.value = center
                self.log("Crossfader: Center")

        elif pad_index == PAD_CROSSFADER_RIGHT:
            # Snap crossfader to right (B side)
            master_track = song.master_track
            if hasattr(master_track, 'mixer_device'):
                crossfader_param = master_track.mixer_device.crossfader
                crossfader_param.value = crossfader_param.max
                self.log("Crossfader: B (right)")

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
        """Handle knob turn in crossfader mode."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        song = self.song()

        # Knob 0: Scroll tracks (same as track navigation)
        if knob_index == 0:
            self._navigate_tracks(delta)

        # Knob 7 (8th knob): Control crossfader position
        elif knob_index == 7:
            master_track = song.master_track

            if hasattr(master_track, 'mixer_device'):
                mixer = master_track.mixer_device
                crossfader_param = mixer.crossfader

                current = crossfader_param.value
                param_range = crossfader_param.max - crossfader_param.min
                step_size = param_range * 0.02  # 2% per step
                new_value = max(crossfader_param.min, min(crossfader_param.max, current + delta * step_size))
                crossfader_param.value = new_value

                self.log(f"Crossfader: {new_value:.2f}")

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

    def _dim_color(self, color):
        """Dim a color by reducing each component."""
        if color == 0:
            return 0
        r = (color & 0xFF) >> 2  # Divide by 4
        g = ((color >> 8) & 0xFF) >> 2
        b = ((color >> 16) & 0xFF) >> 2
        return r | (g << 8) | (b << 16)

    def _get_track_color_rgb(self, track):
        """Get track color as RGB integer."""
        try:
            color_idx = track.color_index
            if color_idx is None or color_idx < 0:
                return COLOR_DIM_WHITE

            # Get color from Live's color table
            color_table = [
                0xFF5C5C, 0xFF7C7C, 0xFF9C9C, 0xFFBCBC,
                0xFFDCDC, 0xFFCCCC, 0xFFAAAA, 0xFF8888,
                0xFFFF5C, 0xFFFF7C, 0xFFFF9C, 0xFFFFBC,
                0xFFFFDC, 0xFFFFCC, 0xFFFFAA, 0xFFFF88,
                0x5CFF5C, 0x7CFF7C, 0x9CFF9C, 0xBCFFBC,
                0xDCFFDC, 0xCCFFCC, 0xAAFFAA, 0x88FF88,
                0x5CFFFF, 0x7CFFFF, 0x9CFFFF, 0xBCFFFF,
                0xDCFFFF, 0xCCFFFF, 0xAAFFFF, 0x88FFFF,
                0x5C5CFF, 0x7C7CFF, 0x9C9CFF, 0xBCBCFF,
                0xDCDCFF, 0xCCCCFF, 0xAAAAFF, 0x8888FF,
                0xFF5CFF, 0xFF7CFF, 0xFF9CFF, 0xFFBCFF,
                0xFFDCFF, 0xFFCCFF, 0xFFAAFF, 0xFF88FF,
                0xFFFFFF, 0xDDDDDD, 0xBBBBBB, 0x999999,
                0x777777, 0x555555, 0x333333, 0x111111
            ]

            if color_idx < len(color_table):
                return color_table[color_idx]
            return COLOR_DIM_WHITE
        except:
            return COLOR_DIM_WHITE

    def disconnect(self):
        """Cleanup when leaving crossfader mode."""
        self.log("Disconnecting crossfader mode...")
        self._remove_track_listeners()
