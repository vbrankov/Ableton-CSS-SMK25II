"""Shift mode - Mode selector displayed when shift is held."""

from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE, COLOR_WHITE, COLOR_OFF

# Shift page settings
SHIFT_PAD_CHANNEL = 9  # Channel 10
SHIFT_PAD_BASE_NOTE = 52  # Notes 52-67 (regular pads use 36-51)


class ShiftMode(ModeBase):
    """Shift mode - Mode selector display."""

    def __init__(self, controller, hardware):
        # Shift mode doesn't have a mode number
        super().__init__(controller, hardware, mode_number=-1)

    def configure(self):
        """Configure shift page pads."""
        # Configure shift pads as MCP type
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=SHIFT_PAD_CHANNEL,
                note=SHIFT_PAD_BASE_NOTE + i,
                shifted=True
            )
            # Set LED state to ON
            self._hw.set_pad_led_state(i, 255, shifted=True)

    def update(self):
        """Update shift page colors to show selected mode."""
        current_mode = self._controller.get_current_mode()

        # All 16 pads represent modes 0-15
        for i in range(16):
            if i == current_mode:
                self._hw.set_pad_color(i, COLOR_WHITE, shifted=True)
            else:
                self._hw.set_pad_color(i, COLOR_OFF, shifted=True)

    def handle_pad(self, pad_index, velocity):
        """Handle mode selection pad press."""
        if velocity > 0:  # Press
            self._controller.switch_mode(pad_index)
            self.update()

    def handle_knob(self, knob_index, value):
        """Handle knob in shift mode (shift knobs)."""
        # Delegate to controller's shift knob handler
        self._controller.handle_shift_knob(knob_index, value)

    def get_pad_labels(self):
        """Get mode names for each pad (modes 0-15)."""
        # Import here to avoid circular dependency
        from ..MyController import MODE_NAMES
        return [MODE_NAMES.get(i, f"Mode {i}") for i in range(16)]

    def get_pad_colors(self):
        """Get pad colors (white for current mode, off for others)."""
        from ..Hardware import COLOR_WHITE, COLOR_OFF
        current_mode = self._controller.get_current_mode()
        return [COLOR_WHITE if i == current_mode else COLOR_OFF for i in range(16)]

    def disconnect(self):
        """Cleanup when leaving shift mode."""
        pass
