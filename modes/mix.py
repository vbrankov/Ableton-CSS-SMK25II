"""Mix mode for SMK25II - control track volumes, mute, solo."""

import Live
from .base import ModeBase
from ..Hardware import (
    PAD_TYPE_NOTE,
    COLOR_WHITE, COLOR_OFF,
    COLOR_ORANGE, COLOR_DIM_WHITE
)

# Pad configuration
MIX_PAD_CHANNEL = 9  # Channel 4 (0-indexed)
MIX_PAD_BASE_NOTE = 36  # C1

# Knob configuration
MIX_KNOB_CHANNEL = 3  # Channel 4
MIX_KNOB_BASE_CC = 20  # CC 20-27

# Pad indices
TOP_ROW_START = 0  # Track mute/solo pads 0-7
BOTTOM_ROW_START = 8  # Function pads 8-15

# Bottom row functions
PAD_MODE_MUTE = 8
PAD_MODE_SOLO = 9
PAD_UNUSED_1 = 10
PAD_UNUSED_2 = 11
PAD_TRACK_LEFT = 12
PAD_TRACK_RIGHT = 13
PAD_UNDO = 14
PAD_REDO = 15

# Mix modes
MODE_MUTE = 0
MODE_SOLO = 1


class MixMode(ModeBase):
    """Mix mode - control track volumes, mute, solo."""

    def __init__(self, controller, hardware, mode_number):
        super(MixMode, self).__init__(controller, hardware, mode_number)
        self._track_offset = 0  # Track offset for 8-track window
        self._mix_mode = MODE_MUTE  # Start in mute mode
        self._track_listeners = []  # Track-related listeners

    def configure(self):
        """Configure hardware for mix mode."""
        self.log("Configuring mix mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all 16 pads as notes
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=MIX_PAD_CHANNEL,
                note=MIX_PAD_BASE_NOTE + i,
                shifted=False
            )

        # Set all LEDs to ON (255)
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs as relative (CW type)
        self._configure_mix_knobs()

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

        self.log("Mix mode configured.")

    def _configure_mix_knobs(self):
        """Configure 8 knobs for track volumes."""
        self.log("Configuring mix knobs...")
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=MIX_KNOB_CHANNEL,
                cc=MIX_KNOB_BASE_CC + i,
                shifted=False
            )

    def update(self):
        """Update pad colors and knob mappings."""
        song = self.song()
        tracks = song.visible_tracks

        # Update top row (track mute/solo pads 0-7)
        for i in range(8):
            track_idx = self._track_offset + i
            if track_idx < len(tracks):
                track = tracks[track_idx]
                track_color = self._get_track_color_rgb(track)

                # Check mute/solo state based on current mode
                if self._mix_mode == MODE_MUTE:
                    is_active = track.mute
                else:  # MODE_SOLO
                    is_active = track.solo

                # Full color if muted/soloed, dim if not
                if is_active:
                    color = track_color
                else:
                    color = self._dim_color(track_color)
            else:
                # No track at this index
                color = COLOR_OFF

            self._hw.set_pad_color(i, color, shifted=False)

        # Update bottom row (function pads 8-15)
        # Mode selector pads show which mode is active
        if self._mix_mode == MODE_MUTE:
            self._hw.set_pad_color(PAD_MODE_MUTE, COLOR_ORANGE, shifted=False)
            self._hw.set_pad_color(PAD_MODE_SOLO, COLOR_DIM_WHITE, shifted=False)
        else:  # MODE_SOLO
            self._hw.set_pad_color(PAD_MODE_MUTE, COLOR_DIM_WHITE, shifted=False)
            self._hw.set_pad_color(PAD_MODE_SOLO, COLOR_ORANGE, shifted=False)

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
        """Handle pad press in mix mode."""
        if velocity == 0:  # Release
            return

        song = self.song()
        tracks = song.visible_tracks

        # Top row: track mute/solo (0-7)
        if 0 <= pad_index <= 7:
            track_idx = self._track_offset + pad_index
            if track_idx < len(tracks):
                track = tracks[track_idx]

                # Toggle mute or solo based on current mode
                if self._mix_mode == MODE_MUTE:
                    track.mute = not track.mute
                else:  # MODE_SOLO
                    track.solo = not track.solo

                self.update()

        # Bottom row: functions (8-15)
        elif pad_index == PAD_MODE_MUTE:
            self._mix_mode = MODE_MUTE
            self.log("Mix mode: Mute")
            self.update()

        elif pad_index == PAD_MODE_SOLO:
            self._mix_mode = MODE_SOLO
            self.log("Mix mode: Solo")
            self.update()

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
        """Handle knob turn in mix mode - control track volume."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        song = self.song()
        tracks = song.visible_tracks
        track_idx = self._track_offset + knob_index

        if track_idx < len(tracks):
            track = tracks[track_idx]

            # Get track mixer device
            if hasattr(track, 'mixer_device'):
                mixer = track.mixer_device
                volume_param = mixer.volume

                current = volume_param.value
                param_range = volume_param.max - volume_param.min
                step_size = param_range * 0.02  # 2% per step
                new_value = max(volume_param.min, min(volume_param.max, current + delta * step_size))
                volume_param.value = new_value

                self.log(f"Track {track.name}: volume = {new_value:.2f}")

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

    def _add_track_listeners(self):
        """Add listeners for track changes."""
        song = self.song()
        tracks = song.visible_tracks

        # Listen for track list changes
        def tracks_changed():
            self.log("Tracks changed")
            self._remove_track_listeners()
            self._add_track_listeners()
            self.update()

        song.add_visible_tracks_listener(tracks_changed)
        self._track_listeners.append(('visible_tracks', tracks_changed))

        # Listen for mute/solo changes on all tracks
        for track in tracks:
            def mute_changed():
                self.update()

            def solo_changed():
                self.update()

            track.add_mute_listener(mute_changed)
            track.add_solo_listener(solo_changed)
            self._track_listeners.append(('track_mute', track, mute_changed))
            self._track_listeners.append(('track_solo', track, solo_changed))

    def _remove_track_listeners(self):
        """Remove track listeners."""
        song = self.song()

        for listener_info in self._track_listeners:
            listener_type = listener_info[0]

            if listener_type == 'visible_tracks':
                _, listener = listener_info
                song.remove_visible_tracks_listener(listener)
            elif listener_type in ['track_mute', 'track_solo']:
                _, track, listener = listener_info
                try:
                    if listener_type == 'track_mute':
                        track.remove_mute_listener(listener)
                    else:
                        track.remove_solo_listener(listener)
                except:
                    pass

        self._track_listeners = []

    def disconnect(self):
        """Cleanup when leaving mix mode."""
        self.log("Disconnecting mix mode...")
        self._remove_track_listeners()
