"""Device mode for SMK25II - control device parameters."""

import Live
from .base import ModeBase
from ..Hardware import (
    PAD_TYPE_NOTE,
    COLOR_WHITE, COLOR_DIM_WHITE, COLOR_OFF,
    COLOR_BLUE, COLOR_ORANGE
)

# Pad configuration
DEVICE_PAD_CHANNEL = 2  # Channel 3 (0-indexed)
DEVICE_PAD_BASE_NOTE = 36  # C1

# Knob configuration
DEVICE_KNOB_CHANNEL = 2  # Channel 3
DEVICE_KNOB_BASE_CC = 20  # CC 20-27

# Pad indices
TOP_ROW_START = 0  # Device selection pads 0-7
BOTTOM_ROW_START = 8  # Function pads 8-15

# Bottom row functions
PAD_BANK_LEFT = 8
PAD_BANK_RIGHT = 9
PAD_DEVICE_LEFT = 10
PAD_DEVICE_RIGHT = 11
PAD_TRACK_LEFT = 12
PAD_TRACK_RIGHT = 13
PAD_UNDO = 14
PAD_REDO = 15


class DeviceMode(ModeBase):
    """Device mode - control device parameters."""

    def __init__(self, controller, hardware, mode_number):
        super(DeviceMode, self).__init__(controller, hardware, mode_number)
        self._device_index = 0  # Selected device on current track
        self._bank_offset = 0  # Parameter bank offset (0, 8, 16, ...)
        self._device_listeners = []  # Track device-related listeners

    def configure(self):
        """Configure hardware for device mode."""
        self.log("Configuring device mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Configure all 16 pads as notes
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=DEVICE_PAD_CHANNEL,
                note=DEVICE_PAD_BASE_NOTE + i,
                shifted=False
            )

        # Set all LEDs to ON (255)
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=False)

        # Configure knobs as relative (CW type)
        self._configure_device_knobs()

        # Add listeners for device changes
        self._add_device_listeners()

        # Initial update
        self.update()

        self.log("Device mode configured.")

    def _configure_device_knobs(self):
        """Configure 8 knobs for device parameters."""
        self.log("Configuring device knobs...")
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=DEVICE_KNOB_CHANNEL,
                cc=DEVICE_KNOB_BASE_CC + i,
                shifted=False
            )

    def update(self):
        """Update pad colors and knob mappings."""
        song = self.song()
        track = song.view.selected_track

        # Get devices on current track
        devices = list(track.devices) if hasattr(track, 'devices') else []

        # Update top row (device selection pads 0-7)
        for i in range(8):
            pad_idx = i
            if i < len(devices):
                # Device exists - show as selectable
                is_selected = (i == self._device_index)
                color = COLOR_BLUE if is_selected else COLOR_DIM_WHITE
            else:
                # No device at this index
                color = COLOR_OFF

            self._hw.set_pad_color(pad_idx, color, shifted=False)

        # Update bottom row (function pads 8-15)
        # Bank navigation pads
        self._hw.set_pad_color(PAD_BANK_LEFT, COLOR_ORANGE, shifted=False)
        self._hw.set_pad_color(PAD_BANK_RIGHT, COLOR_ORANGE, shifted=False)

        # Device navigation pads
        self._hw.set_pad_color(PAD_DEVICE_LEFT, COLOR_ORANGE, shifted=False)
        self._hw.set_pad_color(PAD_DEVICE_RIGHT, COLOR_ORANGE, shifted=False)

        # Track navigation pads
        self._hw.set_pad_color(PAD_TRACK_LEFT, COLOR_ORANGE, shifted=False)
        self._hw.set_pad_color(PAD_TRACK_RIGHT, COLOR_ORANGE, shifted=False)

        # Undo/redo pads
        self._hw.set_pad_color(PAD_UNDO, COLOR_WHITE, shifted=False)
        self._hw.set_pad_color(PAD_REDO, COLOR_WHITE, shifted=False)

    def handle_pad(self, pad_index, velocity):
        """Handle pad press in device mode."""
        if velocity == 0:  # Release
            return

        song = self.song()
        track = song.view.selected_track
        devices = list(track.devices) if hasattr(track, 'devices') else []

        # Top row: device selection (0-7)
        if 0 <= pad_index <= 7:
            if pad_index < len(devices):
                self._device_index = pad_index
                song.view.select_device(devices[pad_index])
                self.log(f"Selected device {pad_index}: {devices[pad_index].name}")
                self.update()

        # Bottom row: functions (8-15)
        elif pad_index == PAD_BANK_LEFT:
            self._bank_offset = max(0, self._bank_offset - 8)
            self.log(f"Bank offset: {self._bank_offset}")

        elif pad_index == PAD_BANK_RIGHT:
            self._bank_offset += 8
            self.log(f"Bank offset: {self._bank_offset}")

        elif pad_index == PAD_DEVICE_LEFT:
            # Navigate devices by 8
            new_index = max(0, self._device_index - 8)
            if new_index < len(devices):
                self._device_index = new_index
                song.view.select_device(devices[new_index])
                self.update()

        elif pad_index == PAD_DEVICE_RIGHT:
            # Navigate devices by 8
            new_index = self._device_index + 8
            if new_index < len(devices):
                self._device_index = new_index
                song.view.select_device(devices[new_index])
                self.update()

        elif pad_index == PAD_TRACK_LEFT:
            # Navigate tracks by 8
            self._navigate_tracks(-8)

        elif pad_index == PAD_TRACK_RIGHT:
            # Navigate tracks by 8
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
        """Handle knob turn in device mode."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        song = self.song()
        device = song.view.selected_device

        if not device:
            self.log("No device selected")
            return

        # Get device parameters
        params = list(device.parameters)
        param_index = self._bank_offset + knob_index

        if param_index < len(params):
            param = params[param_index]

            # Skip non-automatable parameters
            if not param.is_enabled or param.is_quantized:
                return

            # Adjust parameter value
            current = param.value
            param_range = param.max - param.min
            step_size = param_range * 0.02  # 2% per step
            new_value = max(param.min, min(param.max, current + delta * step_size))
            param.value = new_value

            self.log(f"Knob {knob_index}: {param.name} = {new_value:.2f}")
        else:
            self.log(f"No parameter at bank {self._bank_offset} + knob {knob_index}")

    def _navigate_tracks(self, delta):
        """Navigate tracks by delta amount."""
        song = self.song()
        tracks = song.visible_tracks
        view = song.view

        try:
            current_index = list(tracks).index(view.selected_track)
        except (ValueError, AttributeError):
            current_index = 0

        new_index = current_index + delta
        new_index = max(0, min(len(tracks) - 1, new_index))

        if new_index < len(tracks):
            view.selected_track = tracks[new_index]
            self._device_index = 0  # Reset to first device on new track
            self._bank_offset = 0  # Reset bank offset
            self.update()
            self.log(f"Selected track: {tracks[new_index].name}")

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
            self.log(f"ERROR: Unexpected relative knob value: {value}")
            return 0

    def _add_device_listeners(self):
        """Add listeners for device changes."""
        song = self.song()
        view = song.view

        # Listen for selected device changes
        def device_changed():
            self.log("Device changed")
            self.update()

        view.add_selected_track_listener(device_changed)
        self._device_listeners.append(('selected_track', device_changed))

    def _remove_device_listeners(self):
        """Remove device listeners."""
        song = self.song()
        view = song.view

        for listener_type, listener in self._device_listeners:
            if listener_type == 'selected_track':
                view.remove_selected_track_listener(listener)

        self._device_listeners = []

    def disconnect(self):
        """Cleanup when leaving device mode."""
        self.log("Disconnecting device mode...")
        self._remove_device_listeners()
