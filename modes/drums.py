"""Drums mode (Mode 8) - Drum pad mode."""

import os
import json
import colorsys
from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE

# Drum mode settings
DRUM_CHANNEL = 0  # Channel 1
DRUM_BASE_NOTE = 36  # C1
COLOR_DRUM = 0x00A0FF  # Orange

# Knob configuration for device control
DRUM_KNOB_CHANNEL = 1  # Channel 2
DRUM_KNOB_BASE_CC = 20  # CC 20-27


class DrumsMode(ModeBase):
    """Drums mode - Basic drum pad grid."""

    def __init__(self, controller, hardware, mode_number):
        super(DrumsMode, self).__init__(controller, hardware, mode_number)
        self._pad_colors = None  # Will be loaded from config if available

    def configure(self):
        """Configure hardware for drums mode."""
        self.log("Configuring drums mode...")

        # Clear hardware cache
        self._hw.clear_cache()

        # Load colors from drum_color config if available
        self._load_colors()

        # Configure all pads as drum notes
        # Swap rows: top row (0-7) gets upper notes (44-51), bottom row (8-15) gets lower notes (36-43)
        for i in range(16):
            if i < 8:
                # Top row - upper octave (notes 44-51)
                note = DRUM_BASE_NOTE + 8 + i
            else:
                # Bottom row - lower octave (notes 36-43)
                note = DRUM_BASE_NOTE + (i - 8)

            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=DRUM_CHANNEL,
                note=note,
                shifted=False
            )
            # Set color - use saved color if available, otherwise orange
            color = self._pad_colors[i] if self._pad_colors else COLOR_DRUM
            self._hw.set_pad_color(i, color, shifted=False)

        # Configure knobs for device control (blue hand)
        for i in range(8):
            self._hw.configure_knob(
                knob_index=i,
                channel=DRUM_KNOB_CHANNEL,
                cc=DRUM_KNOB_BASE_CC + i,
                shifted=False
            )

        self.log("Drums mode configured.")

    def update(self):
        """Update drum mode (no dynamic updates needed)."""
        pass

    def handle_pad(self, pad_index, velocity):
        """Handle pad press (notes sent automatically by hardware)."""
        pass

    def handle_knob(self, knob_index, value):
        """Handle knob turn in drums mode - control device parameters."""
        delta = self._decode_relative_value(value)
        if delta == 0:
            return

        song = self.song()
        track = song.view.selected_track

        # Get first device on track (typically the instrument/drum rack)
        devices = list(track.devices) if hasattr(track, 'devices') else []
        if not devices:
            return

        device = devices[0]  # Control first device (e.g., Instrument Rack)

        # Get device parameters
        params = list(device.parameters)
        param_index = knob_index + 1  # Skip "Device On" parameter at index 0

        if param_index < len(params):
            param = params[param_index]

            # Skip non-enabled parameters
            if not param.is_enabled:
                return

            current = param.value
            param_range = param.max - param.min

            # Handle quantized parameters (switches, selectors)
            if param.is_quantized:
                new_value = current + delta
            else:
                # For continuous params, use percentage step
                step_size = param_range * 0.02  # 2% per step
                new_value = current + delta * step_size

            # Clamp to valid range
            new_value = max(param.min, min(param.max, new_value))
            param.value = new_value

            self.log(f"Knob {knob_index}: {param.name} = {new_value:.2f}")

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

    def _load_colors(self):
        """Load colors from drum_color config for current instrument."""
        try:
            song = self.song()
            track = song.view.selected_track

            # Get first device on track
            devices = list(track.devices) if hasattr(track, 'devices') else []
            if not devices:
                return

            device = devices[0]
            instrument_id = self._get_instrument_id(device)

            # Load config file
            home = os.path.expanduser("~")
            config_file = os.path.join(home, ".config", "SMK25II", "drum_colors.json")

            if not os.path.exists(config_file):
                return

            with open(config_file, 'r') as f:
                data = json.load(f)
                instrument_colors = data.get('instruments', {})

                if instrument_id in instrument_colors:
                    # Convert HSV to RGB for each pad
                    hsv_colors = instrument_colors[instrument_id]
                    self._pad_colors = [self._hsv_to_rgb(*hsv) for hsv in hsv_colors]
                    self.log(f"Loaded colors for instrument: {instrument_id}")

        except Exception as e:
            self.log(f"Could not load colors: {e}")

    def _get_instrument_id(self, device):
        """Get a unique identifier for the instrument device."""
        try:
            return f"{device.class_name}:{device.name}"
        except:
            return "unknown"

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB integer (for LED)."""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        return r | (g << 8) | (b << 16)

    def disconnect(self):
        """Cleanup when leaving drums mode."""
        self.log("Disconnecting drums mode...")
