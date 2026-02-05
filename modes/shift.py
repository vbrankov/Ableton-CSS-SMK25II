"""Shift mode - Mode selector displayed when shift is held."""

from .base import ModeBase
from ..Hardware import PAD_TYPE_NOTE, COLOR_WHITE, COLOR_OFF

# Shift page settings
SHIFT_PAD_CHANNEL = 15  # Channel 16
SHIFT_PAD_BASE_NOTE = 36


class ShiftMode(ModeBase):
    """Shift mode - Mode selector display."""

    def __init__(self, controller, hardware):
        # Shift mode doesn't have a mode number
        super().__init__(controller, hardware, mode_number=-1)

    def configure(self):
        """Configure shift page pads."""
        self.log("Configuring shift page pads...")

        # Configure all 16 pads for mode selection
        for i in range(16):
            self._hw.configure_pad(
                pad_index=i,
                pad_type=PAD_TYPE_NOTE,
                channel=SHIFT_PAD_CHANNEL,
                note=SHIFT_PAD_BASE_NOTE + i,
                shifted=True
            )

        # Set all shift page LEDs to ON (255)
        self.log("Setting shift page LEDs to 255...")
        for i in range(16):
            self._hw.set_pad_led_state(i, 255, shifted=True)

        self.log("Shift page pads configured.")

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

    def disconnect(self):
        """Cleanup when leaving shift mode."""
        pass
