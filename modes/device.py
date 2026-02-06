"""Device mode for SMK25II - control device parameters."""

import Live
from .base import ModeBase
from ..Hardware import (
    PAD_TYPE_NOTE,
    COLOR_WHITE, COLOR_DIM_WHITE, COLOR_OFF,
    COLOR_BLUE, COLOR_ORANGE,
    COLOR_YELLOW, COLOR_CYAN, COLOR_MAGENTA
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
        self._devices_listener = None  # Current track's devices listener

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
        appointed_device = song.appointed_device

        # Update top row (device selection pads 0-7)
        for i in range(8):
            pad_idx = i
            if i < len(devices):
                # Device exists - show as selectable
                # Check if this device is the appointed device
                is_selected = (devices[i] == appointed_device)
                color = COLOR_BLUE if is_selected else COLOR_DIM_WHITE
            else:
                # No device at this index
                color = COLOR_OFF

            self._hw.set_pad_color(pad_idx, color, shifted=False)

        # Update bottom row (function pads 8-15)
        # Color pads in pairs for visual grouping

        # Bank navigation pads (yellow)
        self._hw.set_pad_color(PAD_BANK_LEFT, COLOR_YELLOW, shifted=False)
        self._hw.set_pad_color(PAD_BANK_RIGHT, COLOR_YELLOW, shifted=False)

        # Device navigation pads (cyan)
        self._hw.set_pad_color(PAD_DEVICE_LEFT, COLOR_CYAN, shifted=False)
        self._hw.set_pad_color(PAD_DEVICE_RIGHT, COLOR_CYAN, shifted=False)

        # Track navigation pads (magenta)
        self._hw.set_pad_color(PAD_TRACK_LEFT, COLOR_MAGENTA, shifted=False)
        self._hw.set_pad_color(PAD_TRACK_RIGHT, COLOR_MAGENTA, shifted=False)

        # Undo/redo pads (white)
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
                device = devices[pad_index]
                song.view.select_device(device)
                song.appointed_device = device  # Show blue hand
                self.log(f"Selected device {pad_index}: {device.name}")
                self.update()

        # Bottom row: functions (8-15)
        elif pad_index == PAD_BANK_LEFT:
            new_offset = max(0, self._bank_offset - 8)
            if new_offset != self._bank_offset:
                self._bank_offset = new_offset

        elif pad_index == PAD_BANK_RIGHT:
            # Check if device has more parameters before banking
            device = song.appointed_device
            if device:
                num_params = len(list(device.parameters))
                # Only bank if there are parameters beyond current bank
                # (We skip parameter 0, so check if there are params at offset+1+8)
                if self._bank_offset + 1 + 8 < num_params:
                    self._bank_offset += 8

        elif pad_index == PAD_DEVICE_LEFT:
            # Navigate devices by 8
            new_index = max(0, self._device_index - 8)
            if new_index < len(devices):
                self._device_index = new_index
                device = devices[new_index]
                song.view.select_device(device)
                song.appointed_device = device  # Show blue hand
                self.update()

        elif pad_index == PAD_DEVICE_RIGHT:
            # Navigate devices by 8
            new_index = self._device_index + 8
            if new_index < len(devices):
                self._device_index = new_index
                device = devices[new_index]
                song.view.select_device(device)
                song.appointed_device = device  # Show blue hand
                self.update()

        elif pad_index == PAD_TRACK_LEFT:
            # Navigate tracks by 1
            self._navigate_tracks(-1)

        elif pad_index == PAD_TRACK_RIGHT:
            # Navigate tracks by 1
            self._navigate_tracks(1)

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
        device = song.appointed_device

        if not device:
            self.log("No device selected")
            return

        # Get device parameters
        params = list(device.parameters)
        param_index = self._bank_offset + knob_index + 1  # Skip "Device On" parameter at index 0

        if param_index < len(params):
            param = params[param_index]

            # Skip non-automatable parameters
            if not param.is_enabled:
                return

            current = param.value
            param_range = param.max - param.min

            # Handle quantized parameters (switches, selectors)
            if param.is_quantized:
                # For quantized params, increment/decrement by delta directly
                # Works for on/off (0/1) and multi-value selectors
                new_value = current + delta
            else:
                # For continuous params, use percentage step
                step_size = param_range * 0.02  # 2% per step
                new_value = current + delta * step_size

            # Clamp to valid range
            new_value = max(param.min, min(param.max, new_value))
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

        # Listen for track changes
        def track_changed():
            self.log("Track changed")
            self._add_devices_listener()  # Re-add devices listener for new track
            self.update()

        view.add_selected_track_listener(track_changed)
        self._device_listeners.append(('selected_track', track_changed))

        # Listen for devices list changes on current track
        self._add_devices_listener()

        # Listen for appointed device changes
        def appointed_device_changed():
            self.log("Appointed device changed")
            # Sync device index with appointed device
            appointed = song.appointed_device
            if appointed:
                track = song.view.selected_track
                devices = list(track.devices) if hasattr(track, 'devices') else []
                try:
                    self._device_index = devices.index(appointed)
                    self.log(f"Synced device index to {self._device_index}")
                except ValueError:
                    # Appointed device not in current track's devices
                    pass
            self.update()

        song.add_appointed_device_listener(appointed_device_changed)
        self._device_listeners.append(('appointed_device', appointed_device_changed))

    def _add_devices_listener(self):
        """Add listener for devices list changes on current track."""
        # Remove old devices listener if it exists
        if self._devices_listener:
            try:
                song = self.song()
                track = song.view.selected_track
                if hasattr(track, 'devices'):
                    track.remove_devices_listener(self._devices_listener)
            except:
                pass
            self._devices_listener = None

        # Add new devices listener for current track
        def devices_changed():
            self.log("Devices list changed")
            self.update()

        try:
            song = self.song()
            track = song.view.selected_track
            if hasattr(track, 'devices'):
                track.add_devices_listener(devices_changed)
                self._devices_listener = devices_changed
                self.log("Added devices listener")
        except:
            self.log("Failed to add devices listener")

    def _remove_device_listeners(self):
        """Remove device listeners."""
        song = self.song()
        view = song.view

        for listener_type, listener in self._device_listeners:
            if listener_type == 'selected_track':
                view.remove_selected_track_listener(listener)
            elif listener_type == 'appointed_device':
                song.remove_appointed_device_listener(listener)

        self._device_listeners = []

        # Remove devices listener
        if self._devices_listener:
            try:
                track = song.view.selected_track
                if hasattr(track, 'devices'):
                    track.remove_devices_listener(self._devices_listener)
            except:
                pass
            self._devices_listener = None

    def disconnect(self):
        """Cleanup when leaving device mode."""
        self.log("Disconnecting device mode...")
        self._remove_device_listeners()
